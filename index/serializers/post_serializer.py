from rest_framework import serializers
from ..model.post import Post, Category, Comment, Audio, Bookmarks
from django.urls import reverse


class PostSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.nickname")
    url = serializers.SerializerMethodField(method_name="get_url")

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "body",
            "audio",
            "owner",
            "created",
            "category",
            "thumbnail",
            "url",
        ]

    def get_url(self, obj):
        return reverse("post-detail", kwargs={"pk": obj.pk})


class PostDetailSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.nickname")
    likes = serializers.SerializerMethodField(method_name="get_likes")
    comments = serializers.SerializerMethodField(method_name="get_comments")
    url = serializers.SerializerMethodField(method_name="get_url")

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "body",
            "audio",
            "owner",
            "created",
            "category",
            "likes",
            "thumbnail_url",
            "comments",
            "url",
        ]

        read_only_fields = [
            "likes",
        ]

    def get_likes(self, obj):
        return obj.likes.count()

    def get_url(self, obj):
        return reverse("post-detail", kwargs={"pk": obj.pk})

    def get_comments(self, obj):
        return CommentSerializer(Comment.objects.filter(post=obj.id), many=True).data


class CategorySerializer(serializers.ModelSerializer):
    authur = serializers.ReadOnlyField(source="authur.nickname")

    class Meta:
        model = Category
        fields = ["id", "name", "authur"]


class CommentSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.nickname")

    class Meta:
        model = Comment
        fields = ["id", "post", "body", "audio", "owner", "created"]


class AudioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Audio
        fields = ("audio_id", "audio")


class BookmarksSerializer(serializers.ModelSerializer):

    post = PostDetailSerializer(many=True)

    class Meta:
        model = Bookmarks
        fields = ("id", "user", "post")
