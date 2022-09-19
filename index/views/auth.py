from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView, ListCreateAPIView
from rest_framework.response import Response
from rest_framework import status, filters 
from ..helper import Helper, get_data
from ..serializers.user_serializer import *
from ..model.user import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404
from django.urls import reverse
import random
import jwt
import os
from django.conf import settings
from django.shortcuts import render
from django.http import Http404
from collections import OrderedDict


class RegisterView(APIView):
    def post(self, request, *args, **kwargs):

        data = get_data(request.POST)
        print(data)
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
                 return render(request, 'try-again.html', {})

            user = User.objects.get(id=payload["user_id"])
            if not user.email_verified:
                user.email_verified = True
                user.save()

                return render(request, 'verify.html', {})

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
        #print(token)
        try:
            payload = token["payload"]
            user = User.objects.get(id=payload["user_id"])
            parent = Parent.objects.filter(user=user).first()
            if not parent.conscent:
                parent.conscent = True
                parent.save()

            return render(request, 'consent.html', {})

        except jwt.ExpiredSignatureError as e:

            return render(request, 'try-consent.html', {})

        except jwt.exceptions.DecodeError as e:
            return render(request, 'try-consent.html', {})

        except Exception as e:
            return render(request, 'try-consent.html', {})

class UserDetails(APIView):
    def get(self, request, pk):

        try :

            user = User.objects.get(pk=pk)
            
        except User.DoesNotExist:
            return Response(
                    {
                        "status": False,
                        "message": "User not found",
                    },
                    status=status.HTTP_200_OK,
                )
        serializers = UserDetailSerializer(user)
        return Response(
            {
                "status": True,
                "message": "User Feteched Successfully",
                "data": serializers.data,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):

        data = get_data(request.POST)
        data["profile_pic"] = request.FILES.get('profile_pic')

        try :

            user = User.objects.get(pk=pk)

        except User.DoesNotExist:
            return Response(
                    {
                        "status": False,
                        "message": "User not found",
                    },
                    status=status.HTTP_200_OK,
                )

        serializer = UserSerializer(user, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()


            return Response(
                    {
                        "status": True,
                        "message": "data updated successfully",
                        "data": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
        else:
            return Response(
                {"status": False, "message": serializer.errors},
                status=status.HTTP_200_OK,
            )

    def delete(self, request, pk):

        user = User.objects.get(id=pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ParentEmail(APIView):
    def post(self, request, *args, **kwargs):

        auth = Helper(request).is_autheticated()
        if auth["status"]:
            user = User.objects.filter(id=auth["payload"]["id"]).first()
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
                    + " Guardian/Parent \n"
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
                {"status": False, "message": "Unathorised"},
                status=status.HTTP_200_OK,
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
        token = Helper(request).get_token(user.id, user.nickname)
        parent = Parent.objects.filter(user=user.id).first()
        age = Helper.calculate_age(user.dob)

        if age < 13 and parent is None:
             return Response(
                {"status": False, "message": "Parent not Found"},
                status=status.HTTP_200_OK,
            )

        if age < 13 and parent.conscent == False:
            return Response(
                {"status": False, 
                 "message": "User is below age and concent is needed",
                 "token": token
                 },
                status=status.HTTP_200_OK,
            )

        
        
        if not user.check_password(password):
            return Response(
                {"status": False, "message": "Incorrect Password"},
                status=status.HTTP_200_OK,
            )

        
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
            + " enter this code to reset your password \n"
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
        return Response({"status": True, "message": "success, your code has been sent"},
                status=status.HTTP_200_OK)

class VerifyForgotPasswordView(APIView):
    def post(self, request, *args, **kwargs):

        email = request.POST.get('email')
        code = int(request.POST.get('code'))
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

        return Response(
            {"status": True, "message": "success"},
                status=status.HTTP_200_OK
        )

class EnterPasswordView(APIView):
    def post(self, request, *args, **kwargs):

        email = request.POST.get('email')
        password = request.POST.get('password')
        user = User.objects.filter(email=email).first()

        if user is None:
            return Response(
                {"status": False, "message": "User not Found"},
                status=status.HTTP_200_OK,
            )

        user.password = make_password(password)
        user.save()
        return Response(
            {"status": True, "message": "success, password has been reset successfully"},
                status=status.HTTP_200_OK
        )

def check_user(data, following):
    if Profile.objects.get(user_id=data["user_id"]) in following:
        data["isfollowing"] = True
        return data

    return data

class FollowUnfollowView(APIView):
    
    def my_profile(self, pk):
        try:

            return Profile.objects.get(user_id=pk)
        except Profile.DoesNotExist:
            raise Http404
        
    def other_profile(self, pk):
        try:
            return Profile.objects.get(user_id=pk)
        except Profile.DoesNotExist:
            raise Http404
    
    def post(self, request, format=None): 
        auth = Helper(request).is_autheticated()

        if auth["status"]:
            data = get_data(request.POST)
            pk = data.get('id')              # Here pk is opposite user's profile ID
            req_type = data.get('type')

            ### types to get
            # follow
            # accept
            # decline
            # unfollow
            # remove
                    
            
            current_profile = self.my_profile(auth["payload"]["id"])
            other_profile = self.other_profile(pk)
                    
            
            if req_type == 'follow':
                if other_profile.private_account:
                    other_profile.pending_request.add(current_profile)
                    return Response({
                        "status": True,
                        "message" : "Follow request has been send!!"
                        },
                        status=status.HTTP_200_OK)
                else:
                    if other_profile.blocked_user.filter(id=current_profile.id).exists():
                        return Response({
                            "status": False,
                            "message" : "You can not follow this profile becuase your ID blocked by this user!!"
                            },
                            status=status.HTTP_400_BAD_REQUEST)

                    current_profile.following.add(other_profile)
                    other_profile.followers.add(current_profile)

                    return Response({
                        "status":True, 
                        "message" : "Following successfully!!"
                        },
                        status=status.HTTP_200_OK) 
            
            elif req_type == 'accept':

                current_profile.followers.add(other_profile)
                other_profile.following.add(current_profile)
                current_profile.pending_request.remove(other_profile)

                return Response({
                    "status":True, 
                    "Accepted" : "Follow request successfuly accespted!!"
                    },
                    status=status.HTTP_200_OK)
            
            elif req_type == 'decline':

                current_profile.pending_request.remove(other_profile)
                return Response({
                    "status":True, 
                    "message":"Follow request successfully declined!!"
                    },
                    status=status.HTTP_200_OK)
            
            elif req_type == 'unfollow':

                current_profile.following.remove(other_profile)
                other_profile.followers.remove(current_profile)
                return Response({
                    "status":True, 
                    "Unfollow" : "Unfollow success!!"
                    },
                    status=status.HTTP_200_OK)
                
            elif req_type == 'remove':     # You can remove your follower
                current_profile.followers.remove(other_profile)
                other_profile.following.remove(current_profile)
                return Response({
                    "status":True,
                    "Remove Success" : "Successfuly removed your follower!!"
                    },
                    status=status.HTTP_200_OK)
        else:
            return Response(
                {
                "status": False, 
                "message": "Unathorised"
                },
                status=status.HTTP_200_OK,
            )

                    # Here we can fetch followers, following detail and blocked user, pending request, sended request.. 

    def patch(self, request, format=None):
    
        req_type = request.data.POST.get('type')
    
        if req_type == 'follow_detail':
            serializer = FollowerSerializer(self.current_profile())
            return Response({"data" : serializer.data},status=status.HTTP_200_OK)
    
        elif req_type == 'block_pending':
            serializer = BlockPendinSerializer(self.current_profile())
            pf = list(Profile.objects.filter(pending_request = self.current_profile().id).values('id','user__nickname','profile_pic'))
            return Response({"data" : serializer.data,"Sended Request" :pf},status=status.HTTP_200_OK)

    # You can block and unblock user

    def put(self, request):

        auth = Helper(request).is_autheticated()

        if auth["status"]:
            data = get_data(request.POST)
            pk = data.get('id')              # Here pk is oppisite user's profile ID
            req_type = data.get('type')
    
        if req_type == 'block':
            self.current_profile().blocked_user.add(self.other_profile(pk))
            return Response({
                "status":True,
                "Blocked" : "This user blocked successfuly"
                },
                status=status.HTTP_200_OK)
        elif req_type == 'unblock':
            self.current_profile().blocked_user.remove(self.other_profile(pk))
            return Response({"Unblocked" : "This user unblocked successfuly"},status=status.HTTP_200_OK)

    def get(self, request):

        auth = Helper(request).is_autheticated()

        if auth["status"]:
            profile = Profile.objects.filter(user_id=auth["payload"]["id"])[0]
            serializer = FollowerSerializer(profile)
            following = profile.following.all()
            sdata = dict(serializer.data)
            data = dict(serializer.data)["followers"]
            data = [i if dict(i)["isfollowing"] == True else OrderedDict(check_user(dict(i), following)) for i in data]
            
            sdata["followers"] = data
            sdata = OrderedDict(sdata)



            return Response(
            {
                "status": True,
                "message": "Followers Feteched Successfully",
                "data": sdata,
            },
            status=status.HTTP_200_OK,
        )
        else:
            return Response(
                {
                "status": False, 
                "message": "Unathorised"
                },
                status=status.HTTP_200_OK,
            )

class ReferAFriend(APIView):
    def post(self, request, *args, **kwargs):

        auth = Helper(request).is_autheticated()
        if auth["status"]:
            user = User.objects.filter(id=auth["payload"]["id"]).first()
            data = {}
            data["email"] = request.POST.get('email')
            site = get_current_site(request).domain

            link = reverse("register")

            url = "http://" + site + link
            body = (
                "Hi Fairy\n"
                + user.fullname
                + "has invite you\n"
                + url
            )
            data = {
                "subject": "Parent Consent",
                "body": body,
                "user_email": data["email"],
            }
            Helper.send_email(data)

            return Response(
                {
                    "status": True,
                    "message": "Invitation Sent",
                    "url": url,
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {"status": False, "message": "Unathorised"},
                status=status.HTTP_200_OK,
            )

class GetContacts(APIView):

    def post(self, request, *args, **kwargs):

        auth = Helper(request).is_autheticated()
        if auth["status"]:
            user = User.objects.filter(id=auth["payload"]["id"]).first()
            print(request.data)
            numbers = request.data["contacts"]
            data = self.check_data(numbers)

            return Response(
                {
                    "status": True,
                    "message": "Contact data checked successfully",
                    "contacts": data,
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {"status": False, "message": "Unathorised"},
                status=status.HTTP_200_OK,
            )
    
    def check_data(self, numbers):
        if len(numbers) > 0:
            data = [{"phone":i, "isAvailable":User.objects.filter(phone=i).exists()} for i in numbers]
            return data 
        else:
             return []


class SearchView(ListCreateAPIView):

    search_fields = ["nickname"]
    filter_backends = (filters.SearchFilter,)
    queryset = User.objects.all()
    serializer_class = UserSearchSerializer