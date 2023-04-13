from django.urls import path, path
from kanban import consumers

websocket_urlpatterns = [
    path('ws_todolist/data', consumers.MyConsumer.as_asgi()),
]
