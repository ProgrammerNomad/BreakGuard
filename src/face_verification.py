"""
Face Verification Module
Handles face registration and verification using OpenCV
"""
from __future__ import annotations

import cv2
import numpy as np
import json
import base64
import logging
from pathlib import Path
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)

class FaceVerification:
    """Face recognition and verification handler"""
    
    def __init__(self, data_dir: str | Path = None):
        """Initialize face verification
        
        Args:
            data_dir: Directory to store face encodings
        """
        if data_dir is None:
            from path_utils import get_data_dir
            data_dir = get_data_dir()
        
        self.data_dir: Path = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.encodings_file = self.data_dir / 'face_encodings.json'
        self.face_cascade = None
        self.registered_faces: List[dict] = []
        
        # Try to load Haar Cascade for face detection
        try:
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
        except (AttributeError, cv2.error) as e:
            logger.warning(f"Could not load face cascade: {e}")
    
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
            # Convert numpy arrays to base64 strings
            faces_data = []
            for face_features in self.registered_faces:
                # Convert float32 array to bytes
                face_bytes = face_features.tobytes()
                # Encode to base64 string
                face_b64 = base64.b64encode(face_bytes).decode('utf-8')
                faces_data.append({
                    'encoding': face_b64,
                    'shape': face_features.shape,
                    'dtype': str(face_features.dtype)
                })
            
            # Save to JSON
            with open(self.encodings_file, 'w') as f:
                json.dump({
                    'version': 1,
                    'faces': faces_data
                }, f, indent=2)
            
            logger.info(f"Saved {len(self.registered_faces)} face encodings")
            return True
        except (IOError, OSError) as e:
            logger.error(f"Error saving faces: {e}", exc_info=True)
            return False
    
    def load_registered_faces(self) -> bool:
        """Load registered faces from file
        
        Returns:
            True if successful, False otherwise
        """
        if not self.encodings_file.exists():
            # Try to migrate old pickle file
            old_pickle_file = self.data_dir / 'face_encodings.pkl'
            if old_pickle_file.exists():
                return self._migrate_from_pickle(old_pickle_file)
            return False
        
        try:
            with open(self.encodings_file, 'r') as f:
                data = json.load(f)
            
            # Validate version
            if data.get('version') != 1:
                logger.warning(f"Unknown face encodings version: {data.get('version')}")
                return False
            
            # Decode base64 strings back to numpy arrays
            self.registered_faces = []
            for face_data in data.get('faces', []):
                face_b64 = face_data['encoding']
                shape = tuple(face_data['shape'])
                dtype = face_data['dtype']
                
                # Decode from base64
                face_bytes = base64.b64decode(face_b64)
                # Reconstruct numpy array
                face_array = np.frombuffer(face_bytes, dtype=dtype).reshape(shape)
                self.registered_faces.append(face_array)
            
            logger.info(f"Loaded {len(self.registered_faces)} face encodings")
            return True
        except (IOError, OSError, json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Error loading faces: {e}", exc_info=True)
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
    
    def _migrate_from_pickle(self, old_file: Path) -> bool:
        """Migrate old pickle file to JSON format
        
        Args:
            old_file: Path to old pickle file
            
        Returns:
            True if migration successful, False otherwise
        """
        try:
            import pickle
            
            # Load old pickle file
            with open(old_file, 'rb') as f:
                self.registered_faces = pickle.load(f)
            
            logger.info(f"Migrating {len(self.registered_faces)} faces from pickle to JSON")
            
            # Save in new format
            if self.save_registered_faces():
                # Backup old file
                backup_file = old_file.with_suffix('.pkl.bak')
                old_file.rename(backup_file)
                logger.info(f"Migrated successfully, backup saved to {backup_file}")
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error migrating from pickle: {e}", exc_info=True)
            return False
    
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
