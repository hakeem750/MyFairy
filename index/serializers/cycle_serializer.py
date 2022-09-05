from rest_framework import serializers
from ..model.menstrual_cycle import MenstrualCycle, Fairy


class MenstrualCycleSerializer(serializers.ModelSerializer):
    Cycle_length = serializers.IntegerField(max_value=33)
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
        model = Fairy
        fields = [
            "email", 
        ]

class ShareCycleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Fairy
        fields = [
            "shared", 
        ]