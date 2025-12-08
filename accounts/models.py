from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birthday = models.DateField(null=True, blank=True)

    bio = models.TextField(max_length=500, blank=True, help_text="Tell us about yourself!")
    nickname = models.CharField(max_length=30, blank=True, help_text="Enter a nickname (optional)")

    def __str__(self):
        return f"{self.user.username}'s Profile"