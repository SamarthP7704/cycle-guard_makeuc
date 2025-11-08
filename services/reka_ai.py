from typing import Optional, List
import requests
import base64
import cv2
import numpy as np
from config import settings


class RekaAIService:
    """Service for advanced vision analysis using Reka AI (optional backup)"""
    
    def __init__(self):
        self.api_key = settings.reka_api_key
        self.api_url = "https://api.reka.ai/v1/chat"  # Update with actual Reka AI API endpoint
        self.is_available = bool(self.api_key and self.api_key != "your_reka_api_key")
        
        if not self.is_available:
            print("ℹ️  Reka AI is not configured. Continuing without Reka AI (will use torchreid only).")
    
    def is_configured(self) -> bool:
        """Check if Reka AI is properly configured"""
        return self.is_available
    
    def analyze_person_similarity(
        self,
        person_image1: bytes,
        person_image2: bytes,
        prompt: str = "Are these two images showing the same person? Consider clothing, body type, posture, and accessories. Respond with 'yes' or 'no' and a confidence score (0-1)."
    ) -> Optional[dict]:
        """
        Use Reka AI to analyze if two person images are the same person
        
        Args:
            person_image1: First person image as bytes
            person_image2: Second person image as bytes
            prompt: Analysis prompt
        
        Returns:
            dict with 'is_same_person' (bool) and 'confidence' (float) or None if error
        """
        if not self.is_available:
            # Silently return None if not configured (already logged during initialization)
            return None
        
        try:
            # Encode images to base64
            img1_b64 = base64.b64encode(person_image1).decode('utf-8')
            img2_b64 = base64.b64encode(person_image2).decode('utf-8')
            
            # Prepare request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "reka-core",  # Update with actual model name
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{img1_b64}"
                                }
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{img2_b64}"
                                }
                            }
                        ]
                    }
                ]
            }
            
            # Make API request
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                # Parse response (adjust based on actual Reka AI response format)
                answer = result.get("choices", [{}])[0].get("message", {}).get("content", "").lower()
                
                # Simple parsing (adjust based on actual response format)
                is_same = "yes" in answer or "same" in answer
                confidence = 0.8  # Default confidence, parse from response if available
                
                # Try to extract confidence score from response
                import re
                conf_match = re.search(r'confidence[:\s]+([0-9.]+)', answer)
                if conf_match:
                    confidence = float(conf_match.group(1))
                
                return {
                    "is_same_person": is_same,
                    "confidence": confidence,
                    "raw_response": answer
                }
            else:
                print(f"Reka AI API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error calling Reka AI: {e}")
            return None
    
    def image_to_bytes(self, image: np.ndarray) -> bytes:
        """Convert numpy image array to bytes"""
        _, buffer = cv2.imencode('.jpg', image)
        return buffer.tobytes()

