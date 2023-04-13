from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from kanban.models import Task, Workspace, User
import json
from threading import Lock
from datetime import date, datetime
from django.core.exceptions import ValidationError

lock = Lock()
active_connections = 0

class MyConsumer(WebsocketConsumer):

    group_name = 'kanban_group'
    channel_name = 'kanban_channel'
    user = None

    def connect(self):

        self.accept()

        if not self.scope["user"].is_authenticated:
            self.send_error(f'You must be logged in')
            self.close()
            return      

        self.user = self.scope["user"]

        with lock:
            global active_connections
            active_connections += 1
            message = '{} active connections'.format(active_connections)
        self.broadcast_message(message)


    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name, self.channel_name
        )

        with lock:
            global active_connections
            active_connections -= 1
            message = '{} active connections'.format(active_connections)
        self.broadcast_message(message)


    def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except:
            self.send_error('invalid JSON sent to server')
            return

        if not 'action' in data:
            self.send_error('action property not sent in JSON')
            return

        action = data['action']

        if action == 'get-tasks':
            if not 'workspace' in data:
                self.send_error('workspace property not sent in JSON')
                return
            workspace_id = data['workspace']
            try:
                workspace = Workspace.objects.get(id=workspace_id)
            except Workspace.DoesNotExist:
                self.send_error(f'workspace={workspace_id} does not exist')
                return
            self.group_name = str(workspace_id)
            async_to_sync(self.channel_layer.group_add)(
                self.group_name, self.channel_name
            )
            self.broadcast_list(workspace)
            return

        if action == 'add-task':
            if not 'task' in data:
                self.send_error('task property not sent in JSON')
                return
            task = data['task']
            self.received_add(task)
            return

        if action == 'delete-task':
            self.received_delete(data)
            return

        self.send_error(f'Invalid action property: "{action}"')

    def validate_date(self, date_string):
        try:
            # parse the date string using the datetime module
            date = datetime.strptime(date_string, '%Y-%m-%d').date()
        except ValueError:
            # the date string is not in the expected format
            return False

        # validate the date using Django's DateField
        try:
            Task._meta.get_field('due_date').run_validators(date)
        except ValidationError:
            # the date is not valid according to the DateField validators
            return False

        # the date is valid according to Django's DateField
        return True
    
    def validate_authorization(self, workspace: Workspace):
        if self.user != workspace.creator and self.user not in workspace.participants:
            self.send_error(f'user="{self.user}" is not a participant of workspace_id={workspace.id}')
            return False
        return True

    def validate_task(self, data):
        task = {}

        if 'id' in data:
            id = data['id']
            task_query = Task.objects.filter(id=id)
            if not task_query.exists():
                self.send_error(f'task_id="{id}" does not exist')
                return None
            task_object = task_query.first()
            if not self.validate_authorization(task_object.workspace):
                return None
            task['id'] = id
            

        if 'workspace' in data:
            workspace_id = data['workspace']
            workspace_query = Workspace.objects.filter(id=workspace_id)
            if not workspace_query.exists():
                self.send_error(f'workspace_id="{workspace_id}" does not exist')
                return None
            workspace = workspace_query.first()
            if not self.validate_authorization(workspace):
                return None
            task['workspace'] = workspace

        if 'taskname' in data:
            taskname = data['taskname']
            try:
                Task._meta.get_field('taskname').run_validators(taskname)
            except ValidationError as e:
                self.send_error(f'taskname="{taskname}" is too long')
                return None
            task['taskname'] = taskname
        
        if 'description' in data:
            description = data['description']
            try:
                Task._meta.get_field('description').run_validators(description)
            except ValidationError as e:
                self.send_error(f'description="{description}" is too long')
                return None
            task['description'] = description

        if 'assignee' in data:
            assignee_id = data['assignee']
            assignee_query = User.objects.filter(id=assignee_id)
            if not assignee_query.exists():
                self.send_error(f'assignee_id="{assignee_id}" does not exist')
                return None
            assignee = assignee_query.first()
            if assignee != workspace.creator and not workspace.participants.filter(id=assignee.id).exists():
                self.send_error(f'assignee="{assignee}" is not a participant of workspace_id={workspace_id}')
                return None
            task['assignee'] = assignee

        creation_date = date.today()
        task['creation_date'] = creation_date

        if 'due_date' in data:
            due_date_str = data['due_date']
            if not self.validate_date(due_date_str):
                self.send_error(f'due_date="{due_date_str}" is not a valid date')
                return None
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            task['due_date'] = due_date

        if 'status' in data:
            status = data['status']
            if not isinstance(status, int):
                self.send_error(f'status="{status}" is not a valid status')
                return None
            task['status'] = status
        
        if 'sprint' in data:
            sprint = data['sprint']
            if not isinstance(sprint, int):
                self.send_error(f'sprint="{sprint}" is not a valid integer')
                return None
            task['sprint'] = sprint

        if 'priority' in data:
            priority = data['priority']
            if not isinstance(priority, int):
                self.send_error(f'priority="{priority}" is not a valid integer')
                return None
            task['priority'] = priority
        
        return task

    def received_add(self, data):
        required_field_names = ['workspace', 'taskname']
        for field_name in required_field_names:
            if not field_name in data:
                return self.send_error(f'{field_name} property not sent in JSON')

        task = self.validate_task(data)

        try:
            new_task = Task(workspace=task['workspace'], taskname=task['taskname'], creation_date=task['creation_date'])
            if 'description' in task:
                new_task.description = task['description']
            if 'assignee' in task: 
                new_task.assignee=task['assignee']
            if 'due_date' in task:
                new_task.due_date=task['due_date']
            if 'status' in task:
                new_task.status=task['status'] 
            if 'sprint' in task:
                new_task.sprint=task['sprint']
            if 'priority' in task:
                new_task.priority=task['priority']      
            new_task.save()

            self.broadcast_task(new_task)
        except:
            self.send_error(f'Invalid task')


    def received_delete(self, data):
        if not 'id' in data:
            self.send_error('id property not sent in JSON')
            return

        try:
            task = Task.objects.get(id=data['id'])
        except Task.DoesNotExist:
            self.send_error(f'Task with id="{data["id"]}" does not exist')
            return

        workspace = task.workspace
        if self.user != workspace.creator and self.user not in workspace.participants:
            return self.send_error(f'user="{self.user}" is not a participant of workspace_id={workspace.id}')

        task.delete()
        self.broadcast_list()

    def make_task_dict(self, task: Task):
        return {
            'id': task.id,
            'workspace': task.workspace.id,
            'taskname': task.taskname,
            'description': task.description,
            'assignee': task.assignee.id,
            'creation_date': task.creation_date.strftime('%Y-%m-%d'),
            'due_date': task.due_date.strftime('%Y-%m-%d'),
            'status': task.status,
            'sprint': task.sprint,
            'priority': task.priority,
        }

    def make_task_dict_list(self, workspace_id):
        task_dict_list = []
        for task in Task.objects.filter(workspace_id=workspace_id):
            task_dict = self.make_task_dict(task)
            task_dict_list.append(task_dict)
        return task_dict_list
    
    def send_error(self, error_message):
        self.send(text_data=json.dumps({'error': error_message}))

    def send_message(self, message):
        self.send(text_data=json.dumps({'message': message}))

    def broadcast_message(self, message):
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'broadcast_event',
                'message': json.dumps({'message': message})
            }
        )

    # send the message only to participants of the workspace, and to the creator of the workspace
    def broadcast_data(self, msg):
        print("[consumers.py] Broadcasting data to group", self.group_name)
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'broadcast_event',
                'message': msg
            },
        )

    def broadcast_list(self, workspace: Workspace):
        self.broadcast_data(json.dumps(self.make_task_dict_list(workspace.id)))

    def broadcast_task(self, task):
        self.broadcast_data(json.dumps([self.make_task_dict(task)]))

    def broadcast_event(self, event):
        self.send(text_data=event['message'])
