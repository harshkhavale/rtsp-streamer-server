from django.urls import path
from stream.views.stream import list_streams, create_stream, update_stream_status, delete_stream, get_stream

urlpatterns = [
    path('streams/', list_streams, name='list_streams'),
    path('streams/create/', create_stream, name='create_stream'),
    path('streams/<int:stream_id>/', get_stream, name='get_stream'),
    path('streams/<int:stream_id>/status/', update_stream_status, name='update_stream_status'),
    path('streams/<int:stream_id>/delete/', delete_stream, name='delete_stream'),
    
]
