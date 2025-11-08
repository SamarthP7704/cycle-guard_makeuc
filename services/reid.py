import torch
import numpy as np
from typing import List, Optional
import cv2
from config import settings

# Try to import torchreid, but continue without it if not available
try:
    from torchreid import models as torchreid_models
    TORCHREID_AVAILABLE = True
except ImportError:
    TORCHREID_AVAILABLE = False
    torchreid_models = None
    print("⚠️  torchreid not installed. Using fallback feature extraction.")


class ReIDService:
    """Service for person re-identification using torchreid"""
    
    def __init__(self):
        self.model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self._load_model()
    
    def _load_model(self):
        """Load torchreid model"""
        if not TORCHREID_AVAILABLE:
            print("⚠️  torchreid not available. Using fallback feature extraction.")
            self.model = None
            return
            
        try:
            # Initialize torchreid model
            self.model = torchreid_models.build_model(
                name=settings.reid_model_name,
                num_classes=1000,  # Dummy number, we only use it for feature extraction
                pretrained=True
            )
            self.model = self.model.to(self.device)
            self.model.eval()
            print(f"✅ Loaded ReID model: {settings.reid_model_name} on {self.device}")
        except Exception as e:
            print(f"⚠️  Error loading ReID model: {e}")
            import traceback
            traceback.print_exc()
            print("Falling back to simpler feature extraction...")
            self.model = None
    
    def extract_embedding(self, person_image: np.ndarray) -> np.ndarray:
        """
        Extract embedding from person image
        
        Args:
            person_image: BGR image array (numpy array)
        
        Returns:
            Normalized embedding vector
        """
        if self.model is None:
            # Fallback: simple feature extraction using histogram and HOG-like features
            return self._simple_feature_extraction(person_image)
        
        try:
            # Preprocess image
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(person_image, cv2.COLOR_BGR2RGB)
            
            # Resize to model input size (typically 256x128 for person re-id)
            resized = cv2.resize(rgb_image, (256, 128))
            
            # Normalize and convert to tensor
            image_tensor = torch.from_numpy(resized).float()
            image_tensor = image_tensor.permute(2, 0, 1)  # HWC to CHW
            image_tensor = image_tensor / 255.0
            image_tensor = image_tensor.unsqueeze(0)  # Add batch dimension
            image_tensor = image_tensor.to(self.device)
            
            # Normalize with ImageNet stats
            mean = torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1).to(self.device)
            std = torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1).to(self.device)
            image_tensor = (image_tensor - mean) / std
            
            # Extract features
            with torch.no_grad():
                features = self.model(image_tensor)
                # Handle different return types
                if isinstance(features, tuple):
                    # If tuple, take first element (features)
                    features = features[0]
                
                # Ensure features is 2D: [batch_size, feature_dim]
                if len(features.shape) > 2:
                    # Flatten if needed (shouldn't happen with torchreid models)
                    features = features.view(features.size(0), -1)
                
                # Extract first (and only) item from batch: [feature_dim]
                embedding = features.cpu().numpy()[0]
            
            # Normalize embedding
            embedding = embedding / (np.linalg.norm(embedding) + 1e-8)
            return embedding
            
        except Exception as e:
            print(f"Error extracting embedding with model: {e}")
            return self._simple_feature_extraction(person_image)
    
    def _simple_feature_extraction(self, person_image: np.ndarray) -> np.ndarray:
        """Fallback feature extraction using color histograms and texture"""
        try:
            # Resize for consistent feature size
            resized = cv2.resize(person_image, (128, 256))
            
            # Convert to different color spaces
            rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
            hsv = cv2.cvtColor(resized, cv2.COLOR_BGR2HSV)
            lab = cv2.cvtColor(resized, cv2.COLOR_BGR2LAB)
            
            features = []
            
            # Color histograms
            for img, bins in [(rgb, 32), (hsv, 32), (lab, 32)]:
                for i in range(3):  # For each channel
                    hist = cv2.calcHist([img], [i], None, [bins], [0, 256])
                    features.extend(hist.flatten())
            
            # Texture features (gradient magnitude)
            gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
            gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            magnitude = np.sqrt(gx**2 + gy**2)
            features.extend(magnitude.flatten()[::100])  # Sample every 100th pixel
            
            # Convert to numpy array and normalize
            embedding = np.array(features, dtype=np.float32)
            embedding = embedding / (np.linalg.norm(embedding) + 1e-8)
            
            return embedding
            
        except Exception as e:
            print(f"Error in simple feature extraction: {e}")
            # Return a random embedding as last resort
            return np.random.randn(512).astype(np.float32)
    
    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings
        
        Returns:
            Similarity score between 0 and 1
        """
        # Ensure embeddings are normalized
        emb1 = embedding1 / (np.linalg.norm(embedding1) + 1e-8)
        emb2 = embedding2 / (np.linalg.norm(embedding2) + 1e-8)
        
        # Cosine similarity
        similarity = np.dot(emb1, emb2)
        
        # Normalize to [0, 1] range (cosine similarity is typically [-1, 1])
        similarity = (similarity + 1) / 2
        
        return float(similarity)

