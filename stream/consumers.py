import asyncio
import cv2
import numpy as np
from channels.generic.websocket import AsyncWebsocketConsumer
import subprocess

class StreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        print("✅ WebSocket connected")

    async def disconnect(self, close_code):
        print("❌ WebSocket disconnected")
        if hasattr(self, 'process'):
            self.process.kill()
            await asyncio.sleep(0.1)

    async def receive(self, text_data):
        rtsp_url = text_data
        print(f"🎯 RTSP URL received: {rtsp_url}")
        # Start streaming and logging stderr concurrently
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


        self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=10**8)
        width, height = 640, 480
        frame_size = width * height * 3  # 3 bytes per pixel for bgr24

        # Log stderr for debugging
        async def log_ffmpeg_errors():
            while True:
                err_line = await asyncio.to_thread(self.process.stderr.readline)
                if not err_line:
                    break
                print("FFmpeg:", err_line.decode(errors="ignore").strip())

        asyncio.create_task(log_ffmpeg_errors())

        frame_count = 0
        try:
            while True:
                raw_frame = await asyncio.to_thread(self.process.stdout.read, frame_size)
                if not raw_frame or len(raw_frame) < frame_size:
                    print(f"🚫 No frame received or incomplete frame: got {len(raw_frame)} bytes, expected {frame_size}")
                    break

                frame = np.frombuffer(raw_frame, np.uint8).reshape((height, width, 3))
                success, buffer = cv2.imencode('.jpg', frame)
                if not success:
                    print("⚠️ Frame encoding failed")
                    continue

                try:
                    await self.send(bytes_data=buffer.tobytes())
                except Exception as e:
                    print(f"❌ Failed to send frame: {e}")


                frame_count += 1
                if frame_count % 10 == 0:
                    print(f"📸 Sent {frame_count} frames")

                # await asyncio.sleep(0.04)  # ~25 FPS

        except Exception as e:
            print(f"🔥 Streaming error: {e}")
        finally:
            print("🧹 Killing ffmpeg process")
            self.process.kill()
            self.process.stdout.close()
            self.process.stderr.close()
