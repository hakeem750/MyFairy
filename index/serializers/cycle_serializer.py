from rest_framework import serializers
from ..model.menstrual_cycle import MenstrualCycle, MyFairy
from ..model.user import User


class MenstrualCycleSerializer(serializers.ModelSerializer):
    Cycle_length = serializers.IntegerField(max_value=40)
    Period_length = serializers.IntegerField(min_value=1)

    class Meta:
        model = MenstrualCycle
        fields = [
            "Last_period_date",
            "Cycle_length",
            "Period_length",
            "period_flow", 
        ]

class FairySerializer(serializers.ModelSerializer):    

    class Meta:
        model = MyFairy
        fields = [
            "email",
        ]
        
class EachFairySerializer(serializers.ModelSerializer):    

    class Meta:
        model = MenstrualCycle
        fields = [
            "Last_period_date",
            "Cycle_length",
            "Period_length",
            "period_flow",
            "email",
        ]

    # def create(self, validated_data):
        
    #     instance = self.Meta.model(**validated_data)
    #     instance.myfairy = True
    #     instance.save()
    #     return instance