"""
Face Verification Module
Handles face registration and verification using OpenCV
"""

import cv2
import numpy as np
import json
from pathlib import Path
from typing import List, Optional, Tuple
import pickle

class FaceVerification:
    """Face recognition and verification handler"""
    
    def __init__(self, data_dir: str = None):
        """Initialize face verification
        
        Args:
            data_dir: Directory to store face encodings
        """
        if data_dir is None:
            base_dir = Path(__file__).parent.parent
            data_dir = base_dir / 'data'
        
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.encodings_file = self.data_dir / 'face_encodings.pkl'
        self.face_cascade = None
        self.registered_faces = []
        
        # Try to load Haar Cascade for face detection
        try:
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
        except Exception as e:
            print(f"Warning: Could not load face cascade: {e}")
    
    def detect_face(self, frame: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """Detect face in frame using Haar Cascade
        
        Args:
            frame: OpenCV frame (BGR format)
            
        Returns:
            (x, y, w, h) tuple of face location or None
        """
        if self.face_cascade is None:
            return None
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(100, 100)
        )
        
        if len(faces) > 0:
            # Return largest face
            faces_sorted = sorted(faces, key=lambda x: x[2] * x[3], reverse=True)
            return tuple(faces_sorted[0])
        
        return None
    
    def extract_face_features(self, frame: np.ndarray, face_location: Tuple[int, int, int, int]) -> np.ndarray:
        """Extract face features from detected face region
        
        Args:
            frame: OpenCV frame (BGR format)
            face_location: (x, y, w, h) tuple from detect_face
            
        Returns:
            Feature vector (flattened face region, normalized)
        """
        x, y, w, h = face_location
        
        # Extract face region
        face_region = frame[y:y+h, x:x+w]
        
        # Resize to standard size
        face_resized = cv2.resize(face_region, (128, 128))
        
        # Convert to grayscale
        gray_face = cv2.cvtColor(face_resized, cv2.COLOR_BGR2GRAY)
        
        # Normalize
        normalized = cv2.normalize(gray_face, None, 0, 255, cv2.NORM_MINMAX)
        
        # Flatten to 1D feature vector
        features = normalized.flatten().astype(np.float32) / 255.0
        
        return features
    
    def register_face(self, frame: np.ndarray) -> bool:
        """Register a face from camera frame
        
        Args:
            frame: OpenCV frame (BGR format)
            
        Returns:
            True if face detected and registered, False otherwise
        """
        face_location = self.detect_face(frame)
        
        if face_location is None:
            return False
        
        # Extract features
        features = self.extract_face_features(frame, face_location)
        
        # Add to registered faces
        self.registered_faces.append(features)
        
        return True
    
    def save_registered_faces(self) -> bool:
        """Save registered faces to file
        
        Returns:
            True if successful, False otherwise
        """
        if not self.registered_faces:
            return False
        
        try:
            with open(self.encodings_file, 'wb') as f:
                pickle.dump(self.registered_faces, f)
            return True
        except Exception as e:
            print(f"Error saving faces: {e}")
            return False
    
    def load_registered_faces(self) -> bool:
        """Load registered faces from file
        
        Returns:
            True if successful, False otherwise
        """
        if not self.encodings_file.exists():
            return False
        
        try:
            with open(self.encodings_file, 'rb') as f:
                self.registered_faces = pickle.load(f)
            return True
        except Exception as e:
            print(f"Error loading faces: {e}")
            return False
    
    def verify_face(self, frame: np.ndarray, threshold: float = 0.6) -> bool:
        """Verify if face in frame matches registered faces
        
        Args:
            frame: OpenCV frame (BGR format)
            threshold: Similarity threshold (0-1, lower is stricter)
            
        Returns:
            True if face matches, False otherwise
        """
        if not self.registered_faces:
            # No faces registered, auto-pass
            return True
        
        face_location = self.detect_face(frame)
        
        if face_location is None:
            return False
        
        # Extract features from current frame
        current_features = self.extract_face_features(frame, face_location)
        
        # Compare with all registered faces
        for registered in self.registered_faces:
            # Calculate normalized correlation
            similarity = np.corrcoef(current_features, registered)[0, 1]
            
            if similarity > threshold:
                return True
        
        return False
    
    def is_configured(self) -> bool:
        """Check if face verification is configured
        
        Returns:
            True if faces are registered, False otherwise
        """
        if self.registered_faces:
            return True
        
        return self.encodings_file.exists()
    
    def clear_registered_faces(self) -> bool:
        """Clear all registered faces
        
        Returns:
            True if successful, False otherwise
        """
        self.registered_faces = []
        
        if self.encodings_file.exists():
            try:
                self.encodings_file.unlink()
                return True
            except Exception as e:
                print(f"Error clearing faces: {e}")
                return False
        
        return True
    
    def get_camera_preview(self, camera_index: int = 0) -> Optional[cv2.VideoCapture]:
        """Initialize camera for preview
        
        Args:
            camera_index: Camera device index (0 for default)
            
        Returns:
            VideoCapture object or None
        """
        try:
            # Use CAP_DSHOW for Windows compatibility
            cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
            if cap.isOpened():
                return cap
        except Exception as e:
            print(f"Error opening camera: {e}")
        
        return None
    
    def draw_face_rectangle(self, frame: np.ndarray, color: Tuple[int, int, int] = (0, 255, 0)) -> np.ndarray:
        """Draw rectangle around detected face
        
        Args:
            frame: OpenCV frame (BGR format)
            color: BGR color tuple for rectangle
            
        Returns:
            Frame with rectangle drawn
        """
        face_location = self.detect_face(frame)
        
        if face_location is not None:
            x, y, w, h = face_location
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(frame, "Face Detected", (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        return frame
