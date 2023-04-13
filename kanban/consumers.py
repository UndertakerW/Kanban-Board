from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from kanban.models import Task, Workspace, User
import json
from threading import Lock
import datetime
from datetime import date
from django.core.exceptions import ValidationError

lock = Lock()
active_connections = 0

class MyConsumer(WebsocketConsumer):

    group_name = 'kanban_group'
    channel_name = 'kanban_channel'
    user = None

    def connect(self):
        async_to_sync(self.channel_layer.group_add)(
            self.group_name, self.channel_name
        )

        self.accept()

        if not self.scope["user"].is_authenticated:
            self.send_error(f'You must be logged in')
            self.close()
            return

        if not self.scope["user"].email.endswith("@andrew.cmu.edu"):
            self.send_error(f'You must be logged with Andrew identity')
            self.close()
            return            

        self.user = self.scope["user"]

        with lock:
            global active_connections
            active_connections += 1
            message = '{} active connections'.format(active_connections)
        self.broadcast_message(message)

        self.broadcast_list()

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

        if action == 'add':
            self.received_add(data)
            return

        if action == 'delete':
            self.received_delete(data)
            return

        self.send_error(f'Invalid action property: "{action}"')

    def validate_date(date_string):
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
    
    def received_add(self, data):
        if not 'text' in data:
            self.send_error('"text" property not sent in JSON')
            return

        workspace_id = data['workspace']
        workspace_query = Workspace.objects.filter(id=workspace_id)
        if not workspace_query.exists():
            self.send_error(f'workspace_id={workspace_id} does not exist')
        workspace = workspace_query.first()
        if self.user != workspace.creator and self.user not in workspace.participants:
            self.send_error(f'user={self.user} is not a participant of workspace_id={workspace_id}"')

        taskname = data['taskname']
        description = data['description']

        assignee_id = data['assignee']
        assignee_query = Workspace.objects.filter(id=assignee_id)
        if not assignee_query.exists():
            self.send_error(f'assignee_id={assignee_id} does not exist')
        assignee = assignee_query.first()
        if assignee != workspace.creator and assignee not in workspace.participants:
            self.send_error(f'assignee={assignee} is not a participant of workspace_id={workspace_id}"')

        creation_date = date.today()
        due_date = data['due_date']
        if not self.validate_date(due_date):
            self.send_error(f'due_date={due_date} is not a valid date"')

        status = data['status']
        if not isinstance(status, int):
            self.send_error(f'status={status} is not a valid status"')
        
        sprint = data['sprint']
        if not isinstance(sprint, int):
            self.send_error(f'sprint={sprint} is not a valid integer"')

        priority = data['priority']
        if not isinstance(priority, int):
            self.send_error(f'priority={priority} is not a valid integer"')


        new_task = Task(workspace=workspace, taskname=taskname, description=description,
                        assignee=assignee, creation_date=creation_date, due_date=due_date,
                        status=status, sprint=sprint, priority=priority)
        new_item = Item(text=text, ip_addr=self.scope['client'][0], user=self.user)
        new_item.save()

        self.broadcast_list()

    def received_delete(self, data):
        if not 'id' in data:
            self.send_error('id property not sent in JSON')
            return

        try:
            item = Item.objects.get(id=data['id'])
        except Item.DoesNotExist:
            self.send_error(f"Item with id={data['id']} does not exist")
            return

        if self.user.id != item.user.id:
            self.send_error("You cannot delete other user's entries")
            return

        item.delete()
        self.broadcast_list()

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

    def broadcast_list(self):
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'broadcast_event',
                'message': json.dumps(Item.make_item_list())
            }
        )

    def broadcast_event(self, event):
        self.send(text_data=event['message'])
