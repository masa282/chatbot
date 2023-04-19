# chat/routing.py
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<lang>[a-zA-Z-]{5})/(?P<chat_id>[0-9a-zA-Z-]+)/$", consumers.ChatConsumer.as_asgi()),
]