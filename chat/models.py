from django.db import models
from accounts.models import CustomUser
import uuid 

# Create your models here.
class Chat(models.Model):
    chat_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lang = models.CharField(max_length=10)
    user1 = models.ForeignKey(CustomUser, related_name='chats1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(CustomUser, related_name='chats2', null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    sender = models.ForeignKey(CustomUser, related_name='messages', null=True, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Bookmark(models.Model):
    user = models.ForeignKey(CustomUser, related_name='bookmarks', on_delete=models.CASCADE)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    #created_at = models.DateTimeField(auto_now_add=True)