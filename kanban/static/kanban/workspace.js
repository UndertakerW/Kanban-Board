// Function to create a task element
function createTaskElement(task) {
    const taskWrapper = document.createElement('div');
    taskWrapper.className = 'task-wrapper';

    const taskTitle = document.createElement('h4');
    taskTitle.className = 'heading-m task-title';
    taskTitle.textContent = task.title;

    taskWrapper.appendChild(taskTitle);

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
      const assignee = task.assignee || 'Unassigned';
  
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
  
  // Function to arrange tasks by status and assignee
  function arrangeTasks(tasks, sortBy) {
    const groupedTasks = groupAndSortTasks(tasks, sortBy);
  
    // Arrange tasks by status
    for (const assignee in groupedTasks) {
      groupedTasks[assignee].forEach((task) => {
        const taskElement = createTaskElement(task);
  
        const column = document.getElementById(`${task.status.toLowerCase()}-column`);
        column.appendChild(taskElement);
      });
    }
  
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
    const tasks = JSON.parse(document.getElementById('tasks-data').textContent);
  
    // Change the sortBy value to the user-specified sorting option
    const sortBy = 'priority'; // Example: sort tasks by priority
  
    arrangeTasks(tasks, sortBy);
  
    // Add event listener to the toggle button
    const toggleColumnsButton = document.getElementById('toggle-columns');
    toggleColumnsButton.addEventListener('click', toggleColumns);
  });