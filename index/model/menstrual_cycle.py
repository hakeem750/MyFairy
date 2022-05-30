from django.db import models
from ..model.user import User


class MenstrualCycle(models.Model):

    Last_period_date = models.DateField()
    Cycle_average = models.PositiveIntegerField()
    Cycle_length = models.PositiveIntegerField(default=28)
    Period_average = models.PositiveIntegerField()
    Period_length = models.PositiveIntegerField(default=4)
    Start_date = models.DateField()
    End_date = models.DateField()
    cycle_event_date = models.DateField(blank=True, null=True)
    # email = models.CharField(max_length=100)
    # name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
