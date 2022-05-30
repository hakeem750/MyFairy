from django.db import models
from ..model.user import User
from django.utils.translation import gettext_lazy as _


class Post(models.Model):

    title = models.CharField(max_length=100, blank=True, default="")
    body = models.TextField(blank=False, default="")
    audio_body = models.FileField(upload_to="assets/", default="")
    owner = models.ForeignKey(User, related_name="posts", on_delete=models.CASCADE)
    category = models.CharField(max_length=100, blank=False, default="")
    created = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(
        User,
        blank=True,
        related_name="blogs_like",
        verbose_name=_("Likes"),
    )

    class Meta:
        ordering = ["created"]


class Category(models.Model):
    authur = models.ForeignKey(User, related_name="catgory", on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=False, default="")
    models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "categories"


class Comment(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    body = models.TextField(blank=False)
    audio_body = models.FileField(upload_to="assets/", default="")
    owner = models.ForeignKey(User, related_name="comments", on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)

    class Meta:
        ordering = ["created"]


# class LikedPost(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     post = models.ForeignKey(Post, on_delete=models.CASCADE)
#     liked_date = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.post.title + " liked by " + self.user.fullname
