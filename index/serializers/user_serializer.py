from rest_framework import serializers
from ..model.user import *
from ..model.post import Post
from ..serializers.post_serializer import PostDetailSerializer
from collections import OrderedDict

from index import google
import os
from rest_framework.exceptions import AuthenticationFailed
from decouple import config


class UserSerializer(serializers.ModelSerializer):

    posts = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "fullname",
            "email",
            "password",
            "code",
            "phone",
            "nickname",
            "dob",
            "profile_pic",
            "posts",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
            "code": {"write_only": True},
        }

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class UserDetailSerializer(serializers.ModelSerializer):

    posts = serializers.SerializerMethodField(method_name="get_posts")

    class Meta:
        model = User
        fields = [
            "id",
            "fullname",
            "email",
            "password",
            "code",
            "phone",
            "nickname",
            "dob",
            "profile_pic_url",
            "posts",
        ]

        extra_kwargs = {
            "password": {"write_only": True},
            "code": {"write_only": True},
        }

    def get_posts(self, obj):
        return PostDetailSerializer(Post.objects.filter(owner=obj.id), many=True).data


class PersonnelSerializer(serializers.ModelSerializer):
    class Meta:

        model = User
        fields = [
            "id",
            "nickname",
            "fullname",
            "email",
        ]


class UserSearchSerializer(serializers.ModelSerializer):
    class Meta:

        model = User
        fields = [
            "nickname",
        ]


class EachUserSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id")
    nickname = serializers.CharField(source="user.nickname")
    profile_pic = serializers.SerializerMethodField(method_name="get_profile_pic")

    class Meta:
        model = Profile
        fields = ("user_id", "nickname", "profile_pic")
        read_only_fields = ("id", "nickname", "profile_pic")

    def get_profile_pic(self, obj):
        return obj.user.profile_pic_url


class EachFollowerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id")
    nickname = serializers.CharField(source="user.nickname")
    profile_pic = serializers.SerializerMethodField(method_name="get_profile_pic")
    # isfollowing = serializers.SerializerMethodField(method_name="get_isfollowing")

    class Meta:
        # list_serializer_class = EachFollowerListSerializer
        model = Profile
        fields = (
            "user_id",
            "nickname",
            "profile_pic",
        )
        read_only_fields = ("nickname", "profile_pic")

    def get_profile_pic(self, obj):
        return obj.user.profile_pic_url

    # def get_isfollowing(self, obj):
    #     return False

    def to_representation(self, instance):

        data = super().to_representation(instance)
        data = dict(data)
        following = Profile.objects.get(user_id=instance.user.id).following.all()
        data["isfollowing"] = True if instance in following else False
        data = OrderedDict(data.items())
        return data


class FollowerSerializer(serializers.ModelSerializer):
    followers = EachFollowerSerializer(many=True, read_only=True)
    following = EachUserSerializer(many=True, read_only=True)

    class Meta:
        model = Profile
        fields = ("followers", "following")
        read_only_fields = ("followers", "following")


class BlockPendinSerializer(serializers.ModelSerializer):
    panding_request = EachUserSerializer(many=True, read_only=True)
    blocked_user = EachUserSerializer(many=True, read_only=True)

    class Meta:
        model = Profile
        fields = ("panding_request", "blocked_user")
        read_only_fields = ("panding_request", "blocked_user")


class ParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parent
        fields = [
            "email",
        ]


class GoogleSocialAuthSerializer(serializers.Serializer):
    AccessToken = serializers.CharField()
    email = serializers.CharField()
    fullname = serializers.CharField()
