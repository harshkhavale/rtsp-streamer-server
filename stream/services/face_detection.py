# detection/services/face_service.py
from mtcnn import MTCNN
import cv2
import time
import os
from django.conf import settings
from stream.models import Detection, Stream, Alert
from django.utils import timezone

class FaceDetectionService:
    def __init__(self):
        self.detector = MTCNN()
        self.cooldown = {}

    def process_stream(self, stream: Stream):
        cap = cv2.VideoCapture(stream.rtsp_url)
        while cap.isOpened() and stream.detection_enabled:
            start_time = time.time()
            ret, frame = cap.read()
            if not ret:
                break

            faces = self.detector.detect_faces(frame)
            for face in faces:
                confidence = face['confidence']
                if confidence >= stream.confidence_threshold:
                    timestamp = timezone.now()
                    image_name = f"{stream.id}_{timestamp.timestamp()}.jpg"
                    image_path = os.path.join(settings.MEDIA_ROOT, 'detections', image_name)
                    cv2.imwrite(image_path, frame)

                    detection = Detection.objects.create(
                        stream=stream,
                        confidence_score=confidence,
                        image_path=f"detections/{image_name}"
                    )

                    # Alert cooldown logic
                    if stream.id not in self.cooldown or (timestamp - self.cooldown[stream.id]).total_seconds() > 30:
                        Alert.objects.create(detection=detection)
                        self.cooldown[stream.id] = timestamp

            elapsed = time.time() - start_time
            sleep_time = max(0, (1/15) - elapsed)
            time.sleep(sleep_time)

        cap.release()
