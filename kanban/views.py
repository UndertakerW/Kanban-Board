from django.contrib.auth.decorators import login_required
import time
import pyopt
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from kanban.forms import LoginForm, RegisterForm, NewWorkspaceForm, TaskForm, ProfileForm, OTPForm
from kanban.models import Profile, Workspace, Task


# Function name:    _status_checkobjects.
# Usage:            A wrapper function that checks if the user's account is activated (2FA is passed)
# Parameter:        An action function
# Return:           A wrapped function
def _status_check(action_function):
    def my_wrapper_function(request, *args, **kwargs):
        print("====== user is: ")
        print(Profile.objects.all()[0].user)
        print(request.user)
        
        profile = Profile.objects.get(user=request.user)
        if not profile.authentication_status:
            return render(request, 'kanban/otp.html')
        return action_function(request, *args, **kwargs)

    return my_wrapper_function


# Function name:    compute_context
# Usage:            Compute the HTTP context
# Parameter:        The http request.
# Return:           HTTP context
def compute_context(request):
    context = {}
    username = None
    fullname = None
    if request.user.is_authenticated:
        user = User.objects.get(username=request.user.username)
        username = user.username
        fullname = user.first_name + ' ' + user.last_name
    context['username'] = username
    context['full_name'] = fullname
    return context


def otp_verify(request):
    context = compute_context(request)

    # Creates a bound form from the request POST parameters and makes the
    # form available in the request context dictionary.
    form = OTPForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'kanban/otp.html', context)

    user = get_object_or_404(User, username=form.cleaned_data['username'])
    profile = get_object_or_404(Profile, user=user)
    if profile.otp == form.cleaned_data['otp']:
        profile.authentication_status = True
        profile.save()
    return redirect(reverse('home'))


@login_required
@_status_check
def compute_edit_workspace_context(request, context, workspace):
    context['workspace'] = workspace
    form = NewWorkspaceForm()
    form.initial['name'] = workspace.name
    context['form'] = form


# Naming regulation: For better understanding, the actions should all name
# in: {name}_action

# Function name:    home_action
# url:
# Usage:            When a user logs in, he will be navigated to his profile page.
#                   On his profile page, he can select his workspace and enter.
# Parameter:        The http request.
# Return:
@login_required
@_status_check
def home_action(request):
    context = compute_context(request)
    user = request.user

    profile = get_object_or_404(Profile, user=user)
    workspaces = Workspace.objects.filter(participants=user)

    context["profile_form"] = profile
    context["workspaces"] = workspaces
    return render(request, "kanban/profile.html", context)


# Function name:    login_action
# url:              /login
# Usage:            Deal with the login action.
# Parameter:        The http request.
# Return:           render() or redirect()
def login_action(request):
    context = compute_context(request)

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = LoginForm()
        return render(request, 'kanban/login.html', context)

    # Creates a bound form from the request POST parameters and makes the
    # form available in the request context dictionary.
    form = LoginForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'kanban/login.html', context)

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])

    login(request, new_user)
    return redirect(reverse('home'))


@login_required
def logout_action(request):
    return redirect(reverse('login'))


