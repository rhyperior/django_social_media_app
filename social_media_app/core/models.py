from tkinter import CASCADE
from django.db import models
from django.contrib.auth import get_user_model
import uuid
import datetime

User = get_user_model()

# Create your models here.
class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id_user = models.IntegerField()
    bio = models.TextField(blank=True)
    profileimg = models.ImageField(upload_to='profile_images', default='default_profile_pic.jpeg')
    location = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.username

class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.CharField(max_length=100)
    image = models.ImageField(upload_to='post_images')
    caption = models.TextField(blank=True)
    created_at = models.DateTimeField(default=datetime.datetime.now())
    like_count = models.IntegerField(default=0)

    def __str__(self) -> str:
        return self.user


class LikePost(models.Model):
    # id = models.ForeignKey(Post, on_delete=models.CASCADE)
    post_id = models.CharField(max_length=500)
    username = models.CharField(max_length=100)

    def __str__(self):
        return self.username


class FollowersCount(models.Model):
    follower = models.CharField(max_length=100)
    user = models.CharField(max_length=100)
    
    def __str__(self):
        return f'user: {self.user} --- follower: {self.follower}'
