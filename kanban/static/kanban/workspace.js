const statusList = ['TODO', 'DOING', 'DONE'];
const statusDict = {1 : 'TODO', 2 : 'DOING', 3 : 'DONE'};
const priority_levels = ['low', 'medium', 'high'];

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
    taskPriorityValue.className = 'task-priority-' + priority_levels[task.fields.priority];
    taskPriorityValue.textContent = priority_levels[task.fields.priority]

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

// Function to group tasks by assignee and sort them based on the sortBy parameter
function groupAndSortTasks(tasks, sortBy) {
    const groupedTasks = {};
    tasks.forEach((task) => {
      const assignee = task.fields.assignee || 'Unassigned';
  
      if (!groupedTasks[assignee]) {
        groupedTasks[assignee] = [];
      }
      groupedTasks[assignee].push(task);
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
      const groupedTasks = groupAndSortTasks(processedTasks, sortBy);
      console.log("sorted tasks:");
      console.log(groupedTasks);
      // Create the status columns and append them to the columns div
      const columnsDiv = document.getElementById('columns-div');
      const statusColumns = statusList.map(createStatusColumn);
      statusColumns.forEach(column => columnsDiv.appendChild(column));
    
      // Arrange tasks by status
      for (const assignee in groupedTasks) {
        groupedTasks[assignee].forEach(async (task) => {
          const taskElement = createTaskElement(task);
    
          const column = document.getElementById(`${statusDict[task.fields.status]}-column`);
          console.log(statusDict[task.fields.status]);
          column.appendChild(taskElement);
        });
      }
      return;
      // Arrange tasks by assignee
      const workspaceBoardAssignee = document.getElementById('workspace-board-assignee');
      for (const assignee in groupedTasks) {
        const assigneeColumn = createAssigneeColumn(assignee);
        workspaceBoardAssignee.appendChild(assigneeColumn);
    
        groupedTasks[assignee].forEach((task) => {
          const taskElement = createTaskElement(task);
    
          const column = assigneeColumn.querySelector(`[data-assignee="${assignee}"]`);
          column.appendChild(taskElement);
        });
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