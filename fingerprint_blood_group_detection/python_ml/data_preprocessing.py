# File: python_ml/data_preprocessing.py

import os
import sys
from pathlib import Path
import numpy as np
import cv2
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tqdm import tqdm
import pickle

sys.path.insert(0, str(Path(__file__).parent))
import config

class DataPreprocessor:
    def __init__(self):
        self.config = config.Config
        self.label_encoder = LabelEncoder()
        self.X_train = None
        self.X_val = None
        self.X_test = None
        self.y_train = None
        self.y_val = None
        self.y_test = None
        self.y_train_categorical = None
        self.y_val_categorical = None
        self.y_test_categorical = None
        self.class_weights = None
        
    def load_images_from_folder(self, folder_path, blood_group):
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff'}
        images = []
        labels = []
        
        if not folder_path.exists():
            return images, labels
        
        image_files = [f for f in folder_path.iterdir() if f.is_file() and f.suffix.lower() in image_extensions]
        
        for img_file in image_files:
            try:
                img = cv2.imread(str(img_file))
                if img is not None:
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    img = cv2.resize(img, self.config.IMG_SIZE)
                    images.append(img)
                    labels.append(blood_group)
            except Exception as e:
                print(f"⚠️  Error loading {img_file.name}: {str(e)}")
                continue
        
        return images, labels
    
    def load_all_data(self):
        print("\n" + "═" * 60)
        print("LOADING DATASET")
        print("═" * 60)
        
        all_images = []
        all_labels = []
        
        for blood_group in self.config.BLOOD_GROUPS:
            folder_path = self.config.DATASET_ROOT / blood_group
            print(f"\n📂 Loading {blood_group} images...")
            images, labels = self.load_images_from_folder(folder_path, blood_group)
            all_images.extend(images)
            all_labels.extend(labels)
            print(f"   ✅ Loaded {len(images)} images from {blood_group}")
        
        print(f"\n📊 TOTAL LOADED: {len(all_images)} images")
        
        if len(all_images) == 0:
            raise ValueError("❌ No images loaded! Check your dataset path.")
        
        X = np.array(all_images, dtype=np.float32)
        y = np.array(all_labels)
        
        if self.config.NORMALIZE:
            print("🔄 Normalizing pixel values to [0, 1]...")
            X = X / 255.0
        
        print(f"✅ Data shape: {X.shape}")
        print(f"✅ Labels shape: {y.shape}")
        
        return X, y
    
    def encode_labels(self, y):
        print("\n" + "─" * 60)
        print("ENCODING LABELS")
        print("─" * 60)
        
        self.label_encoder.fit(self.config.BLOOD_GROUPS)
        y_encoded = self.label_encoder.transform(y)
        
        print("Label mapping:")
        for i, blood_group in enumerate(self.label_encoder.classes_):
            count = np.sum(y_encoded == i)
            print(f"   {blood_group:6s} → {i} ({count} samples)")
        
        y_categorical = to_categorical(y_encoded, num_classes=self.config.NUM_CLASSES)
        return y_encoded, y_categorical
    
    def split_data(self, X, y, y_categorical):
        print("\n" + "─" * 60)
        print("SPLITTING DATASET")
        print("─" * 60)
        
        X_temp, X_test, y_temp, y_test, y_temp_cat, y_test_cat = train_test_split(
            X, y, y_categorical, test_size=self.config.TEST_SPLIT, random_state=42, stratify=y
        )
        
        val_size_adjusted = self.config.VAL_SPLIT / (1 - self.config.TEST_SPLIT)
        
        X_train, X_val, y_train, y_val, y_train_cat, y_val_cat = train_test_split(
            X_temp, y_temp, y_temp_cat, test_size=val_size_adjusted, random_state=42, stratify=y_temp
        )
        
        print(f"Training set:   {X_train.shape[0]} samples ({X_train.shape[0]/len(X)*100:.1f}%)")
        print(f"Validation set: {X_val.shape[0]} samples ({X_val.shape[0]/len(X)*100:.1f}%)")
        print(f"Test set:       {X_test.shape[0]} samples ({X_test.shape[0]/len(X)*100:.1f}%)")
        
        print("\n📊 Class distribution in training set:")
        for i, blood_group in enumerate(self.label_encoder.classes_):
            count = np.sum(y_train == i)
            print(f"   {blood_group:6s} : {count} samples")
        
        self.X_train = X_train
        self.X_val = X_val
        self.X_test = X_test
        self.y_train = y_train
        self.y_val = y_val
        self.y_test = y_test
        self.y_train_categorical = y_train_cat
        self.y_val_categorical = y_val_cat
        self.y_test_categorical = y_test_cat
        
        return X_train, X_val, X_test, y_train_cat, y_val_cat, y_test_cat
    
    def calculate_class_weights(self):
        from sklearn.utils.class_weight import compute_class_weight
        
        classes = np.unique(self.y_train)
        weights = compute_class_weight(class_weight='balanced', classes=classes, y=self.y_train)
        class_weights_dict = dict(enumerate(weights))
        
        print("\n" + "─" * 60)
        print("CLASS WEIGHTS (for imbalanced data)")
        print("─" * 60)
        for i, blood_group in enumerate(self.label_encoder.classes_):
            print(f"   {blood_group:6s} : {class_weights_dict[i]:.3f}")
        
        self.class_weights = class_weights_dict
        return class_weights_dict
    
    def create_data_generator(self):
        if not self.config.USE_AUGMENTATION:
            return None
        
        print("\n" + "─" * 60)
        print("DATA AUGMENTATION ENABLED")
        print("─" * 60)
        print("Augmentation parameters:")
        for key, value in self.config.AUGMENTATION_CONFIG.items():
            print(f"   {key:25s} : {value}")
        
        datagen = ImageDataGenerator(**self.config.AUGMENTATION_CONFIG)
        return datagen
    
    def save_preprocessing_artifacts(self):
        artifacts_path = self.config.MODELS_DIR / "preprocessing_artifacts.pkl"
        artifacts = {
            'label_encoder': self.label_encoder,
            'class_weights': self.class_weights,
            'blood_groups': self.config.BLOOD_GROUPS,
            'img_size': self.config.IMG_SIZE,
            'num_classes': self.config.NUM_CLASSES
        }
        with open(artifacts_path, 'wb') as f:
            pickle.dump(artifacts, f)
        print(f"\n💾 Preprocessing artifacts saved to: {artifacts_path}")
    
    def run_full_preprocessing(self):
        print("\n╔" + "═" * 58 + "╗")
        print("║" + " " * 15 + "DATA PREPROCESSING PIPELINE" + " " * 15 + "║")
        print("╚" + "═" * 58 + "╝")
        
        X, y = self.load_all_data()
        y_encoded, y_categorical = self.encode_labels(y)
        X_train, X_val, X_test, y_train_cat, y_val_cat, y_test_cat = self.split_data(X, y_encoded, y_categorical)
        class_weights = self.calculate_class_weights()
        datagen = self.create_data_generator()
        self.save_preprocessing_artifacts()
        
        print("\n" + "═" * 60)
        print("✅ PREPROCESSING COMPLETE!")
        print("═" * 60)
        
        return {
            'X_train': X_train, 'X_val': X_val, 'X_test': X_test,
            'y_train': y_train_cat, 'y_val': y_val_cat, 'y_test': y_test_cat,
            'class_weights': class_weights, 'datagen': datagen, 'label_encoder': self.label_encoder
        }

# File: python_ml/data_preprocessing.py