from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birthday = models.DateField(null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True, help_text="Write a short bio about yourself.")
    nickname = models.CharField(max_length=30, blank=True, help_text="What should we call you?")
    
    # Friend System
    friends = models.ManyToManyField('self', blank=True, symmetrical=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.from_user.username} to {self.to_user.username}"