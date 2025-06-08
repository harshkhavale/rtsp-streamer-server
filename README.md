# RTSP Stream Viewer – Backend

This repository contains the **backend service** for the **RTSP Stream Viewer** project, built using **Django**, **Django Channels**, and **FFmpeg**. It processes RTSP stream URLs and relays live video frames to the frontend via **WebSockets**.

---

## Features

* Accepts RTSP stream URLs via WebSocket connection
* Uses FFmpeg to process and transcode streams
* Sends video frames to frontend in real-time
* AI-based face detection using MTCNN
* Real-time performance monitoring and metrics
* Gracefully handles errors and broken streams
* Scalable and containerized using Docker
* Production-ready ASGI server setup with Daphne

---

## Technologies Used

* **Python 3.11**
* **Django 4+**
* **Django Channels**
* **ASGI & Daphne**
* **FFmpeg**
* **OpenCV (cv2)**
* **MTCNN for Face Detection**
* **WebSockets**
* **Docker**
* **Redis** (for channel layers)

---

## Database Design

### Models

1. **Stream**
   ```python
   class Stream(models.Model):
       name = models.CharField(max_length=100)
       description = models.TextField(blank=True)
       rtsp_url = models.URLField()
       detection_enabled = models.BooleanField(default=True)
       confidence_threshold = models.FloatField(default=0.8)
       last_connected = models.DateTimeField(null=True, blank=True)
       status = models.CharField(max_length=50, default="offline")
   ```
   - Manages RTSP stream configurations
   - Tracks stream status and connection state
   - Configurable face detection settings

2. **Detection**
   ```python
   class Detection(models.Model):
       stream = models.ForeignKey(Stream, on_delete=models.CASCADE)
       timestamp = models.DateTimeField(auto_now_add=True)
       confidence_score = models.FloatField()
       image_path = models.ImageField(upload_to='detections/')
   ```
   - Stores face detection results
   - Links detections to their source stream
   - Maintains detection confidence scores
   - Stores captured images

3. **Alert**
   ```python
   class Alert(models.Model):
       detection = models.OneToOneField(Detection, on_delete=models.CASCADE)
       timestamp = models.DateTimeField(auto_now_add=True)
       viewed = models.BooleanField(default=False)
   ```
   - Manages alerts generated from detections
   - Tracks alert status and viewing state
   - One-to-one relationship with detections

---

## Implementation Approach

### 1. Stream Processing Pipeline

1. **Stream Initialization**
   - RTSP URL validation and connection setup
   - FFmpeg process initialization with optimized parameters
   - WebSocket connection establishment

2. **Frame Processing**
   - Frame capture at 15 FPS
   - Image preprocessing and scaling
   - Real-time performance monitoring
   - Frame buffering and delivery

3. **Face Detection**
   - MTCNN-based face detection
   - Configurable confidence thresholds
   - Asynchronous processing to maintain stream performance
   - Detection result storage and alert generation

### 2. Performance Monitoring

The system includes comprehensive performance monitoring:

```python
{
    "current_fps": 15.0,              # Current frames per second
    "avg_processing_time": 33.45,     # Average frame processing time (ms)
    "avg_detection_time": 150.23,     # Average face detection time (ms)
    "total_frames": 1500,             # Total frames processed
    "total_detections": 25,           # Total faces detected
    "uptime": 120.5                   # System uptime in seconds
}
```

### 3. API Endpoints

1. **Stream Management**
   - `POST /api/streams/` - Create new stream
   - `GET /api/streams/` - List all streams
   - `GET /api/streams/<id>/` - Get stream details
   - `PATCH /api/streams/<id>/status/` - Update stream status

2. **Detection Management**
   - `GET /api/detections/` - List all detections
   - `GET /api/detections/<id>/` - Get detection details
   - `POST /api/detections/` - Create new detection

3. **Alert Management**
   - `GET /api/alerts/` - List all alerts
   - `GET /api/alerts/<id>/` - Get alert details
   - `PATCH /api/alerts/<id>/` - Update alert status

### 4. WebSocket Communication

1. **Connection**
   ```
   ws://localhost:8000/ws/stream/?url=<encoded_rtsp_url>
   ```

2. **Message Types**
   - Video frames (binary)
   - Performance stats (JSON)
   - Face detection alerts (JSON)
   - System status updates (JSON)

---

## Getting Started

### Prerequisites

* Docker installed
* RTSP stream URLs for testing
* Frontend client (React-based) ready to consume MJPEG/WebSocket stream

### Environment Variables

Create a `.env` file:

```
SECRET_KEY=
DEBUG=
ALLOWED_HOSTS=localhost,127.0.0.1
WS_BASE_URL=ws://localhost:8000
CORS_ALLOWED_ORIGINS=http://localhost:5173
REDIS_URL=
```

### Running Locally with Docker

1. Clone the repository:
   ```bash
   git clone https://github.com/harshkhavale/rtsp-streamer-server.git
   cd rtsp-streamer-server
   ```

2. Build the Docker image:
   ```bash
   docker-compose up --build
   ```

3. Run the container:
   ```bash
   docker run -p 8000:8000 rtsp_backend
   ```

Your backend will be accessible at:
**WebSocket URL**: `ws://localhost:8000/ws/stream/`

---

## Performance Considerations

1. **Frame Processing**
   - Target frame rate: 15 FPS
   - Frame size: 640x480 pixels
   - Color format: BGR24

2. **Face Detection**
   - Asynchronous processing
   - Configurable confidence threshold
   - Alert cooldown period: 30 seconds

3. **Resource Management**
   - Automatic cleanup of old detections
   - Efficient image storage
   - Memory-optimized frame processing

---

## Error Handling

1. **Stream Errors**
   - Automatic reconnection attempts
   - Graceful degradation
   - Error logging and monitoring

2. **Detection Errors**
   - Fallback mechanisms
   - Error reporting
   - System state preservation

---

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.
