from django.db import models

class Tile(models.Model):
    row = models.IntegerField()
    column = models.IntegerField()
    value = models.CharField(max_length=1, default='_')


class Player(models.Model):
    name = models.CharField(max_length=20)
    row = models.IntegerField()
    column = models.IntegerField()
    score = models.IntegerField(default=0)

# Create your models here.
