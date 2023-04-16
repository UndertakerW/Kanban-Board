const statusList = ['TODO', 'DOING', 'DONE'];
const statusDict = {1 : 'TODO', 2 : 'DOING', 3 : 'DONE'};
const priority_levels = ['High', 'Medium', 'Low'];

// Function to create a task element
function createTaskElement(task) {
    const taskWrapper = document.createElement('div');
    taskWrapper.className = 'task-wrapper';

    const taskTitle = document.createElement('h4');
    taskTitle.className = 'heading-m task-title';
    taskTitle.textContent = task.fields.taskname;

    const taskInfo = document.createElement('div');
    taskInfo.className = 'task-info';

    const taskSprintTag = document.createElement('div');
    taskSprintTag.className = 'task-tag';
    taskSprintTag.textContent = 'Sprint ' + task.fields.sprint;

    const taskPriorityTag = document.createElement('div');
    taskPriorityTag.className = 'task-tag';
    taskPriorityTag.textContent = 'Priority: ';

    const taskPriorityValue = document.createElement('div');
    taskPriorityValue.className = 'task-priority-' + priority_levels[task.fields.priority - 1].toLowerCase();
    taskPriorityValue.textContent = priority_levels[task.fields.priority - 1]

    taskPriorityTag.appendChild(taskPriorityValue);

    const taskAssignee = document.createElement('div');
    taskAssignee.className = 'task-assignee';
    taskAssignee.textContent = task.fields.assignee_name;

    taskInfo.appendChild(taskSprintTag);
    taskInfo.appendChild(taskPriorityTag);
    taskInfo.appendChild(taskAssignee);

    taskWrapper.appendChild(taskTitle);
    taskWrapper.appendChild(taskInfo);

    return taskWrapper;
}


// Function to compare tasks for sorting
function compareTasks(a, b, sortBy) {
    switch (sortBy) {
      case 'sprint':
        return a.sprint - b.sprint;
      case 'priority':
        return a.priority - b.priority;
      case 'status':
        return a.status.localeCompare(b.status);
      case 'due_date':
        return new Date(a.due_date) - new Date(b.due_date);
      default:
        return 0;
    }
}

// Function to update tasks on receiving a list of tasks from WebSocket
// Paramater tasks is a list of tasks
function updateTasks(tasks) {
  // Update HTML and put updated task to correct location
  tasks.forEach(task => {
    // locate assignee collapsible and column by assignee and status
    let column = document.querySelector(`#collapse-body-${task.assignee} #${statusDict[task.status]}-column`);
    let assigneeNameBtn = document.querySelector(`#collapse-btn-${task.assignee}`);

    // create tasks with matching structure to use createTaskElement
    if (column && assigneeNameBtn) {
      let taskBody = {};
      taskBody['fields'] = task;
      taskBody['fields']['assignee_name'] = assigneeNameBtn.childNodes[0].data;
      let newTask = createTaskElement(taskBody);
      column.appendChild(newTask);
    }
  })
}

// Function to group tasks by assignee and sort them based on the sortBy parameter
function groupAndSortTasks(tasks, sortBy) {
    const groupedTasks = {};
    tasks.forEach((task) => {
      const assignee_name = task.fields.assignee_name || 'Unassigned';
  
      if (!groupedTasks[assignee_name]) {
        groupedTasks[assignee_name] = [];
      }
      groupedTasks[assignee_name].push(task);
    });

    Object.values(groupedTasks).forEach((taskGroup) => {
      taskGroup.sort((a, b) => compareTasks(a, b, sortBy));
    });

    return groupedTasks;
}

