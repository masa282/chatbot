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
        response_type = text_data_json["response_type"]
        message = text_data_json["message"]

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat.message",
                "response_type": response_type,
                "message": message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        response_type = event["response_type"]
        message = event["message"]
        chat_id = ""

        if self.room_name in initial_message_cache:
            del initial_message_cache[self.room_name]        
            chat_id = await self.__class__.create_chatroom_record(self.current_user, self.lang)
            self.scope["session"][self.lang] = str(chat_id)
            self.scope["session"].save()
            self.chat_id = chat_id
            
            #chat_session = CHATSESSION(self.scope["session"])
            #chat_session.set(str(chat_id))

        # Send message to WebSocket
        response_message = self.create_response(response_type, message)

        if not self.current_user.is_anonymous:
            if response_type == "chat":
                await self.__class__.save_message(self.chat_id, self.current_user, message)
                await self.__class__.save_message(self.chat_id, None, response_message)

        await self.send(text_data = json.dumps({"response_type": response_type,
                                                "message": response_message,
                                                "chat_id": str(chat_id)}))
       
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

    def get_user(self, scope):
        if "user" in scope:
            return scope["user"]
        else:
            return AnonymousUser
        
    def create_response(self, type, msg):
        openai.api_key = settings.OPENAI_API_KEY
        """
        validate text input
        """ 
        if type == "chat":
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt= generate_prompt_chat(msg),
                temperature=0.5,
                max_tokens=60,
                top_p=1.0,
                frequency_penalty=0.5,
                presence_penalty=0.0,
                stop=["You:"]
            )
            return response.choices[0].text
        elif type=="analyze":
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt= generate_prompt_analyze(msg),
                temperature=0,
                max_tokens=60,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            return response.choices[0].text
        else:
            response = None

        return response


def generate_prompt_chat(msg):
    return "You:{}\n\
            Friend:".format(msg)
            # Friend: Watching old movies.\n\
            # You: Did you watch anything interesting?\n\


def generate_prompt_analyze(msg):
    return "Correct this to old English:{}".format(msg)