from django.http import JsonResponse, HttpResponseNotAllowed
from stream.models import Alert, Detection
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

def parse_json(request):
    try:
        return json.loads(request.body)
    except json.JSONDecodeError:
        return None


# 📌 1. List Alerts
@require_http_methods(["GET"])
def list_alerts(request):
    alerts = Alert.objects.select_related("detection", "detection__stream").all().order_by('-timestamp')
    alert_list = []

    for alert in alerts:
        alert_list.append({
            "id": alert.id,
            "detection_id": alert.detection.id,
            "stream_id": alert.detection.stream.id,
            "confidence_score": alert.detection.confidence_score,
            "image_url": alert.detection.image_path.url if alert.detection.image_path else None,
            "timestamp": alert.timestamp,
            "viewed": alert.viewed
        })

    return JsonResponse({"alerts": alert_list})


# 📌 2. Get Alert by ID
@require_http_methods(["GET"])
def get_alert(request, alert_id):
    try:
        alert = Alert.objects.select_related("detection", "detection__stream").get(id=alert_id)
        data = {
            "id": alert.id,
            "detection_id": alert.detection.id,
            "stream_id": alert.detection.stream.id,
            "confidence_score": alert.detection.confidence_score,
            "image_url": alert.detection.image_path.url if alert.detection.image_path else None,
            "timestamp": alert.timestamp,
            "viewed": alert.viewed
        }
        return JsonResponse({"alert": data})
    except Alert.DoesNotExist:
        return JsonResponse({"error": "Alert not found"}, status=404)


# 📌 3. Update Alert (e.g., mark as viewed)
@csrf_exempt
@require_http_methods(["PATCH"])
def update_alert(request, alert_id):
    data = parse_json(request)
    if data is None:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    try:
        alert = Alert.objects.get(id=alert_id)
        alert.viewed = data.get("viewed", alert.viewed)
        alert.save()
        return JsonResponse({"message": "Alert updated", "viewed": alert.viewed})
    except Alert.DoesNotExist:
        return JsonResponse({"error": "Alert not found"}, status=404)


# 📌 4. Delete Alert
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_alert(request, alert_id):
    try:
        alert = Alert.objects.get(id=alert_id)
        alert.delete()
        return JsonResponse({"message": "Alert deleted"})
    except Alert.DoesNotExist:
        return JsonResponse({"error": "Alert not found"}, status=404)
