import cv2
import os
import numpy as np
from pathlib import Path

DATASET_PATH = "dataset/raw"
OUTPUT_LOG = "outputs/logs/quality_check.log"

def verify_dataset_quality():
    """Check for corrupted or problematic images"""
    
    print("="*70)
    print("🔍 DATASET QUALITY VERIFICATION")
    print("="*70 + "\n")
    
    Path("outputs/logs").mkdir(parents=True, exist_ok=True)
    
    valid_images = []
    corrupted_images = []
    small_images = []
    low_quality = []
    
    blood_groups = ['A+', 'A-', 'AB+', 'AB-', 'B+', 'B-', 'O+', 'O-']
    
    print("Checking images...\n")
    
    for bg in blood_groups:
        folder_path = os.path.join(DATASET_PATH, bg)
        
        if not os.path.exists(folder_path):
            continue
        
        image_files = list(Path(folder_path).glob('*.*'))
        
        for img_path in image_files:
            if img_path.suffix.lower() not in ['.jpg', '.jpeg', '.png', '.bmp', '.tif']:
                continue
            
            try:
                # Try to read image
                img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
                
                if img is None:
                    corrupted_images.append(str(img_path))
                    continue
                
                # Check dimensions
                height, width = img.shape
                
                if height < 50 or width < 50:
                    small_images.append((str(img_path), img.shape))
                    continue
                
                # Check quality (variance)
                variance = np.var(img)
                
                if variance < 100:  # Very low variance = poor quality
                    low_quality.append((str(img_path), variance))
                
                valid_images.append({
                    'path': str(img_path),
                    'blood_group': bg,
                    'shape': img.shape,
                    'mean': np.mean(img),
                    'std': np.std(img),
                    'variance': variance
                })
                
            except Exception as e:
                corrupted_images.append(str(img_path))
    
    # Print results
    print("📊 Quality Check Results:")
    print("-"*70)
    print(f"  ✅ Valid Images:      {len(valid_images)}")
    print(f"  ❌ Corrupted Images:  {len(corrupted_images)}")
    print(f"  ⚠️  Small Images:      {len(small_images)}")
    print(f"  ⚠️  Low Quality:       {len(low_quality)}")
    
    # Save log
    with open(OUTPUT_LOG, 'w') as f:
        f.write("DATASET QUALITY VERIFICATION LOG\n")
        f.write("="*70 + "\n\n")
        
        f.write(f"Valid Images: {len(valid_images)}\n")
        f.write(f"Corrupted Images: {len(corrupted_images)}\n")
        f.write(f"Small Images: {len(small_images)}\n")
        f.write(f"Low Quality: {len(low_quality)}\n\n")
        
        if corrupted_images:
            f.write("\nCORRUPTED IMAGES:\n")
            f.write("-"*70 + "\n")
            for img in corrupted_images:
                f.write(f"  - {img}\n")
        
        if small_images:
            f.write("\nSMALL IMAGES (< 50x50):\n")
            f.write("-"*70 + "\n")
            for img, shape in small_images:
                f.write(f"  - {img} : {shape}\n")
        
        if low_quality:
            f.write("\nLOW QUALITY IMAGES:\n")
            f.write("-"*70 + "\n")
            for img, var in low_quality[:20]:  # First 20
                f.write(f"  - {img} : variance={var:.2f}\n")
    
    print(f"\n✅ Log saved: {OUTPUT_LOG}")
    print("\n" + "="*70)
    print("✅ Quality Check Complete!")
    print("="*70 + "\n")
    
    return valid_images

if __name__ == "__main__":
    verify_dataset_quality()
