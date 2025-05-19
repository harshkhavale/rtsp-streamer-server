# stream/urls.py
from django.urls import path
from .views import StreamInitAPIView

urlpatterns = [
    path('start/', StreamInitAPIView.as_view())
]
