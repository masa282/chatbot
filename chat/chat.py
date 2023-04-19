from django.conf import settings


class CHATSESSION:
    def __init__(self, session):
        self.session = session
        chat = self.session.get(settings.CHAT_SESSION_ID)
        if not chat:
            chat = self.session[settings.CHAT_SESSION_ID] = {}
        self.chat = chat
    
    def set(self, lang:str, chat_id: int):
        self.chat[lang] = chat_id
        self.save()

    def save(self):
        self.session.modified = True
        self.session.save()

    def get(self, key):
        #if self.chat.get(key):
        pass