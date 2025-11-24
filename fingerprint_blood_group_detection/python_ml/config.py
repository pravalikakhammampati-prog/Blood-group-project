# File: python_ml/config.py

import os
from pathlib import Path

class Config:
    PROJECT_ROOT = Path(__file__).parent.parent
    DATASET_ROOT = PROJECT_ROOT / "archive(1)" / "dataset_blood_group"
    BLOOD_GROUPS = ["A+", "A-", "AB+", "AB-", "B+", "B-", "O+", "O-"]
    NUM_CLASSES = len(BLOOD_GROUPS)
    MODELS_DIR = PROJECT_ROOT / "python_ml" / "models"
    MODEL_PATH = MODELS_DIR / "blood_group_model.h5"
    TFLITE_MODEL_PATH = MODELS_DIR / "blood_group_model.tflite"
    LOGS_DIR = PROJECT_ROOT / "python_ml" / "logs"
    TEST_IMAGES_DIR = PROJECT_ROOT / "python_ml" / "test_images"
    IMG_HEIGHT = 128
    IMG_WIDTH = 128
    IMG_CHANNELS = 3
    IMG_SIZE = (IMG_HEIGHT, IMG_WIDTH)
    NORMALIZE = True
    BATCH_SIZE = 32
    EPOCHS = 50
    LEARNING_RATE = 0.001
    TRAIN_SPLIT = 0.7
    VAL_SPLIT = 0.15
    TEST_SPLIT = 0.15
    USE_AUGMENTATION = True
    AUGMENTATION_CONFIG = {
        'rotation_range': 20,
        'width_shift_range': 0.2,
        'height_shift_range': 0.2,
        'shear_range': 0.2,
        'zoom_range': 0.2,
        'horizontal_flip': True,
        'fill_mode': 'nearest'
    }
    DROPOUT_RATE = 0.5
    SERIAL_PORT = "COM3"
    BAUD_RATE = 115200
    SERIAL_TIMEOUT = 5
    FINGERPRINT_WIDTH = 256
    FINGERPRINT_HEIGHT = 288
    SERVER_HOST = "0.0.0.0"
    SERVER_PORT = 5000
    DEBUG_MODE = True
    CONFIDENCE_THRESHOLD = 0.6
    VERBOSE = True
    SAVE_PLOTS = True
    
    @classmethod
    def create_directories(cls):
        directories = [cls.MODELS_DIR, cls.LOGS_DIR, cls.TEST_IMAGES_DIR]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        if cls.VERBOSE:
            print("✅ All directories created successfully!")
    
    @classmethod
    def verify_dataset_exists(cls):
        if not cls.DATASET_ROOT.exists():
            raise FileNotFoundError(
                f"❌ Dataset not found at: {cls.DATASET_ROOT}\n"
                f"Please ensure the 'archive(1)' folder is in the project root."
            )
        return True
    
    @classmethod
    def get_class_folders(cls):
        return [cls.DATASET_ROOT / bg for bg in cls.BLOOD_GROUPS]
    
    @classmethod
    def print_config(cls):
        print("\n" + "═" * 60)
        print("         FINGERPRINT BLOOD GROUP DETECTION")
        print("              CONFIGURATION SETTINGS")
        print("═" * 60)
        print(f"\n📁 PROJECT ROOT: {cls.PROJECT_ROOT}")
        print(f"📁 DATASET ROOT: {cls.DATASET_ROOT}")
        print(f"\n🩸 BLOOD GROUPS: {', '.join(cls.BLOOD_GROUPS)}")
        print(f"🔢 NUMBER OF CLASSES: {cls.NUM_CLASSES}")
        print(f"\n🖼️  IMAGE SIZE: {cls.IMG_WIDTH}x{cls.IMG_HEIGHT}x{cls.IMG_CHANNELS}")
        print(f"📊 BATCH SIZE: {cls.BATCH_SIZE}")
        print(f"🔄 EPOCHS: {cls.EPOCHS}")
        print(f"📈 LEARNING RATE: {cls.LEARNING_RATE}")
        print(f"\n📂 DATA SPLIT: Train={cls.TRAIN_SPLIT*100}%, Val={cls.VAL_SPLIT*100}%, Test={cls.TEST_SPLIT*100}%")
        print(f"🔀 AUGMENTATION: {'Enabled' if cls.USE_AUGMENTATION else 'Disabled'}")
        print(f"\n🔌 SERIAL PORT: {cls.SERIAL_PORT}")
        print(f"⚡ BAUD RATE: {cls.BAUD_RATE}")
        print("═" * 60 + "\n")

# File: python_ml/config.py