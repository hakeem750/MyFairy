from ..model.post import Post  # , Comment, Category, LikedPost
from ..model.user import User
from ..helper import Helper, get_data
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView,
)
from rest_framework import status
from ..serializers.post_serializer import *
from ..model.post import Bookmarks
from django.shortcuts import redirect, get_object_or_404
import json
import time


class Feed(APIView):
    def get(self, request):
        auth_status = Helper(request).is_autheticated()
        user = User.objects.filter(id=auth_status["payload"]["id"]).first()
        posts = Post.objects.all()
        serializer = PostDetailSerializer(posts, many=True)
        print(serializer.data)

        return Response(
            {
                "status": True,
                "message": "Posts fetched successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def user_liked(self, user):
        pass


class PostList(APIView):
    def post(self, request):

        auth_status = Helper(request).is_autheticated()
        if auth_status["status"]:
            user = User.objects.filter(id=auth_status["payload"]["id"]).first()

            data = get_data(request.POST)
            serializer = PostSerializer(data=data)
            audio_data = request.FILES.get("audio")
            data["thumbnail"] = request.FILES.get("thumbnail")
            if audio_data:

                audio_id = (
                    str(int(time.time())) + "_" + str(auth_status["payload"]["id"])
                )
                modified_data = Helper(request).modify_audio_input(audio_id, audio_data)
                file_serializer = AudioSerializer(data=modified_data)
                if file_serializer.is_valid():
                    file_serializer.save()
                    data["audio"] = json.dumps(file_serializer.data["audio"])

                else:
                    return Response(
                        {"status": False, "message": file_serializer.errors},
                        status=status.HTTP_200_OK,
                    )

            if serializer.is_valid():
                serializer.save(owner=user)

                return Response(
                    {
                        "status": True,
                        "message": "Post created successfully",
                        "data": serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
                )

            else:
                return Response(
                    {"status": False, "message": serializer.errors},
                    status=status.HTTP_200_OK,
                )
        else:
            return Response(
                {"status": False, "message": "Unathorised"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

    def get(self, request):
        posts = Post.objects.all()
        serializer = PostDetailSerializer(posts, many=True)
        return Response(
            {
                "status": True,
                "message": "Posts fetched successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class PostDetail(RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostDetailSerializer


class LikeBlog(APIView):
    """
    get:
        Likes the desired blog.
        parameters = [pk]
    """

    def get(self, request, pk):
        auth_status = Helper(request).is_autheticated()

        if auth_status["status"]:
            user = User.objects.filter(id=auth_status["payload"]["id"]).first()
            post = get_object_or_404(Post, pk=pk)

            if user in post.likes.all():
                post.likes.remove(user)
                return Response(
                    {"status": True, "message": "Post Unliked"},
                    status=status.HTTP_200_OK,
                )

            else:
                post.likes.add(user)

            return Response(
                {"status": True, "message": "Post liked"},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"status": False, "message": "Unathorised"},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class CategoryList(APIView):
    def post(self, request):

        auth_status = Helper(request).is_autheticated()
        if auth_status["status"]:
            user = User.objects.filter(id=auth_status["payload"]["id"]).first()
            data = get_data(request.POST)
            serializer = CategorySerializer(data=data)
            if serializer.is_valid():
                serializer.save(authur=user)

                return Response(
                    {
                        "status": True,
                        "message": "Post created successfully",
                        "data": serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
                )

            else:
                return Response(
                    {"status": False, "message": serializer.errors},
                    status=status.HTTP_200_OK,
                )
        else:
            return Response(
                {"status": False, "message": "Unathorised"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

    def get(self, request):
        cats = Category.objects.all()
        serializer = CategorySerializer(cats, many=True)
        return Response(
            {
                "status": True,
                "message": "Category fetched successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class CategoryDetail(RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CommentList(APIView):
    def post(self, request, pk):

        auth_status = Helper(request).is_autheticated()
        if auth_status["status"]:
            data = get_data(request.POST)
            post = get_object_or_404(Post, pk=pk)
            data["post"] = post.id
            user = User.objects.filter(id=auth_status["payload"]["id"]).first()
            audio_data = request.FILES.get("audio")
            if audio_data:

                audio_id = (
                    str(int(time.time())) + "_" + str(auth_status["payload"]["id"])
                )
                modified_data = Helper(request).modify_audio_input(audio_id, audio_data)
                file_serializer = AudioSerializer(data=modified_data)
                if file_serializer.is_valid():
                    file_serializer.save()
                    data["audio"] = json.dumps(file_serializer.data["audio"])

            serializer = CommentSerializer(data=data)
            if serializer.is_valid():
                serializer.save(
                    owner=user,
                )

                return Response(
                    {
                        "status": True,
                        "message": "Comment created successfully",
                        "data": serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
                )

            else:
                return Response(
                    {"status": False, "message": serializer.errors},
                    status=status.HTTP_200_OK,
                )
        else:
            return Response(
                {"status": False, "message": "Unathorised"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(
            {
                "status": True,
                "message": "Posts fetched successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class BookmarksView(APIView):
    def post(self, request):

        pid = request.GET.get("post")
        auth_status = Helper(request).is_autheticated()
        if auth_status["status"]:
            user = User.objects.filter(id=auth_status["payload"]["id"]).first()
            post = get_object_or_404(Post, pk=pid)

            if not Bookmarks.objects.filter(user=user).exists():

                bmk = Bookmarks.objects.create(user=user)
                bmk.post.add(post)
                bmk.save()
                serializer = BookmarksSerializer(bmk)

                return Response(
                    {
                        "status": True,
                        "message": "New bookmark created successfully",
                        "data": serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
                )
            else:
                bmk = Bookmarks.objects.get(user=user)
                bmk.post.add(post)
                serializer = BookmarksSerializer(bmk)
                return Response(
                    {
                        "status": True,
                        "message": "New post added successfully",
                        "data": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
        else:

            return Response(
                {
                    "status": False,
                    "message": "Unathorised",
                },
                status=status.HTTP_200_OK,
            )

    def get(self, request):

        auth_status = Helper(request).is_autheticated()
        if auth_status["status"]:
            user = User.objects.filter(id=auth_status["payload"]["id"]).first()
            bmk = get_object_or_404(Bookmarks, user=user)
            serializer = BookmarksSerializer(bmk)

            return Response(
                {
                    "status": True,
                    "message": "Bookmark fetched successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        else:

            return Response(
                {
                    "status": False,
                    "message": "Unathorised",
                },
                status=status.HTTP_200_OK,
            )

    def delete(self, request):

        pid = request.GET.get("post")
        auth_status = Helper(request).is_autheticated()
        if auth_status["status"]:
            user = User.objects.filter(id=auth_status["payload"]["id"]).first()
            post = get_object_or_404(Post, pk=pid)
            bmk = get_object_or_404(Bookmarks, user=user)

            bmk.post.remove(post)
            bmk.save()
            serializer = BookmarksSerializer(bmk)

            return Response(
                {
                    "status": True,
                    "message": "Bookmark removed successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_204_NO_CONTENT,
            )
        else:

            return Response(
                {
                    "status": False,
                    "message": "Unathorised",
                },
                status=status.HTTP_200_OK,
            )
