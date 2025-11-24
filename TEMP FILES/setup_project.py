import os
from pathlib import Path
import shutil

def create_project_structure():
    """Create organized project structure"""
    
    print("🏗️  Creating project structure...\n")
    
    # Define folder structure
    folders = [
        "dataset/raw",
        "processed/sample_images",
        "models",
        "scripts",
        "esp32_code/fingerprint_capture",
        "esp32_code/final_integration",
        "outputs/logs",
        "outputs/visualizations",
        "outputs/results"
    ]
    
    # Create folders
    for folder in folders:
        Path(folder).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {folder}/")
    
    # Move existing dataset
    source_dataset = "archive (1)/dataset_blood_group"
    target_dataset = "dataset/raw"
    
    if os.path.exists(source_dataset):
        print(f"\n📦 Moving dataset from '{source_dataset}' to '{target_dataset}'...")
        
        blood_groups = ['A+', 'A-', 'AB+', 'AB-', 'B+', 'B-', 'O+', 'O-']
        
        for bg in blood_groups:
            src = os.path.join(source_dataset, bg)
            dst = os.path.join(target_dataset, bg)
            
            if os.path.exists(src):
                # Create destination
                Path(dst).mkdir(parents=True, exist_ok=True)
                
                # Copy files
                files = list(Path(src).glob('*.*'))
                for file in files:
                    if file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.tif']:
                        shutil.copy2(file, dst)
                
                print(f"   ✅ {bg}: {len(list(Path(dst).glob('*.*')))} files")
    
    # Move ESP32 code
    old_esp_code = "Verifaication_code_copy_20251124114440"
    if os.path.exists(old_esp_code):
        new_location = "esp32_code/fingerprint_capture"
        ino_file = os.path.join(old_esp_code, "Verifaication_code_copy_20251124114440.ino")
        if os.path.exists(ino_file):
            shutil.copy2(ino_file, os.path.join(new_location, "fingerprint_capture.ino"))
            print(f"\n✅ Moved ESP32 code to {new_location}/")
    
    print("\n" + "="*60)
    print("✅ Project structure created successfully!")
    print("="*60)

if __name__ == "__main__":
    create_project_structure()
