from rest_framework import serializers
from index.models import Chat, Contact
from index.views.chat_view import get_user_contact


class ContactSerializer(serializers.StringRelatedField):
    def to_internal_value(self, value):
        return value


class ChatSerializer(serializers.ModelSerializer):
    participants = ContactSerializer(many=True)

    class Meta:
        model = Chat
        fields = ('id', 'messages', 'participants')
        read_only = ('id')

    def create(self, validated_data):
        participants = validated_data.pop('participants')
        chat = Chat()
        chat.save()
        for nickname in participants:
            contact = get_user_contact(nickname)
            chat.participants.add(contact)
        chat.save()
        return chat

