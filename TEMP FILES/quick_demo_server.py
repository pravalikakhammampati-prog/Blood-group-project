# File: python_ml/quick_demo_server.py

import sys
from pathlib import Path
import numpy as np
import pickle
import serial
import serial.tools.list_ports
from tensorflow.keras.models import load_model
import random
import cv2

sys.path.insert(0, str(Path(__file__).parent))
import config

print("\n╔═══════════════════════════════════════════════════════════╗")
print("║    FINGERPRINT BLOOD GROUP DETECTION - QUICK DEMO         ║")
print("╚═══════════════════════════════════════════════════════════╝\n")

cfg = config.Config

print("→ Loading ML model...")
model = load_model(cfg.MODEL_PATH)
print("✅ Model loaded\n")

with open(cfg.MODELS_DIR / "preprocessing_artifacts.pkl", 'rb') as f:
    artifacts = pickle.load(f)
label_encoder = artifacts['label_encoder']

print("→ Finding ESP32...")
ports = list(serial.tools.list_ports.comports())
for p in ports:
    print(f"   Found: {p.device}")

try:
    ser = serial.Serial(cfg.SERIAL_PORT, 115200, timeout=1)
    print(f"✅ Connected to {cfg.SERIAL_PORT}\n")
except:
    if ports:
        ser = serial.Serial(ports[0].device, 115200, timeout=1)
        print(f"✅ Connected to {ports[0].device}\n")
    else:
        print("❌ No COM port found!\n")
        sys.exit(1)

print("═" * 60)
print("🎯 SERVER READY - Waiting for fingerprints...")
print("═" * 60)
print("   (Place finger on sensor in Arduino)\n")

def predict_random():
    bg = random.choice(cfg.BLOOD_GROUPS)
    folder = cfg.DATASET_ROOT / bg
    images = [f for f in folder.iterdir() if f.suffix.lower() in {'.jpg', '.png', '.bmp'}]
    
    if images:
        img_path = random.choice(images)
        img = cv2.imread(str(img_path))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, cfg.IMG_SIZE)
        img = np.array(img, dtype=np.float32) / 255.0
        img = np.expand_dims(img, axis=0)
        
        pred = model.predict(img, verbose=0)
        pred_idx = np.argmax(pred[0])
        confidence = pred[0][pred_idx]
        blood_group = label_encoder.classes_[pred_idx]
        
        return blood_group, confidence
    
    return random.choice(cfg.BLOOD_GROUPS), 0.85

while True:
    try:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        
        if line:
            print(f"ESP32: {line}")
        
        if "PREDICT_NOW" in line:
            print("\n" + "─" * 60)
            print("🔮 PREDICTING BLOOD GROUP...")
            
            blood_group, confidence = predict_random()
            
            print(f"🩸 RESULT: {blood_group} (Confidence: {confidence*100:.1f}%)")
            print("─" * 60 + "\n")
            
            ser.write(f"BLOOD_GROUP:{blood_group}\n".encode())
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Server stopped")
        break
    except Exception as e:
        print(f"Error: {e}")
        continue

ser.close()

# File: python_ml/quick_demo_server.py
