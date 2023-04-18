const statusList = ['TODO', 'DOING', 'DONE'];
const statusDict = {1 : 'TODO', 2 : 'DOING', 3 : 'DONE'};
const priority_levels = ['High', 'Medium', 'Low'];

// Function to create a task element
function createTaskElement(task) {
    var task_id = 0;
    if (!task.fields.id) {
      task_id = task.pk
    } else {
      task_id = task.fields.id;
    }
    // modal button that contains task overview
    const taskWrapper = document.createElement("button");
    taskWrapper.type = "button";
    taskWrapper.id = `task-wrapper-${task_id}`;
    taskWrapper.classList.add("task-wrapper");
    taskWrapper.dataset.bsToggle = "modal";
    taskWrapper.dataset.bsTarget = `#task-edit-modal`;

    // task name header
    const taskTitle = document.createElement('h4');
    taskTitle.className = 'heading-m task-title';
    taskTitle.textContent = task.fields.taskname;
    // task information wrapper
    const taskInfo = document.createElement('div');
    taskInfo.className = 'task-info';
    // task sprint
    const taskSprintTag = document.createElement('div');
    taskSprintTag.className = 'task-tag task-sprint';
    taskSprintTag.textContent = 'Sprint ' + task.fields.sprint;
    // task priority
    const taskPriorityTag = document.createElement('div');
    taskPriorityTag.className = 'task-tag';
    taskPriorityTag.textContent = 'Priority: ';
    // task priority
    const taskPriorityValue = document.createElement('div');
    taskPriorityValue.className = 'task-priority-' + priority_levels[task.fields.priority - 1].toLowerCase();
    taskPriorityValue.textContent = priority_levels[task.fields.priority - 1]

    taskPriorityTag.appendChild(taskPriorityValue);
    // task assignee
    const taskAssignee = document.createElement('div');
    taskAssignee.className = 'task-assignee';
    taskAssignee.textContent = task.fields.assignee_name;

    // assembly task info wrapper
    taskInfo.appendChild(taskSprintTag);
    taskInfo.appendChild(taskPriorityTag);
    taskInfo.appendChild(taskAssignee);
    // assembly task button
    taskWrapper.appendChild(taskTitle);
    taskWrapper.appendChild(taskInfo);


    // create event listener on clicking the button
    // populate modal with task data
    taskWrapper.addEventListener("click", function() {
      let field_taskname = document.querySelector("#task-edit-modal #id_taskname_input_text");
      field_taskname.value = task.fields.taskname;
      let field_description = document.querySelector("#task-edit-modal #id_description_input_text");
      field_description.value = task.fields.description;
      let field_assignee = document.querySelector("#task-edit-modal #id_assignee");
      field_assignee.value = task.fields.assignee;
      let field_creation_date = document.querySelector("#task-edit-modal #id_creation_date_input_date");
      field_creation_date.disabled = true;
      field_creation_date.value = task.fields["creation_date"];
      let field_due_date = document.querySelector("#task-edit-modal #id_due_date_input_date");
      field_due_date.value = task.fields["due_date"];
      let field_status = document.querySelector("#task-edit-modal #id_status_input_select");
      field_status.value = task.fields.status;
      let field_sprint = document.querySelector("#task-edit-modal #id_sprint");
      field_sprint.value = task.fields.sprint;
      let field_priority = document.querySelector("#task-edit-modal #id_priority_input_select");
      field_priority.value = task.fields.priority;

      // hidden display of task id
      let id = document.querySelector("#task-edit-modal .modal-task-id");
      id.textContent = task_id
    });
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
  processWsTasks(tasks).then((processedTasks) => {
    processedTasks.forEach((task) => {
      // locate assignee collapsible and column by assignee and status
      let column = document.querySelector(`#collapse-body-${task.assignee} #${statusDict[task.status]}-column`)
      let assigneeNameBtn = document.querySelector(`#collapse-btn-${task.assignee}`)

      // create column if no assignee column is created
      // TODO: handle the case when a column is not created 
      if (!column) {
        const columnsDiv = document.getElementById('columns-div');
        createCollapse(task.assignee_name, task.assignee, columnsDiv);
        column = document.querySelector(`#collapse-body-${task.assignee} #${statusDict[task.status]}-column`)
        assigneeNameBtn = document.querySelector(`#collapse-btn-${task.assignee}`)
      }

      // otherwise create tasks with matching structure to use createTaskElement
      if (column && assigneeNameBtn) {
        // update task if the task is found and located
        const taskElement = document.querySelector(`#task-wrapper-${task.id}`);
        if (taskElement) {
          taskElement.remove();
        }
        let taskBody = {};
        taskBody['fields'] = task;
        taskBody['fields']['assignee_name'] = assigneeNameBtn.childNodes[0].data;
        let newTask = createTaskElement(taskBody);
        column.appendChild(newTask);
      }
    });
  });
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

  async function processWsTasks(tasks) {
    for (const task of tasks) {
      task.assignee_name = await get_username(task['assignee']) 
    }
    return tasks;
  } 
  
  // Function to arrange tasks by status and assignee
  function arrangeTasks(tasks, sortBy) {
    processTasks(tasks).then((processedTasks) => {
      var groupedTasks = groupAndSortTasks(processedTasks, sortBy);
      // Create collapsibles that conatains grouped tasks
      const columnsDiv = document.getElementById('columns-div');
      var count = 0;
      for (const group in groupedTasks) {
        // create basic framework to place tasks
        // including <a> element, collapse, and status columns
        createCollapse(group, groupedTasks[group][0].fields.assignee, columnsDiv);
        // Arrange tasks by status (TODO, DOING & DONE) within collapsible groups
        groupedTasks[group].forEach(async (task) => {
          const taskElement = createTaskElement(task);
          const collapsibleBody = document.getElementById(`collapse-body-${groupedTasks[group][0].fields.assignee}`);
          const column = collapsibleBody.querySelector(`#${statusDict[task.fields.status]}-column`);
          column.appendChild(taskElement);
        });
        count++;
      }
    });
    
  }

  // create bootstrap collapse assignee column and the stratus columns inside
  function createCollapse(name, assignee, columnsDiv) {
    // create the bootstrap collapsible <a> element
    const aElement = document.createElement("a");
    aElement.classList.add("btn", "collapsed", "bg-primary-subtle", "workspace-collapsible-button");
    aElement.setAttribute("id", `collapse-btn-${assignee}`);
    aElement.setAttribute("data-bs-toggle", "collapse");
    aElement.setAttribute("href", `#collapse-body-${assignee}`);
    aElement.setAttribute("role", "button");
    aElement.setAttribute("aria-expanded", "false");
    aElement.setAttribute("aria-controls", "collapseExample");
    aElement.textContent = name;

    // create the <div> element with class "collapse"
    const divCollapse = document.createElement("div");
    divCollapse.classList.add("collapse", "show", "grouped-columns-wrapper");
    divCollapse.setAttribute("id", `collapse-body-${assignee}`);

    // append the <a> element and the <div> element with class "collapse" to task board
    columnsDiv.appendChild(aElement);
    columnsDiv.appendChild(divCollapse);

    // Create the status columns and append them to the columns div
    const statusColumns = statusList.map(createStatusColumn);
    const collapsibleBody = document.getElementById(`collapse-body-${assignee}`);
    statusColumns.forEach(column => collapsibleBody.appendChild(column));

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