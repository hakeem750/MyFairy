from rest_framework import serializers
from ..model.post import Post, Category, Comment, Audio


class PostSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.nickname")

    class Meta:
        model = Post
        fields = ["id", 
                  "title", 
                  "body", 
                  "audio", 
                  "owner", 
                  "created", 
                  "category", 
                  "thumbnail"]


class PostDetailSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.nickname")
    likes = serializers.SerializerMethodField(method_name="get_likes")
    comments = serializers.SerializerMethodField(method_name="get_comments")

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
            
        ]

        read_only_fields = [
            "likes",
        ]

    def get_likes(self, obj):
        return obj.likes.count()

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
        fields = ('audio_id','audio')