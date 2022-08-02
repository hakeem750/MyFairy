from django.db import models
from .model.user import User
from django.db.models.signals import post_save


class Contact(models.Model):
    user = models.ForeignKey(User, related_name='friends', on_delete=models.CASCADE)
    friends = models.ManyToManyField('self', blank=True)

    def __str__(self):
        return self.user.fullname


class Message(models.Model):
    contact = models.ForeignKey(Contact, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.contact.user.nickname


class Chat(models.Model):
    participants = models.ManyToManyField(Contact, related_name='chats', blank=True)
    messages = models.ManyToManyField(Message, blank=True)

    def __str__(self):
        return f"{self.pk}"


def user_post_save(sender, instance, *arg, **kwargs):

    if not Contact.objects.filter(user=instance).exists():
        Contact.objects.create(user=instance)

post_save.connect(user_post_save, sender=User)