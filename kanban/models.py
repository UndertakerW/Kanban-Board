from django.db import models
from django.contrib.auth.models import User
# Create your models here.

# Model name:               Registration
# Usage:                    When a new user register for the app, he should input the following info
# username:                 The identification of a user
# password:                 The password for the user
# confirm_password:         Re-input the password to make sure it is correct
# email:                    The email of the user
# first_name:               The first name of the user
# last_name:                The last_name of the user
# register_type:            To identify the user is registered from OAuth, or directly register
# authentication_status:    After registration, the user must complete a 2fa before use any
#                           function of the app. If he does not complete it, the status is False.
class Registration(models.Model):
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=200)
    confirm_password = models.CharField(max_length=200)
    email = models.EmailField(max_length=50)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    register_type = models.CharField(max_length=20)
    authentication_status = models.BooleanField(default=False)


# Model name:               Workspace
# Usage:                    The workspace information stores here, it contains a creation user
#                           and many participant.
# workspacename:            The identification of the workspace
# user:                     The user who created the workspace
# participating:            The participating relationship indicates which users are participant
#                           of this workspace. A workspace can have multiple participant, while a
#                           user can also join different workspaces. Thus, the relationship is a
#                           many-to-many.
# colorscheme:              The color scheme chosen for this workspace. It is an integer, the user
#                           choose color scheme from a bar in the frontend. All the color scheme are
#                           defined by backend. Users can only choose between them.

class Workspace(models.Model):
    worspacename = models.CharField(max_length=50)
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    participating = models.ManyToManyField(User, related_name="participant")
    colorscheme = models.IntegerField()


# Model name:               Task
# Usage:                    The task information stores here. A task is assigned to only one
#                           user, who is the assignee. It doesn't matter who created the task.
# taskname:                 The identification of the task.
# description:              The description of the task.
# assignee:                 The assignee of the task is a user in the workspace.
# creation_date:            The date to create the task. The granularity is one day.
# due_date:                 The date of the task due. The granularity is one day.
# status:                   There are 3 status:
#                               1. To do    2. In progress  3. Done
# sprint:                   The sprint of the task
# priority:                 There are 3 priority:
#                               1. High     2.Medium    3.Low
class Task(models.Model):
    taskname = models.TextField(max_length=50)
    description = models.TextField(max_length=500)
    assignee = models.ForeignKey(User, default=None, on_delete=models.PROTECT, to_field='id')
    creation_date = models.DateField()
    due_date = models.DateField()
    status = models.IntegerField()
    sprint = models.IntegerField()
    priority = models.IntegerField()