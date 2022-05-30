from ..model.post import Post  # , Comment, Category, LikedPost
from ..model.user import User
from ..helper import Helper
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView,
)
from rest_framework import status
from ..serializers.post_serializer import *
from rest_framework import permissions
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.owner == request.user


class PostList(APIView):
    def post(self, request):

        auth_status = Helper(request).is_autheticated()
        print(auth_status)
        if auth_status["status"]:
            user = User.objects.filter(id=auth_status["payload"]["id"]).first()
            serializer = PostSerializer(data=request.data)
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
    serializer_class = PostSerializer


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

            else:
                post.likes.add(user)

            return Response(
                {
                    "ok": "Your request was successful.",
                },
                status=200,
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
            serializer = CategorySerializer(data=request.data)
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
            post = get_object_or_404(Post, pk=pk)
            request.data["post"] = post.id
            user = User.objects.filter(id=auth_status["payload"]["id"]).first()
            serializer = CommentSerializer(data=request.data)
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


# class CommentDetail(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Comment.objects.all()
#     serializer_class = CommentSerializer
#     permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
