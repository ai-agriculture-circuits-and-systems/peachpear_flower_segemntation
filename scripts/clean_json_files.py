#!/usr/bin/env python3
"""
Delete all previously generated JSON files from original data directories.
This script should be run from the dataset root directory.
"""

import os
import glob
from pathlib import Path

def clean_json_files():
    """Delete all previously generated JSON files"""
    
    # Get the root directory (parent of scripts directory)
    root_dir = Path(__file__).parent.parent
    
    # Define the folders to clean (now in data/origin)
    folders_to_clean = [
        "data/origin/AppleA/FlowerImages",
        "data/origin/AppleB_1/AppleB", 
        "data/origin/Peach_1/PeachSelected",
        "data/origin/Pear_1/Pear",
        "data/origin/AppleA_Labels_1/AppleA_Labels",
        "data/origin/AppleB_Labels_1/AppleB_Labels",
        "data/origin/PeachLabels_1/PeachLabels",
        "data/origin/PearLabels_2/PearLabels"
    ]
    
    total_deleted = 0
    
    for folder in folders_to_clean:
        folder_path = root_dir / folder
        if folder_path.exists():
            # Find all JSON files in the folder
            json_pattern = str(folder_path / "*.json")
            json_files = glob.glob(json_pattern)
            
            for json_file in json_files:
                try:
                    os.remove(json_file)
                    print(f"Deleted: {json_file}")
                    total_deleted += 1
                except Exception as e:
                    print(f"Error deleting {json_file}: {e}")
        else:
            print(f"Folder {folder_path} does not exist")
    
    print(f"\nTotal deleted: {total_deleted} JSON files")

if __name__ == "__main__":
    clean_json_files() 