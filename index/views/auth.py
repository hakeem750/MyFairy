from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..helper import Helper, get_data
from ..serializers.user_serializer import *
from ..model.user import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404
from django.urls import reverse
import random
import jwt
import os
from django.conf import settings



class RegisterView(APIView):
    def post(self, request, *args, **kwargs):

        data = get_data(request.POST)
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            token = Helper(request).get_token(
                serializer.data["id"], serializer.data["fullname"]
            )
            site = get_current_site(request).domain
            user = User.objects.get(email=serializer.validated_data["email"])
            access_token = Helper(request).get_verify_token(user)

            link = reverse("verify-email")

            url = "http://" + site + link + "?token=" + str(access_token)
            body = (
                "Hi "
                + user.fullname
                + " Use the link below to verif your e-mail address \n"
                + url
            )
            data = {
                "subject": "VerIfy Your Email",
                "body": body,
                "user_email": user.email,
            }
            Helper.send_email(data)

            return Response(
                {
                    "status": True,
                    "message": "User created successfully",
                    "token": token,
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        else:
            return Response(
                {"status": False, "message": serializer.errors},
                status=status.HTTP_200_OK,
            )

class VerifyEmail(APIView):
    def get(self, request):
        token = Helper(request).return_token()
        try:
            payload = token["payload"]
            if payload is None:
                 return Response(
                {"status": False, "message": "Activation expired, try again"},
                status=status.HTTP_200_OK,
            )
            user = User.objects.get(id=payload["user_id"])
            if not user.email_verified:
                user.email_verified = True

            return Response(
                {"status": True, "email": "E-mail verified successfully"},
                status=status.HTTP_200_OK,
            )

        except jwt.ExpiredSignatureError as e:

            return Response(
                {"status": False, "error": "Activation expired"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except jwt.exceptions.DecodeError as e:
            return Response(
                {"status": False, "error": "Invalid token"},
                status=status.HTTP_404_NOT_FOUND,
            )


class GetConsent(APIView):
    def get(self, request):
        token = Helper(request).return_token()
        print(token)
        try:
            payload = token["payload"]
            user = User.objects.get(id=payload["user_id"])
            parent = Parent.objects.filter(user=user).first()
            if not parent.conscent:
                parent.conscent = True

            return Response(
                {"status": True, "parent": "parent consent successfully"},
                status=status.HTTP_200_OK,
            )

        except jwt.ExpiredSignatureError as e:

            return Response(
                {"status": False, "error": "Activation expired"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except jwt.exceptions.DecodeError as e:
            return Response(
                {"status": False, "error": "Invalid token"},
                status=status.HTTP_404_NOT_FOUND,
            )


class UserDetails(APIView):
    def get(self, request):
        auth_status = Helper(request).is_autheticated()
        if auth_status["status"]:
            user = User.objects.filter(id=auth_status["payload"]["id"]).first()
            serializers = UserDetailSerializer(user)
            return Response(
                {
                    "status": True,
                    "message": "User Feteched Successfully",
                    "data": serializers.data,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"status": False, "message": "Unathorised"}, status=status.HTTP_200_OK
            )

    def put(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        pass


class ParentEmail(APIView):
    def post(self, request, *args, **kwargs):

        auth_status = Helper(request).is_autheticated()
        if auth_status["status"]:
            user = User.objects.filter(id=auth_status["payload"]["id"]).first()
            data = {}
            data["email"] = request.POST.get('email')
            serializer = ParentSerializer(data=data)
            if serializer.is_valid():
                serializer.save(user=user)
                site = get_current_site(request).domain
                access_token = Helper(request).get_verify_token(user)

                link = reverse("get-parent-consent")

                url = "http://" + site + link + "?token=" + str(access_token)
                body = (
                    "Hi "
                    + user.fullname
                    + " guardian/parent \n"
                    + "Use the link below to consent for your ward to use this platform \n"
                    + url
                )
                data = {
                    "subject": "Parent Consent",
                    "body": body,
                    "user_email": serializer.data["email"],
                }
                Helper.send_email(data)

                return Response(
                    {
                        "status": True,
                        "message": "Consent email sent to parent",
                        "url": url,
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
                {"status": False, "message": serializer.errors},
                status=status.HTTP_200_OK,
            )


class GetParentConsent(APIView):
    def get(self, request):
        token = Helper(request).return_token()
        try:
            payload = token["payload"]
            if payload is None:
                 return Response(
                {"status": False, "message": "Consent expired, try again"},
                status=status.HTTP_200_OK,
            )
            user = User.objects.get(id=payload["user_id"])
            parent = Parent.objects.filter(user=user.id)

            if not parent.consent:
                parent.consent = True

            return Response(
                {"status": True, 
                 "email": "E-mail verified successfully"},
                status=status.HTTP_200_OK,
            )

        except jwt.ExpiredSignatureError as e:

            return Response(
                {"status": False, "error": "Activation expired"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except jwt.exceptions.DecodeError as e:
            return Response(
                {"status": False, "error": "Invalid token"},
                status=status.HTTP_404_NOT_FOUND,
            )


class Login(APIView):
    def post(self, request, *args, **kwargs):

        email = request.POST.get("email")
        password = request.POST.get("password")
        user = User.objects.filter(email=email).first()
        
        if user is None:
            return Response(
                {"status": False, "message": "User not Found Invalid email or password"},
                status=status.HTTP_200_OK,
            )

        parent = Parent.objects.filter(user=user.id)
        age = Helper.calculate_age(user.dob)

        if age < 13 and parent is None:
             return Response(
                {"status": False, "message": "Parent not Found"},
                status=status.HTTP_200_OK,
            )

        if age < 13 and parent.conscent == false:
            return Response(
                {"status": False, "message": "User is below age and concent is needed"},
                status=status.HTTP_200_OK,
            )

        
        
        if not user.check_password(password):
            return Response(
                {"status": False, "message": "Incorrect Password"},
                status=status.HTTP_200_OK,
            )

        token = Helper(request).get_token(user.id, user.nickname)
        serializers = UserSerializer(user)
        return Response(
            {
                "status": True,
                "message": "success",
                "token": token,
                "data": serializers.data,
            }
        )


class VerifyCode(APIView):
    def post(self, request, *args, **kwargs):

        phone = request.POST.get('phone')
        user = User.objects.filter(phone=phone).first()
        if user is None:
            return Response(
                {"status": False, "message": "User not Found"},
                status=status.HTTP_200_OK,
            )

        if not user.code == request.data["code"]:
            return Response(
                {"status": False, "message": "Code did not match"},
                status=status.HTTP_200_OK,
            )
        else:
            user.phone_verified = True
            user.save()
        return Response({"status": True, "message": "success"})


class ForgotPasswordView(APIView):
    def post(self, request, *args, **kwargs):

        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        if user is None:
            return Response(
                {"status": False, "message": "User not Found"},
                status=status.HTTP_200_OK,
            )

        random_number = random.randint(100000, 999999)  # generate a random number
        body = (
            "Hi "
            + user.fullname
            + " enter this code reset your password \n"
            + str(random_number)
        )
        data = {
            "subject": "Password Reset",
            "body": body,
            "user_email": user.email,
        }
        Helper.send_email(data)
        user.code = random_number
        user.save()
        return Response({"status": True, "message": "success, your code has been sent"})


class VerifyForgotPasswordView(APIView):
    def post(self, request, *args, **kwargs):

        email = request.POST.get('email')
        code = request.POST.get('code')
        user = User.objects.filter(email=email).first()

        if user is None:
            return Response(
                {"status": False, "message": "User not Found"},
                status=status.HTTP_200_OK,
            )
        if user.code != code:
            return Response(
                {"status": False, "message": "Code does not match"},
                status=status.HTTP_200_OK,
            )

        user.password = make_password(request.data["password"])
        user.save()
        return Response(
            {"status": True, "message": "success, password has been reset successfully"}
        )
