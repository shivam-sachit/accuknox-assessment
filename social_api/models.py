from django.contrib.auth.models import AbstractUser
from django.db import models

from social_api.managers import UserManager


class User(AbstractUser):

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=100)
    username = None
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    def __str__(self):
        return self.email


class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_friend_requests')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_friend_requests')
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"Friend Request from {self.from_user} to {self.to_user}"