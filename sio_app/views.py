from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

import os
import jwt
from django.http import HttpResponse
import socketio
import json
from index.helper import Helper
from index.models import Message, Chat, Contact
from index.model.user import User
from decouple import config
from django.shortcuts import get_object_or_404
from enum import Enum



thread = None
MODE = "eventlet"
basedir = os.path.dirname(os.path.realpath(__file__))
sio = socketio.Server(async_mode=MODE, 
                      logger=True, 
                      #engineio_logger=True, 
                      cors_allowed_origins='*')

def get_user_contact(id):
    user = get_object_or_404(User, id=id)
    return get_object_or_404(Contact, user=user)

def get_last_10_messages(chatId):
    chat = get_object_or_404(Chat, id=chatId)
    return chat.messages.order_by('-timestamp').all()[:50]

def get_current_chat(chatId):
    return get_object_or_404(Chat, id=chatId)


class Index(APIView):

	def get(self, request):

		global thread
		if thread is None:  thread = sio.start_background_task(background_thread)
		return Response(
		    {
		        "status": True,
		        "message": "Socketio connection",
		    },
		    status=status.HTTP_200_OK,
		)

def index(request):
    # global thread
    # if thread is None:
    #     thread = sio.start_background_task(background_thread)
    return HttpResponse(open(os.path.join(basedir, 'static/index.html')))

def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        sio.sleep(10)
        count += 1
        sio.emit('response', {'data': 'Server generated event'})

def fetch_messages(data):
    messages = get_last_10_messages(data['chatId'])
    content = {
        'command': 'messages',
        'messages': messages_to_json(messages)
    }
    return content

def new_message(data):
    user_contact = get_user_contact(data['from'])
    message = Message.objects.create(
        contact=user_contact,
        content=data['message'], 
        #msg=data["msg"]
        )
    current_chat = get_current_chat(data['chatId'])
    current_chat.messages.add(message)
    current_chat.save()
    content = {
        'command': 'new_message',
        'message': message_to_json(message)
    }
    return content

def messages_to_json(messages):
    result = []
    for message in messages:
        result.append(message_to_json(message))
    return result

def message_to_json(message):
    return {
        'id': message.id,
        'author': message.contact.user.nickname,
        'content': message.content,
        "msg": message.msg,
        'timestamp': str(message.timestamp)
    }

def typing(message):
    return {

        'author': message.contact.user.nickname,
        'is_typing': True
    }

# def send_message(self, message):
#     self.send(text_data=json.dumps(message))

# def chat_message(self, event):
#     message = event['message']
#     self.send(text_data=json.dumps(message))

commands = {
        'fetch_messages': fetch_messages,
        'new_message': new_message,
        'typing': typing,
    }

def handle_type(msg):
    _type = msg["type"]
    if _type == "image":
        pass
        

    return msg


@sio.event
def connect(sid, environ):
    
    global chats, auth
    jwt_str = dict(environ["headers_raw"]).get('Authorization')
    auth = jwt.decode(jwt_str, config("secret_key"), algorithms=[config("algorithm")])
    contact = get_user_contact(auth["id"])
    chats = list(contact.chats.all().values_list("id", flat=True))
    #print(chats)
    if User.objects.filter(id=auth["id"]).first().is_staff:
        sio.emit('response', {"online":True}, broadcast=True, include_self=False)
    else:
        sio.emit('response', {"online":True}, to=chats, room=sid)



@sio.event
def join(sid, message):
    print(sid)
    sio.enter_room(sid, message['chatId'])
    sio.emit('response', {'data': 'Entered room: ' + str(message['chatId'])}, room=sid)


@sio.event
def my_join(sid, message):
    sio.enter_room(sid, message['room'])
    sio.emit('response', {'data': 'Entered room: ' + str(message['room'])}, room=sid)


@sio.event
def room_event(sid, message):
    # message = {
    #     "command":new_message,
    #     "from": 1,
    #     "message": "This is a new message"
    #     "chatId": 1
    # }       
    data = commands[message['command']](message)
    #print(data)
    sio.emit('response', data, room=message['chatId'])

@sio.event
def my_room_event(sid, message):
    sio.emit('response', {'data': message['data']}, room=message['room'])


@sio.event
def my_leave(sid, message):
    sio.leave_room(sid, message['room'])
    sio.emit('response', {'data': 'Left room: ' + message['room']},
             room=sid)

@sio.event
def leave(sid, message):
    sio.leave_room(sid, message['chatId'])
    sio.emit('response', {'data': 'Left room: ' + message['chatId']}, room=sid)


@sio.event
def close_room(sid, message):
    sio.emit('response', {'data': 'Room ' + message['chatId'] + ' is closing.'}, room=message['chatId'])
    sio.close_room(message['room'])


@sio.event
def my_close_room(sid, message):
    sio.emit('response', {'data': 'Room ' + message['room'] + ' is closing.'}, room=message['room'])
    sio.close_room(message['room'])

@sio.event
def my_event(sid, message):
    sio.emit('response', {'data': message['data']}, room=sid)


@sio.event
def my_broadcast_event(sid, message):
    sio.emit('response', {'data': message['data']})


@sio.event
def disconnect_request(sid):
    # print(chats)
    sio.emit('response', {'data': 'Disconnected', "online":False}, room=sid)
    sio.disconnect(sid)




@sio.event
def disconnect(sid):
    if User.objects.filter(id=auth["id"]).first().is_staff:
        sio.emit('response', {"online":True}, broadcast=True, include_self=False)
    else:
        sio.emit('response', {"online":True}, to=chats, room=sid)
    #print('Client disconnected')