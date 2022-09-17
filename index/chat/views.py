from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    CreateAPIView,
    DestroyAPIView,
    UpdateAPIView
)
from index.models import Chat, Contact
from index.chat.serializers import ChatSerializer
from index.model.user import User
from django.shortcuts import get_object_or_404
from index.views.chat_view import get_user_contact
from rest_framework.views import APIView
from index.helper import Helper, get_data

class ChatListView(APIView):

    def get(self, request):
        auth = Helper(request).is_autheticated()
 
        if auth["status"]:
            #user = User.objects.filter(id=auth["payload"]["id"])[0].id
            contact = get_user_contact(auth["payload"]["id"])
            # print(contact)
            chats = ChatSerializer(contact.chats.all(), many=True)

            return Response({"status":True, "data":chats.data}, status=status.HTTP_200_OK)

        return  Response({"status":False, "message":"Unathorised"})



    # serializer_class = ChatSerializer
    # permission_classes = (permissions.AllowAny, )

    # def get_queryset(self):
    #     queryset = Chat.objects.all()
    #     nickname = self.request.query_params.get('nickname', None)
    #     if username is not None:
    #         contact = get_user_contact(nickname)
    #         queryset = contact.chats.all()
    #     return queryset


class ChatDetailView(RetrieveAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = (permissions.AllowAny, )

    # def get(self, request, pk):

        



class ChatCreateView(APIView):

    def post(self, request):
        auth = Helper(request).is_autheticated()
        data = get_data(request.POST)
        if auth["status"]:
            user = User.objects.get(id=auth["payload"]["id"]).id

            other_user = User.objects.get(id=data["id"]).id

            print(user, other_user)
            my_contact = get_user_contact(user)
            other_contact = get_user_contact(other_user)
            chat = Chat.objects.create()
            chat.participants.add(my_contact, other_contact)
            chat.save()

            serializer = ChatSerializer(chat)

            return Response({
                "status":True, 
                "message":"Chat created successfully", 
                "data": serializer.data}, status=status.HTTP_201_CREATED)


        return Response({
                "status":True, 
                "message":"Unathorised",}, status=status.HTTP_200_OK)







# class ChatCreateView(CreateAPIView):
#     queryset = Chat.objects.all()
#     serializer_class = ChatSerializer
#     permission_classes = (permissions.IsAuthenticated, )


class ChatUpdateView(UpdateAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = (permissions.IsAuthenticated, )


class ChatDeleteView(DestroyAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = (permissions.IsAuthenticated, )
