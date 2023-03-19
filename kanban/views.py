from django.contrib.auth.decorators import login_required
from django.shortcuts import render


# Naming regulation: For better understanding, the actions should all name
# in: {name}_action

# Function name:    home_action
# url:
# Usage:            When a user logs in, he will be navigated to his profile page.
#                   On his profile page, he can select his workspace and enter.
# Parameter:        The http request.
# Return:
@login_required
def home_action(request):
    context = {}
    render(request, "kanban/profile.html", context)


# Function name:    login_action
# url:              login
# Usage:            Deal with the login action.
# Parameter:        The http request.
# Return:
def login_action(request):
    context = {}
    render(request, "kanban/login.html", context)


def logout_action(request):
    context = {}
    render(request, "kanban/login.html", context)


def register_action(request):
    context = {}
    render(request, "kanban/register.html", context)


def create_workspace_action(request):
    context = {}
    render(request, "kanban/workspace.html", context)


def edit_workspace_name_action(request):
    context = {}
    render(request, "kanban/workspace.html", context)


def create_task_action(request):
    context = {}
    render(request, "kanban/task.html", context)


def edit_task_action(request):
    context = {}
    render(request, "kanban/task.html", context)


def edit_user_profile(request):
    context = {}
    render(request, "kanban/profile.html", context)

