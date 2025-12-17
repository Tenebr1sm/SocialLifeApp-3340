from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Personal details
    bio = models.TextField(max_length=500, blank=True)
    birthday = models.DateField(null=True, blank=True)
    nickname = models.CharField(max_length=50, blank=True)
    
    # Friend system
    friends = models.ManyToManyField('self', blank=True, symmetrical=True)
    
    # Privacy setting
    is_private = models.BooleanField(default=False, help_text="If checked, only friends can see your birthday and bio.")
    
    # Customizable duration for upcoming birthday notifications (in days)
    birthday_notification_days = models.IntegerField(
        default=30,
        validators=[MinValueValidator(1), MaxValueValidator(365)],
        help_text="Days in advance to show upcoming birthdays."
    )

    def __str__(self):
        return f'{self.user.username} Profile'

class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='friend_requests_sent', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='friend_requests_received', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f'Request from {self.from_user.username} to {self.to_user.username}'

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Post by {self.author.username} at {self.created_at}'

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField(max_length=1000)
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f'From {self.sender.username} to {self.receiver.username}'