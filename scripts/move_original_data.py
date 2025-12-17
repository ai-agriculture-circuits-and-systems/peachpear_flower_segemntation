#!/usr/bin/env python3
"""
Move original dataset files to data/origin directory and clean up.
"""

import os
import shutil
from pathlib import Path

def main():
    """Move original data to data/origin and clean up."""
    root_dir = Path(__file__).parent.parent
    
    # Create data/origin directory
    origin_dir = root_dir / 'data' / 'origin'
    origin_dir.mkdir(parents=True, exist_ok=True)
    
    # Directories to move
    original_dirs = [
        'AppleA',
        'AppleA_Labels_1',
        'AppleALabels_Train',
        'AppleB_1',
        'AppleB_Labels_1',
        'Peach_1',
        'PeachLabels_1',
        'Pear_1',
        'PearLabels_2',
        'train.txt',
        'val_0.txt'
    ]
    
    print("Moving original data to data/origin...")
    for item in original_dirs:
        src = root_dir / item
        if src.exists():
            dst = origin_dir / item
            if dst.exists():
                print(f"  Warning: {dst} already exists, skipping {item}")
            else:
                print(f"  Moving {item}...")
                shutil.move(str(src), str(dst))
    
    # Delete original JSON files in original directories
    print("\nDeleting original JSON files...")
    json_count = 0
    for json_file in origin_dir.rglob('*.json'):
        if json_file.is_file():
            json_file.unlink()
            json_count += 1
    
    print(f"  Deleted {json_count} JSON files")
    
    print("\nDone!")

if __name__ == '__main__':
    main()





