# Peach-Pear Flower Segmentation Dataset

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/your-repo/peachpear-flower-segmentation)

A comprehensive dataset of peach and pear flower images for segmentation tasks, collected and organized for computer vision and deep learning research in agricultural applications.

**Project page**: `https://agdatacommons.nal.usda.gov/download/articles/24852636/versions/1/`

## TL;DR

- **Task**: Object Detection, Instance Segmentation
- **Modality**: RGB
- **Platform**: Ground/Field
- **Real/Synthetic**: Real
- **Images**: 207 flower images across 4 categories (apples, applebs, peaches, pears)
- **Resolution**: Variable (typically 5184×3456 pixels or larger)
- **Annotations**: CSV (per-image), JSON (per-image), COCO JSON (generated)
- **Segmentation masks**: PNG format with white regions indicating flower areas
- **License**: CC BY 4.0
- **Citation**: see below

## Table of Contents

- [Download](#download)
- [Dataset Structure](#dataset-structure)
- [Sample Images](#sample-images)
- [Annotation Schema](#annotation-schema)
- [Stats and Splits](#stats-and-splits)
- [Quick Start](#quick-start)
- [Evaluation and Baselines](#evaluation-and-baselines)
- [Datasheet (Data Card)](#datasheet-data-card)
- [Known Issues and Caveats](#known-issues-and-caveats)
- [License](#license)
- [Citation](#citation)
- [Changelog](#changelog)
- [Contact](#contact)

## Download

**Original dataset**: `https://agdatacommons.nal.usda.gov/download/articles/24852636/versions/1/`

This repo hosts structure and conversion scripts only; place the downloaded folders under this directory.

**Local license file**: See `LICENSE` in the root directory.

## Dataset Structure

```
peachpear_flower_segmentation/
├── apples/                          # Apple variety A flowers
│   ├── csv/                         # CSV annotation files (per-image)
│   ├── json/                        # JSON annotation files (per-image)
│   ├── images/                      # Image files
│   ├── segmentations/               # Segmentation mask files
│   ├── labelmap.json               # Label mapping file
│   └── sets/                        # Dataset split files
│       ├── train.txt                # Training set image list
│       ├── val.txt                  # Validation set image list
│       ├── all.txt                  # All images list
│       └── train_val.txt            # Train+val images list
├── applebs/                         # Apple variety B flowers
│   └── ...                         # Same structure as apples
├── peaches/                         # Peach flowers
│   └── ...                         # Same structure as apples
├── pears/                           # Pear flowers
│   └── ...                         # Same structure as apples
├── annotations/                     # COCO format JSON files (generated)
│   ├── apples_instances_train.json
│   ├── apples_instances_val.json
│   ├── applebs_instances_train.json
│   ├── peaches_instances_train.json
│   ├── pears_instances_train.json
│   └── combined_instances_*.json   # Combined multi-category files
├── scripts/                         # Utility scripts
│   ├── reorganize_dataset.py       # Reorganize dataset to standard structure
│   └── convert_to_coco.py         # Convert CSV to COCO format
├── LICENSE                          # License file
├── README.md                        # This file
└── requirements.txt                # Python dependencies
```

**Splits**: Splits provided via `{category}/sets/*.txt`. List image basenames (no extension). If missing, all images are used.

## Sample Images

<table>
  <tr>
    <th>Category</th>
    <th>Sample</th>
  </tr>
  <tr>
    <td><strong>Apples</strong></td>
    <td>
      <img src="apples/images/IMG_0248.JPG" alt="Apple flower" width="260"/>
      <div align="center"><code>apples/images/IMG_0248.JPG</code></div>
    </td>
  </tr>
  <tr>
    <td><strong>AppleBs</strong></td>
    <td>
      <img src="applebs/images/14.bmp" alt="AppleB flower" width="260"/>
      <div align="center"><code>applebs/images/14.bmp</code></div>
    </td>
  </tr>
  <tr>
    <td><strong>Peaches</strong></td>
    <td>
      <img src="peaches/images/10.bmp" alt="Peach flower" width="260"/>
      <div align="center"><code>peaches/images/10.bmp</code></div>
    </td>
  </tr>
  <tr>
    <td><strong>Pears</strong></td>
    <td>
      <img src="pears/images/1_100.bmp" alt="Pear flower" width="260"/>
      <div align="center"><code>pears/images/1_100.bmp</code></div>
    </td>
  </tr>
</table>

## Annotation Schema

### CSV Format

Each image has a corresponding CSV annotation file in `{category}/csv/{image_name}.csv`:

```csv
#item,x,y,width,height,label
0,153,2346,564,454,1
```

- **Coordinates**: `x, y` - top-left corner of bounding box (pixels)
- **Dimensions**: `width, height` - bounding box dimensions (pixels)
- **Label**: Category ID (1=flower for each category)

### JSON Format (Per-Image)

Each image has a corresponding JSON annotation file in `{category}/json/{image_name}.json`:

```json
{
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
  "images": [
    {
      "id": 8610922705,
      "width": 512,
      "height": 512,
      "file_name": "IMG_0316.JPG",
      "size": 8230748,
      "format": "JPEG",
      "url": "",
      "hash": "",
      "status": "success"
    }
  ],
  "annotations": [
    {
      "id": 1,
      "image_id": 8610922705,
      "category_id": 1,
      "segmentation": [],
      "area": 256056,
      "bbox": [153, 2346, 564, 454]
    }
  ],
  "categories": [
    {
      "id": 1,
      "name": "flower",
      "supercategory": "flower"
    }
  ]
}
```

### COCO Format

COCO format JSON files are generated in the `annotations/` directory. Example structure:

```json
{
  "info": {
    "year": 2025,
    "version": "1.0",
    "description": "Peach-Pear Flower Segmentation apples train split",
    "url": "https://agdatacommons.nal.usda.gov/download/articles/24852636/versions/1/"
  },
  "images": [
    {
      "id": 1234567890,
      "file_name": "apples/images/IMG_0248.JPG",
      "width": 5184,
      "height": 3456
    }
  ],
  "annotations": [
    {
      "id": 1,
      "image_id": 1234567890,
      "category_id": 1,
      "bbox": [153, 2346, 564, 454],
      "area": 256056,
      "iscrowd": 0
    }
  ],
  "categories": [
    {"id": 1, "name": "flower", "supercategory": "flower"}
  ]
}
```

### Label Maps

Label mapping is defined in `{category}/labelmap.json`:

```json
[
  {"object_id": 0, "label_id": 0, "keyboard_shortcut": "0", "object_name": "background"},
  {"object_id": 1, "label_id": 1, "keyboard_shortcut": "1", "object_name": "flower"}
]
```

### Segmentation Masks

Segmentation masks are provided in PNG format in `{category}/segmentations/` directory. White regions indicate flower areas, black regions indicate background.

## Stats and Splits

### Image Statistics

| Category | Train | Val | Total |
|----------|-------|-----|-------|
| Apples | 118 | 29 | 147 |
| AppleBs | 18 | 0 | 18 |
| Peaches | 24 | 0 | 24 |
| Pears | 18 | 0 | 18 |
| **Total** | **178** | **29** | **207** |

### Split Distribution

- **Training set**: ~86% (178 images)
- **Validation set**: ~14% (29 images)

Splits provided via `{category}/sets/*.txt`. You may define your own splits by editing those files.

## Quick Start

### Load COCO Format Annotations

```python
from pycocotools.coco import COCO
import matplotlib.pyplot as plt

# Load COCO annotation file
coco = COCO('annotations/combined_instances_train.json')

# Get all image IDs
img_ids = coco.getImgIds()
print(f"Total images: {len(img_ids)}")

# Get all category IDs
cat_ids = coco.getCatIds()
print(f"Categories: {[coco.loadCats(cat_id)[0]['name'] for cat_id in cat_ids]}")

# Load a specific image and its annotations
img_id = img_ids[0]
img_info = coco.loadImgs(img_id)[0]
ann_ids = coco.getAnnIds(imgIds=img_id)
anns = coco.loadAnns(ann_ids)

print(f"Image: {img_info['file_name']}")
print(f"Annotations: {len(anns)}")
```

### Convert CSV to COCO Format

```bash
# Convert all categories to COCO format
python scripts/convert_to_coco.py --root . --out annotations --combined

# Convert specific categories
python scripts/convert_to_coco.py --root . --out annotations \
    --categories apples peaches --splits train val

# Generate combined files
python scripts/convert_to_coco.py --root . --out annotations --combined
```

### Dependencies

**Required**:
- Python 3.6+
- Pillow>=9.5

**Optional** (for COCO API):
- pycocotools>=2.0.7

Install dependencies:
```bash
pip install -r requirements.txt
```

## Evaluation and Baselines

### Evaluation Metrics

- **Object Detection**: mAP@[.50:.95], mAP@.50, mAP@.75
- **Instance Segmentation**: mAP@[.50:.95] (if segmentation masks are used)

### Baseline Results

Baseline results will be added as they become available.

## Datasheet (Data Card)

### Motivation

This dataset was created to support research in agricultural computer vision, specifically for flower detection and segmentation in peach and pear orchards. The dataset enables the development of automated systems for flower counting, yield estimation, and precision agriculture applications.

### Composition

The dataset consists of:
- **4 flower categories**: Apple variety A, Apple variety B, Peach, and Pear flowers
- **207 high-resolution images** collected from orchards
- **Segmentation masks** indicating flower regions
- **Bounding box annotations** extracted from segmentation masks

### Collection Process

- Images were collected from USDA Ag Data Commons
- Original images were processed and annotated with segmentation masks
- Bounding boxes were automatically extracted from segmentation masks
- Images were organized into categories and splits

### Preprocessing

- Images are provided in original resolution (typically 5184×3456 pixels or larger)
- Some images are in JPG format, others in BMP format
- Segmentation masks are provided in PNG format with white regions indicating flower areas
- JSON annotations were generated for each image with COCO-compatible format

### Distribution

The dataset is distributed via:
- USDA Ag Data Commons: `https://agdatacommons.nal.usda.gov/download/articles/24852636/versions/1/`
- This repository provides standardized structure and conversion scripts

### Maintenance

The dataset is maintained by the community. Issues and contributions are welcome.

## Known Issues and Caveats

1. **Image Formats**: The dataset contains both JPG and BMP format images. Both formats are supported by the conversion scripts.

2. **Segmentation Masks**: Not all images have corresponding segmentation masks. Some categories (AppleBs, Peaches, Pears) have masks for all images, while Apples category has masks for only a subset of images.

3. **Validation Splits**: Some categories (AppleBs, Peaches, Pears) do not have validation splits defined. All images in these categories are currently in the training set.

4. **Bounding Box Format**: Bounding boxes are in `[x, y, width, height]` format, where `(x, y)` is the top-left corner.

5. **Category Naming**: The dataset uses plural forms for category directory names (apples, applebs, peaches, pears) following the standard convention.

## License

This dataset is licensed under the Creative Commons Attribution 4.0 International License (CC BY 4.0).

Check the original dataset terms and cite appropriately.

See `LICENSE` file for full license text.

## Citation

If you use this dataset, please cite:

```bibtex
@dataset{peachpear_flower_segmentation_2025,
  title={Peach-Pear Flower Segmentation Dataset},
  author={USDA Ag Data Commons},
  year={2025},
  url={https://agdatacommons.nal.usda.gov/download/articles/24852636/versions/1/},
  license={CC BY 4.0}
}
```

## Changelog

### V1.0.0 (2025)
- Initial standardized structure and COCO conversion utility
- Reorganized dataset to follow standard directory structure
- Added CSV and JSON annotation formats
- Created conversion scripts for COCO format
- Added comprehensive documentation

## Contact

**Maintainers**: Dataset maintainers

**Original authors**: USDA Ag Data Commons

**Source**: `https://agdatacommons.nal.usda.gov/download/articles/24852636/versions/1/`
