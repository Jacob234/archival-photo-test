"""
Wikimedia Commons photo downloader for historical/archival images.

This module handles downloading historical photos from Wikimedia Commons for
vision model testing. It focuses on 20th century American photographs from
1920s-1980s, including portraits, street scenes, buildings, events, and work scenes.

Main functionality:
- Downloads photos from predefined Wikimedia categories
- Extracts metadata (title, date, description, license)
- Classifies photos by type (portrait, street, building, event, work)
- Filters for quality (minimum width requirement)
- Saves organized metadata for later analysis

Example:
    Basic usage to download 50 photos:

    >>> from src.download_photos import WikimediaDownloader
    >>> downloader = WikimediaDownloader()
    >>> downloader.download_from_categories(target_count=50)
"""

import os
import json
import time
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from urllib.parse import unquote
from tqdm import tqdm
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO

from utils import (
    setup_logging,
    save_json,
    load_json,
    generate_photo_id,
    sanitize_filename,
    get_decade_from_year,
    ensure_directory
)

class WikimediaDownloader:
    """Downloads historical photos from Wikimedia Commons.

    This class handles the complete workflow of downloading historical photos:
    1. Queries Wikimedia Commons API for photos in target categories
    2. Downloads images that meet quality requirements (min width)
    3. Extracts and stores metadata (title, date, description, license)
    4. Classifies photos by type and balances distribution
    5. Saves everything organized for vision model testing

    Attributes:
        BASE_URL: Wikimedia Commons API endpoint
        USER_AGENT: User agent string for API requests
        CATEGORIES: List of target photo categories (1920s-1980s)
        PHOTO_TYPES: Classification keywords for photo types
    """

    BASE_URL = "https://commons.wikimedia.org/w/api.php"
    USER_AGENT = "ArchivalPhotoTest/1.0 (https://github.com/username/project; contact@email.com)"

    # Target categories for historical town photography
    CATEGORIES = [
        "Category:1920s photographs of the United States",
        "Category:1930s photographs of the United States",
        "Category:1940s photographs of the United States",
        "Category:1950s photographs of the United States",
        "Category:1960s photographs of the United States",
        "Category:1970s photographs of the United States",
        "Category:1980s photographs of the United States",
        "Category:20th-century portrait photographs",
        "Category:Historical photographs of people",
        "Category:Black and white photographs by decade",
    ]

    # Photo type classification keywords
    PHOTO_TYPES = {
        "portrait": ["portrait", "person", "people", "man", "woman", "child", "family"],
        "street": ["street", "road", "avenue", "main street", "downtown", "city", "town"],
        "building": ["building", "house", "store", "shop", "church", "school"],
        "event": ["event", "gathering", "celebration", "parade", "festival", "meeting"],
        "work": ["work", "worker", "industrial", "factory", "labor", "occupation", "job"],
    }

    def __init__(self, output_dir: str = "data/photos", metadata_file: str = "data/metadata.json"):
        """
        Initialize downloader.

        Args:
            output_dir: Directory to save downloaded photos
            metadata_file: Path to metadata JSON file
        """
        self.output_dir = output_dir
        self.metadata_file = metadata_file
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.USER_AGENT})
        self.logger = setup_logging()
        self.metadata = []

        ensure_directory(self.output_dir)

    def get_category_members(self, category: str, limit: int = 50) -> List[str]:
        """
        Get file members from a Wikimedia category.

        Args:
            category: Category name
            limit: Maximum number of files to retrieve

        Returns:
            List of file titles
        """
        params = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": category,
            "cmtype": "file",
            "cmlimit": limit,
            "format": "json"
        }

        try:
            response = self.session.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()

            files = []
            for member in data.get("query", {}).get("categorymembers", []):
                if member["title"].startswith("File:"):
                    files.append(member["title"])

            return files

        except Exception as e:
            self.logger.error(f"Error fetching category {category}: {e}")
            return []

    def get_image_info(self, file_title: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about an image file.

        Args:
            file_title: Wikimedia file title (e.g., "File:Example.jpg")

        Returns:
            Dictionary with image metadata or None
        """
        params = {
            "action": "query",
            "titles": file_title,
            "prop": "imageinfo",
            "iiprop": "timestamp|user|url|size|mime|extmetadata",
            "format": "json"
        }

        try:
            response = self.session.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()

            pages = data.get("query", {}).get("pages", {})
            for page_id, page_data in pages.items():
                if "imageinfo" in page_data:
                    return page_data["imageinfo"][0]

            return None

        except Exception as e:
            self.logger.error(f"Error fetching info for {file_title}: {e}")
            return None

    def classify_photo_type(self, title: str, description: str = "") -> str:
        """
        Classify photo type based on title and description.

        Args:
            title: File title
            description: File description

        Returns:
            Photo type category
        """
        combined_text = f"{title} {description}".lower()

        for photo_type, keywords in self.PHOTO_TYPES.items():
            for keyword in keywords:
                if keyword in combined_text:
                    return photo_type

        return "miscellaneous"

    def download_image(self, url: str, filename: str, min_width: int = 500) -> bool:
        """
        Download image from URL with size validation.

        Args:
            url: Image URL
            filename: Local filename to save
            min_width: Minimum width requirement

        Returns:
            True if successful, False otherwise
        """
        try:
            response = self.session.get(url, stream=True)
            response.raise_for_status()

            # Check image dimensions
            img = Image.open(BytesIO(response.content))
            width, height = img.size

            if width < min_width:
                self.logger.info(f"Skipping {filename}: width {width}px < {min_width}px")
                return False

            # Save image
            filepath = os.path.join(self.output_dir, filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)

            return True

        except Exception as e:
            self.logger.error(f"Error downloading {url}: {e}")
            return False

    def extract_metadata(self, file_title: str, image_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and format metadata from image info.

        Args:
            file_title: Wikimedia file title
            image_info: Raw image info from API

        Returns:
            Formatted metadata dictionary
        """
        extmetadata = image_info.get("extmetadata", {})

        # Extract basic metadata
        metadata = {
            "wikimedia_title": file_title,
            "url": image_info.get("url", ""),
            "timestamp": image_info.get("timestamp", ""),
            "user": image_info.get("user", "Unknown"),
            "width": image_info.get("width", 0),
            "height": image_info.get("height", 0),
            "size": image_info.get("size", 0),
            "mime": image_info.get("mime", ""),
        }

        # Extract extended metadata
        if "ImageDescription" in extmetadata:
            metadata["description"] = extmetadata["ImageDescription"].get("value", "")

        if "DateTimeOriginal" in extmetadata:
            metadata["date_taken"] = extmetadata["DateTimeOriginal"].get("value", "")
        elif "DateTime" in extmetadata:
            metadata["date_taken"] = extmetadata["DateTime"].get("value", "")
        else:
            metadata["date_taken"] = "Unknown"

        if "License" in extmetadata:
            metadata["license"] = extmetadata["License"].get("value", "")

        if "Artist" in extmetadata:
            metadata["author"] = extmetadata["Artist"].get("value", metadata["user"])

        if "Categories" in extmetadata:
            metadata["categories"] = extmetadata["Categories"].get("value", "").split("|")

        # Derive decade
        metadata["decade"] = get_decade_from_year(metadata.get("date_taken", ""))

        # Classify photo type
        metadata["photo_type"] = self.classify_photo_type(
            file_title,
            metadata.get("description", "")
        )

        # Add download timestamp
        metadata["download_date"] = datetime.now().isoformat()

        return metadata

    def download_from_categories(self, target_count: int = 50) -> None:
        """
        Download photos from all configured categories.

        Args:
            target_count: Total number of photos to download
        """
        photos_per_category = max(1, target_count // len(self.CATEGORIES))
        all_files = []

        self.logger.info(f"Collecting files from {len(self.CATEGORIES)} categories...")

        # Collect files from each category
        for category in self.CATEGORIES:
            self.logger.info(f"Fetching from {category}...")
            files = self.get_category_members(category, limit=photos_per_category * 2)
            all_files.extend([(f, category) for f in files])
            time.sleep(1)  # Rate limiting

        # Shuffle to get diversity
        import random
        random.shuffle(all_files)

        # Download photos
        downloaded = 0
        photo_types_count = {pt: 0 for pt in self.PHOTO_TYPES.keys()}
        photo_types_count["miscellaneous"] = 0

        pbar = tqdm(total=target_count, desc="Downloading photos")

        for file_title, source_category in all_files:
            if downloaded >= target_count:
                break

            # Get image info
            image_info = self.get_image_info(file_title)
            if not image_info:
                continue

            # Extract metadata
            metadata = self.extract_metadata(file_title, image_info)
            metadata["source_category"] = source_category

            # Balance photo types
            photo_type = metadata["photo_type"]
            max_per_type = target_count // 5 + 2  # Allow some flexibility
            if photo_types_count[photo_type] >= max_per_type:
                continue

            # Generate filename
            photo_id = generate_photo_id(metadata["url"])
            extension = os.path.splitext(metadata["url"])[1] or ".jpg"
            filename = f"photo_{photo_id}{extension}"
            metadata["local_filename"] = filename

            # Download image
            if self.download_image(metadata["url"], filename):
                self.metadata.append(metadata)
                photo_types_count[photo_type] += 1
                downloaded += 1
                pbar.update(1)

                self.logger.info(
                    f"Downloaded {filename} ({photo_type}, {metadata['decade']})"
                )

            # Rate limiting
            time.sleep(1)

        pbar.close()

        # Save metadata
        self.save_metadata()

        # Print summary
        self.logger.info(f"\nDownload complete: {downloaded} photos")
        self.logger.info("Photo type distribution:")
        for ptype, count in photo_types_count.items():
            if count > 0:
                self.logger.info(f"  {ptype}: {count}")

    def save_metadata(self) -> None:
        """Save metadata to JSON file."""
        save_json(self.metadata, self.metadata_file)
        self.logger.info(f"Metadata saved to {self.metadata_file}")

def main():
    """Main function to run the downloader."""
    downloader = WikimediaDownloader()
    downloader.download_from_categories(target_count=50)

if __name__ == "__main__":
    main()