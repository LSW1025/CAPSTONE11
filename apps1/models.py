from __future__ import unicode_literals

from django.db import models

class Word(models.Model):
    idx = models.IntegerField(primary_key=True)
    word = models.TextField()
    session_num = models.TextField(blank=True, null=True)

class Checkdup(models.Model):
    idx = models.IntegerField(primary_key=True)
    time = models.TextField()

class InitWord(models.Model):
    idx = models.IntegerField(primary_key=True)
    word = models.TextField()

# Create your models here.
