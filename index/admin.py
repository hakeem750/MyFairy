from django.contrib import admin
from .model.post import Post
from .model.menstrual_cycle import MenstrualCycle
from .model.user import *


admin.site.register(Post)
admin.site.register(MenstrualCycle)
admin.site.register(User)
