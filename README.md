

# RTSP Stream Viewer – Backend

This repository contains the **backend service** for the **RTSP Stream Viewer** project, built using **Django**, **Django Channels**, and **FFmpeg**. It processes RTSP stream URLs and relays live video frames to the frontend via **WebSockets**.

---

## Features

* Accepts RTSP stream URLs via WebSocket connection
* Uses FFmpeg to process and transcode streams
* Sends video frames to frontend in real-time
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
* **WebSockets**
* **Docker**

---

## Folder Structure

```
rtsp_backend/
├── asgi.py             # ASGI application setup
├── settings.py         # Django project settings
├── urls.py             # Route definitions
├── stream/             # App handling stream logic
│   ├── consumers.py    # WebSocket consumer
│   ├── utils.py        # FFmpeg & stream handlers
│   ├── routing.py      # Routing
│   ├── urls.py         
├── manage.py
requirements.txt
Dockerfile
```

---

## Getting Started

### Prerequisites

* Docker installed
* RTSP stream URLs for testing
* Frontend client (React-based) ready to consume MJPEG/WebSocket stream

---

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

---

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

## WebSocket API

* **URL**: `/api/start/`
* **Payload Format**:

```curl
curl --location 'http://localhost:8000/api/start/' \
--header 'Content-Type: application/json' \
--data '{"rtsp_url": "rtsp://192.168.0.114:8554/mystream" }'
```

