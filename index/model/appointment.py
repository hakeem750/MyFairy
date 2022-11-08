from django.db import models
from ..model.user import User



class Personel(models.Model):

     owner = models.ForeignKey(User, related_name="personel", on_delete=models.CASCADE)
     bio = models.CharField(max_length=300)
     qualification = models.CharField(max_length=100)
     speciality = models.CharField(max_length=200)
     is_available = models.BooleanField(default=True)


class Time_Slots(models.Model):
    personel = models.ForeignKey(Personel, related_name="personel", on_delete=models.CASCADE)
    from_time = models.CharField(max_length=10)
    to_time = models.CharField(max_length=10)


class Appointments(models.Model):
    
    patient = models.CharField(max_length=100)
    personel = models.CharField(max_length=100)
    date = models.CharField(max_length=50)
    time_alloted = models.CharField(max_length=50)
    is_completed = models.BooleanField(default=False)
    is_confirmed = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    is_disabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        get_latest_by ='created_at'