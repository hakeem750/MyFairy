from django.db import models
from ..model.user import User


class MenstrualCycle(models.Model):

    LIGHT = 'LT'
    MEDIUM = 'MD'
    HEAVY = 'HV'
    PERIOD_FLOW_CHOICE = (
        (LIGHT, 'light'),
        (MEDIUM, 'medium'),
        (HEAVY, 'heavy'),
    )
    Last_period_date = models.DateField()
    # Cycle_average = models.PositiveIntegerField()
    Cycle_length = models.PositiveIntegerField(default=28)
    # Period_average = models.PositiveIntegerField()
    Period_length = models.PositiveIntegerField(default=4)
    # Start_date = models.DateField()
    # End_date = models.DateField()
    # cycle_event_date = models.DateField(blank=True, null=True)
    # email = models.CharField(max_length=100)
    # name = models.CharField(max_length=100)
    period_flow = models.CharField(max_length=2,
                                   choices=PERIOD_FLOW_CHOICE,
                                   default=MEDIUM, )
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
