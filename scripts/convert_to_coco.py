#!/usr/bin/env python3
"""
Convert CSV annotations to COCO format for Peach-Pear Flower Segmentation dataset.
"""

import os
import json
import csv
import argparse
from pathlib import Path
from PIL import Image
import random

def load_labelmap(labelmap_path):
    """Load labelmap.json"""
    with open(labelmap_path, 'r', encoding='utf-8') as f:
        labelmap = json.load(f)
    return {item['object_id']: item['object_name'] for item in labelmap}

def parse_csv(csv_path):
    """Parse CSV annotation file"""
    annotations = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Skip comment lines
            if row.get('#item', '').startswith('#'):
                continue
            try:
                item = int(row.get('#item', 0))
                x = float(row.get('x', 0))
                y = float(row.get('y', 0))
                width = float(row.get('width', row.get('w', row.get('dx', 0))))
                height = float(row.get('height', row.get('h', row.get('dy', 0))))
                label = int(row.get('label', row.get('class', row.get('category_id', 1))))
                annotations.append({
                    'item': item,
                    'bbox': [x, y, width, height],
                    'label': label
                })
            except (ValueError, KeyError) as e:
                continue
    return annotations

def get_image_info(image_path):
    """Get image dimensions"""
    try:
        with Image.open(image_path) as img:
            return img.size
    except Exception:
        return (512, 512)  # Default

