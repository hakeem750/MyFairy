from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import ugettext_lazy as _
from datetime import datetime
from django.db.models.signals import post_save


class UserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):

    fullname = models.CharField(max_length=255)
    email = models.CharField(max_length=255, unique=True)
    phone = models.CharField(max_length=25, unique=True)
    password = models.CharField(max_length=255)
    code = models.IntegerField(default=0)
    username = None
    nickname = models.CharField(max_length=255)
    dob = models.DateField(verbose_name="Date of Birth")
    email_verified = models.BooleanField(null=True)
    user_verified = models.BooleanField(default=False)
    profile_pic = models.ImageField(blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    @property
    def profile_pic_url(self):

        if self.profile_pic and hasattr(self.profile_pic, 'url'):
            return self.profile_pic.url
        else:
            return "pictures/default.jpg"
            
    def __str__(self):
        return self.nickname


class Parent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.CharField(max_length=255)
    conscent = models.BooleanField(default=False)
    datetime = models.DateTimeField(auto_now_add=True)

class Profile(models.Model):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    private_account = models.BooleanField(default=False)
    followers = models.ManyToManyField('self', blank=True, related_name='user_followers', symmetrical=False)
    following = models.ManyToManyField('self', blank=True, related_name='user_following', symmetrical=False)
    pending_request = models.ManyToManyField('self', blank=True, related_name='pendingRequest',symmetrical=False)
    blocked_user = models.ManyToManyField('self', blank=True, related_name='user_blocked', symmetrical=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.user.nickname


def user_post_save(sender, instance, *arg, **kwargs):

    if not Profile.objects.filter(user=instance).exists():
        Profile.objects.create(user=instance)

    # if not Message.objects.filter(user=instance).exists():
    #     Message.objects.create(user=instance, )

post_save.connect(user_post_save, sender=User)
