"""
Face Verification for BreakGuard
Offline face matching using OpenCV
"""
import cv2
import numpy as np
from pathlib import Path
from typing import Optional, Tuple
import pickle

class FaceVerification:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.face_data_file = self.data_dir / "face_data.pkl"
        self.reference_image_file = self.data_dir / "reference_face.jpg"
        
        # Load Haar Cascade for face detection
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        # Load saved face data if exists
        self.reference_encoding = self._load_reference_face()
    
    def _load_reference_face(self) -> Optional[np.ndarray]:
        """Load saved reference face encoding"""
        if self.face_data_file.exists():
            try:
                with open(self.face_data_file, 'rb') as f:
                    data = pickle.load(f)
                    print("Reference face data loaded")
                    return data
            except Exception as e:
                print(f"Error loading face data: {e}")
        return None
    
    def _save_reference_face(self, encoding: np.ndarray):
        """Save reference face encoding"""
        try:
            with open(self.face_data_file, 'wb') as f:
                pickle.dump(encoding, f)
            print("Reference face data saved")
        except Exception as e:
            print(f"Error saving face data: {e}")
    
    def capture_from_camera(self, camera_index: int = 0) -> Optional[np.ndarray]:
        """
        Capture image from camera
        Returns: numpy array of captured image or None
        """
        cap = cv2.VideoCapture(camera_index)
        
        if not cap.isOpened():
            print("Error: Could not open camera")
            return None
        
        print("Camera opened. Press SPACE to capture, ESC to cancel")
        
        captured_image = None
        
        while True:
            ret, frame = cap.read()
            
            if not ret:
                print("Error: Could not read frame")
                break
            
            # Detect faces in the frame
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(100, 100)
            )
            
            # Draw rectangles around detected faces
            display_frame = frame.copy()
            for (x, y, w, h) in faces:
                cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(display_frame, "Face Detected", (x, y-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Display instructions
            cv2.putText(display_frame, "SPACE: Capture | ESC: Cancel", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.imshow('BreakGuard Face Capture', display_frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == 32:  # SPACE key
                if len(faces) > 0:
                    captured_image = frame
                    print("Image captured successfully")
                    break
                else:
                    print("No face detected. Please try again.")
            elif key == 27:  # ESC key
                print("Capture cancelled")
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        return captured_image
    
    def detect_face(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        Detect face in image and extract face region
        Returns: cropped face image or None
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(100, 100)
        )
        
        if len(faces) == 0:
            print("No face detected in image")
            return None
        
        # Get the largest face
        faces = sorted(faces, key=lambda x: x[2] * x[3], reverse=True)
        x, y, w, h = faces[0]
        
        # Extract face region with some padding
        padding = int(w * 0.2)
        x = max(0, x - padding)
        y = max(0, y - padding)
        w = min(image.shape[1] - x, w + 2 * padding)
        h = min(image.shape[0] - y, h + 2 * padding)
        
        face_image = image[y:y+h, x:x+w]
        return face_image
    
    def create_face_encoding(self, face_image: np.ndarray) -> np.ndarray:
        """
        Create simple face encoding using histogram
        This is a simple approach - can be enhanced with deep learning
        """
        # Resize to standard size
        face_resized = cv2.resize(face_image, (128, 128))
        
        # Convert to grayscale
        gray = cv2.cvtColor(face_resized, cv2.COLOR_BGR2GRAY)
        
        # Normalize
        normalized = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)
        
        # Flatten to create encoding
        encoding = normalized.flatten()
        
        return encoding
    
    def compare_faces(self, encoding1: np.ndarray, encoding2: np.ndarray, 
                      threshold: float = 0.85) -> Tuple[bool, float]:
        """
        Compare two face encodings
        Returns: (is_match, similarity_score)
        """
        # Calculate correlation coefficient
        correlation = np.corrcoef(encoding1, encoding2)[0, 1]
        
        # Higher correlation means more similar
        is_match = correlation >= threshold
        
        return is_match, correlation
    
    def register_face(self, camera_index: int = 0) -> bool:
        """
        Register reference face for verification
        """
        print("=== Face Registration ===")
        print("Position your face in front of the camera")
        
        # Capture image
        image = self.capture_from_camera(camera_index)
        
        if image is None:
            print("Face registration failed")
            return False
        
        # Detect and extract face
        face = self.detect_face(image)
        
        if face is None:
            print("Could not detect face in captured image")
            return False
        
        # Create encoding
        encoding = self.create_face_encoding(face)
        
        # Save reference
        self.reference_encoding = encoding
        self._save_reference_face(encoding)
        
        # Save reference image
        cv2.imwrite(str(self.reference_image_file), face)
        
        print("Face registered successfully!")
        return True
    
    def verify_face(self, camera_index: int = 0, 
                    threshold: float = 0.85) -> Tuple[bool, Optional[float]]:
        """
        Verify face against registered reference
        Returns: (is_verified, similarity_score)
        """
        if self.reference_encoding is None:
            print("No reference face registered. Please register first.")
            return False, None
        
        print("=== Face Verification ===")
        print("Position your face in front of the camera")
        
        # Capture image
        image = self.capture_from_camera(camera_index)
        
        if image is None:
            return False, None
        
        # Detect and extract face
        face = self.detect_face(image)
        
        if face is None:
            print("Could not detect face in captured image")
            return False, None
        
        # Create encoding
        encoding = self.create_face_encoding(face)
        
        # Compare with reference
        is_match, similarity = self.compare_faces(
            self.reference_encoding,
            encoding,
            threshold
        )
        
        if is_match:
            print(f"✓ Face verified! Similarity: {similarity:.2%}")
        else:
            print(f"✗ Face verification failed. Similarity: {similarity:.2%}")
        
        return is_match, similarity
    
    def is_registered(self) -> bool:
        """Check if a reference face is registered"""
        return self.reference_encoding is not None
    
    def delete_registration(self):
        """Delete registered face data"""
        self.reference_encoding = None
        
        if self.face_data_file.exists():
            self.face_data_file.unlink()
        
        if self.reference_image_file.exists():
            self.reference_image_file.unlink()
        
        print("Face registration deleted")
