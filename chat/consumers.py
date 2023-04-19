# chat/consumers.py
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from accounts.models import CustomUser
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.exceptions import ObjectDoesNotExist
import json
import uuid
from datetime import datetime as dt

from channels.db import database_sync_to_async
import openai

from .models import Chat, Message
from .chat import CHATSESSION


initial_message_cache = {}


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["chat_id"]
        self.chat_id = self.room_name
        self.lang = self.scope["url_route"]["kwargs"]["lang"]

        # ユーザの接続情報をchannel_layerに登録する
        self.current_user = self.get_user(self.scope)
        if not self.current_user.is_anonymous:
            if len(self.room_name) == settings.RANDOM_DIGIT:
                initial_message_cache[self.room_name] = True

        if self.current_user.is_anonymous:
            try: # 12digit [1-9a-zA-Z]
                uuid.UUID(self.room_name)
                await self.close()
            except ValueError:
                pass
        
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat.message",
                "message": message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        chat_id = ""

        if self.room_name in initial_message_cache:
            del initial_message_cache[self.room_name]        
            chat_id = await self.__class__.create_chatroom_record(self.current_user, self.lang)
            self.scope["session"][self.lang] = str(chat_id)
            self.scope["session"].save()
            self.chat_id = chat_id
            print("[+]set chat id: ", str(chat_id))
            
            #chat_session = CHATSESSION(self.scope["session"])
            #chat_session.set(str(chat_id))

        if not self.current_user.is_anonymous:
            await self.__class__.save_message(self.chat_id, self.current_user, message)

        # Send message to WebSocket
        openai.api_key = settings.OPENAI_API_KEY
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt= self.generate_prompt(message),
            temperature=0.5,
            max_tokens=60,
            top_p=1.0,
            frequency_penalty=0.5,
            presence_penalty=0.0,
            stop=["You:"]
        )
        response_message = response.choices[0].text

        if not self.current_user.is_anonymous:
            await self.__class__.save_message(self.chat_id, None, response_message)

        await self.send(text_data = json.dumps({"message": response_message,
                                                "chat_id": str(chat_id)}))

    def generate_prompt(self, msg):
        return "You: {}\n\
                Friend:".format(msg)
                # Friend: Watching old movies.\n\
                # You: Did you watch anything interesting?\n\
    
    def get_user(self, scope):
        if "user" in scope:
            return scope["user"]
        else:
            return AnonymousUser
        
    @classmethod
    @database_sync_to_async
    def save_message(cls, chat_id, user, msg):
        try:
            chat = Chat.objects.get(chat_id=chat_id)
            if user != None:
                Message.objects.create(chat=chat, sender=user, content=msg)
            else: 
                Message.objects.create(chat=chat, content=msg)
        except ObjectDoesNotExist:
            pass

    @classmethod
    @database_sync_to_async
    def create_chatroom_record(cls, user, lang):
        new_chat = Chat.objects.create(user1=user, lang=lang)
        return new_chat.chat_id