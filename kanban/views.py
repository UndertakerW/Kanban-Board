from django.contrib.auth.decorators import login_required
import time
import pyopt
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, Http404

from kanban.forms import LoginForm, RegisterForm, NewWorkspaceForm, TaskForm, ProfileForm, OTPForm
from kanban.models import Profile, Workspace, Task


# Function name:    _status_checkobjects.
# Usage:            A wrapper function that checks if the user's account is activated (2FA is passed)
# Parameter:        An action function
# Return:           A wrapped function
def _status_check(action_function):
    def my_wrapper_function(request, *args, **kwargs):
        print('====== user is: ')
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
    if request.user.is_authenticated:
        workspaces = Workspace.objects.filter(participants=request.user)
        context = {
            'username': request.user.first_name + ' ' + request.user.last_name,
            'workspaces': workspaces,
            'form': NewWorkspaceForm(user=request.user),
            'message': '',
            'task_form': TaskForm(),
        }
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
    edit_form = NewWorkspaceForm(user=request.user, instance=workspace)
    edit_form.initial['name'] = workspace.name
    context['edit_form'] = edit_form
    print(edit_form)


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
    print("user id is:")
    print(profile.user.id)

    context['profile'] = profile
    context['profile_form'] = ProfileForm(initial={'profile_description': profile.profile_description})
    context['workspaces'] = workspaces

    return render(request, 'kanban/profile.html', context)


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
        # messages.error(request, 'This username is already taken')
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
# url:              /create-workspace
# Usage:            Deal with the create workspace action.
# Parameter:        The http request.
# Return:           render() or redirect()
@login_required
@_status_check
def create_workspace_action(request):
    context = compute_context(request)

    if request.method == 'GET':
        # workspaces = Workspace.objects.filter(participants=request.user)
        return render(request, 'kanban/workspace.html', context)

    workspace = Workspace()

    workspace.creator = request.user

    new_workspace_form = NewWorkspaceForm(request.POST, instance=workspace)
    # print(request.POST['name'])

    # TODO: should clarify where the create action happens. If it happens
    # on the profile page, then it should return profile page.
    if not new_workspace_form.is_valid():
        context['form'] = new_workspace_form
        context['task_form'] = TaskForm()
        return render(request, 'kanban/workspace.html', context)

    new_workspace_form.save()
    # Add the current user to participants
    workspace.participants.add(request.user.id)
    context['message'] = 'The board \'{}\' is created Successfully! :)'.format(new_workspace_form.cleaned_data['name'])
    context['selected_workspace'] = new_workspace_form.cleaned_data['name']
    context['task_form'] = TaskForm()
    return redirect('workspace/{}'.format(workspace.id))


# Function name:    workspace_action
# url:              /workspace
# Usage:            Render workspace screen on visit
# Parameter:        The http request.
# Return:           render()
@login_required
@_status_check
def workspace_action(request, selected_workspace_id):
    # Currently its visiting the workspace anyways
    workspaces = Workspace.objects.filter(participants=request.user)
    selected_workspace = get_object_or_404(Workspace, id=selected_workspace_id)
    context = compute_context(request)
    context['selected_workspace'] = selected_workspace

    # If the current user is the creator
    if selected_workspace.creator == request.user:
        compute_edit_workspace_context(request, context, selected_workspace)
        # Enable edit button in template

    return render(request, 'kanban/workspace.html', context)


# Function name:    edit_workspace_action
# url:              /workspace/:id/edit
# Usage:            Deal with the edit workspace action.
# Parameter:        The http request.
# Return:           render() or redirect()
@login_required
@_status_check
def edit_workspace_action(request, selected_workspace_id):
    context = compute_context(request)
    workspace = get_object_or_404(Workspace, id=selected_workspace_id)

    compute_edit_workspace_context(request, context, workspace)

    # Just display the workspace if this is a GET request.
    if request.method == 'GET':
        return redirect(reverse('workspace', args=[selected_workspace_id]))

    if request.method == 'POST' and request.user == workspace.creator:
        edit_form = NewWorkspaceForm(request.POST, request.FILES, instance=workspace)
        if not edit_form.is_valid():
            context['edit_form'] = edit_form
            return redirect(reverse('workspace', args=[selected_workspace_id]))
        else:
            edit_form.save()
            # Add the current user to participants
            workspace.participants.add(request.user.id)
            context['message'] = 'Workspace #{0} updated.'.format(workspace.id)
            return redirect(reverse('workspace', args=[selected_workspace_id]))


@login_required
@_status_check
def create_task_action(request, selected_workspace_id):
    workspaces = Workspace.objects.filter(participants=request.user)
    selected_workspace = get_object_or_404(Workspace, id=selected_workspace_id)
    context = {
        'username': request.user.first_name + ' ' + request.user.last_name,
        'workspaces': workspaces,
        'form': NewWorkspaceForm(user=request.user),
        'message': '',
        'selected_workspace': selected_workspace,
        'task_form': TaskForm(initial={
            'taskname': '',
            'description': '',
            'assignee': '',
            'creation_date': '',
            'due_date': '',
            'status': '',
            'priority': '',
        }),
    }

    if request.method == 'GET':
        return render(request, 'kanban/workspace.html', context)

    task_form = TaskForm(request.POST)
    # TODO: check validation of the form and give error message
    task_form.save()
    context['form'] = task_form

    return render(request, 'kanban/workspace.html', context)


@login_required
@_status_check
def edit_task_action(request, selected_workspace_id, task_id):
    context = compute_context(request)

    task = get_object_or_404(Task, id=task_id)
    if request.method == 'GET':
        form = TaskForm(instance=task)
        context['task_form'] = form
        return render(request, 'kanban/task.html', context)

    task_form = TaskForm(request.POST, instance=task)
    # TODO: check validation of the form and give error message
    task_form.save()
    context['task_form'] = task_form

    return render(request, 'kanban/task.html', context)


@login_required
@_status_check
def edit_user_profile(request):
    context = compute_context(request)
    user = request.user


    profile = get_object_or_404(Profile, user=user)
    workspaces = Workspace.objects.filter(participants=user)
    print("user id is:")
    print(profile.user.id)

    if request.method == 'GET':
        context['profile'] = profile
        context['profile_form'] = ProfileForm(initial={'profile_description': profile.profile_description})
        context['workspaces'] = workspaces
        return render(request, 'kanban/profile.html', context)

    profile_form = ProfileForm(request.POST, request.FILES)
    if not profile_form.is_valid():
        context = {'profile_form': profile}
        return render(request, 'kanban/profile.html', context)

    profile.picture = profile_form.cleaned_data['picture']
    profile.content_type = profile_form.cleaned_data['picture'].content_type
    print(profile.content_type)
    profile.profile_description = profile_form.cleaned_data['profile_description']

    profile.save()

    context['profile'] = profile
    context['profile_form'] = ProfileForm(initial={'picture': profile.picture, 'profile_description': profile.profile_description})

    return render(request, 'kanban/profile.html', context)

@login_required
def get_user_photo(request, id):
    item = get_object_or_404(Profile, user=id)

    if not item.picture:
        raise Http404

    return HttpResponse(item.picture, content_type=item.content_type)
