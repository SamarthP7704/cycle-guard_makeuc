import cv2
import numpy as np
from PIL import Image
from typing import Optional, Tuple
import aiofiles
import os


async def save_uploaded_file(file, upload_dir: str = "uploads") -> str:
    """Save uploaded file to disk"""
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    return file_path


def extract_frame_from_video(video_path: str, frame_index: Optional[int] = None) -> np.ndarray:
    """
    Extract a frame from video file
    
    Args:
        video_path: Path to video file
        frame_index: Frame index to extract (None = middle frame, 0 = first frame)
    
    Returns:
        Extracted frame as numpy array
    """
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        cap.release()
        raise ValueError(f"Could not open video file: {video_path}")
    
    # Get total frame count
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    if total_frames == 0:
        cap.release()
        raise ValueError(f"Video file has no frames: {video_path}")
    
    # If frame_index is None, use middle frame (better for person detection)
    if frame_index is None:
        frame_index = total_frames // 2
    
    # Ensure frame_index is within valid range
    frame_index = max(0, min(frame_index, total_frames - 1))
    
    # Set frame position and read
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
    ret, frame = cap.read()
    cap.release()
    
    if not ret or frame is None:
        # Fallback: try first frame
        cap = cv2.VideoCapture(video_path)
        ret, frame = cap.read()
        cap.release()
        if not ret or frame is None:
            raise ValueError(f"Could not extract frame from video: {video_path}")
    
    return frame


def validate_image(image: np.ndarray) -> bool:
    """Validate that image is not empty and has valid dimensions"""
    if image is None:
        return False
    if len(image.shape) < 2:
        return False
    if image.shape[0] < 32 or image.shape[1] < 32:
        return False
    return True


def load_image(image_path: str) -> np.ndarray:
    """Load image from file path"""
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not load image from {image_path}")
    return image


def crop_bbox(image: np.ndarray, bbox: list) -> np.ndarray:
    """Crop image using bounding box [x1, y1, x2, y2]"""
    x1, y1, x2, y2 = map(int, bbox)
    # Ensure coordinates are within image bounds
    h, w = image.shape[:2]
    x1 = max(0, min(x1, w))
    y1 = max(0, min(y1, h))
    x2 = max(0, min(x2, w))
    y2 = max(0, min(y2, h))
    
    if x2 <= x1 or y2 <= y1:
        raise ValueError(f"Invalid bbox: {bbox}")
    
    crop = image[y1:y2, x1:x2]
    return crop


def resize_image(image: np.ndarray, size: Tuple[int, int] = (256, 256)) -> np.ndarray:
    """Resize image to specified size"""
    return cv2.resize(image, size)

