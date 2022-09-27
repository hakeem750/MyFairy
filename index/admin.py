from django.contrib import admin
from .model.post import Post
from .model.user import User, Parent, Profile
from .model.menstrual_cycle import MenstrualCycle
from .models import Chat

admin.site.register(Post)
admin.site.register(User)
admin.site.register(MenstrualCycle)
admin.site.register(Parent)
admin.site.register(Profile)
admin.site.register(Chat)
