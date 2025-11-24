# File: python_ml/inference_server.py

import os
import sys
from pathlib import Path
import numpy as np
import cv2
import pickle
import serial
import serial.tools.list_ports
from tensorflow.keras.models import load_model

sys.path.insert(0, str(Path(__file__).parent))
import config

class BloodGroupPredictor:
    def __init__(self):
        self.config = config.Config
        self.model = None
        self.label_encoder = None
        self.serial_port = None
        
    def load_model_and_artifacts(self):
        print("\n" + "═" * 60)
        print("LOADING MODEL AND ARTIFACTS")
        print("═" * 60)
        
        if not self.config.MODEL_PATH.exists():
            raise FileNotFoundError(f"Model not found: {self.config.MODEL_PATH}")
        
        print(f"→ Loading model from: {self.config.MODEL_PATH}")
        self.model = load_model(self.config.MODEL_PATH)
        print("✅ Model loaded successfully")
        
        artifacts_path = self.config.MODELS_DIR / "preprocessing_artifacts.pkl"
        if not artifacts_path.exists():
            raise FileNotFoundError(f"Artifacts not found: {artifacts_path}")
        
        print(f"→ Loading preprocessing artifacts...")
        with open(artifacts_path, 'rb') as f:
            artifacts = pickle.load(f)
        
        self.label_encoder = artifacts['label_encoder']
        print("✅ Label encoder loaded")
        
        print(f"\n📊 Model ready to predict {len(self.label_encoder.classes_)} classes:")
        print(f"   {', '.join(self.label_encoder.classes_)}")
        
    def find_esp32_port(self):
        print("\n" + "─" * 60)
        print("SEARCHING FOR ESP32")
        print("─" * 60)
        
        ports = list(serial.tools.list_ports.comports())
        
        print(f"Found {len(ports)} serial port(s):")
        for i, port in enumerate(ports):
            print(f"   {i+1}. {port.device} - {port.description}")
        
        if not ports:
            print("❌ No serial ports found!")
            return None
        
        print(f"\nTrying to connect to {self.config.SERIAL_PORT}...")
        
        try:
            ser = serial.Serial(
                self.config.SERIAL_PORT,
                self.config.BAUD_RATE,
                timeout=self.config.SERIAL_TIMEOUT
            )
            print(f"✅ Connected to {self.config.SERIAL_PORT}")
            return ser
        except Exception as e:
            print(f"❌ Failed to connect: {str(e)}")
            
            if len(ports) > 0:
                print(f"\nAttempting to connect to {ports[0].device}...")
                try:
                    ser = serial.Serial(
                        ports[0].device,
                        self.config.BAUD_RATE,
                        timeout=self.config.SERIAL_TIMEOUT
                    )
                    print(f"✅ Connected to {ports[0].device}")
                    return ser
                except Exception as e:
                    print(f"❌ Failed: {str(e)}")
            
            return None
    
    def predict_from_image(self, image):
        img_resized = cv2.resize(image, self.config.IMG_SIZE)
        
        if len(img_resized.shape) == 2:
            img_resized = cv2.cvtColor(img_resized, cv2.COLOR_GRAY2RGB)
        
        img_array = np.array(img_resized, dtype=np.float32)
        
        if self.config.NORMALIZE:
            img_array = img_array / 255.0
        
        img_array = np.expand_dims(img_array, axis=0)
        
        predictions = self.model.predict(img_array, verbose=0)
        
        predicted_class_idx = np.argmax(predictions[0])
        confidence = predictions[0][predicted_class_idx]
        
        blood_group = self.label_encoder.classes_[predicted_class_idx]
        
        return blood_group, confidence, predictions[0]
    
    def predict_from_dataset(self):
        print("\n" + "─" * 60)
        print("DEMO MODE: Using random image from dataset")
        print("─" * 60)
        
        import random
        blood_group_folder = random.choice(self.config.BLOOD_GROUPS)
        folder_path = self.config.DATASET_ROOT / blood_group_folder
        
        image_files = [f for f in folder_path.iterdir() if f.suffix.lower() in {'.jpg', '.jpeg', '.png', '.bmp'}]
        
        if not image_files:
            print("❌ No images found in dataset")
            return None, 0, None
        
        random_image_path = random.choice(image_files)
        print(f"→ Using image: {random_image_path.name}")
        print(f"→ Actual blood group: {blood_group_folder}")
        
        image = cv2.imread(str(random_image_path))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        return self.predict_from_image(image)
    
    def run_inference_server(self):
        print("\n")
        print("╔" + "═" * 58 + "╗")
        print("║" + " " * 10 + "BLOOD GROUP INFERENCE SERVER" + " " * 19 + "║")
        print("╚" + "═" * 58 + "╝")
        
        self.load_model_and_artifacts()
        
        self.serial_port = self.find_esp32_port()
        
        if self.serial_port is None:
            print("\n⚠️  Running in DEMO MODE (no ESP32 connected)")
            print("   Will use random images from dataset for testing")
            demo_mode = True
        else:
            demo_mode = False
        
        print("\n" + "═" * 60)
        print("SERVER RUNNING - Waiting for fingerprint data...")
        print("═" * 60)
        
        if demo_mode:
            print("\n→ Press ENTER to run demo prediction...")
        else:
            print("\n→ Send fingerprint from ESP32 (press 'D' in Arduino Serial Monitor)")
        
        while True:
            try:
                if demo_mode:
                    input()
                    print("\n" + "─" * 60)
                    blood_group, confidence, all_probs = self.predict_from_dataset()
                    
                    if blood_group is not None:
                        print(f"\n🩸 PREDICTED BLOOD GROUP: {blood_group}")
                        print(f"📊 Confidence: {confidence*100:.2f}%")
                        
                        print("\n📊 All predictions:")
                        for i, bg in enumerate(self.label_encoder.classes_):
                            print(f"   {bg:6s} : {all_probs[i]*100:5.2f}%")
                        
                        print("\n→ Press ENTER for another prediction...")
                
                else:
                    line = self.serial_port.readline().decode('utf-8', errors='ignore').strip()
                    
                    if line:
                        print(f"ESP32: {line}")
                    
                    if line == "FINGERPRINT_START":
                        print("\n" + "─" * 60)
                        print("→ Receiving fingerprint data...")
                        
                        data_received = False
                        while True:
                            line = self.serial_port.readline().decode('utf-8', errors='ignore').strip()
                            
                            if line == "FINGERPRINT_END":
                                break
                            
                            if line.startswith("FINGERPRINT_DATA:"):
                                data_received = True
                        
                        if data_received:
                            print("✅ Fingerprint data received")
                            print("→ Running prediction (using demo image)...")
                            
                            blood_group, confidence, all_probs = self.predict_from_dataset()
                            
                            print(f"\n🩸 PREDICTED BLOOD GROUP: {blood_group}")
                            print(f"📊 Confidence: {confidence*100:.2f}%")
                            
                            self.serial_port.write(f"BLOOD_GROUP:{blood_group}\n".encode())
                            print(f"✅ Result sent to ESP32: {blood_group}")
                            
                            print("\n→ Waiting for next fingerprint...")
                
            except KeyboardInterrupt:
                print("\n\n⚠️  Server stopped by user")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                continue
        
        if self.serial_port:
            self.serial_port.close()
        
        print("\n✅ Server shutdown complete")

def main():
    predictor = BloodGroupPredictor()
    predictor.run_inference_server()

if __name__ == "__main__":
    main()

# File: python_ml/inference_server.py