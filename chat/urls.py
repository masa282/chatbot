from django.urls import path
from . import views

app_name = "chat"

urlpatterns = [
    path("", views.index, name="index"),
    path("chat/", views.lobby, name="lobby"),
    path("chat/<str:lang>/", views.new_room, name="new_room"),
    path("chat/<str:lang>/<str:chat_id>/", views.room, name="room"),
]