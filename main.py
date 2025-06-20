import tkinter as tk
from tkinter import messagebox
import cv2
from PIL import Image, ImageTk
import os
from datetime import datetime
import numpy as np

class CameraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Camera App with Age & Emotion Detection")
        self.root.geometry("1000x750")
        
        # Initialize camera
        self.cap = cv2.VideoCapture(0)
        
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Could not open camera")
            root.destroy()
            return
        
        # Load detection models
        self.load_models()
        
        # Detection toggles
        self.age_detection_enabled = tk.BooleanVar(value=True)
        self.emotion_detection_enabled = tk.BooleanVar(value=True)
        
        # Create GUI elements
        self.create_widgets()
        
        # Start video feed
        self.update_frame()
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def load_models(self):
        """Load pre-trained models for face, age, and emotion detection"""
        try:
            # Age groups
            self.age_list = ['(18-20)', '(24-26)', '(28-32)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']
            
            # Emotion labels
            self.emotion_list = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']
            
            # Load face detection model (Haar Cascade)
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            # Load additional cascade for better emotion detection features
            self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
            self.smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')
            
            self.model_loaded = True
            self.status_text = "Detection models loaded successfully"
            
        except Exception as e:
            self.model_loaded = False
            self.status_text = f"Error loading models: {str(e)}"
    
    def create_widgets(self):
        # Main frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control frame
        control_frame = tk.Frame(main_frame, bg="#e8f4fd", relief=tk.RAISED, bd=2)
        control_frame.pack(fill=tk.X, pady=5, padx=5)
        
        control_title = tk.Label(control_frame, text="Detection Controls", font=("Arial", 12, "bold"), bg="#e8f4fd")
        control_title.pack(pady=5)
        
        # Toggle buttons frame
        toggle_frame = tk.Frame(control_frame, bg="#e8f4fd")
        toggle_frame.pack(pady=5)
        
        # Age detection toggle
        age_toggle = tk.Checkbutton(
            toggle_frame,
            text="🎂 Age Detection",
            variable=self.age_detection_enabled,
            font=("Arial", 11),
            bg="#e8f4fd"
        )
        age_toggle.pack(side=tk.LEFT, padx=20)
        
        # Emotion detection toggle
        emotion_toggle = tk.Checkbutton(
            toggle_frame,
            text="😊 Emotion Detection",
            variable=self.emotion_detection_enabled,
            font=("Arial", 11),
            bg="#e8f4fd"
        )
        emotion_toggle.pack(side=tk.LEFT, padx=20)
        
        # Video frame
        self.video_label = tk.Label(main_frame, bg="black")
        self.video_label.pack(pady=10)
        
        # Button frame
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        # Capture button
        self.capture_btn = tk.Button(
            button_frame, 
            text="📸 Capture Photo", 
            command=self.capture_photo,
            font=("Arial", 14, "bold"),
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=10,
            relief=tk.RAISED
        )
        self.capture_btn.pack(side=tk.LEFT, padx=10)
        
        # Quit button
        self.quit_btn = tk.Button(
            button_frame,
            text="❌ Quit",
            command=self.on_closing,
            font=("Arial", 14, "bold"),
            bg="#f44336",
            fg="white",
            padx=20,
            pady=10,
            relief=tk.RAISED
        )
        self.quit_btn.pack(side=tk.LEFT, padx=10)
        
        # Detection info frame
        info_frame = tk.Frame(main_frame, bg="#f9f9f9", relief=tk.SUNKEN, bd=2)
        info_frame.pack(fill=tk.X, pady=10, padx=5)
        
        info_title = tk.Label(info_frame, text="Detection Results", font=("Arial", 12, "bold"), bg="#f9f9f9")
        info_title.pack(pady=5)
        
        self.detection_info = tk.Label(
            info_frame, 
            text="No faces detected", 
            font=("Arial", 11),
            bg="#f9f9f9",
            wraplength=900,
            justify=tk.LEFT
        )
        self.detection_info.pack(pady=5, padx=10)
        
        # Status label
        self.status_label = tk.Label(main_frame, text=self.status_text, font=("Arial", 10))
        self.status_label.pack(pady=5)
    
    def estimate_age_simple(self, face_roi):
        """Simple age estimation based on face characteristics"""
        # Convert to grayscale for analysis
        gray_face = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
        
        # Calculate some basic features
        height, width = gray_face.shape
        
        # Calculate edge density (more edges might indicate older age due to wrinkles)
        edges = cv2.Canny(gray_face, 50, 150)
        edge_density = np.sum(edges) / (height * width)
        
        # Normalize edge density
        edge_density_norm = min(edge_density / 50, 1.0)
        
        # Simple age estimation based on edge density and face size
        if edge_density_norm < 0.1:
            return self.age_list[0]  # (0-2)
        elif edge_density_norm < 0.2:
            return self.age_list[1]  # (4-6)
        elif edge_density_norm < 0.3:
            return self.age_list[2]  # (8-12)
        elif edge_density_norm < 0.4:
            return self.age_list[3]  # (15-20)
        elif edge_density_norm < 0.5:
            return self.age_list[4]  # (25-32)
        elif edge_density_norm < 0.6:
            return self.age_list[5]  # (38-43)
        elif edge_density_norm < 0.7:
            return self.age_list[6]  # (48-53)
        else:
            return self.age_list[7]  # (60-100)
    
    def detect_emotion_simple(self, face_roi, face_gray):
        """Simple emotion detection based on facial features"""
        try:
            # Detect eyes and smile within the face region
            eyes = self.eye_cascade.detectMultiScale(face_gray, 1.1, 3)
            smiles = self.smile_cascade.detectMultiScale(face_gray, 1.8, 20)
            
            # Calculate basic features for emotion estimation
            height, width = face_gray.shape
            
            # Analyze brightness and contrast
            mean_brightness = np.mean(face_gray)
            brightness_std = np.std(face_gray)
            
            # Detect edges for expression analysis
            edges = cv2.Canny(face_gray, 30, 100)
            edge_density = np.sum(edges) / (height * width)
            
            # Simple heuristic-based emotion detection
            if len(smiles) > 0:
                # Strong smile detected
                return 'Happy'
            elif len(eyes) >= 2 and brightness_std > 45:
                # Eyes detected with high contrast (possibly surprise/fear)
                if edge_density > 0.15:
                    return 'Surprise'
                else:
                    return 'Fear'
            elif edge_density > 0.2:
                # High edge density might indicate anger (furrowed brow)
                return 'Angry'
            elif mean_brightness < 80:
                # Darker image might indicate sadness
                return 'Sad'
            elif edge_density < 0.05:
                # Very smooth face might indicate neutral
                return 'Neutral'
            else:
                # Default to neutral for ambiguous cases
                return 'Neutral'
                
        except Exception as e:
            return 'Neutral'
    
    def get_emotion_color(self, emotion):
        """Get color for emotion label"""
        color_map = {
            'Happy': (0, 255, 0),      # Green
            'Sad': (255, 0, 0),        # Blue
            'Angry': (0, 0, 255),      # Red
            'Surprise': (0, 255, 255), # Yellow
            'Fear': (128, 0, 128),     # Purple
            'Disgust': (0, 128, 128),  # Teal
            'Neutral': (128, 128, 128) # Gray
        }
        return color_map.get(emotion, (255, 255, 255))
    
    def detect_faces_age_emotion(self, frame):
        """Detect faces and estimate ages and emotions"""
        if not self.model_loaded:
            return frame, []
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        detection_results = []
        
        for (x, y, w, h) in faces:
            # Draw rectangle around face
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
            # Extract face ROI
            face_roi = frame[y:y+h, x:x+w]
            face_gray = gray[y:y+h, x:x+w]
            
            if face_roi.size > 0:
                estimated_age = None
                estimated_emotion = None
                
                # Estimate age if enabled
                if self.age_detection_enabled.get():
                    estimated_age = self.estimate_age_simple(face_roi)
                
                # Detect emotion if enabled
                if self.emotion_detection_enabled.get():
                    estimated_emotion = self.detect_emotion_simple(face_roi, face_gray)
                
                # Prepare label text
                label_parts = []
                if estimated_age:
                    label_parts.append(f'Age: {estimated_age}')
                if estimated_emotion:
                    label_parts.append(f'Emotion: {estimated_emotion}')
                
                # Draw labels
                y_offset = y - 10
                for i, label in enumerate(label_parts):
                    color = (0, 255, 0)  # Default green
                    if 'Emotion:' in label and estimated_emotion:
                        color = self.get_emotion_color(estimated_emotion)
                    
                    cv2.putText(frame, label, (x, y_offset - (i * 25)), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                
                detection_results.append({
                    'position': (x, y, w, h),
                    'age': estimated_age,
                    'emotion': estimated_emotion
                })
        
        return frame, detection_results
    
    def update_frame(self):
        ret, frame = self.cap.read()
        
        if ret:
            # Apply face, age, and emotion detection
            processed_frame, detections = self.detect_faces_age_emotion(frame.copy())
            
            # Update detection info
            if detections:
                info_text = f"🎯 Detected {len(detections)} face(s):\n\n"
                for i, detection in enumerate(detections):
                    info_text += f"👤 Face {i+1}:\n"
                    if detection['age']:
                        info_text += f"   🎂 Age: {detection['age']}\n"
                    if detection['emotion']:
                        info_text += f"   😊 Emotion: {detection['emotion']}\n"
                    info_text += "\n"
                self.detection_info.config(text=info_text.strip())
            else:
                active_detections = []
                if self.age_detection_enabled.get():
                    active_detections.append("age")
                if self.emotion_detection_enabled.get():
                    active_detections.append("emotion")
                
                if active_detections:
                    self.detection_info.config(text=f"No faces detected\n({' & '.join(active_detections)} detection active)")
                else:
                    self.detection_info.config(text="All detection disabled")
            
            # Convert frame from BGR to RGB
            frame_rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
            
            # Resize frame to fit in window
            height, width = frame_rgb.shape[:2]
            max_width, max_height = 700, 500
            
            if width > max_width or height > max_height:
                scale = min(max_width/width, max_height/height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                frame_rgb = cv2.resize(frame_rgb, (new_width, new_height))
            
            # Convert to PIL Image and then to PhotoImage
            pil_image = Image.fromarray(frame_rgb)
            photo = ImageTk.PhotoImage(pil_image)
            
            # Update label with new frame
            self.video_label.config(image=photo)
            self.video_label.image = photo  # Keep a reference
            
            # Store current frame for capture
            self.current_frame = frame
        
        # Schedule next frame update
        self.root.after(10, self.update_frame)
    
    def capture_photo(self):
        if hasattr(self, 'current_frame'):
            # Create captures directory if it doesn't exist
            if not os.path.exists("captures"):
                os.makedirs("captures")
            
            # Apply detection to the captured frame
            processed_frame, detections = self.detect_faces_age_emotion(self.current_frame.copy())
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"captures/photo_{timestamp}.jpg"
            
            # Save the photo with detections
            cv2.imwrite(filename, processed_frame)
            
            # Create info text for the capture
            if detections:
                info_text = f"📸 Captured photo with {len(detections)} face(s) detected:\n"
                for i, detection in enumerate(detections):
                    info_parts = []
                    if detection['age']:
                        info_parts.append(f"Age: {detection['age']}")
                    if detection['emotion']:
                        info_parts.append(f"Emotion: {detection['emotion']}")
                    if info_parts:
                        info_text += f"Face {i+1}: {', '.join(info_parts)}\n"
            else:
                info_text = "📸 Photo captured (no faces detected)"
            
            # Update status
            self.status_label.config(text=f"Photo saved: {filename}")
            
            # Show success message with detection info
            messagebox.showinfo("Photo Captured", f"{info_text}\n📁 Saved as: {filename}")
        else:
            messagebox.showerror("Error", "No frame available to capture")
    
    def on_closing(self):
        # Release camera and close window
        if hasattr(self, 'cap'):
            self.cap.release()
        self.root.destroy()

# Create and run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = CameraApp(root)
    root.mainloop()