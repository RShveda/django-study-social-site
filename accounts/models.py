from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserProfileInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    karma = models.IntegerField(default=0)

    def update_karma(self, x):
        self.karma += x
        return self.karma

    def __str__(self):
        return self.user.username
