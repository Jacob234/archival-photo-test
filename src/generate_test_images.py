#!/usr/bin/env python3
"""
Generate synthetic test images for vision model testing.
Since external downloads are blocked, we'll create test images locally.
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import json
from pathlib import Path
from datetime import datetime
import random

# Create output directories
PHOTOS_DIR = Path("data/photos")
PHOTOS_DIR.mkdir(parents=True, exist_ok=True)

def create_test_image(filename, width=800, height=600, image_type="landscape"):
    """Create a synthetic test image with various elements."""

    # Create base image with gradient background
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)

    if image_type == "landscape":
        # Sky-like gradient (blue to lighter blue)
        for y in range(height // 2):
            color = (100 + y // 4, 150 + y // 4, 200 + y // 4)
            draw.rectangle([(0, y), (width, y + 1)], fill=color)
        # Ground (green to brown)
        for y in range(height // 2, height):
            offset = y - height // 2
            color = (100 - offset // 10, 150 - offset // 8, 50 - offset // 20)
            draw.rectangle([(0, y), (width, y + 1)], fill=color)

        # Add simple shapes (trees, buildings)
        # Tree 1
        draw.ellipse([100, 250, 180, 350], fill=(34, 139, 34))
        draw.rectangle([130, 350, 150, 450], fill=(101, 67, 33))

        # Tree 2
        draw.ellipse([250, 230, 350, 350], fill=(34, 139, 34))
        draw.rectangle([290, 350, 310, 450], fill=(101, 67, 33))

        # Building
        draw.rectangle([500, 200, 650, 450], fill=(150, 150, 150))
        # Windows
        for wx in range(520, 640, 30):
            for wy in range(230, 420, 40):
                draw.rectangle([wx, wy, wx + 20, wy + 25], fill=(255, 255, 200))

    elif image_type == "portrait":
        # Solid background
        draw.rectangle([(0, 0), (width, height)], fill=(180, 160, 140))

        # Simple face (circle for head, features)
        center_x, center_y = width // 2, height // 2 - 50
        head_radius = 120

        # Head
        draw.ellipse([center_x - head_radius, center_y - head_radius,
                     center_x + head_radius, center_y + head_radius],
                    fill=(255, 220, 177), outline=(0, 0, 0), width=3)

        # Eyes
        draw.ellipse([center_x - 50, center_y - 30, center_x - 20, center_y - 10],
                    fill=(255, 255, 255), outline=(0, 0, 0), width=2)
        draw.ellipse([center_x + 20, center_y - 30, center_x + 50, center_y - 10],
                    fill=(255, 255, 255), outline=(0, 0, 0), width=2)

        # Pupils
        draw.ellipse([center_x - 40, center_y - 25, center_x - 30, center_y - 15],
                    fill=(0, 0, 0))
        draw.ellipse([center_x + 30, center_y - 25, center_x + 40, center_y - 15],
                    fill=(0, 0, 0))

        # Nose
        draw.line([center_x, center_y - 10, center_x, center_y + 20],
                 fill=(0, 0, 0), width=2)

        # Mouth (smile)
        draw.arc([center_x - 40, center_y + 10, center_x + 40, center_y + 60],
                start=0, end=180, fill=(0, 0, 0), width=3)

    elif image_type == "building":
        # Sky
        draw.rectangle([(0, 0), (width, height // 2)], fill=(135, 206, 235))
        # Ground
        draw.rectangle([(0, height // 2), (width, height)], fill=(169, 169, 169))

        # Main building
        draw.rectangle([200, 150, 600, 500], fill=(180, 180, 180), outline=(0, 0, 0), width=3)

        # Roof
        draw.polygon([(180, 150), (400, 50), (620, 150)], fill=(139, 69, 19))

        # Door
        draw.rectangle([350, 380, 450, 500], fill=(101, 67, 33), outline=(0, 0, 0), width=2)

        # Windows (grid)
        for wx in range(240, 560, 80):
            for wy in range(200, 350, 70):
                draw.rectangle([wx, wy, wx + 50, wy + 50], fill=(173, 216, 230), outline=(0, 0, 0), width=2)

    elif image_type == "street":
        # Sky
        draw.rectangle([(0, 0), (width, height // 3)], fill=(135, 206, 250))
        # Buildings
        colors = [(180, 180, 180), (160, 160, 160), (200, 200, 200)]
        for i, bx in enumerate(range(0, width, width // 5)):
            building_height = random.randint(150, 300)
            draw.rectangle([bx, height // 3, bx + width // 5, height // 3 + building_height],
                          fill=colors[i % 3], outline=(0, 0, 0), width=2)
            # Windows
            for wx in range(bx + 10, bx + width // 5 - 30, 25):
                for wy in range(height // 3 + 20, height // 3 + building_height - 20, 30):
                    draw.rectangle([wx, wy, wx + 15, wy + 20], fill=(255, 255, 200))

        # Road
        draw.rectangle([(0, height // 3 + 300), (width, height)], fill=(60, 60, 60))
        # Road lines
        for lx in range(50, width, 100):
            draw.rectangle([lx, height // 2 + 250, lx + 40, height // 2 + 260], fill=(255, 255, 255))

    elif image_type == "group":
        # Background (indoor setting)
        draw.rectangle([(0, 0), (width, height)], fill=(210, 180, 140))

        # Multiple simple figures
        positions = [(150, 200), (350, 250), (550, 220)]
        for px, py in positions:
            # Head
            draw.ellipse([px - 40, py - 40, px + 40, py + 40],
                        fill=(255, 220, 177), outline=(0, 0, 0), width=2)
            # Body (rectangle)
            draw.rectangle([px - 50, py + 40, px + 50, py + 150],
                          fill=(random.choice([(100, 100, 200), (200, 100, 100), (100, 200, 100)])),
                          outline=(0, 0, 0), width=2)

    # Add subtle noise/texture
    img = img.filter(ImageFilter.SMOOTH)

    # Save image
    filepath = PHOTOS_DIR / filename
    img.save(filepath, 'JPEG', quality=85)

    return filepath

def main():
    """Generate synthetic test images."""

    print("=" * 60)
    print("Generating Synthetic Test Images")
    print("=" * 60)
    print()

    # Define test images to create
    test_images = [
        ("landscape_1.jpg", "landscape", "Rural landscape with trees and building"),
        ("landscape_2.jpg", "landscape", "Countryside scene"),
        ("landscape_3.jpg", "landscape", "Outdoor scenery"),
        ("portrait_1.jpg", "portrait", "Simple portrait of a person"),
        ("portrait_2.jpg", "portrait", "Person facing forward"),
        ("portrait_3.jpg", "portrait", "Individual portrait"),
        ("building_1.jpg", "building", "Historic-style building with windows"),
        ("building_2.jpg", "building", "Architectural structure"),
        ("building_3.jpg", "building", "Building facade"),
        ("street_1.jpg", "street", "Urban street scene with buildings"),
        ("street_2.jpg", "street", "City street view"),
        ("street_3.jpg", "street", "Street with multiple buildings"),
        ("group_1.jpg", "group", "Group of people gathering"),
        ("group_2.jpg", "group", "Multiple people together"),
        ("group_3.jpg", "group", "Social gathering scene"),
    ]

    photos = []

    for filename, img_type, description in test_images:
        print(f"Creating {filename}...")

        try:
            filepath = create_test_image(filename, image_type=img_type)

            photo_data = {
                'title': filename.replace('_', ' ').replace('.jpg', '').title(),
                'description': description,
                'type': img_type,
                'local_filename': filename,
                'source': 'Synthetic Test Image',
                'width': 800,
                'height': 600,
                'generation_date': datetime.now().isoformat()
            }
            photos.append(photo_data)
            print(f"✓ Created: {filename}")

        except Exception as e:
            print(f"✗ Failed to create {filename}: {e}")

    # Save metadata
    metadata_file = Path("data/metadata_synthetic.json")
    with open(metadata_file, 'w') as f:
        json.dump(photos, f, indent=2)

    print()
    print("=" * 60)
    print(f"Successfully created {len(photos)} synthetic test images")
    print(f"Metadata saved to: {metadata_file}")
    print(f"Images saved to: {PHOTOS_DIR}/")
    print("=" * 60)
    print()
    print("These synthetic images can be used to test the vision models:")
    print("  python src/test_models.py")
    print()
    print("Note: While not real historical photos, these will allow you to:")
    print("  - Test that all vision model APIs are working")
    print("  - Compare model response styles and detail levels")
    print("  - Verify the testing pipeline end-to-end")
    print("  - When real photos are available, simply replace these")

if __name__ == "__main__":
    main()
