from rest_framework import serializers
from index.models import Chat, Contact, Message
from index.views.chat_view import get_user_contact


class ContactSerializer(serializers.ModelSerializer):
    nickname = serializers.CharField(source='user.nickname')
    profile_pic = serializers.SerializerMethodField(method_name="get_profile_pic")

    class Meta:
        model = Contact
        fields = ('nickname', 'profile_pic')
        read_only_fields = ('id','username','profile_pic')

    def get_profile_pic(self, obj):
        return obj.user.profile_pic_url

class ChatMessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = ("content", "timestamp")


class ChatSerializer(serializers.ModelSerializer):
    participants = ContactSerializer(many=True)
    last_message = serializers.SerializerMethodField("get_last_message")

    class Meta:
        model = Chat
        fields = ('id', 'last_message', 'participants')
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

    def get_last_message(self, obj):

        if len(list(obj.messages.all())) < 1:

            return []
        return ChatMessageSerializer(list(obj.messages.all())[-1]).data


