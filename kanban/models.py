from django.db import models
from django.contrib.auth.models import User


# Create your models here.

# Model name:               Profile
# Usage:                    When a new user register for the app, he should input the following info
# register_type:            To identify the user is registered on our website or from OAuth
# authentication_status:    After registration, the user must complete a 2fa before use any
#                           function of the app. If they do not complete it, the status is False.
class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="profile_user")
    register_type = models.CharField(max_length=20)
    otp = models.CharField(max_length=30, default=0)
    authentication_status = models.BooleanField(default=False)
    profile_description = models.TextField(max_length=50, null=True)
    picture = models.FileField(blank=True, null=True)
    content_type = models.CharField(max_length=50, default='image/jpg')


# Model name:               Workspace
# Usage:                    The workspace information stores here, it contains a creation user
#                           and many participant.
# id:                       A unique identifier (auto generated)
# name:                     The identification of the workspace
# creator:                  The user who created the workspace
# participants:             The participating relationship indicates which users are participant
#                           of this workspace. A workspace can have multiple participant, while a
#                           user can also join different workspaces. Thus, the relationship is a
#                           many-to-many.
# color_scheme:             The color scheme chosen for this workspace. It is an integer, the user
#                           choose color scheme from a bar in the frontend. All the color scheme are
#                           defined by backend. Users can only choose between them.

class Workspace(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_workspaces')
    participants = models.ManyToManyField(User, related_name="participant")
    color_scheme = models.IntegerField()


# Model name:               Task
# Usage:                    The task information stores here. A task is assigned to only one
#                           user, who is the assignee. It doesn't matter who created the task.
# id:                       A unique identifier (auto generated)
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
    id = models.AutoField(primary_key=True)
    workspace = models.ForeignKey(Workspace, on_delete=models.PROTECT, related_name="task_workspace")
    taskname = models.TextField(max_length=50)
    description = models.TextField(max_length=500)
    assignee = models.ForeignKey(User, on_delete=models.PROTECT, related_name="task_assignee")
    creation_date = models.DateField()
    due_date = models.DateField()
    status = models.IntegerField()
    sprint = models.IntegerField()
    priority = models.IntegerField()
