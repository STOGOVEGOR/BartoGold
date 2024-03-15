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