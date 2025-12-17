#!/usr/bin/env python3
"""
Reorganize peachpear_flower_segmentation dataset to standard structure.

This script reorganizes the dataset from the original structure to the standardized
structure following the dataset structure specification.
"""

import os
import shutil
import json
from pathlib import Path
from collections import defaultdict

# Mapping from original category names to standardized plural names
CATEGORY_MAPPING = {
    'AppleA': 'apples',
    'AppleB': 'applebs',
    'Peach_1': 'peaches',
    'Pear_1': 'pears'
}

# Mapping from original label folder names to categories
LABEL_FOLDER_MAPPING = {
    'AppleA_Labels_1': 'apples',
    'AppleALabels_Train': 'apples',
    'AppleB_Labels_1': 'applebs',
    'PeachLabels_1': 'peaches',
    'PearLabels_2': 'pears'
}

# Original image folder paths
IMAGE_FOLDERS = {
    'apples': 'AppleA/FlowerImages',
    'applebs': 'AppleB_1/AppleB',
    'peaches': 'Peach_1/PeachSelected',
    'pears': 'Pear_1/Pear'
}

# Original label folder paths
LABEL_FOLDERS = {
    'apples': ['AppleA_Labels_1/AppleA_Labels', 'AppleALabels_Train/Masks_Train'],
    'applebs': ['AppleB_Labels_1/AppleB_Labels'],
    'peaches': ['PeachLabels_1/PeachLabels'],
    'pears': ['PearLabels_2/PearLabels']
}


def find_image_files(root_dir, category):
    """Find all image files for a category."""
    image_folder = Path(root_dir) / IMAGE_FOLDERS[category]
    if not image_folder.exists():
        return []
    
    images = []
    for ext in ['.JPG', '.jpg', '.BMP', '.bmp', '.PNG', '.png']:
        images.extend(list(image_folder.glob(f'*{ext}')))
    
    return images


def find_label_files(root_dir, category):
    """Find all label/mask files for a category."""
    label_folders = LABEL_FOLDERS[category]
    labels = []
    
    for label_folder in label_folders:
        label_path = Path(root_dir) / label_folder
        if label_path.exists():
            labels.extend(list(label_path.glob('*.png')))
    
    return labels


def get_image_stem(image_path):
    """Get image stem (filename without extension)."""
    stem = image_path.stem
    # Handle special cases like IMG_0248 -> 248
    if stem.startswith('IMG_'):
        stem = stem.replace('IMG_', '')
    return stem


def get_label_stem(label_path):
    """Get label stem (filename without extension)."""
    return label_path.stem


def copy_image(image_path, dest_dir, category):
    """Copy image to destination directory."""
    dest_path = dest_dir / 'images' / image_path.name
    shutil.copy2(image_path, dest_path)
    return dest_path


def copy_json(json_path, dest_dir, category):
    """Copy JSON annotation to destination directory."""
    dest_path = dest_dir / 'json' / json_path.name
    shutil.copy2(json_path, dest_path)
    return dest_path


def copy_segmentation(label_path, dest_dir, category, image_stem):
    """Copy segmentation mask to destination directory."""
    # Use image stem as filename
    dest_path = dest_dir / 'segmentations' / f'{image_stem}.png'
    shutil.copy2(label_path, dest_path)
    return dest_path


def json_to_csv(json_path, csv_path):
    """Convert JSON annotation to CSV format."""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    csv_lines = ['#item,x,y,width,height,label']
    
    if 'annotations' in data and len(data['annotations']) > 0:
        for idx, ann in enumerate(data['annotations']):
            bbox = ann.get('bbox', [])
            if len(bbox) == 4:
                x, y, w, h = bbox
                # Use label 1 for all annotations (each category folder has only one non-background category)
                label = 1
                csv_lines.append(f'{idx},{x},{y},{w},{h},{label}')
    
    with open(csv_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(csv_lines) + '\n')


def reorganize_category(root_dir, category):
    """Reorganize a single category."""
    print(f"\nProcessing category: {category}")
    root_path = Path(root_dir)
    dest_dir = root_path / category
    
    # Find all images
    images = find_image_files(root_dir, category)
    print(f"  Found {len(images)} images")
    
    # Find all labels
    labels = find_label_files(root_dir, category)
    print(f"  Found {len(labels)} segmentation masks")
    
    # Create mapping from label stem to label path
    label_map = {}
    for label_path in labels:
        label_stem = get_label_stem(label_path)
        label_map[label_stem] = label_path
    
    # Process each image
    processed_images = []
    for image_path in images:
        image_stem = get_image_stem(image_path)
        
        # Copy image
        dest_image = copy_image(image_path, dest_dir, category)
        processed_images.append(dest_image.stem)
        
        # Copy JSON if exists
        json_path = image_path.parent / f'{image_path.stem}.json'
        if json_path.exists():
            copy_json(json_path, dest_dir, category)
            
            # Create CSV from JSON
            csv_path = dest_dir / 'csv' / f'{image_path.stem}.csv'
            json_to_csv(json_path, csv_path)
        
        # Copy segmentation mask if exists
        # Try multiple possible label stems
        label_found = False
        for possible_stem in [image_stem, image_path.stem, str(int(image_stem)) if image_stem.isdigit() else None]:
            if possible_stem and possible_stem in label_map:
                copy_segmentation(label_map[possible_stem], dest_dir, category, image_path.stem)
                label_found = True
                break
        
        if not label_found:
            # Try to find by partial match
            for label_stem, label_path in label_map.items():
                if image_stem in label_stem or label_stem in image_stem:
                    copy_segmentation(label_path, dest_dir, category, image_path.stem)
                    break
    
    print(f"  Processed {len(processed_images)} images")
    return processed_images


