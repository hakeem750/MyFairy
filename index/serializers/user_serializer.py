from rest_framework import serializers
from ..model.user import *
from ..model.post import Post 
from ..serializers.post_serializer import PostDetailSerializer
from collections import OrderedDict



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

class EachUserSerializer(serializers.ModelSerializer):
    nickname = serializers.CharField(source='user.nickname')
    profile_pic = serializers.SerializerMethodField(method_name="get_profile_pic")

    class Meta:
        model = Profile
        fields = ('id','nickname','profile_pic')
        read_only_fields = ('id','username','profile_pic')

    def get_profile_pic(self, obj):
        return obj.user.profile_pic_url



class EachFollowerSerializer(serializers.ModelSerializer):
    nickname = serializers.CharField(source='user.nickname')
    profile_pic = serializers.SerializerMethodField(method_name="get_profile_pic")
    #isfollowing = serializers.SerializerMethodField(method_name="get_isfollowing")

    class Meta:
        #list_serializer_class = EachFollowerListSerializer
        model = Profile
        fields = ('id','nickname','profile_pic',)
        read_only_fields = ('id','username','profile_pic')


    def get_profile_pic(self, obj):
        return obj.user.profile_pic_url

    # def get_isfollowing(self, obj):
    #     return False

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data = dict(data)
        data["isfollowing"] = True if  instance in instance.following.all() else False
        # if  instance in instance.following.all():
        #     data["isfollowing"] = True
        # else:
        #     data["isfollowing"] = False

        data = OrderedDict(data.items())
        return data

class FollowerSerializer(serializers.ModelSerializer):
    followers = EachFollowerSerializer(many=True, read_only=True)
    following = EachUserSerializer(many=True, read_only=True)
    
    class Meta:
        model = Profile
        fields = ('followers','following')
        read_only_fields = ('followers','following')

class BlockPendinSerializer(serializers.ModelSerializer):
    panding_request = EachUserSerializer(many=True, read_only=True)
    blocked_user = EachUserSerializer(many=True,read_only=True)

    class Meta:
        model = Profile
        fields = ('panding_request','blocked_user')  
        read_only_fields = ('panding_request','blocked_user')

class ParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parent
        fields = [
                    "email",
                ]
