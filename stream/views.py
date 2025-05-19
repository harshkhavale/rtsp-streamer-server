from django.shortcuts import render
import urllib.parse

# Create your views here.
# stream/views.py
from rest_framework.views import APIView
from rest_framework.response import Response

class StreamInitAPIView(APIView):
    def post(self, request):
        rtsp_url = request.data.get("rtsp_url")
        from urllib.parse import quote
        # Properly URL-encode the RTSP URL as a query parameter
        encoded_url = quote(rtsp_url, safe='')
        return Response({
            "ws_url": f"ws://localhost:8000/ws/stream/?url={encoded_url}"
        })


