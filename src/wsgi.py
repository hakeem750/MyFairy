"""
WSGI config for MyFairy project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
import socketio
from sio_app.views import sio
import eventlet
import eventlet.wsgi as wsg

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')

django_app = get_wsgi_application()
application = socketio.WSGIApp(sio, django_app)

# from gevent import pywsgi
# from geventwebsocket.handler import WebSocketHandler
# application = socketio.WSGIApp(sio, django_app, socketio_path='socket.io')
# pywsgi.WSGIServer(('', 8000), application, handler_class=WebSocketHandler).serve_forever()

wsg.server(eventlet.listen(('', 8000)), application)
