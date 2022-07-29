from django.shortcuts import get_object_or_404
from index.models import Contact
from index.model.user import User


def get_user_contact(username):
    user = get_object_or_404(User, username=username)
    return get_object_or_404(Contact, user=user)

