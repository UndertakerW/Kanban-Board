from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from kanban.forms import LoginForm, RegisterForm, NewWorkspaceForm
from kanban.models import Profile, Workspace

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

# Function name:    _status_check
# Usage:            A wrapper function that checks if the user's account is activated (2FA is passed)
# Parameter:        An action function
# Return:           A wrapped function
def _status_check(action_function):
    def my_wrapper_function(request, *args, **kwargs):
        profile = Profile.objects.get(user=request.user)
        if not profile.authentication_status:
            return render(request, 'kanban/2fa.html')
        return action_function(request, *args, **kwargs)
    return my_wrapper_function

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
    context = {}
    render(request, "kanban/profile.html", context)


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
    context = {}
    render(request, "kanban/login.html", context)

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
    profile.save()

    login(request, new_user)
    return redirect(reverse('home'))

# Function name:    home_action
# url:              /
# Usage:            Deal with the home action.
# Parameter:        The http request.
# Return:           render() or redirect()
@login_required
@_status_check
def home_action(request):
    return
    #TODO

# Function name:    create_workspace_action
# url:              /workspace/create
# Usage:            Deal with the create workspace action.
# Parameter:        The http request.
# Return:           render() or redirect()
@login_required
@_status_check
def create_workspace_action(request):
    if request.method == 'GET':
        return home_action(request)

    workspace = Workspace()

    workspace.creator = request.user

    new_workspace_form = NewWorkspaceForm(request.POST, instance=workspace)

    if not new_workspace_form.is_valid():
        context = compute_context(request)
        return render(request, 'kanban/home.html', context)

    new_workspace_form.save()

    message = 'Workspace created'
    
    context = compute_context(request)
    context['message'] = message
    context['new_post_form'] = NewWorkspaceForm()
    return render(request, 'kanban/home.html', context)

@login_required
@_status_check
def edit_workspace_name_action(request):
    context = {}
    render(request, "kanban/workspace.html", context)

@login_required
@_status_check
def create_task_action(request):
    context = {}
    render(request, "kanban/task.html", context)

@login_required
@_status_check
def edit_task_action(request):
    context = {}
    render(request, "kanban/task.html", context)

@login_required
@_status_check
def edit_user_profile(request):
    context = {}
    render(request, "kanban/profile.html", context)

