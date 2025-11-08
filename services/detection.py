import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Optional, Tuple
from config import settings


class DetectionService:
    """Service for object detection using YOLOv8"""
    
    def __init__(self):
        self.model = YOLO(settings.yolo_model_path)
        # COCO class IDs: 0 = person, 2 = car, 3 = motorcycle, 4 = airplane, 5 = bus
        # For cycles/scooters, we'll use bicycle (class 1) or motorcycle (class 3)
        self.person_class_id = 0
        self.cycle_class_ids = [1, 2, 3]  # bicycle, car, motorcycle (covers escooters as motorcycle-like)
    
    def detect_objects(self, image: np.ndarray) -> dict:
        """
        Detect person and cycle/escooter in image
        
        Returns:
            dict with 'person' and 'cycle' keys containing bbox lists
        """
        results = self.model(image, verbose=False)
        detections = {
            'person': None,
            'cycle': None
        }
        
        if len(results) == 0:
            return detections
        
        result = results[0]
        boxes = result.boxes
        
        if boxes is None or len(boxes) == 0:
            return detections
        
        # Find person with highest confidence
        person_conf = 0
        person_box = None
        
        # Find cycle with highest confidence
        cycle_conf = 0
        cycle_box = None
        
        for box in boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            xyxy = box.xyxy[0].cpu().numpy().tolist()
            
            if cls == self.person_class_id and conf > person_conf:
                person_conf = conf
                person_box = xyxy
            
            if cls in self.cycle_class_ids and conf > cycle_conf:
                cycle_conf = conf
                cycle_box = xyxy
        
        if person_box:
            detections['person'] = person_box
        
        if cycle_box:
            detections['cycle'] = cycle_box
        
        return detections
    
    def detect_and_crop_person(self, image: np.ndarray) -> Tuple[Optional[np.ndarray], Optional[List[float]]]:
        """
        Detect person in image and return cropped person image and bbox
        
        Returns:
            (cropped_person_image, bbox) or (None, None) if not found
        """
        detections = self.detect_objects(image)
        
        if detections['person'] is None:
            return None, None
        
        bbox = detections['person']
        x1, y1, x2, y2 = map(int, bbox)
        
        # Crop person from image
        h, w = image.shape[:2]
        x1 = max(0, min(x1, w))
        y1 = max(0, min(y1, h))
        x2 = max(0, min(x2, w))
        y2 = max(0, min(y2, h))
        
        if x2 <= x1 or y2 <= y1:
            return None, None
        
        person_crop = image[y1:y2, x1:x2]
        return person_crop, bbox

