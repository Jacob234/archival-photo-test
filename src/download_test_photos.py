#!/usr/bin/env python3
"""
Download test photos using multiple fallback methods.
Try direct public domain sources and APIs.
"""

import requests
import json
import os
from pathlib import Path
from datetime import datetime
import time

# Create output directories
PHOTOS_DIR = Path("data/photos")
PHOTOS_DIR.mkdir(parents=True, exist_ok=True)

def download_image(url, filename, description=""):
    """Download image from URL to local file."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30, stream=True)
        response.raise_for_status()

        filepath = PHOTOS_DIR / filename
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        file_size = filepath.stat().st_size
        print(f"✓ Downloaded: {filename} ({file_size:,} bytes)")
        return True

    except Exception as e:
        print(f"✗ Failed to download {filename}: {e}")
        return False

def download_from_picsum(count=30):
    """
    Download random photos from Lorem Picsum (picsum.photos).
    Free service that provides random placeholder images.
    Not historical, but useful for testing vision models.
    """
    photos = []

    print("\n--- Downloading from Lorem Picsum (Random Photos) ---")

    for i in range(count):
        # Use their API to get random photo info
        info_url = f"https://picsum.photos/id/{100 + i * 10}/info"

        try:
            response = requests.get(info_url, timeout=10)
            if response.status_code == 200:
                info = response.json()

                # Download the actual image (medium resolution)
                image_url = info['download_url']
                filename = f"picsum_{info['id']}.jpg"

                if download_image(image_url, filename):
                    photo_data = {
                        'title': f"Photo by {info.get('author', 'Unknown')}",
                        'url': image_url,
                        'width': info.get('width'),
                        'height': info.get('height'),
                        'author': info.get('author', 'Unknown'),
                        'source': 'Lorem Picsum',
                        'local_filename': filename,
                        'download_date': datetime.now().isoformat()
                    }
                    photos.append(photo_data)

                    time.sleep(0.3)  # Be nice to the server
            else:
                # Try next ID
                continue

        except Exception as e:
            print(f"  Error with ID {100 + i * 10}: {e}")
            continue

    return photos

def download_known_public_domain():
    """
    Download specific known public domain images that should work.
    Using direct URLs to confirmed public domain sources.
    """
    photos = []

    print("\n--- Downloading Known Public Domain Images ---")

    # Public domain images from various sources
    public_images = [
        {
            'url': 'https://images.unsplash.com/photo-1506748686214-e9df14d4d9d0',
            'title': 'Landscape Photo',
            'description': 'Test landscape image',
            'params': '?w=1200&h=800&fit=crop'
        },
        {
            'url': 'https://images.pexels.com/photos/4588065/pexels-photo-4588065.jpeg',
            'title': 'Portrait Photo',
            'description': 'Test portrait image',
            'params': '?auto=compress&cs=tinysrgb&w=1200'
        },
        {
            'url': 'https://images.pexels.com/photos/210182/pexels-photo-210182.jpeg',
            'title': 'Street Scene',
            'description': 'Urban street scene',
            'params': '?auto=compress&cs=tinysrgb&w=1200'
        },
        {
            'url': 'https://images.pexels.com/photos/1563356/pexels-photo-1563356.jpeg',
            'title': 'Building Architecture',
            'description': 'Historic building',
            'params': '?auto=compress&cs=tinysrgb&w=1200'
        },
        {
            'url': 'https://images.pexels.com/photos/1181406/pexels-photo-1181406.jpeg',
            'title': 'Group of People',
            'description': 'People gathering',
            'params': '?auto=compress&cs=tinysrgb&w=1200'
        },
    ]

    for idx, img in enumerate(public_images):
        full_url = img['url'] + img.get('params', '')
        filename = f"public_{idx + 1}.jpg"

        if download_image(full_url, filename, img['title']):
            photo_data = {
                'title': img['title'],
                'description': img['description'],
                'url': full_url,
                'source': 'Public Domain Collection',
                'local_filename': filename,
                'download_date': datetime.now().isoformat()
            }
            photos.append(photo_data)
            time.sleep(0.5)

    return photos

def main():
    """Download test photos using multiple methods."""

    print("=" * 60)
    print("Downloading Test Photos for Vision Model Testing")
    print("=" * 60)

    all_photos = []

    # Method 1: Try public domain images first (more reliable)
    public_photos = download_known_public_domain()
    all_photos.extend(public_photos)

    # Method 2: Try Lorem Picsum for additional variety
    if len(all_photos) < 30:
        picsum_photos = download_from_picsum(count=25)
        all_photos.extend(picsum_photos)

    # Save metadata
    metadata_file = Path("data/metadata_test.json")
    with open(metadata_file, 'w') as f:
        json.dump(all_photos, f, indent=2)

    print()
    print("=" * 60)
    print(f"Successfully downloaded {len(all_photos)} photos")
    print(f"Metadata saved to: {metadata_file}")
    print(f"Photos saved to: {PHOTOS_DIR}/")
    print("=" * 60)
    print()

    if len(all_photos) > 0:
        print("You can now test vision models with:")
        print("  python src/test_models.py")
    else:
        print("⚠ No photos were downloaded. Network restrictions may be blocking downloads.")
        print("Try running this script from a different network or manually add photos to data/photos/")

if __name__ == "__main__":
    main()