# Function name:    register_action
# url:              /register
# Usage:            Deal with the register action.
# Parameter:        The http request.
# Return:           render() or redirect()
def register_action(request):
    context = compute_context(request)

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = RegisterForm()
        return render(request, 'kanban/register.html', context)

    # Creates a bound form from the request POST parameters and makes the
    # form available in the request context dictionary.
    form = RegisterForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'kanban/register.html', context)

    if User.objects.filter(username=form.cleaned_data['username']).first():
        # messages.error(request, "This username is already taken")
        return redirect('home')

    # At this point, the form data is valid.  Register and login the user.
    new_user = User.objects.create_user(username=form.cleaned_data['username'],
                                        password=form.cleaned_data['password1'],
                                        email=form.cleaned_data['email'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'])
    new_user.save()

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password1'])

    profile = Profile()
    profile.user = new_user
    profile.otp = 111
    # random.randint(1000, 9999)

    profile.save()

    # return render(request, 'kanban/otp.html', context)
    # login(request, new_user)
    return redirect(reverse('otp_verify'))



# Function name:    create_workspace_action
# url:              /workspace/create
# Usage:            Deal with the create workspace action.
# Parameter:        The http request.
# Return:           render() or redirect()
@login_required
@_status_check
def create_workspace_action(request):
    if request.method == 'GET':
        context = compute_context(request)
        context['form'] = NewWorkspaceForm()
        return render(request, 'kanban/create_workspace.html', context)

    workspace = Workspace()

    workspace.creator = request.user

    new_workspace_form = NewWorkspaceForm(request.POST, instance=workspace)

    if not new_workspace_form.is_valid():
        context = compute_context(request)
        return render(request, 'kanban/workspace.html', context)

    new_workspace_form.save()

    message = 'Workspace created'

    context = compute_context(request)
    context['message'] = message
    context['new_post_form'] = NewWorkspaceForm()
    return render(request, 'kanban/profile.html', context)

# Function name:    workspace_action
# url:              /workspace
# Usage:            Render workspace screen on visit
# Parameter:        The http request.
# Return:           render()
@login_required
@_status_check
def workspace_action(request):
    # Currently its visiting workspace anyways
    # if request.method == 'GET':
    #     context = compute_context(request)
    #     return render(request, 'kanban/workspace.html')
    context = compute_context(request)
    context["username"] = request.user.first_name + ' ' + request.user.last_name
    return render(request, 'kanban/workspace.html', context)


# Function name:    edit_workspace_action
# url:              /workspace/:id/edit
# Usage:            Deal with the edit workspace action.
# Parameter:        The http request.
# Return:           render() or redirect()
@login_required
@_status_check
def edit_workspace_action(request, workspace_id):
    context = compute_context(request)
    workspace = get_object_or_404(Workspace, id=workspace_id)

    compute_edit_workspace_context(request, context, workspace)

    # Just display the workspace form if this is a GET request.
    if request.method == 'GET':
        return render(request, 'kanban/edit_workspace.html', context)

    if request.method == 'POST':
        form = NewWorkspaceForm(request.POST, request.FILES, instance=workspace)
        if not form.is_valid():
            context['form'] = form
            return render(request, 'kanban/edit_workspace.html', context)
        else:
            form.save()
            context['message'] = 'Workspace #{0} updated.'.format(workspace.id)
            return render(request, 'kanban/workspace.html', context)


@login_required
@_status_check
def create_task_action(request):
    context = compute_context(request)

    if request.method == "GET":
        context["form"] = TaskForm(initial={
            "taskname": "",
            "description": "",
            "assignee": "",
            "creation_date": "",
            "due_date": "",
            "status": "",
            "priority": "",
        })
        return render(request, "kanban/task.html", context)

    task_form = TaskForm(request.POST)
    # TODO: check validation of the form and give error message
    task_form.save()
    context["form"] = task_form

    return render(request, "kanban/task.html", context)


@login_required
@_status_check
def edit_task_action(request, task_id):
    context = compute_context(request)

    task = get_object_or_404(Task, id=task_id)
    if request.method == "GET":
        form = TaskForm(instance=task)
        context["task_form"] = form
        return render(request, "kanban/task.html", context)

    task_form = TaskForm(request.POST, instance=task)
    # TODO: check validation of the form and give error message
    task_form.save()
    context["task_form"] = task_form

    return render(request, "kanban/task.html", context)


@login_required
@_status_check
def edit_user_profile(request):
    context = compute_context(request)
    user = request.user

    profile = get_object_or_404(Profile, user=user)
    workspaces = Workspace.objects.filter(participants=user)

    if request.method == "GET":
        context["profile_form"] = profile
        context["workspaces"] = workspaces
        return render(request, "kanban/profile.html", context)

    profile_form = ProfileForm(request.POST)
    profile_form.save()
    context["profile_form"] = profile

    return render(request, "kanban/profile.html", context)
