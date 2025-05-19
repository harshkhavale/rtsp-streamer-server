import os
from urllib.parse import quote
from rest_framework.views import APIView
from rest_framework.response import Response

class StreamInitAPIView(APIView):
    def post(self, request):
        rtsp_url = request.data.get("rtsp_url")
        encoded_url = quote(rtsp_url, safe='')
        
        # Read base WS URL from environment variable, fallback to default
        ws_base_url = os.getenv("WS_BASE_URL", "ws://localhost:8000")
        
        return Response({
            "ws_url": f"{ws_base_url}/ws/stream/?url={encoded_url}"
        })
