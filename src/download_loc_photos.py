#!/usr/bin/env python3
"""
Download historical photos from Library of Congress API.
LOC has excellent public domain archival photos and a good API.
"""

import requests
import json
import os
import time
from pathlib import Path
from datetime import datetime

# Create output directories
PHOTOS_DIR = Path("data/photos")
PHOTOS_DIR.mkdir(parents=True, exist_ok=True)

def search_loc_photos(query, num_results=50):
    """
    Search Library of Congress for photos.
    API docs: https://www.loc.gov/apis/json-and-yaml/
    """
    base_url = "https://www.loc.gov/search/"

    params = {
        'q': query,
        'fo': 'json',  # Format: JSON
        'at': 'results,pagination',  # Include results and pagination
        'c': 100,  # Results per page
        'fa': 'original-format:photo|partof:lot',  # Filter for photos
        'st': 'grid'  # Grid view
    }

    print(f"Searching Library of Congress for: '{query}'")

    try:
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        if 'results' not in data:
            print(f"No results found for query: {query}")
            return []

        results = data['results']
        print(f"Found {len(results)} results for '{query}'")

        photos = []
        for item in results[:num_results]:
            # Extract photo metadata
            photo_info = {
                'title': item.get('title', 'Untitled'),
                'url': item.get('image_url', [''])[0] if item.get('image_url') else '',
                'loc_id': item.get('id', ''),
                'date': item.get('date', 'Unknown'),
                'description': item.get('description', [''])[0] if item.get('description') else '',
                'subjects': item.get('subject', []),
                'source': 'Library of Congress',
                'query': query
            }

            # Try to get higher resolution image
            if photo_info['loc_id']:
                # Try to get item details for better image URL
                item_url = f"https://www.loc.gov/item/{photo_info['loc_id'].split('/')[-2]}/?fo=json"
                try:
                    item_response = requests.get(item_url, timeout=10)
                    if item_response.status_code == 200:
                        item_data = item_response.json()
                        if 'item' in item_data and 'image_url' in item_data['item']:
                            photo_info['url'] = item_data['item']['image_url'][0]
                except:
                    pass

            if photo_info['url']:
                photos.append(photo_info)

        return photos

    except requests.exceptions.RequestException as e:
        print(f"Error searching LOC: {e}")
        return []

def download_image(url, filename):
    """Download image from URL to local file."""
    try:
        # LOC doesn't require special headers
        response = requests.get(url, timeout=30, stream=True)
        response.raise_for_status()

        filepath = PHOTOS_DIR / filename
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"✓ Downloaded: {filename}")
        return True

    except Exception as e:
        print(f"✗ Failed to download {filename}: {e}")
        return False

def main():
    """Download diverse historical photos from Library of Congress."""

    # Define search queries for diverse historical content
    queries = [
        "historical photographs 1900s",
        "historical photographs 1920s",
        "historical photographs 1940s",
        "historical photographs 1960s",
        "family portrait photographs historical",
        "street scenes historical photographs",
        "industrial photographs historical",
        "vintage photographs buildings",
    ]

    all_photos = []
    target_count = 30  # Target at least 30 photos

    print("=" * 60)
    print("Downloading Historical Photos from Library of Congress")
    print("=" * 60)
    print()

    for query in queries:
        if len(all_photos) >= target_count:
            break

        photos = search_loc_photos(query, num_results=10)

        for photo in photos:
            if len(all_photos) >= target_count:
                break

            # Generate unique filename
            import hashlib
            photo_hash = hashlib.md5(photo['url'].encode()).hexdigest()[:8]
            filename = f"loc_{photo_hash}.jpg"

            # Download the image
            if download_image(photo['url'], filename):
                photo['local_filename'] = filename
                photo['download_date'] = datetime.now().isoformat()
                all_photos.append(photo)

                # Be nice to the server
                time.sleep(0.5)

        # Pause between queries
        time.sleep(1)

    # Save metadata
    metadata_file = Path("data/metadata_loc.json")
    with open(metadata_file, 'w') as f:
        json.dump(all_photos, f, indent=2)

    print()
    print("=" * 60)
    print(f"Successfully downloaded {len(all_photos)} photos")
    print(f"Metadata saved to: {metadata_file}")
    print(f"Photos saved to: {PHOTOS_DIR}/")
    print("=" * 60)

if __name__ == "__main__":
    main()
