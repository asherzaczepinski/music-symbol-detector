#!/usr/bin/env python3
"""
Upscale image and process with Audiveris
"""

import sys
from PIL import Image

def upscale_image(input_path, output_path, scale_factor=4):
    """Upscale image for better Audiveris processing."""
    img = Image.open(input_path)
    print(f"Original size: {img.size}")

    new_size = (img.width * scale_factor, img.height * scale_factor)
    img_upscaled = img.resize(new_size, Image.Resampling.LANCZOS)

    print(f"New size: {img_upscaled.size}")
    img_upscaled.save(output_path, dpi=(300, 300))
    print(f"Saved to: {output_path}")

    return output_path

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python upscale_and_process.py input.png output.png [scale_factor]")
        sys.exit(1)

    scale = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    upscale_image(sys.argv[1], sys.argv[2], scale)
