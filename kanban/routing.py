from django.urls import path
from kanban import consumers

websocket_urlpatterns = [
    path('kanban/data', consumers.MyConsumer.as_asgi()),
]