// Function to create a column for an assignee
function createAssigneeColumn(assignee) {
    const columnWrapper = document.createElement('div');
    columnWrapper.className = 'column-wrapper';
  
    const columnHeader = document.createElement('div');
    columnHeader.className = 'column-header heading-s';
    columnHeader.textContent = assignee;
  
    const column = document.createElement('div');
    column.className = 'column';
    column.setAttribute('data-assignee', assignee);
  
    columnWrapper.appendChild(columnHeader);
    columnWrapper.appendChild(column);
  
    return columnWrapper;
  }

  // Function to create a status column
  function createStatusColumn(status) {
    const columnWrapper = document.createElement('div');
    columnWrapper.className = 'column-wrapper';
  
    const columnHeader = document.createElement('div');
    columnHeader.className = 'column-header heading-s';
    columnHeader.textContent = status.toUpperCase();
  
    const column = document.createElement('div');
    column.className = 'column';
    column.id = `${status}-column`;
  
    columnWrapper.appendChild(columnHeader);
    columnWrapper.appendChild(column);
  
    return columnWrapper;
  }

  function get_username(id) {
    return fetch(`/get-username/${id}`)
    .then(response => response.json())
    .then(data => {
      return data.username
    })
    .catch(error => {
      console.error(error)
      return 'Unknown'
    });
  }

  // refine the structure, add assignee_name to each task
  async function processTasks(tasks) {
    for (const task of tasks) {
      task.fields['assignee_name'] = await get_username(task.fields['assignee']) 
    }
    return tasks;
  } 
  
  // Function to arrange tasks by status and assignee
  function arrangeTasks(tasks, sortBy) {
    processTasks(tasks).then((processedTasks) => {
      var groupedTasks = groupAndSortTasks(processedTasks, sortBy);
      // [IMPORTANT] TEST DATA, comment if necessary
      // groupedTasks = {
      //   "Minhui Xie": [
      //       {
      //           "model": "kanban.task",
      //           "pk": 1,
      //           "fields": {
      //               "workspace": 1,
      //               "taskname": "Add task to workspace",
      //               "description": "This is a new task",
      //               "assignee": 1,
      //               "creation_date": "2023-04-03",
      //               "due_date": "2022-04-30",
      //               "status": 1,
      //               "sprint": 1,
      //               "priority": 2,
      //               "assignee_name": "Minhui Xie"
      //           }
      //         },
      //         {
      //           "model": "kanban.task",
      //           "pk": 1,
      //           "fields": {
      //               "workspace": 1,
      //               "taskname": "Refine frontend design",
      //               "description": "This is a new task",
      //               "assignee": 1,
      //               "creation_date": "2023-04-03",
      //               "due_date": "2022-04-30",
      //               "status": 1,
      //               "sprint": 1,
      //               "priority": 1,
      //               "assignee_name": "Minhui Xie"
      //           }
      //         },
      //         {
      //           "model": "kanban.task",
      //           "pk": 1,
      //           "fields": {
      //               "workspace": 1,
      //               "taskname": "Arrange tasks using Bootsrtap collapse",
      //               "description": "This is a new task",
      //               "assignee": 1,
      //               "creation_date": "2023-04-03",
      //               "due_date": "2022-04-30",
      //               "status": 2,
      //               "sprint": 1,
      //               "priority": 3,
      //               "assignee_name": "Minhui Xie"
      //           }
      //         },
      //         {
      //           "model": "kanban.task",
      //           "pk": 1,
      //           "fields": {
      //               "workspace": 1,
      //               "taskname": "Create workspace interface",
      //               "description": "This is a new task",
      //               "assignee": 1,
      //               "creation_date": "2023-04-03",
      //               "due_date": "2022-04-30",
      //               "status": 3,
      //               "sprint": 1,
      //               "priority": 3,
      //               "assignee_name": "Minhui Xie"
      //           }
      //         },
      //       ],
      //       "Wei Wu": [
      //         {
      //             "model": "kanban.task",
      //             "pk": 1,
      //             "fields": {
      //                 "workspace": 1,
      //                 "taskname": "Use web socket to add tasks",
      //                 "description": "This is a new task",
      //                 "assignee": 1,
      //                 "creation_date": "2023-04-03",
      //                 "due_date": "2022-04-30",
      //                 "status": 1,
      //                 "sprint": 2,
      //                 "priority": 2,
      //                 "assignee_name": "Wei Wu"
      //             }
      //           },
      //           {
      //             "model": "kanban.task",
      //             "pk": 1,
      //             "fields": {
      //                 "workspace": 1,
      //                 "taskname": "Use web socket to modify tasks",
      //                 "description": "This is a new task",
      //                 "assignee": 1,
      //                 "creation_date": "2023-04-03",
      //                 "due_date": "2022-04-30",
      //                 "status": 1,
      //                 "sprint": 2,
      //                 "priority": 2,
      //                 "assignee_name": "Wei Wu"
      //             }
      //           },
      //           {
      //             "model": "kanban.task",
      //             "pk": 1,
      //             "fields": {
      //                 "workspace": 1,
      //                 "taskname": "Group tasks by status",
      //                 "description": "This is a new task",
      //                 "assignee": 1,
      //                 "creation_date": "2023-04-03",
      //                 "due_date": "2022-04-30",
      //                 "status": 2,
      //                 "sprint": 1,
      //                 "priority": 2,
      //                 "assignee_name": "Wei Wu"
      //             }
      //           },
      //           {
      //             "model": "kanban.task",
      //             "pk": 1,
      //             "fields": {
      //                 "workspace": 1,
      //                 "taskname": "Update task model",
      //                 "description": "This is a new task",
      //                 "assignee": 1,
      //                 "creation_date": "2023-04-03",
      //                 "due_date": "2022-04-30",
      //                 "status": 2,
      //                 "sprint": 1,
      //                 "priority": 3,
      //                 "assignee_name": "Wei Wu"
      //             }
      //           },
      //           {
      //             "model": "kanban.task",
      //             "pk": 1,
      //             "fields": {
      //                 "workspace": 1,
      //                 "taskname": "Edit workspace",
      //                 "description": "This is a new task",
      //                 "assignee": 1,
      //                 "creation_date": "2023-04-03",
      //                 "due_date": "2022-04-30",
      //                 "status": 3,
      //                 "sprint": 1,
      //                 "priority": 3,
      //                 "assignee_name": "Wei Wu"
      //             }
      //           }
      //         ],
      //     }

      // Create collapsibles that conatains grouped tasks
      const columnsDiv = document.getElementById('columns-div');
      var count = 0;
      for (const name in groupedTasks) {
        // create the bootstrap collapsible <a> element
        const aElement = document.createElement("a");
        aElement.classList.add("btn", "collapsed", "bg-primary-subtle", "workspace-collapsible-button");
        aElement.setAttribute("id", `collapse-btn-${groupedTasks[name][0].fields.assignee}`);
        aElement.setAttribute("data-bs-toggle", "collapse");
        aElement.setAttribute("href", `#collapse-body-${groupedTasks[name][0].fields.assignee}`);
        aElement.setAttribute("role", "button");
        aElement.setAttribute("aria-expanded", "false");
        aElement.setAttribute("aria-controls", "collapseExample");
        aElement.textContent = name;

        // create the <div> element with class "collapse"
        const divCollapse = document.createElement("div");
        divCollapse.classList.add("collapse", "show", "grouped-columns-wrapper");
        divCollapse.setAttribute("id", `collapse-body-${groupedTasks[name][0].fields.assignee}`);

        // append the <a> element and the <div> element with class "collapse" to task board
        columnsDiv.appendChild(aElement);
        columnsDiv.appendChild(divCollapse);

        // Create the status columns and append them to the columns div
        const statusColumns = statusList.map(createStatusColumn);
        const collapsibleBody = document.getElementById(`collapse-body-${groupedTasks[name][0].fields.assignee}`);
        statusColumns.forEach(column => collapsibleBody.appendChild(column));

        // Arrange tasks by status (TODO, DOING & DONE) within collapsible groups
        groupedTasks[name].forEach(async (task) => {
          const taskElement = createTaskElement(task);
          const column = collapsibleBody.querySelector(`#${statusDict[task.fields.status]}-column`);
          column.appendChild(taskElement);
        });
        count++;
      }
    });
    
  }
  
  // Function to toggle between the two sets of columns
  function toggleColumns() {
    const workspaceBoardStatus = document.getElementById('workspace-board-status');
    const workspaceBoardAssignee = document.getElementById('workspace-board-assignee');
  
    workspaceBoardStatus.style.display = workspaceBoardStatus.style.display === 'none' ? '' : 'none';
    workspaceBoardAssignee.style.display = workspaceBoardAssignee.style.display === 'none' ? '' : 'none';
  }
  
  // Call the arrangeTasks function and toggle button event listener when the page is loaded
  document.addEventListener('DOMContentLoaded', function () {
    const tasksJSON = document.getElementById('workspace-js').textContent;
    const tasks = JSON.parse(tasksJSON);
    console.log(tasks);
  
    // Change the sortBy value to the user-specified sorting option
    const sortBy = 'priority'; // Example: sort tasks by priority
  
    arrangeTasks(tasks, sortBy);
  
    // Add event listener to the toggle button
    const toggleColumnsButton = document.getElementById('toggle-columns');
    // toggleColumnsButton.addEventListener('click', toggleColumns);
  });