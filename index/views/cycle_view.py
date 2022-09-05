from rest_framework import permissions, status
from ..model.user import User
from ..helper import Helper
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from ..model.menstrual_cycle import MenstrualCycle, Fairy
from ..helper import *
from ..serializers.cycle_serializer import *
from rest_framework.generics import CreateAPIView, UpdateAPIView
from django.db import IntegrityError



class CreateCycleView(APIView):
    def post(self, request):

        auth_status = Helper(request).is_autheticated()
        if auth_status["status"]:
            user = User.objects.filter(id=auth_status["payload"]["id"]).first()
            user_data = request.data
            serializer = MenstrualCycleSerializer(data=user_data)

            if serializer.is_valid():
                serializer.save(owner=user)

                return Response(
                {
                "status": True,
                "message": "Cycle created successfully", 
                "data": serializer.data 
                },
                status=status.HTTP_201_CREATED,
            )

            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)            

        else:
            return Response(
                {"status": False, "message": "Unathorised"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

    def put(self, request, **kwargs):
        auth_status = Helper(request).is_autheticated()
        if auth_status["status"]:

            user = User.objects.filter(id=auth_status["payload"]["id"]).first()
            update_period = MenstrualCycle.objects.filter(owner=user).first()
            serializer = MenstrualCycleSerializer(data=request.data, partial=True)

            if serializer.is_valid():
                serializer.instance = update_period
                serializer.save()
                user_data = serializer.data
                last_period_date = user_data.get("Last_period_date", "")
                cycle_length = user_data.get("Cycle_length", "")
                period_length = user_data.get("Period_length", "")
                period_flow = user_data.get("period_flow", "")
                owner = user
                #name = owner.nickname
                return Response(
                    {"status": True, "data": serializer.data, },
                    status=status.HTTP_201_CREATED,
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"status": False, "message": "Unathorised"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

class ListEvent(APIView):
    def get(self, request, *args, **kwargs):

        auth_status = Helper(request).is_autheticated()
        if auth_status["status"]:
            user = User.objects.filter(id=auth_status["payload"]["id"]).first()
            user_data = MenstrualCycle.objects.filter(owner=user).last()

            if user_data is None:
                return Response(
                {"status": False,
                 "message": "You need to create a cycle first",
                 "Events": None},
                status=status.HTTP_200_OK,
            )
            serializer = MenstrualCycleSerializer(user_data)
            Last_period_date = user_data.Last_period_date#serializer.data.get("Last_period_date", "")
            Cycle_length = serializer.data.get("Cycle_length", "")
            Period_length = serializer.data.get("Period_length", "")

            events = cycle_events(Last_period_date, Cycle_length, Period_length)

            return Response({"status": True,"Events":events}, status=status.HTTP_200_OK)

        else:
            return Response(
                {"status": False, "message": "Unathorised"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

class AddListFairy(APIView):
    def post(self, request):

        auth_status = Helper(request).is_authenticated()
        if auth_status["status"]:
            user = User.objects.filter(id=auth_status["payload"]["id"]).first()
            serializer = MenstrualCycleSerializer(request.data)

            if serializer.is_valid():
                serializer.save(owner=user)

                return Response(
                    {
                        "status": True,
                        "message": "Fairy created successfully",
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
    
        auth_status = Helper(request).is_authenticated()
        if auth_status["status"]:
            user = User.objects.filter(id=auth_status["payload"]["id"]).first()
            
            faries = MenstrualCycle.objects.filter(owner=user)
            serializer = MenstrualCycleSerializer(faries, many=True)
            
            return Response({"status": True, "Faires":serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"status": False, "message": "Unathorised"},
                status=status.HTTP_401_UNAUTHORIZED)
                        
class CreateFairyCycleView(APIView):
    def post(self, request):

        auth_status = Helper(request).is_autheticated()
        if auth_status["status"]:
            user = User.objects.filter(id=auth_status["payload"]["id"]).first()
            user_data = request.data
            serializer = FairySerializer(data=user_data)

            if serializer.is_valid():
                serializer.save(owner=user)
                return Response(
                {
                "status": True,
                "message": "Fairy created successfully", 
                "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)            

        else:
            return Response(
                {"status": False, "message": "Unathorised"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

    def put(self, request, **kwargs):
        auth_status = Helper(request).is_autheticated()
        if auth_status["status"]:

            user = User.objects.filter(id=auth_status["payload"]["id"]).first()
            update_fairy = Fairy.objects.filter(owner=user).first()
            serializer = FairySerializer(data=request.data, partial=True)

            if serializer.is_valid():
                serializer.instance = update_fairy
                serializer.save()
                user_data = serializer.data
                email = user_data.get("email", "")
                owner = user
                return Response(
                    {"status": True, "data": serializer.data,},
                    status=status.HTTP_201_CREATED,
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"status": False, "message": "Unathorised"},
                status=status.HTTP_401_UNAUTHORIZED,
            )            
            

class ShareCycleView(APIView):


    def send_email(self, email, user):
    
        body = (
            "Hi Fairy\n"
            + user.fullname
            + "has shared her Menstrual Cycle with you\n"
            
        )
        email_data = {
            "subject": "Menstrual Cycle",
            "body": body,
            "user_email": email,
        }
        Helper.send_email(email_data)

    def post(self, request):

        auth_status = Helper(request).is_autheticated()
        if auth_status["status"]:
            user = User.objects.filter(id=auth_status["payload"]["id"]).first()
            data = get_data(request.POST)
            print(data)
            serializer = ShareCycleSerializer(data=data)

            if serializer.is_valid():
                serializer.save(owner=user)
                email = data.get("shared", "")
                self.send_email(email, user)

                return Response(
                {
                "status": True,
                "message": "Cycle Shared successfully", 
                "data": serializer.data 
                },
                status=status.HTTP_201_CREATED,
            )

            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)            

        else:
            return Response(
                {"status": False, "message": "Unathorised"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

    def put(self, request, **kwargs):
        auth_status = Helper(request).is_autheticated()
        if auth_status["status"]:

            user = User.objects.filter(id=auth_status["payload"]["id"]).first()
            update_fairy = Fairy.objects.filter(owner=user).first()
            serializer = ShareCycleSerializer(data=request.data, partial=True)

            if serializer.is_valid():
                serializer.instance = update_fairy
                serializer.save()
                user_data = serializer.data
                email = user_data.get("email", "")
                
                return Response(
                    {"status": True, "data": serializer.data,},
                    status=status.HTTP_201_CREATED,
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"status": False, "message": "Unathorised"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
   