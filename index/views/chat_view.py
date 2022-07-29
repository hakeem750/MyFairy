from django.shortcuts import get_object_or_404
from index.models import Chat, Contact
from index.model.user import User


def get_last_10_messages(chatId):
    chat = get_object_or_404(Chat, id=chatId)
    return chat.messages.order_by('-timestamp').all()[:10]


def get_user_contact(id):
    user = get_object_or_404(User, id=id)
    return get_object_or_404(Contact, user=user)


def get_current_chat(chatId):
    return get_object_or_404(Chat, id=chatId)
