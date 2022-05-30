from rest_framework import serializers
from ..model.post import Post, Category, Comment


class PostSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.fullname")

    class Meta:
        model = Post
        fields = ["id", "title", "body", "audio_body", "owner", "created", "category"]


class PostDetailSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.fullname")
    likes = serializers.SerializerMethodField(method_name="get_likes")

    def get_likes(self, obj):
        return obj.likes.count()

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "body",
            "audio_body",
            "owner",
            "created",
            "category",
            "likes",
        ]

        read_only_fields = [
            "likes",
        ]


class CategorySerializer(serializers.ModelSerializer):
    authur = serializers.ReadOnlyField(source="authur.fullname")

    class Meta:
        model = Category
        fields = ["id", "name", "authur"]


class CommentSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.fullname")

    class Meta:
        model = Comment
        fields = ["id", "post", "body", "audio_body", "owner", "created"]
