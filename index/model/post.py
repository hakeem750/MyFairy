from django.db import models
from ..model.user import User
from django.utils.translation import gettext_lazy as _
from datetime import datetime


class Post(models.Model):

    title = models.CharField(max_length=100, blank=True, default="")
    body = models.TextField(blank=True, default="")
    audio = models.JSONField(default=str)
    owner = models.ForeignKey(User, related_name="posts", on_delete=models.CASCADE)
    category = models.CharField(max_length=100, blank=False, default="")
    created = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(
        User,
        blank=True,
        related_name="blogs_like",
        verbose_name=_("Likes"),
    )
    thumbnail = models.ImageField(blank=True, null=True)

    class Meta:
        ordering = ["created"]

    @property
    def thumbnail_url(self):

        if self.thumbnail and hasattr(self.thumbnail, "url"):
            return self.thumbnail.url
        else:
            return "/pictures/default.jpg"


class Category(models.Model):
    authur = models.ForeignKey(User, related_name="catgory", on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=False, default="", unique=True)
    models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "categories"


class Comment(models.Model):

    body = models.TextField(blank=True)
    audio = models.JSONField(default=str)
    owner = models.ForeignKey(User, related_name="comments", on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created"]


class Audio(models.Model):
    audio_id = models.CharField(max_length=150)
    audio = models.FileField(upload_to="myfairy/assets/")


class Bookmarks(models.Model):
    user = models.ForeignKey(User, related_name="bookmark", on_delete=models.CASCADE)
    post = models.ManyToManyField(
        Post,
        blank=True,
    )
    created = models.DateTimeField(auto_now_add=True)


# class LikedPost(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     post = models.ForeignKey(Post, on_delete=models.CASCADE)
#     liked_date = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.post.title + " liked by " + self.user.fullname
