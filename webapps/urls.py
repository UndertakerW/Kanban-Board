"""webapps URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from kanban import views

urlpatterns = [
    path('', views.home_action, name='home'),
    path('login', views.login_action, name='login'),
    path('logout', views.logout_action, name='logout'),
    path('register', views.register_action, name='register'),
    path('create-workspace', views.create_workspace_action, name='create-workspace'),
    path('workspace/<int:selected_workspace_id>/edit/<int:workspace_id>', views.edit_workspace_action, name='edit-workspace'),
    path('workspace/<int:selected_workspace_id>', views.workspace_action, name="workspace"),
    path('workspace/<int:selected_workspace_id>/task/create/', views.create_task_action, name='create-task'),
    path('workspace/<int:selected_workspace_id>/task/edit/<int:task_id>', views.edit_task_action, name='edit-task'),
    path('edit-user-profile', views.edit_user_profile, name='edit-user-profile'),
    path('otp_verify', views.otp_verify, name="otp_verify")
]
