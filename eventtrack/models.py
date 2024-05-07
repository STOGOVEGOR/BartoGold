from django.contrib.auth.forms import UserCreationForm
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser


class User(models.Model):
    email = models.EmailField(unique=True, null=True)
    department_id = models.IntegerField(null=True)
    level_id = models.IntegerField(null=True)
    objects = models.Manager()


class SafeAct(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True)
    location = models.CharField(max_length=50, null=True)
    q1 = models.IntegerField(null=True)
    q2 = models.IntegerField(null=True)
    q3 = models.IntegerField(null=True)
    q4 = models.IntegerField(null=True)
    q5 = models.IntegerField(null=True)


class Take5(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True)
    hazard = models.ForeignKey('Hazard', on_delete=models.SET_NULL, null=True)
    description = models.CharField(max_length=250, null=True)
    qA = models.IntegerField(null=True)
    qB = models.IntegerField(null=True)
    qC = models.IntegerField(null=True)
    qD = models.IntegerField(null=True)
    qE = models.IntegerField(null=True)
    qF = models.IntegerField(null=True)
    hazard_num = models.CharField(max_length=50, null=True)
    control_measure = models.CharField(max_length=250, null=True)
    supervisor = models.CharField(max_length=50, null=True)
    superv_ack_id = models.IntegerField(null=True)
    superv_ack_date = models.DateTimeField(null=True)
    superv_action = models.CharField(max_length=250, null=True)
    user_ip = models.CharField(max_length=50, null=True)


class Hazard(models.Model):
    level = models.CharField(max_length=50, null=True)


class SafeActAction(models.Model):
    form_id = models.IntegerField()
    location = models.CharField(max_length=50, null=True)
    action = models.CharField(max_length=250, null=True)
    act_by = models.CharField(max_length=50, null=True)
    act_date = models.DateTimeField(null=True)
    status = models.CharField(max_length=50, null=True)
    safe_act = models.ForeignKey(SafeAct, on_delete=models.CASCADE, related_name='actions')


class CorrectiveAction(models.Model):
    form_id = models.IntegerField()
    location = models.CharField(max_length=50, null=True)
    action = models.CharField(max_length=250, null=True)
    act_by = models.CharField(max_length=50, null=True)
    act_date = models.DateTimeField(null=True)
    status = models.CharField(max_length=50, null=True)


class RoomCleaning(models.Model):
    # user = models.ForeignKey('User', on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True)
    # room = models.ForeignKey('Room', on_delete=models.SET_NULL, null=True)
    room = models.CharField(max_length=20, null=False)
    maintenance = models.ForeignKey("Maintenance", on_delete=models.PROTECT)
    q1_1 = models.BooleanField(default=True)
    q1_2 = models.BooleanField(default=True)
    q2_1 = models.BooleanField(default=True)
    q2_2 = models.BooleanField(default=True)
    q2_3 = models.BooleanField(default=True)
    comment = models.CharField(max_length=250, null=True)
    time_start = models.DateTimeField(default=timezone.now)
    time_end = models.DateTimeField(default=timezone.now)
    time_spent = models.IntegerField(default=0)
    file_links = models.TextField()

class Maintenance(models.Model):
    level = models.CharField(max_length=50, choices=[
        ('0', 'No need'),
        ('1', 'Preventive'),
        ('2', 'Corrective'),
        ('3', 'Major'),
    ])