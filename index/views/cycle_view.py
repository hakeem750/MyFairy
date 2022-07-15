from rest_framework import permissions, status
from ..model.user import User
from ..helper import Helper
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from ..model.menstrual_cycle import MenstrualCycle
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
            print(user_data)
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


# class ListCycleEvent(APIView):
#     def get(self, request, *args, **kwargs):

#         auth_status = Helper(request).is_autheticated()
#         if auth_status["status"]:
#             user = User.objects.filter(id=auth_status["payload"]["id"]).first()
#             user_data = MenstrualCycle.objects.filter(owner=user)[0]
#             serializer = MenstrualCycleSerializer(user_data)
#             cycle_event = request.query_params.get("date")
#             Last_period_date = serializer.data.get("Last_period_date", "")
#             Cycle_average = serializer.data.get("Cycle_average", "")
#             Period_average = serializer.data.get("Period_average", "")
#             date_data = get_closest_date_from_list(
#                 cycle_event, Last_period_date, Cycle_average, Start_date, End_date
#             )
#             try:
#                 last_periods = date_data[0]
#                 next_periods = date_data[1]
#             except KeyError:
#                 return Response(
#                     {"error": "date not in range of record available"},
#                     status=status.HTTP_400_BAD_REQUEST,
#                 )
#             print(date_data)
#             user_info = cycle_event_analyst(
#                 last_periods, cycle_event, Cycle_average, Period_average, next_periods
#             )

#             return Response(user_info, status=status.HTTP_200_OK)

#         else:
#             return Response(
#                 {"status": False, "message": "Unathorised"},
#                 status=status.HTTP_401_UNAUTHORIZED,
#             )


class ListEvent(APIView):
    def get(self, request, *args, **kwargs):

        auth_status = Helper(request).is_autheticated()
        if auth_status["status"]:
            user = User.objects.filter(id=auth_status["payload"]["id"]).first()
            user_data = MenstrualCycle.objects.filter(owner=user).first()
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
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
   