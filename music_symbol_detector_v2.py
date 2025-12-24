#!/usr/bin/env python3
"""
Music Symbol Detector using Audiveris V2
This script processes sheet music images (PNG/JPG) and draws bounding boxes
around sharps, flats, naturals, and noteheads.
"""

import os
import sys
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import argparse
import zipfile
import tempfile


class MusicSymbolDetector:
    """Detects and visualizes music symbols using Audiveris."""

    # Symbol types we're interested in
    TARGET_SYMBOLS = {
        'sharp': '#',
        'flat': 'b',
        'natural': 'n',
        'notehead': 'o'
    }

    # Colors for bounding boxes
    COLORS = {
        'sharp': '#FF0000',      # Red
        'flat': '#00FF00',       # Green
        'natural': '#0000FF',    # Blue
        'notehead': '#FF00FF'    # Magenta
    }

    def __init__(self, audiveris_path=None):
        """Initialize the detector."""
        self.audiveris_path = audiveris_path

    def process_image(self, image_path, output_path=None):
        """Process a sheet music image and draw bounding boxes."""
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        if output_path is None:
            output_path = image_path.parent / f"{image_path.stem}_detected{image_path.suffix}"

        print(f"Processing: {image_path}")

        # Step 1: Run Audiveris on the image
        print("Running Audiveris...")
        omr_file = self._run_audiveris(image_path)

        # Step 2: Parse the OMR output
        print("Parsing symbols...")
        symbols = self._parse_omr_file(omr_file)

        # Step 3: Draw bounding boxes
        print("Drawing bounding boxes...")
        self._draw_bounding_boxes(image_path, symbols, output_path)

        print(f"Output saved to: {output_path}")
        print(f"Total symbols detected: {len(symbols)}")
        self._print_summary(symbols)

        return output_path

    def _run_audiveris(self, image_path):
        """Run Audiveris on the image to extract symbols."""
        if not self.audiveris_path:
            raise RuntimeError("Audiveris path not provided")

        output_dir = image_path.parent / "audiveris_output"
        output_dir.mkdir(exist_ok=True)

        # Run Audiveris in batch mode
        cmd = [
            self.audiveris_path,
            '-batch',
            '-export',
            '-output', str(output_dir),
            str(image_path)
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300,
                                  env={**os.environ, 'JAVA_HOME': '/opt/homebrew/opt/openjdk',
                                       'PATH': f'/opt/homebrew/opt/openjdk/bin:{os.environ.get("PATH", "")}'})
            if result.returncode != 0:
                print(f"Audiveris stderr: {result.stderr}")
        except subprocess.TimeoutExpired:
            raise RuntimeError("Audiveris timed out (5 minutes)")

        # Find the output .omr file
        omr_file = output_dir / f"{image_path.stem}.omr"

        if not omr_file.exists():
            raise RuntimeError(f"OMR output not found: {omr_file}")

        return omr_file

    def _parse_omr_file(self, omr_file):
        """Parse Audiveris .omr file (ZIP archive) to extract symbol positions."""
        symbols = []

        try:
            # Extract the .omr file (it's a ZIP)
            with tempfile.TemporaryDirectory() as temp_dir:
                with zipfile.ZipFile(omr_file, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)

                # Find sheet XML files
                temp_path = Path(temp_dir)
                sheet_dirs = list(temp_path.glob('sheet#*'))

                for sheet_dir in sheet_dirs:
                    sheet_xml = sheet_dir / f"{sheet_dir.name}.xml"
                    if sheet_xml.exists():
                        symbols.extend(self._parse_sheet_xml(sheet_xml))

        except Exception as e:
            print(f"Error parsing OMR file: {e}")

        return symbols

    def _parse_sheet_xml(self, sheet_xml):
        """Parse a sheet XML file to extract symbol positions."""
        symbols = []

        try:
            tree = ET.parse(sheet_xml)
            root = tree.getroot()

            # Look for different types of symbols in the <sig><inters> section
            inters = root.find('.//sig/inters')
            if inters is None:
                print("No inters section found in sheet XML")
                return symbols

            # Parse head elements (noteheads)
            for head in inters.findall('.//head'):
                bounds = head.find('bounds')
                if bounds is not None:
                    x = int(bounds.get('x', 0))
                    y = int(bounds.get('y', 0))
                    w = int(bounds.get('w', 20))
                    h = int(bounds.get('h', 20))

                    symbols.append({
                        'type': 'notehead',
                        'bbox': (x, y, x + w, y + h),
                        'shape': head.get('shape', 'NOTEHEAD')
                    })

            # Parse accidentals (sharps, flats, naturals)
            for accidental in inters.findall('.//key-alter'):
                shape = accidental.get('shape', '')
                bounds = accidental.find('bounds')

                if bounds is not None:
                    symbol_type = self._classify_symbol(shape)
                    if symbol_type:
                        x = int(bounds.get('x', 0))
                        y = int(bounds.get('y', 0))
                        w = int(bounds.get('w', 20))
                        h = int(bounds.get('h', 20))

                        symbols.append({
                            'type': symbol_type,
                            'bbox': (x, y, x + w, y + h),
                            'shape': shape
                        })

            # Parse all <inter> elements for accidentals
            for inter in inters.findall('.//inter'):
                shape = inter.get('shape', '')
                if 'SHARP' in shape or 'FLAT' in shape or 'NATURAL' in shape:
                    bounds = inter.find('bounds')
                    if bounds is not None:
                        symbol_type = self._classify_symbol(shape)
                        if symbol_type:
                            x = int(bounds.get('x', 0))
                            y = int(bounds.get('y', 0))
                            w = int(bounds.get('w', 20))
                            h = int(bounds.get('h', 20))

                            symbols.append({
                                'type': symbol_type,
                                'bbox': (x, y, x + w, y + h),
                                'shape': shape
                            })

        except Exception as e:
            print(f"Error parsing sheet XML: {e}")
            import traceback
            traceback.print_exc()

        return symbols

    def _classify_symbol(self, shape):
        """Classify a shape into our target symbol types."""
        shape_lower = shape.lower()

        if 'sharp' in shape_lower:
            return 'sharp'
        elif 'flat' in shape_lower:
            return 'flat'
        elif 'natural' in shape_lower:
            return 'natural'
        elif 'notehead' in shape_lower or 'head' in shape_lower:
            return 'notehead'

        return None

    def _draw_bounding_boxes(self, image_path, symbols, output_path):
        """Draw bounding boxes on the image."""
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)

        # Try to load a font
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
            small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
        except:
            font = ImageFont.load_default()
            small_font = font

        # Draw bounding boxes
        for symbol in symbols:
            symbol_type = symbol['type']
            if symbol_type not in self.TARGET_SYMBOLS:
                continue

            bbox = symbol.get('bbox')
            if not bbox:
                continue

            color = self.COLORS.get(symbol_type, '#FFFFFF')

            # Draw rectangle
            draw.rectangle(bbox, outline=color, width=3)

            # Draw label
            label = self.TARGET_SYMBOLS[symbol_type]
            text_y = max(bbox[1] - 30, 0)
            text_bbox = draw.textbbox((bbox[0], text_y), label, font=font)
            draw.rectangle(text_bbox, fill=color)
            draw.text((bbox[0], text_y), label, fill='white', font=font)

        # Add info banner
        info_text = f"Detected: {len(symbols)} symbols"
        info_bbox = draw.textbbox((10, 10), info_text, font=small_font)
        draw.rectangle(info_bbox, fill='yellow')
        draw.text((10, 10), info_text, fill='black', font=small_font)

        # Save output
        img.save(output_path)

    def _print_summary(self, symbols):
        """Print summary of detected symbols."""
        counts = {}
        for symbol in symbols:
            symbol_type = symbol['type']
            counts[symbol_type] = counts.get(symbol_type, 0) + 1

        print("\nDetected symbols:")
        for symbol_type, count in sorted(counts.items()):
            label = self.TARGET_SYMBOLS.get(symbol_type, symbol_type)
            color = self.COLORS.get(symbol_type, '#FFFFFF')
            print(f"  {symbol_type} ({label}): {count} [{color}]")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Detect and visualize music symbols in sheet music images'
    )
    parser.add_argument(
        'image',
        help='Path to input image (PNG or JPG)'
    )
    parser.add_argument(
        '-o', '--output',
        help='Path to output image (optional)'
    )
    parser.add_argument(
        '-a', '--audiveris',
        required=True,
        help='Path to Audiveris executable'
    )

    args = parser.parse_args()

    try:
        detector = MusicSymbolDetector(audiveris_path=args.audiveris)
        detector.process_image(args.image, args.output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
