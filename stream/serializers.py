from rest_framework import serializers
from .models import Detection

class DetectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Detection
        fields = ['id', 'timestamp', 'confidence_score', 'image_path']
