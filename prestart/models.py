from django.db import models
from django.contrib.auth.models import User


class CheckList(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    vehicle = models.CharField(max_length=100)
    refuelled = models.CharField(max_length=10)
    washed = models.CharField(max_length=10)
    engine_t = models.CharField(max_length=10)
    converter_t = models.CharField(max_length=10)
    shift = models.CharField(max_length=10)

    # models.IntegerField()
