from rest_framework import serializers
from ..model.user import User, Parent
from ..model.post import Post 
from ..serializers.post_serializer import PostDetailSerializer



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


class ParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parent
        fields = [
                    "email",
                ]
