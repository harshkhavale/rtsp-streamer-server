from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponseBadRequest
from stream.models import Stream
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from stream.services.stream_init import generate_ws_url

def parse_json(request):
    try:
        return json.loads(request.body)
    except json.JSONDecodeError:
        return None

@csrf_exempt
@require_http_methods(["POST"])
def create_stream(request):
    data = parse_json(request)
    if data is None:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    required_fields = ['name', 'rtsp_url']
    for field in required_fields:
        if field not in data:
            return JsonResponse({'error': f'Missing required field: {field}'}, status=400)

    try:
        stream = Stream.objects.create(
            name=data['name'],
            description=data.get('description', ''),
            rtsp_url=data['rtsp_url'],
            confidence_threshold=data.get('confidence_threshold', 0.8),
            detection_enabled=True
        )
        ws_url = generate_ws_url(stream.rtsp_url)
        return JsonResponse({
            'id': stream.id,
            'message': 'Stream created and started',
            'ws_url': ws_url
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def list_streams(request):
    all_streams = Stream.objects.all()
    streams = []

    for stream in all_streams:
        streams.append({
            "id": stream.id,
            "name": stream.name,
            "description": stream.description,
            "rtsp_url": stream.rtsp_url,
            "confidence_threshold": stream.confidence_threshold,
            "detection_enabled": stream.detection_enabled,
            "ws_url": generate_ws_url(stream.rtsp_url)
        })

    return JsonResponse({'streams': streams})


@require_http_methods(["GET"])
def get_stream(request, stream_id):
    try:
        stream = Stream.objects.get(id=stream_id)
        stream_data = {
            "id": stream.id,
            "name": stream.name,
            "description": stream.description,
            "rtsp_url": stream.rtsp_url,
            "confidence_threshold": stream.confidence_threshold,
            "detection_enabled": stream.detection_enabled,
            "ws_url": generate_ws_url(stream.rtsp_url)
        }
        return JsonResponse({'stream': stream_data})
    except Stream.DoesNotExist:
        return JsonResponse({'error': 'Stream not found'}, status=404)


@csrf_exempt
@require_http_methods(["PATCH"])
def update_stream_status(request, stream_id):
    data = parse_json(request)
    if data is None:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    try:
        stream = Stream.objects.get(id=stream_id)
    except Stream.DoesNotExist:
        return JsonResponse({'error': 'Stream not found'}, status=404)

    action = data.get('action')
    if action == 'pause':
        stream.detection_enabled = False
    elif action == 'resume':
        stream.detection_enabled = True
    elif action == 'start':
        # If you want a dedicated start action:
        stream.detection_enabled = True
        # Add any other "start" logic here
    else:
        return JsonResponse({'error': 'Invalid action'}, status=400)

    stream.save()
    return JsonResponse({'message': f'Stream {action}d', 'status': stream.detection_enabled})


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_stream(request, stream_id):
    try:
        stream = Stream.objects.get(id=stream_id)
        stream.delete()
        return JsonResponse({'message': 'Stream deleted'})
    except Stream.DoesNotExist:
        return JsonResponse({'error': 'Stream not found'}, status=404)
