from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from stream.models import Detection
import json

def parse_json(request):
    try:
        return json.loads(request.body)
    except json.JSONDecodeError:
        return None

@csrf_exempt
@require_http_methods(["POST"])
def create_detection(request):
    data = parse_json(request)
    if data is None:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    required_fields = ['name', 'confidence']
    for field in required_fields:
        if field not in data:
            return JsonResponse({'error': f'Missing required field: {field}'}, status=400)

    try:
        detection = Detection.objects.create(
            name=data['name'],
            confidence=data['confidence']
        )
        return JsonResponse({
            'id': detection.id,
            'message': 'Detection created'
        }, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def list_detections(request):
    detections = Detection.objects.all()
    result = []
    for d in detections:
        result.append({
            'id': d.id,
            'name': d.name,
            'confidence': d.confidence,
        })
    return JsonResponse({'detections': result})


@require_http_methods(["GET"])
def get_detection(request, detection_id):
    try:
        d = Detection.objects.get(id=detection_id)
        data = {
            'id': d.id,
            'name': d.name,
            'confidence': d.confidence,
        }
        return JsonResponse({'detection': data})
    except Detection.DoesNotExist:
        return JsonResponse({'error': 'Detection not found'}, status=404)


@csrf_exempt
@require_http_methods(["PUT", "PATCH"])
def update_detection(request, detection_id):
    data = parse_json(request)
    if data is None:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    try:
        detection = Detection.objects.get(id=detection_id)
    except Detection.DoesNotExist:
        return JsonResponse({'error': 'Detection not found'}, status=404)

    if request.method == "PUT":
        # For PUT, replace all fields
        required_fields = ['name', 'confidence']
        for field in required_fields:
            if field not in data:
                return JsonResponse({'error': f'Missing required field: {field}'}, status=400)
        detection.name = data['name']
        detection.confidence = data['confidence']
    else:
        # PATCH - update fields partially
        if 'name' in data:
            detection.name = data['name']
        if 'confidence' in data:
            detection.confidence = data['confidence']

    detection.save()
    return JsonResponse({'message': 'Detection updated'})


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_detection(request, detection_id):
    try:
        detection = Detection.objects.get(id=detection_id)
        detection.delete()
        return JsonResponse({'message': 'Detection deleted'})
    except Detection.DoesNotExist:
        return JsonResponse({'error': 'Detection not found'}, status=404)
