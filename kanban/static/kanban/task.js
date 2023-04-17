"use strict"

// Use a global variable for the socket.  Poor programming style, I know,
// but I think the simpler implementations of the deleteItem() and addItem()
// functions will be more approachable for students with less JS experience.
var socket = null
var test = false

function connectToServer() {
    // Create a new WebSocket.
    // When the user opens a WebSocket connection, 
    // the session cookie is sent along with the WebSocket handshake request, 
    // and the Django authentication middleware can use the session ID 
    // to retrieve the user's User object and associate it with the WebSocket connection.
    socket = new WebSocket("ws://" + window.location.host + "/kanban/data")

    // Handle any errors that occur.
    socket.onerror = function(error) {
        displayMessage("WebSocket Error: " + error)
    }

    // Show a connected message when the WebSocket is opened.
    socket.onopen = function(event) {
        getWorkspaceTasks(workspaceId)
        displayMessage("WebSocket Connected")
    }

    // Show a disconnected message when the WebSocket is closed.
    socket.onclose = function(event) {
        displayMessage("WebSocket Disconnected")
    }

    // Handle messages received from the server.
    socket.onmessage = function(event) {
        let response = JSON.parse(event.data)
        if (Array.isArray(response)) {
            updateTasks(response)

            // TEST CODE STARTS
            if (test === true) {
                test = false;
                let task = {
                    'id': 2217,
                    'workspace': 2,
                    'taskname': 'XXXXX GLITCHED OUT! XXXXX',
                    'description': 'EDITED!',
                    'assignee': 1,
                    'due_date': '2023-04-15',
                    'status': 1,
                    'sprint': 1,
                    'priority': 1,
                }
                sendDeleteTask(task);
            }
            // TEST CODE ENDS

        } else {
            displayResponse(response)
        }
    }
}

function displayError(message) {
    let errorElement = document.getElementById("error")
    errorElement.innerHTML = message
}

function displayMessage(message) {
    let errorElement = document.getElementById("message")
    errorElement.innerHTML = message
}

function displayResponse(response) {
    if ("error" in response) {
        displayError(response.error)
    } else if ("message" in response) {
        displayMessage(response.message)
    } else {
        displayMessage("Unknown response")
    }
}

function sendAddTask(task) {
    let data = {"action": "add-task", "task": task}
    socket.send(JSON.stringify(data))
}

function sendEditTask(task) {
    let data = {"action": "edit-task", "task": task}
    socket.send(JSON.stringify(data))
}

function sendDeleteTask(task) {
    let data = {"action": "delete-task", "task": task}
    socket.send(JSON.stringify(data))
}

function getWorkspaceTasks(workspace_id) {
    let data = {"action": "get-tasks", "workspace": workspace_id}
    socket.send(JSON.stringify(data))
}

