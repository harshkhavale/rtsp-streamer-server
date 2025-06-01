from django.db import models
from django.contrib.auth.models import AbstractUser

# 1. Users
class User(AbstractUser):
    last_login_timestamp = models.DateTimeField(null=True, blank=True)

# 2. Streams
class Stream(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    rtsp_url = models.URLField()
    detection_enabled = models.BooleanField(default=True)
    confidence_threshold = models.FloatField(default=0.8)
    last_connected = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, default="offline")

    def __str__(self):
        return self.name

# 3. Detections
class Detection(models.Model):
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    confidence_score = models.FloatField()
    image_path = models.ImageField(upload_to='detections/')

# 4. Alerts
class Alert(models.Model):
    detection = models.OneToOneField(Detection, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    viewed = models.BooleanField(default=False)
