from django.urls import path, include
from stream.views.auth import AdminLoginView, AdminRegisterView
from stream.views.stream import list_streams, create_stream, update_stream_status, delete_stream, get_stream
from stream.views.alert import list_alerts,  get_alert, update_alert, delete_alert
from stream.views.detection import create_detection, list_detections, get_detection, update_detection, delete_detection

urlpatterns = [
    #auth
    path('login/', AdminLoginView.as_view(), name='admin_login'),
    path('register/', AdminRegisterView.as_view(), name='admin_register'),
    #streams
    path('streams/', list_streams, name='list_streams'),
    path('streams/create/', create_stream, name='create_stream'),
    path('streams/<int:stream_id>/', get_stream, name='get_stream'),
    path('streams/<int:stream_id>/status/', update_stream_status, name='update_stream_status'),
    path('streams/<int:stream_id>/delete/', delete_stream, name='delete_stream'),
    #alerts
    path("alerts/", list_alerts, name="list_alerts"),
    path("alerts/<int:alert_id>/", get_alert, name="get_alert"),
    path("alerts/<int:alert_id>/update/", update_alert, name="update_alert"),
    path("alerts/<int:alert_id>/delete/", delete_alert, name="delete_alert"),
    #detections
    path('detections/create', create_detection, name='create_detection'),  # POST
    path('detections/', list_detections, name='list_detections'),    # GET
    path('detections/<int:detection_id>/', get_detection, name='get_detection'),  # GET
    path('detections/<int:detection_id>/', update_detection, name='update_detection'),  # PUT, PATCH
    path('detections/<int:detection_id>/', delete_detection, name='delete_detection'),  # DELETE
]
