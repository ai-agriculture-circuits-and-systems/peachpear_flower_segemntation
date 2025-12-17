#!/usr/bin/env python3
"""
Generate COCO format JSON annotation files for each image.
This script processes images from data/origin directory and generates JSON files.
This script should be run from the dataset root directory.
"""

import os
import json
import random
import time
import cv2
import numpy as np
from pathlib import Path

def generate_unique_id():
    """Generate unique ID: 7 random digits + 3 digit timestamp"""
    random_part = random.randint(1000000, 9999999)
    timestamp_part = int(time.time()) % 1000
    return int(f"{random_part}{timestamp_part:03d}")

def get_image_info(image_path, image_id):
    """Generate image information for COCO format"""
    file_name = os.path.basename(image_path)
    file_size = os.path.getsize(image_path)
    
    return {
        "id": image_id,
        "width": 512,
        "height": 512,
        "file_name": file_name,
        "size": file_size,
        "format": "JPEG" if image_path.lower().endswith('.jpg') else "BMP",
        "url": "",
        "hash": "",
        "status": "success"
    }

def find_white_bbox(label_image_path):
    """Find minimum bounding box of white regions in the label image"""
    try:
        # Read image
        img = cv2.imread(str(label_image_path))
        if img is None:
            print(f"Could not read label image: {label_image_path}")
            return [0, 0, 512, 512]
        
        # Get image dimensions
        height, width = img.shape[:2]
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Threshold to find white regions (assuming white is close to 255)
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            print(f"No white regions found in {os.path.basename(label_image_path)}")
            return [0, 0, width, height]
        
        # Find the largest contour (assumed to be the main white region)
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Get bounding box
        x, y, w, h = cv2.boundingRect(largest_contour)
        
        # Ensure coordinates are within image bounds
        x = max(0, min(x, width - 1))
        y = max(0, min(y, height - 1))
        w = min(w, width - x)
        h = min(h, height - y)
        
        return [x, y, w, h]
        
    except Exception as e:
        print(f"Error processing label image {label_image_path}: {e}")
        return [0, 0, 512, 512]

def get_annotation_info(image_id, category_id, bbox):
    """Generate annotation information for COCO format"""
    annotation_id = generate_unique_id()
    
    return {
        "id": annotation_id,
        "image_id": image_id,
        "category_id": category_id,
        "segmentation": [],
        "area": bbox[2] * bbox[3],
        "bbox": bbox
    }

def get_category_info(category_name):
    """Generate category information for COCO format"""
    category_id = generate_unique_id()
    
    return {
        "id": category_id,
        "name": category_name,
        "supercategory": "Flower Image"
    }

def find_corresponding_label_image(image_path, label_folders):
    """Find the corresponding label image for a given image in multiple label folders"""
    image_name = os.path.splitext(os.path.basename(image_path))[0]
    
    # Try different possible label image names
    possible_extensions = ['.png', '.jpg', '.jpeg', '.bmp']
    
    for label_folder in label_folders:
        if not os.path.exists(label_folder):
            continue
            
        for ext in possible_extensions:
            label_image_path = os.path.join(label_folder, f"{image_name}{ext}")
            if os.path.exists(label_image_path):
                return label_image_path
        
        # If not found, try with just the number part (for IMG_XXXX.JPG -> XXXX.png)
        if image_name.startswith('IMG_'):
            number_part = image_name[4:]  # Remove 'IMG_' prefix
            for ext in possible_extensions:
                label_image_path = os.path.join(label_folder, f"{number_part}{ext}")
                if os.path.exists(label_image_path):
                    return label_image_path
                
                # Try removing leading zeros
                number_part_no_zeros = str(int(number_part))
                label_image_path = os.path.join(label_folder, f"{number_part_no_zeros}{ext}")
                if os.path.exists(label_image_path):
                    return label_image_path
    
    return None

def create_single_image_coco_json(image_path, category_name, label_folders):
    """Create COCO format JSON for a single image with bbox from label image"""
    
    # Generate category info
    category_info = get_category_info(category_name)
    category_id = category_info["id"]
    
    # Generate image info
    image_id = generate_unique_id()
    image_info = get_image_info(str(image_path), image_id)
    
    # Find corresponding label image and get bbox
    label_image_path = find_corresponding_label_image(image_path, label_folders)
    if label_image_path:
        bbox = find_white_bbox(label_image_path)
    else:
        bbox = [0, 0, 512, 512]
    
    # Generate annotation info
    annotation_info = get_annotation_info(image_id, category_id, bbox)
    
    # Create COCO format JSON
    coco_data = {
        "info": {
            "description": "data",
            "version": "1.0",
            "year": 2025,
            "contributor": "search engine",
            "source": "augmented",
            "license": {
                "name": "Creative Commons Attribution 4.0 International",
                "url": "https://creativecommons.org/licenses/by/4.0/"
            }
        },
        "images": [image_info],
        "annotations": [annotation_info],
        "categories": [category_info]
    }
    
    # Save JSON file in the same directory as the image
    image_dir = os.path.dirname(image_path)
    image_name = os.path.splitext(os.path.basename(image_path))[0]
    json_filename = f"{image_name}.json"
    json_path = os.path.join(image_dir, json_filename)
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(coco_data, f, indent=2, ensure_ascii=False)
    
    print(f"Generated {json_path}")

def process_image_folder(folder_path, category_name, label_folders):
    """Process all images in a folder and create individual JSON files"""
    
    # Get all image files
    image_extensions = ['.jpg', '.jpeg', '.bmp', '.png']
    image_files = []
    
    for ext in image_extensions:
        image_files.extend(Path(folder_path).glob(f"*{ext}"))
        image_files.extend(Path(folder_path).glob(f"*{ext.upper()}"))
    
    if not image_files:
        print(f"No image files found in {folder_path}")
        return
    
    print(f"Processing {len(image_files)} images in {folder_path}...")
    print(f"Using label folders: {label_folders}")
    
    for image_path in image_files:
        create_single_image_coco_json(str(image_path), category_name, label_folders)

def main():
    """Main function to process all image folders"""
    
    # Get the root directory (parent of scripts directory)
    root_dir = Path(__file__).parent.parent
    
    # Define the image folders and their corresponding label folders (now in data/origin)
    image_label_pairs = [
        (root_dir / "data/origin/AppleA/FlowerImages", "FlowerImages", 
         [str(root_dir / "data/origin/AppleA_Labels_1/AppleA_Labels"), 
          str(root_dir / "data/origin/AppleALabels_Train/Masks_Train")]),
        (root_dir / "data/origin/AppleB_1/AppleB", "AppleB", 
         [str(root_dir / "data/origin/AppleB_Labels_1/AppleB_Labels")]),
        (root_dir / "data/origin/Peach_1/PeachSelected", "PeachSelected", 
         [str(root_dir / "data/origin/PeachLabels_1/PeachLabels")]),
        (root_dir / "data/origin/Pear_1/Pear", "Pear", 
         [str(root_dir / "data/origin/PearLabels_2/PearLabels")])
    ]
    
    # Process image folders with their corresponding label folders
    print("Processing image folders with label information...")
    for image_folder, category_name, label_folders in image_label_pairs:
        if image_folder.exists():
            print(f"Processing {image_folder}...")
            process_image_folder(str(image_folder), category_name, label_folders)
        else:
            print(f"Image folder {image_folder} does not exist")

if __name__ == "__main__":
    main() 