#!/usr/bin/env python3
"""
Download images from existing metadata file.
Since Wikimedia API is blocking requests, we'll download directly from the URLs in metadata.
"""

import json
import requests
import time
from pathlib import Path
from tqdm import tqdm

def download_images_from_metadata(metadata_file="data/metadata.json", output_dir="data/photos"):
    """Download images using URLs from metadata file."""

    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Load metadata
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)

    print(f"Found {len(metadata)} photos in metadata")

    # Download each photo
    downloaded = 0
    skipped = 0
    failed = 0

    for photo in tqdm(metadata, desc="Downloading photos"):
        url = photo.get('url')
        filename = photo.get('local_filename')

        if not url or not filename:
            skipped += 1
            continue

        output_path = Path(output_dir) / filename

        # Skip if already exists
        if output_path.exists():
            downloaded += 1
            continue

        try:
            # Download with a user agent
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            # Save image
            with open(output_path, 'wb') as f:
                f.write(response.content)

            downloaded += 1
            time.sleep(0.5)  # Be nice to the server

        except Exception as e:
            print(f"\n⚠️  Failed to download {filename}: {e}")
            failed += 1
            time.sleep(1)

    print(f"\n✅ Download complete!")
    print(f"   Downloaded: {downloaded}")
    print(f"   Skipped: {skipped}")
    print(f"   Failed: {failed}")

    return downloaded

if __name__ == "__main__":
    download_images_from_metadata()
