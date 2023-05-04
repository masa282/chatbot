from django.shortcuts import render
from django.utils.crypto import get_random_string
from django.http import Http404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from datetime import datetime as dt
from django.conf import settings

from .models import Chat, Message
from .chat import CHATSESSION


# Create your views here.
def index(request):
    return render(request, "chat/index.html")


def lobby(request):
    return render(request, "chat/lobby.html")
    # if request.user.is_authenticated:
    #     room_name = request.user.id
    # else: 
    #     room_name = get_random_string(length=10)
    # return render(request, "chat/lobby.html", {"room_name": room_name})


@require_http_methods(["GET"])
def new_room(request, lang):
    user = request.user
    cuurent_chat_id = get_random_string(length=settings.RANDOM_DIGIT)
    context = {"lang": lang, "chat_id": cuurent_chat_id}

    # Authorized User
    if not user.is_anonymous:
        chats = Chat.objects.filter(user1=user).order_by('-created_at') # .exclude(chat_id=now)
        massages = []
        for chat in chats:
            msg = Message.objects.filter(chat=chat).last()#.latest('created_at')
            massages.append(msg)
        context["friends_log"] = zip(chats, massages)

    return render(request, "chat/room.html", context)


@login_required
@require_http_methods(["GET"])
def room(request, lang, chat_id):
        user = request.user

        # Authorized User
        # chat_session = CHATSESSION(request.session)
        # if chat_session.get(lang) != chat_id:
        #      chat_session.set(chat_id)
        current_chat = Chat.objects.filter(chat_id=chat_id)
        if not current_chat.exists():
             raise Http404("Not Found")
        
        # get friends log
        chats = Chat.objects.filter(user1=user).exclude(chat_id=chat_id).order_by('-created_at')
        massages = []
        for chat in chats:
            msg = Message.objects.filter(chat=chat).last() #latest('created_at'), chatルームがあるのにmsgがない場合ができてしまった場合、エラーになる
            massages.append(msg)

        # get message log
        current_message = Message.objects.filter(chat=current_chat[0]).order_by("created_at")

        #chat_ids = Chat.objects.filter(user1=user).order_by('-chat_id') # .exclude(chat_id=now)
        #messages = Message.objects.filter(chat=chat_id).order_by("-created_at")

        context = {"lang": lang, "chat_id": chat_id, "friends_log": zip(chats, massages), "messages_log": current_message}
    
        return render(request, "chat/room.html", context)

        # now = dt.now().strftime("%Y{%.2f}%M%d%H%M%S")
        # _ = Chat.objects.create(
        #         user = user,
        #         chat_id = int(now[2:]) # 235718125714
        #     )