# chat/consumers.py
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from accounts.models import CustomUser
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.exceptions import ObjectDoesNotExist
import os
import json
import uuid
from datetime import datetime as dt

from channels.db import database_sync_to_async
import openai
import pinecone
from pinecone.core.client.exceptions import ApiException

from .models import Chat, Message
from .chat import CHATSESSION


PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.environ.get("PINECONE_ENVIRONMENT")
PINECONE_INDEX = os.environ.get("PINECONE_INDEX")

pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)


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

        # Send message to WebSocket
        meta_data = {"user": self.current_user.id, "chat_id": str(self.chat_id)}
        response_message = self.create_response(response_type, message, meta_data)

        if self.room_name in initial_message_cache:
            del initial_message_cache[self.room_name]        
            chat_id = await self.__class__.create_chatroom_record(self.current_user, self.lang)
            self.scope["session"][self.lang] = str(chat_id)
            self.scope["session"].save()
            self.chat_id = chat_id
            
        if not self.current_user.is_anonymous:
            if response_type == "chat":
                emb_text = generate_prompt_chat(message)+response_message
                emb_vectors = get_embeddings(emb_text)
                store_vectors([(emb_text, emb_vectors[0], meta_data),])
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
        
    def create_response(self, type, msg, meta_data=None):
        openai.api_key = settings.OPENAI_API_KEY
        """
        validate text input
        """ 
        if type == "chat":
            # query and ceate messages
            messages = [{"role": "system", "content": "The following is a conversation with a person. The person is creative, clever, and very friendly."}]
            for m in query_vectors(get_embeddings(msg), meta_data):
                messages.append({"role": "user", "content": m})
            messages.append({"role": "user", "content": generate_prompt_chat(msg)})
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages = messages,
                temperature=0.9,#0.5,
                max_tokens=100,
                top_p=1.0,
                frequency_penalty=0, #0.5,
                presence_penalty=0.6,#0.0,
                stop=["You:", "Yo:", "Me:", "\n"]
                # messages = [{"role": "system",
                #              "content": "You are ChatGPT, a large language model trained by OpenAI. Answer as concisely as possible.\nKnowledge cutoff: 2021-09-01\nCurrent date: 2023-03-02"},
                #             {"role":"user",
                #              "content": "How are you?"},
                #             {"role": "assistant",
                #              "content": "I am doing well"},
                #             {"role": "user",
                #              "content": "What is the mission of the company OpenAI?"}]
            )
            # response = openai.Completion.create(
            #     #model="text-davinci-003",
            #     model = "gpt-3.5-turbo",
            #     prompt= generate_prompt_chat(msg),
            #     temperature=0.5,
            #     max_tokens=60,
            #     top_p=1.0,
            #     frequency_penalty=0.5,
            #     presence_penalty=0.0,
            #     stop=["You:", "Yo:", "Me:", "\n"]
            # )
            return response["choices"][0]["message"]["content"]
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


def generate_prompt_chat(msg) -> str:
    return "You:{}\n\
            Friend:".format(msg)
            # Friend: Watching old movies.\n\
            # You: Did you watch anything interesting?\n\


def generate_prompt_analyze(msg) -> str:
    return "Correct this to old English:{}".format(msg)


def get_embeddings(text) -> list:
    vectors = openai.Embedding.create(input=text, model="text-embedding-ada-002")
    return [vec["embedding"] for vec in vectors["data"]]


def store_vectors(vectors):
    index = pinecone.Index(PINECONE_INDEX)
    try:
        index.upsert(vectors=vectors)
    except ApiException as e:
        return e

    return None


def query_vectors(vectors, filter, top_k=5, thresh_score=0.65) -> list:
    index = pinecone.Index(PINECONE_INDEX)
    results_vectors = index.query(vectors, filter=filter, top_k=top_k)
    vectors = []
    for vec in results_vectors["matches"]:
        # threshold by score
        if vec["score"] > thresh_score:
            vectors.append(vec["id"])
        else: break
    return vectors


def delete_vectors(meta_data):
    index = pinecone.Index(PINECONE_INDEX)
    try:
        index.delete(filter=meta_data)
    except ApiException as e:
        return e

    return None