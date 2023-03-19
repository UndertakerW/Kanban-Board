from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from kanban.forms import LoginForm, RegisterForm
from kanban.models import Profile

# Function name:    compute_context
# url:
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


def logout_action(request):
    context = {}
    render(request, "kanban/login.html", context)


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

