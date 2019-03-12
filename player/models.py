from django.db import models

# Create your models here.

class Playlist(models.Model):
    name = models.CharField(max_length=30)
    singers =  models.CharField(max_length=12)
    url = models.CharField(max_length=64)
    saveTime = models.DateTimeField(max_length=6)
    exc = models.CharField(max_length=64)