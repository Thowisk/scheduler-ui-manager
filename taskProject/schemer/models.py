import os

from django.conf import settings
from django.db import models
from django.utils import timezone
import datetime
# Create your models here.

class Task(models.Model):

    cyclic_choices = [
        ('seconds', 'seconds'),
        ('minutes', 'minutes'),
        ('hours', 'hours'),
        ('days', 'days'),
        ('weeks', 'weeks'),
    ]

    is_child = models.BooleanField(default=False)
    dependency = models.CharField(max_length=250, default=None, null=True)
    file = models.FilePathField(null=False, path='C:/Users/'+ os.getlogin() + '/Documents/schedulerService/scripts/', default=None, match='^.*\.(bat|py)$')
    date = models.DateField(default=datetime.date.today,)
    time = models.TimeField(auto_now=False,)
    label = models.CharField(max_length=100, default='')
    cyclic_on = models.CharField(blank=True, null=True, choices=cyclic_choices, max_length=10)
    interval = models.IntegerField(default=1)
    state = models.IntegerField(default=-1) # -1: None / 0: OK / 1: KO
    option = models.IntegerField(default=0)
