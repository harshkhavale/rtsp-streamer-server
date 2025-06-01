import asyncio
import cv2
import numpy as np
import os
import time
import subprocess
from mtcnn import MTCNN
from django.conf import settings
from django.utils.timezone import now
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.core.files import File
from stream.models import Alert, Detection, Stream
from urllib.parse import parse_qs, unquote

from asgiref.sync import sync_to_async

class FaceDetector:
    def __init__(self, confidence_threshold=0.3):  # Lower threshold for testing
        self.detector = MTCNN()
        self.confidence_threshold = confidence_threshold

    def detect_faces(self, frame_bgr):
        rgb_frame = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        detections = self.detector.detect_faces(rgb_frame)
        print(f"DEBUG: MTCNN detections raw: {detections}")
        results = [det for det in detections if det['confidence'] >= self.confidence_threshold]
        print(f"DEBUG: MTCNN filtered detections: {results}")
        return results


class StreamConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.detector = FaceDetector(confidence_threshold=0.3)
        self.last_alert_time = 0
        self.alert_cooldown = 30  # seconds cooldown between alerts
        self.frame_interval = 1 / 15  # max ~15 FPS detection
        self.last_frame_processed_time = 0
        self.process = None
        self.log_task = None
        self.snapshots_dir = os.path.join(settings.MEDIA_ROOT, 'snapshots')
        os.makedirs(self.snapshots_dir, exist_ok=True)

    async def connect(self):
        await self.accept()
        print("✅ WebSocket connected")
        self.stream_id = None  # Initialize stream_id
        query_string = self.scope["query_string"].decode()  # bytes to str
        query_params = parse_qs(query_string)
        stream_ids = query_params.get("stream_id", [])
        if stream_ids:
            self.stream_id = stream_ids[0]
            print(f"📡 Connected with stream_id: {self.stream_id}")
        
        rtsp_urls = query_params.get("url", [])
        if rtsp_urls:
            rtsp_url = unquote(rtsp_urls[0])
            print(f"Starting stream for RTSP URL from query string: {rtsp_url}")
            self.pause = False
            asyncio.create_task(self.stream_video(rtsp_url))
        else:
            print("No RTSP URL in query string, waiting for start command.")

    async def disconnect(self, close_code):
        print("❌ WebSocket disconnected")
        if self.process:
            self.process.kill()
            await asyncio.sleep(0.1)
            if self.process.stdout:
                self.process.stdout.close()
            if self.process.stderr:
                self.process.stderr.close()
            self.process = None

    async def receive(self, text_data):
        data = json.loads(text_data)
        command = data.get('command')

        if command == 'start':
            rtsp_url = data.get('rtsp_url')
            if not rtsp_url:
                await self.send_json({'error': 'No RTSP URL provided'})
                return

            if self.process:
                self.process.kill()
                self.process = None

            self.pause = False
            asyncio.create_task(self.stream_video(rtsp_url))

        elif command == 'pause':
            self.pause = True

        elif command == 'resume':
            self.pause = False

        elif command == 'stop_stream':
            if self.process:
                self.process.kill()
                self.process = None

        elif command == 'close':
            await self.disconnect(1000)


        # Otherwise, treat text_data as RTSP URL
        rtsp_url = data.get('rtsp_url')
        if rtsp_url:
            print(f"🎯 RTSP URL received: {rtsp_url}")

            if self.process:
                self.process.kill()
                await asyncio.sleep(0.1)

            self.pause = False  # Reset pause state
            asyncio.create_task(self.stream_video(rtsp_url))


    async def stream_video(self, rtsp_url):
        command = [
            'ffmpeg',
            '-rtsp_transport', 'tcp',
            '-fflags', 'nobuffer',
            '-flags', 'low_delay',
            '-flush_packets', '1',
            '-avioflags', 'direct',
            '-analyzeduration', '10000000',
            '-probesize', '10000000',
            '-i', rtsp_url,
            '-vf', 'scale=640:480',
            '-f', 'image2pipe',
            '-pix_fmt', 'bgr24',
            '-vcodec', 'rawvideo',
            '-'
        ]

        try:
            self.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=10 ** 8
            )
        except Exception as e:
            print(f"❌ Failed to start ffmpeg process: {e}")
            return

        width, height = 640, 480
        frame_size = width * height * 3  # bgr24

        async def log_ffmpeg_errors():
            while self.process:
                try:
                    err_line = await asyncio.to_thread(self.process.stderr.readline)
                except ValueError:
                    print("⚠️ Tried to read from closed stderr")
                    break
                if not err_line:
                    break
                print("FFmpeg:", err_line.decode(errors="ignore").strip())

        self.log_task = asyncio.create_task(log_ffmpeg_errors())

        frame_count = 0
        try:
            while True:
                if self.pause:
                    await asyncio.sleep(0.5)
                    continue
                raw_frame = await asyncio.to_thread(self.process.stdout.read, frame_size)
                if not raw_frame or len(raw_frame) < frame_size:
                    print(f"🚫 No frame or incomplete frame: got {len(raw_frame) if raw_frame else 0} bytes, expected {frame_size}")
                    break

                frame = np.frombuffer(raw_frame, np.uint8).reshape((height, width, 3))

                # Debug frame shape
                if frame_count == 0:
                    print(f"Frame shape: {frame.shape}")

                now_time = time.time()
                if now_time - self.last_frame_processed_time >= self.frame_interval:
                    await self.detect_and_alert(frame, stream_id=self.stream_id)
                    self.last_frame_processed_time = now_time

                success, buffer = cv2.imencode('.jpg', frame)
                if not success:
                    print("⚠️ Frame encoding failed")
                    continue

                try:
                    await self.send(bytes_data=buffer.tobytes())
                except Exception as e:
                    print(f"❌ Failed to send frame: {e}")
                    break

                frame_count += 1
                if frame_count % 10 == 0:
                    print(f"📸 Sent {frame_count} frames")

        except Exception as e:
            print(f"🔥 Streaming error: {e}")
        finally:
            if self.process:
                print("🧹 Killing ffmpeg process")
                self.process.kill()
                if self.process.stdout:
                    self.process.stdout.close()
                if self.process.stderr:
                    self.process.stderr.close()
                self.process = None

            if self.log_task:
                self.log_task.cancel()
                try:
                    await self.log_task
                except asyncio.CancelledError:
                    print("🛑 FFmpeg error logging task cancelled")
    async def detect_and_alert(self, frame, stream_id=None):
        try:
            # Detect faces (run in thread to avoid blocking)
            detections = await asyncio.to_thread(self.detector.detect_faces, frame)
            print(f"📸 Number of faces detected: {len(detections)}")

            confident_faces = [d for d in detections if d['confidence'] >= self.detector.confidence_threshold]
            print(f"💡 Confident faces (above {self.detector.confidence_threshold}): {len(confident_faces)}")

            if not confident_faces:
                print("😕 No confident faces detected.")
                return

            now_time = time.time()
            if now_time - self.last_alert_time < self.alert_cooldown:
                print("⏳ Alert cooldown not finished.")
                return

            # Pick best face
            best_face = max(confident_faces, key=lambda x: x['confidence'])
            x, y, w, h = best_face['box']
            confidence = best_face['confidence']
            print(f"✅ Detected face with confidence {confidence:.2f} at [{x}, {y}, {w}, {h}]")

            # Draw rectangle around detected face
            frame_copy = frame.copy()
            cv2.rectangle(frame_copy, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Save snapshot
            timestamp_str = now().strftime('%Y%m%d_%H%M%S_%f')
            filename = f"detection_{timestamp_str}.jpg"
            filepath = os.path.join(self.snapshots_dir, filename)
            saved = cv2.imwrite(filepath, frame_copy)
            print(f"💾 Saving snapshot: {filepath} -> {'Success' if saved else 'Failed'}")

            if saved:
                stream = await sync_to_async(Stream.objects.get)(id=stream_id)
                with open(filepath, 'rb') as f:
                    detection = await sync_to_async(Detection.objects.create)(
                        confidence_score=confidence,
                        image_path=File(f, name=filename),
                        stream=stream
                    )
                    await sync_to_async(Alert.objects.create)(
                        detection=detection
                    )

                print(f"📦 Saved detection to DB: {detection}")
                print("🚨 Created alert for detection.")

                self.last_alert_time = now_time

                await self.send_json({
                    'type': 'face_alert',
                    'timestamp': timestamp_str,
                    'confidence': confidence,
                    'snapshot': detection.image_path.url if detection.image_path else ''
                })

        except Exception as e:
            print(f"❌ Error in detect_and_alert: {e}")

    async def send_json(self, data):
        await self.send(text_data=json.dumps(data))