def create_labelmap(category_dir, category_name):
    """Create labelmap.json for a category."""
    labelmap = [
        {
            "object_id": 0,
            "label_id": 0,
            "keyboard_shortcut": "0",
            "object_name": "background"
        },
        {
            "object_id": 1,
            "label_id": 1,
            "keyboard_shortcut": "1",
            "object_name": category_name.lower().rstrip('s')  # Remove 's' for singular
        }
    ]
    
    labelmap_path = Path(category_dir) / 'labelmap.json'
    with open(labelmap_path, 'w', encoding='utf-8') as f:
        json.dump(labelmap, f, indent=2, ensure_ascii=False)
    
    print(f"  Created labelmap.json")


def reorganize_splits(root_dir):
    """Reorganize dataset splits."""
    root_path = Path(root_dir)
    
    # Read original split files
    train_file = root_path / 'train.txt'
    val_file = root_path / 'val_0.txt'
    
    train_images = set()
    val_images = set()
    
    if train_file.exists():
        with open(train_file, 'r', encoding='utf-8') as f:
            train_images = {line.strip() for line in f if line.strip()}
    
    if val_file.exists():
        with open(val_file, 'r', encoding='utf-8') as f:
            val_images = {line.strip() for line in f if line.strip()}
    
    # Organize by category
    category_splits = defaultdict(lambda: {'train': [], 'val': [], 'all': []})
    
    # Process each category
    for category in ['apples', 'applebs', 'peaches', 'pears']:
        category_dir = root_path / category
        images_dir = category_dir / 'images'
        
        if not images_dir.exists():
            continue
        
        # Get all images in this category
        all_category_images = []
        for ext in ['.JPG', '.jpg', '.BMP', '.bmp', '.PNG', '.png']:
            all_category_images.extend([img.stem for img in images_dir.glob(f'*{ext}')])
        
        # Categorize into train/val
        category_train = []
        category_val = []
        
        for img_stem in all_category_images:
            # Check if image is in train or val
            img_name_with_ext = None
            for ext in ['.JPG', '.jpg', '.BMP', '.bmp', '.PNG', '.png']:
                if f'{img_stem}{ext}' in train_images or img_stem in train_images:
                    category_train.append(img_stem)
                    break
                elif f'{img_stem}{ext}' in val_images or img_stem in val_images:
                    category_val.append(img_stem)
                    break
        
        # If not found in splits, add remaining to train
        for img_stem in all_category_images:
            if img_stem not in category_train and img_stem not in category_val:
                category_train.append(img_stem)
        
        category_splits[category]['train'] = sorted(category_train)
        category_splits[category]['val'] = sorted(category_val)
        category_splits[category]['all'] = sorted(all_category_images)
    
    # Write split files for each category
    for category, splits in category_splits.items():
        sets_dir = root_path / category / 'sets'
        sets_dir.mkdir(parents=True, exist_ok=True)
        
        # Write train.txt
        with open(sets_dir / 'train.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(splits['train']) + '\n')
        
        # Write val.txt
        with open(sets_dir / 'val.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(splits['val']) + '\n')
        
        # Write all.txt
        with open(sets_dir / 'all.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(splits['all']) + '\n')
        
        # Write train_val.txt
        train_val = sorted(splits['train'] + splits['val'])
        with open(sets_dir / 'train_val.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(train_val) + '\n')
        
        print(f"  Created split files for {category}: {len(splits['train'])} train, {len(splits['val'])} val, {len(splits['all'])} total")


def main():
    """Main function."""
    root_dir = Path(__file__).parent.parent
    
    print("Reorganizing peachpear_flower_segmentation dataset...")
    print(f"Root directory: {root_dir}")
    
    # Reorganize each category
    for category in ['apples', 'applebs', 'peaches', 'pears']:
        reorganize_category(root_dir, category)
        create_labelmap(root_dir / category, category)
    
    # Reorganize splits
    print("\nReorganizing dataset splits...")
    reorganize_splits(root_dir)
    
    print("\nReorganization complete!")


if __name__ == '__main__':
    main()