def convert_to_coco(root_dir, output_dir, categories=None, splits=None, combined=False):
    """Convert CSV annotations to COCO format"""
    root = Path(root_dir)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    
    if categories is None:
        categories = ['apples', 'applebs', 'peaches', 'pears']
    if splits is None:
        splits = ['train', 'val', 'test']
    
    # Build combined categories first (for proper ID mapping)
    combined_categories = []
    cat_id = 1
    category_name_map = {}  # Map category folder name to category name in labelmap
    
    for category in categories:
        category_dir = root / category
        labelmap_path = category_dir / 'labelmap.json'
        if labelmap_path.exists():
            labelmap = load_labelmap(labelmap_path)
            for obj_id, obj_name in sorted(labelmap.items()):
                if obj_id == 0:
                    continue
                combined_categories.append({
                    'id': cat_id,
                    'name': obj_name,
                    'supercategory': 'flower'
                })
                category_name_map[category] = obj_name
                cat_id += 1
    
    # Process each category
    all_coco_data = {}
    
    for category in categories:
        category_dir = root / category
        images_dir = category_dir / 'images'
        csv_dir = category_dir / 'csv'
        sets_dir = category_dir / 'sets'
        
        if not images_dir.exists():
            print(f"Warning: {images_dir} does not exist, skipping {category}")
            continue
        
        # Load labelmap for this category
        labelmap_path = category_dir / 'labelmap.json'
        if not labelmap_path.exists():
            print(f"Warning: {labelmap_path} does not exist, skipping {category}")
            continue
        
        labelmap = load_labelmap(labelmap_path)
        
        # Build category list from labelmap (only non-background categories)
        coco_categories = []
        for obj_id, obj_name in sorted(labelmap.items()):
            if obj_id == 0:
                continue  # Skip background
            coco_categories.append({
                'id': 1,  # Each category folder has only one non-background category
                'name': obj_name,
                'supercategory': 'flower'
            })
        
        # Process each split
        for split in splits:
            coco_data = {
                'info': {
                    'year': 2025,
                    'version': '1.0',
                    'description': f'Peach-Pear Flower Segmentation {category} {split} split',
                    'url': 'https://agdatacommons.nal.usda.gov/download/articles/24852636/versions/1/'
                },
                'images': [],
                'annotations': [],
                'categories': coco_categories,
                'licenses': []
            }
            
            # Load split file
            split_file = sets_dir / f'{split}.txt'
            split_images = set()
            if split_file.exists():
                with open(split_file, 'r', encoding='utf-8') as f:
                    split_images = {line.strip() for line in f if line.strip()}
                print(f"Loaded {len(split_images)} images for {category}/{split}")
            else:
                print(f"Warning: Split file '{split_file}' does not exist, skipping {category}/{split}")
                continue
            
            # Get images in this split
            image_files = []
            for stem in split_images:
                for ext in ['.jpg', '.JPG', '.png', '.PNG', '.jpeg', '.JPEG', '.bmp', '.BMP']:
                    img_path = images_dir / f"{stem}{ext}"
                    if img_path.exists():
                        image_files.append(img_path)
                        break
            
            print(f"  Found {len(image_files)}/{len(split_images)} images for {category}/{split}")
            
            # Process images
            image_id_map = {}
            annotation_id = 1
            
            for img_path in image_files:
                stem = img_path.stem
                
                # Get image info
                width, height = get_image_info(img_path)
                image_id = random.randint(1000000000, 9999999999)
                image_id_map[stem] = image_id
                
                coco_data['images'].append({
                    'id': image_id,
                    'file_name': f'{category}/images/{img_path.name}',
                    'width': width,
                    'height': height
                })
                
                # Load CSV annotations
                csv_path = csv_dir / f'{stem}.csv'
                if csv_path.exists():
                    annotations = parse_csv(csv_path)
                    for ann in annotations:
                        bbox = ann['bbox']
                        label = ann['label']
                        
                        # Map label to category_id (use 1 for single category per folder)
                        category_id = 1  # Each category folder has only one non-background category
                        
                        coco_data['annotations'].append({
                            'id': annotation_id,
                            'image_id': image_id,
                            'category_id': category_id,
                            'bbox': bbox,
                            'area': bbox[2] * bbox[3],
                            'iscrowd': 0
                        })
                        annotation_id += 1
            
            # Save single category file
            if len(coco_data['images']) > 0:
                output_file = output / f'{category}_instances_{split}.json'
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(coco_data, f, indent=2, ensure_ascii=False)
                print(f"Created {output_file}: {len(coco_data['images'])} images, {len(coco_data['annotations'])} annotations")
            
            # Add to combined data
            if split not in all_coco_data:
                all_coco_data[split] = {
                    'info': {
                        'year': 2025,
                        'version': '1.0',
                        'description': f'Peach-Pear Flower Segmentation combined {split} split',
                        'url': 'https://agdatacommons.nal.usda.gov/download/articles/24852636/versions/1/'
                    },
                    'images': [],
                    'annotations': [],
                    'categories': combined_categories,
                    'licenses': []
                }
            
            # Map category names to IDs in combined file
            combined_cat_map = {}
            for cat in combined_categories:
                combined_cat_map[cat['name']] = cat['id']
            
            # Get the category name for this category folder
            category_name = category_name_map.get(category, 'flower')
            combined_category_id = combined_cat_map.get(category_name, 1)
            
            # Add images and annotations to combined data
            for img in coco_data['images']:
                all_coco_data[split]['images'].append(img)
            
            # Remap category IDs for combined file
            for ann in coco_data['annotations']:
                new_ann = ann.copy()
                new_ann['category_id'] = combined_category_id
                all_coco_data[split]['annotations'].append(new_ann)
    
    # Create combined files if requested
    if combined:
        for split in splits:
            if split in all_coco_data and len(all_coco_data[split]['images']) > 0:
                output_file = output / f'combined_instances_{split}.json'
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(all_coco_data[split], f, indent=2, ensure_ascii=False)
                print(f"Created {output_file}: {len(all_coco_data[split]['images'])} images, {len(all_coco_data[split]['annotations'])} annotations")

def main():
    parser = argparse.ArgumentParser(description='Convert CSV annotations to COCO format')
    parser.add_argument('--root', type=str, default='.', help='Dataset root directory')
    parser.add_argument('--out', type=str, default='annotations', help='Output directory')
    parser.add_argument('--categories', nargs='+', 
                        default=['apples', 'applebs', 'peaches', 'pears'],
                        help='Categories to process')
    parser.add_argument('--splits', nargs='+', default=['train', 'val', 'test'], help='Splits to process')
    parser.add_argument('--combined', action='store_true', help='Create combined COCO files')
    
    args = parser.parse_args()
    convert_to_coco(args.root, args.out, args.categories, args.splits, args.combined)

if __name__ == '__main__':
    main()

