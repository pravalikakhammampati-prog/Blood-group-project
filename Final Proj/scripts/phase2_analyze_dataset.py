import os
import cv2
import numpy as np
from collections import Counter
import matplotlib.pyplot as plt
from pathlib import Path

# Dataset path
DATASET_PATH = "dataset/raw"
OUTPUT_PATH = "outputs/visualizations"

def analyze_dataset():
    """Analyze the fingerprint dataset"""
    
    print("="*70)
    print("📊 FINGERPRINT BLOOD GROUP DATASET ANALYSIS")
    print("="*70)
    
    # Check if dataset exists
    if not os.path.exists(DATASET_PATH):
        print(f"❌ Dataset not found at: {DATASET_PATH}")
        return
    
    # Data collection
    dataset_info = {
        'blood_group': [],
        'file_path': [],
        'image_shape': [],
        'mean_intensity': [],
        'std_intensity': []
    }
    
    blood_groups = ['A+', 'A-', 'AB+', 'AB-', 'B+', 'B-', 'O+', 'O-']
    
    print(f"\n🔍 Scanning dataset...\n")
    
    total_images = 0
    
    # Scan each blood group folder
    for bg in blood_groups:
        folder_path = os.path.join(DATASET_PATH, bg)
        
        if not os.path.exists(folder_path):
            print(f"⚠️  Folder not found: {bg}")
            continue
        
        # Get all images in folder
        image_files = list(Path(folder_path).glob('*.*'))
        image_files = [f for f in image_files if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.tif']]
        
        print(f"📁 {bg:4s} : {len(image_files):4d} images", end="")
        
        # Analyze first image as sample
        if image_files:
            sample_img = cv2.imread(str(image_files[0]), cv2.IMREAD_GRAYSCALE)
            if sample_img is not None:
                print(f"  | Shape: {sample_img.shape} | Type: {sample_img.dtype}")
        else:
            print()
        
        # Collect info from all images
        for img_path in image_files:
            img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
            
            if img is not None:
                dataset_info['blood_group'].append(bg)
                dataset_info['file_path'].append(str(img_path))
                dataset_info['image_shape'].append(img.shape)
                dataset_info['mean_intensity'].append(np.mean(img))
                dataset_info['std_intensity'].append(np.std(img))
                total_images += 1
    
    print(f"\n{'='*70}")
    print(f"✅ Total Valid Images: {total_images}")
    print(f"{'='*70}\n")
    
    # Statistics
    bg_counter = Counter(dataset_info['blood_group'])
    
    print("📊 Blood Group Distribution:")
    print("-" * 40)
    for bg in blood_groups:
        count = bg_counter.get(bg, 0)
        percentage = (count / total_images * 100) if total_images > 0 else 0
        bar = "█" * int(percentage / 2)
        print(f"  {bg:4s} | {count:4d} ({percentage:5.1f}%) {bar}")
    
    # Image shape analysis
    print(f"\n🖼️  Image Shape Analysis:")
    print("-" * 40)
    shape_counter = Counter(dataset_info['image_shape'])
    for shape, count in shape_counter.most_common(5):
        print(f"  {shape}: {count} images")
    
    # Intensity statistics
    print(f"\n💡 Intensity Statistics:")
    print("-" * 40)
    print(f"  Mean Intensity: {np.mean(dataset_info['mean_intensity']):.2f} ± {np.std(dataset_info['mean_intensity']):.2f}")
    print(f"  Std Intensity:  {np.mean(dataset_info['std_intensity']):.2f} ± {np.std(dataset_info['std_intensity']):.2f}")
    
    # Visualizations
    create_visualizations(dataset_info, bg_counter)
    
    # Save summary
    save_summary(dataset_info, total_images)
    
    print(f"\n{'='*70}")
    print("✅ Analysis Complete!")
    print(f"{'='*70}\n")
    
    return dataset_info

def create_visualizations(dataset_info, bg_counter):
    """Create visualization charts"""
    
    Path(OUTPUT_PATH).mkdir(parents=True, exist_ok=True)
    
    # 1. Blood Group Distribution Bar Chart
    plt.figure(figsize=(12, 6))
    
    blood_groups = ['A+', 'A-', 'AB+', 'AB-', 'B+', 'B-', 'O+', 'O-']
    counts = [bg_counter.get(bg, 0) for bg in blood_groups]
    colors = ['#ff6b6b', '#ee5a6f', '#4ecdc4', '#45b7aa', '#ffd93d', '#fcbf49', '#95e1d3', '#38ada9']
    
    bars = plt.bar(blood_groups, counts, color=colors, edgecolor='black', linewidth=1.5)
    
    # Add value labels on bars
    for bar, count in zip(bars, counts):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(count)}',
                ha='center', va='bottom', fontweight='bold', fontsize=11)
    
    plt.xlabel('Blood Group', fontsize=14, fontweight='bold')
    plt.ylabel('Number of Samples', fontsize=14, fontweight='bold')
    plt.title('Blood Group Distribution in Dataset', fontsize=16, fontweight='bold', pad=20)
    plt.grid(axis='y', alpha=0.3, linestyle='--')
    plt.tight_layout()
    
    chart_path = os.path.join(OUTPUT_PATH, 'blood_group_distribution.png')
    plt.savefig(chart_path, dpi=150, bbox_inches='tight')
    print(f"  ✅ Saved: {chart_path}")
    plt.close()
    
    # 2. Sample Images Grid
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    fig.suptitle('Sample Fingerprints from Each Blood Group', fontsize=16, fontweight='bold')
    
    for idx, bg in enumerate(blood_groups):
        row = idx // 4
        col = idx % 4
        
        # Find first image of this blood group
        bg_images = [i for i, x in enumerate(dataset_info['blood_group']) if x == bg]
        
        if bg_images:
            img_path = dataset_info['file_path'][bg_images[0]]
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            
            axes[row, col].imshow(img, cmap='gray')
            axes[row, col].set_title(f'{bg} ({len(bg_images)} samples)', fontweight='bold', fontsize=12)
            axes[row, col].axis('off')
        else:
            axes[row, col].text(0.5, 0.5, 'No Data', ha='center', va='center')
            axes[row, col].set_title(bg, fontweight='bold')
            axes[row, col].axis('off')
    
    plt.tight_layout()
    sample_path = os.path.join(OUTPUT_PATH, 'sample_fingerprints.png')
    plt.savefig(sample_path, dpi=150, bbox_inches='tight')
    print(f"  ✅ Saved: {sample_path}")
    plt.close()
    
    # 3. Pie Chart
    plt.figure(figsize=(10, 10))
    
    non_zero_bg = [bg for bg in blood_groups if bg_counter.get(bg, 0) > 0]
    non_zero_counts = [bg_counter[bg] for bg in non_zero_bg]
    
    plt.pie(non_zero_counts, labels=non_zero_bg, autopct='%1.1f%%',
            startangle=90, colors=colors[:len(non_zero_bg)],
            textprops={'fontsize': 12, 'fontweight': 'bold'})
    plt.title('Blood Group Distribution (Percentage)', fontsize=16, fontweight='bold', pad=20)
    
    pie_path = os.path.join(OUTPUT_PATH, 'blood_group_pie.png')
    plt.savefig(pie_path, dpi=150, bbox_inches='tight')
    print(f"  ✅ Saved: {pie_path}")
    plt.close()

def save_summary(dataset_info, total_images):
    """Save dataset summary to text file"""
    
    summary_path = "processed/dataset_summary.txt"
    
    with open(summary_path, 'w') as f:
        f.write("="*60 + "\n")
        f.write("FINGERPRINT BLOOD GROUP DATASET SUMMARY\n")
        f.write("="*60 + "\n\n")
        
        f.write(f"Total Images: {total_images}\n\n")
        
        f.write("Blood Group Distribution:\n")
        f.write("-"*40 + "\n")
        
        bg_counter = Counter(dataset_info['blood_group'])
        for bg in ['A+', 'A-', 'AB+', 'AB-', 'B+', 'B-', 'O+', 'O-']:
            count = bg_counter.get(bg, 0)
            percentage = (count / total_images * 100) if total_images > 0 else 0
            f.write(f"{bg:4s} : {count:4d} images ({percentage:5.1f}%)\n")
        
        f.write("\n" + "="*60 + "\n")
    
    print(f"  ✅ Saved: {summary_path}")

if __name__ == "__main__":
    analyze_dataset()
