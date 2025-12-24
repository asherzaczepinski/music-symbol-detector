#!/usr/bin/env python3
"""
Test script that demonstrates bounding box drawing without Audiveris.
This uses mock data to show what the final output will look like.
"""

import sys
from PIL import Image, ImageDraw, ImageFont


def test_bounding_boxes(image_path, output_path=None):
    """Test bounding box drawing with mock data."""

    if output_path is None:
        output_path = image_path.replace('.png', '_test_output.png')

    # Open the image
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)

    # Try to load a font
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
    except:
        font = ImageFont.load_default()

    # Mock symbol data (estimated positions from the sheet music)
    # These are example positions - Audiveris will detect the real ones
    mock_symbols = [
        # Format: (type, x, y, width, height, label, color)
        ('notehead', 55, 180, 15, 15, 'o', '#FF00FF'),   # First note
        ('notehead', 95, 175, 15, 15, 'o', '#FF00FF'),   # Second note
        ('notehead', 130, 172, 15, 15, 'o', '#FF00FF'),  # Third note
        ('notehead', 165, 170, 15, 15, 'o', '#FF00FF'),  # Fourth note
        ('notehead', 205, 168, 15, 15, 'o', '#FF00FF'),  # Fifth note
        ('notehead', 230, 168, 15, 15, 'o', '#FF00FF'),  # Sixth note
        ('notehead', 265, 165, 15, 15, 'o', '#FF00FF'),  # Seventh note
        ('notehead', 310, 163, 15, 15, 'o', '#FF00FF'),  # Eighth note
        ('notehead', 340, 163, 15, 15, 'o', '#FF00FF'),  # Ninth note
        ('notehead', 370, 163, 15, 15, 'o', '#FF00FF'),  # Tenth note
        ('notehead', 405, 160, 15, 15, 'o', '#FF00FF'),  # Note with flat
        ('flat', 390, 155, 12, 25, 'b', '#00FF00'),      # Flat sign
        ('notehead', 430, 160, 15, 15, 'o', '#FF00FF'),  # After flat
        ('notehead', 465, 158, 15, 15, 'o', '#FF00FF'),  # Next note
        ('notehead', 520, 153, 15, 15, 'o', '#FF00FF'),  # Higher note
        ('notehead', 540, 153, 15, 15, 'o', '#FF00FF'),  # Next
        ('notehead', 525, 178, 15, 15, 'o', '#FF00FF'),  # Lower note (beam)
    ]

    # Draw bounding boxes
    for symbol in mock_symbols:
        symbol_type, x, y, w, h, label, color = symbol

        # Draw rectangle
        bbox = (x, y, x + w, y + h)
        draw.rectangle(bbox, outline=color, width=2)

        # Draw label
        text_bbox = draw.textbbox((x, y - 25), label, font=font)
        draw.rectangle(text_bbox, fill=color)
        draw.text((x, y - 25), label, fill='white', font=font)

    # Add watermark
    watermark_text = "MOCK DATA - Install Audiveris for real detection"
    watermark_bbox = draw.textbbox((10, 10), watermark_text, font=font)
    draw.rectangle(watermark_bbox, fill='yellow')
    draw.text((10, 10), watermark_text, fill='red', font=font)

    # Save output
    img.save(output_path)

    print(f"Test output saved to: {output_path}")
    print(f"\nThis is MOCK DATA to demonstrate the concept.")
    print(f"Install Audiveris (see INSTALL_AUDIVERIS.md) for real symbol detection.")
    print(f"\nMock symbols drawn: {len(mock_symbols)}")
    print(f"  - Noteheads: {sum(1 for s in mock_symbols if s[0] == 'notehead')}")
    print(f"  - Flats: {sum(1 for s in mock_symbols if s[0] == 'flat')}")
    print(f"  - Sharps: {sum(1 for s in mock_symbols if s[0] == 'sharp')}")
    print(f"  - Naturals: {sum(1 for s in mock_symbols if s[0] == 'natural')}")

    return output_path


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python test_without_audiveris.py <image.png>")
        sys.exit(1)

    test_bounding_boxes(sys.argv[1])
