from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Game(models.Model):
    user = models.ForeignKey(User, default=None)
    game_id = models.AutoField(primary_key=True)
    answer = models.CharField(max_length=20)
    guessed = models.CharField(max_length=10, default="")
    status = models.CharField(max_length=10, default="ongoing")

    def __unicode__(self):
        return "game is: " + self.answer + "written by " + self.user.first_name \
               + self.user.last_name