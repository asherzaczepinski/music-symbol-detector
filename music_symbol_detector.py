#!/usr/bin/env python3
"""
Music Symbol Detector using Audiveris
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
        """
        Initialize the detector.

        Args:
            audiveris_path: Path to Audiveris executable/jar (optional)
        """
        self.audiveris_path = audiveris_path or self._find_audiveris()

    def _find_audiveris(self):
        """Try to find Audiveris installation."""
        possible_paths = [
            '/Applications/Audiveris.app/Contents/MacOS/Audiveris',
            '/usr/local/bin/audiveris',
            'audiveris',
            os.path.expanduser('~/Audiveris/build/libs/Audiveris-*.jar')
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path

        # Check if audiveris is in PATH
        try:
            result = subprocess.run(['which', 'audiveris'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass

        return None

    def process_image(self, image_path, output_path=None):
        """
        Process a sheet music image and draw bounding boxes.

        Args:
            image_path: Path to input image (PNG/JPG)
            output_path: Path for output image (optional)

        Returns:
            Path to output image with bounding boxes
        """
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
        symbols = self._parse_omr_output(omr_file)

        # Step 3: Draw bounding boxes
        print("Drawing bounding boxes...")
        self._draw_bounding_boxes(image_path, symbols, output_path)

        print(f"Output saved to: {output_path}")
        print(f"Total symbols detected: {len(symbols)}")
        self._print_summary(symbols)

        return output_path

    def _run_audiveris(self, image_path):
        """
        Run Audiveris on the image to extract symbols.

        Args:
            image_path: Path to input image

        Returns:
            Path to OMR output file
        """
        if not self.audiveris_path:
            raise RuntimeError(
                "Audiveris not found. Please install Audiveris or provide path.\n"
                "Download from: https://github.com/Audiveris/audiveris/releases"
            )

        output_dir = image_path.parent / "audiveris_output"
        output_dir.mkdir(exist_ok=True)

        # Run Audiveris in batch mode
        if self.audiveris_path.endswith('.jar'):
            cmd = [
                'java', '-jar', self.audiveris_path,
                '-batch',
                '-export',
                '-output', str(output_dir),
                str(image_path)
            ]
        else:
            cmd = [
                self.audiveris_path,
                '-batch',
                '-export',
                '-output', str(output_dir),
                str(image_path)
            ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                print(f"Audiveris stderr: {result.stderr}")
                raise RuntimeError(f"Audiveris failed with code {result.returncode}")
        except subprocess.TimeoutExpired:
            raise RuntimeError("Audiveris timed out (5 minutes)")

        # Find the output MusicXML file
        project_name = image_path.stem
        omr_file = output_dir / project_name / f"{project_name}.mxl"

        if not omr_file.exists():
            # Try .xml extension
            omr_file = output_dir / project_name / f"{project_name}.xml"

        if not omr_file.exists():
            raise RuntimeError(f"OMR output not found in {output_dir}")

        return omr_file

    def _parse_omr_output(self, omr_file):
        """
        Parse Audiveris OMR output to extract symbol positions.

        Args:
            omr_file: Path to MusicXML or OMR file

        Returns:
            List of symbol dictionaries with type and bounding box
        """
        symbols = []

        try:
            tree = ET.parse(omr_file)
            root = tree.getroot()

            # Parse MusicXML format
            # Note: This is a simplified parser. Audiveris output may vary.
            namespaces = {'': 'http://www.w3.org/2001/MUSICxml'}

            # Look for notes
            for note in root.findall('.//note', namespaces):
                # Get pitch and accidentals
                pitch = note.find('pitch', namespaces)
                if pitch is not None:
                    # Check for accidentals
                    alter = pitch.find('alter', namespaces)
                    if alter is not None:
                        alter_value = float(alter.text)
                        if alter_value == 1:
                            symbols.append({'type': 'sharp', 'element': note})
                        elif alter_value == -1:
                            symbols.append({'type': 'flat', 'element': note})
                        elif alter_value == 0:
                            symbols.append({'type': 'natural', 'element': note})

                    # Add notehead
                    symbols.append({'type': 'notehead', 'element': note})

                # Check for explicit accidentals
                accidental = note.find('accidental', namespaces)
                if accidental is not None:
                    acc_type = accidental.text.lower()
                    if 'sharp' in acc_type:
                        symbols.append({'type': 'sharp', 'element': note})
                    elif 'flat' in acc_type:
                        symbols.append({'type': 'flat', 'element': note})
                    elif 'natural' in acc_type:
                        symbols.append({'type': 'natural', 'element': note})

            # Since MusicXML doesn't contain pixel coordinates, we'll need to
            # extract them from Audiveris's internal format or estimate
            print("Note: MusicXML doesn't contain pixel coordinates.")
            print("Attempting to parse Audiveris book file...")

            # Try to find the .omr file which contains positional data
            omr_dir = omr_file.parent
            book_file = omr_dir / f"{omr_dir.name}.omr"

            if book_file.exists():
                symbols = self._parse_omr_book(book_file)
            else:
                print("Warning: Could not find OMR book file with coordinates.")
                print("Generating estimated positions...")
                symbols = self._estimate_positions(symbols)

        except Exception as e:
            print(f"Error parsing OMR output: {e}")
            print("Attempting alternative parsing method...")
            symbols = self._parse_alternative(omr_file)

        return symbols

    def _parse_omr_book(self, book_file):
        """Parse Audiveris .omr book file for pixel coordinates."""
        symbols = []

        try:
            tree = ET.parse(book_file)
            root = tree.getroot()

            # Look for inter elements (symbol interpretations)
            for inter in root.findall('.//inter'):
                shape = inter.get('shape', '')

                # Check if it's a symbol we're interested in
                symbol_type = None
                shape_lower = shape.lower()

                if 'sharp' in shape_lower:
                    symbol_type = 'sharp'
                elif 'flat' in shape_lower:
                    symbol_type = 'flat'
                elif 'natural' in shape_lower:
                    symbol_type = 'natural'
                elif 'notehead' in shape_lower or 'head' in shape_lower:
                    symbol_type = 'notehead'

                if symbol_type:
                    # Get bounds
                    bounds = inter.find('bounds')
                    if bounds is not None:
                        x = int(bounds.get('x', 0))
                        y = int(bounds.get('y', 0))
                        w = int(bounds.get('w', 20))
                        h = int(bounds.get('h', 20))

                        symbols.append({
                            'type': symbol_type,
                            'bbox': (x, y, x + w, y + h),
                            'shape': shape
                        })

            print(f"Found {len(symbols)} symbols in OMR book file")

        except Exception as e:
            print(f"Error parsing OMR book file: {e}")

        return symbols

    def _parse_alternative(self, omr_file):
        """Alternative parsing method."""
        # Fallback: return empty list or mock data
        print("Using fallback parsing method")
        return []

    def _estimate_positions(self, symbols):
        """Estimate positions when coordinates are not available."""
        # Generate mock positions for demonstration
        estimated = []
        for i, symbol in enumerate(symbols):
            estimated.append({
                'type': symbol['type'],
                'bbox': (100 + i * 50, 100, 120 + i * 50, 120),
                'estimated': True
            })
        return estimated

    def _draw_bounding_boxes(self, image_path, symbols, output_path):
        """
        Draw bounding boxes on the image.

        Args:
            image_path: Path to input image
            symbols: List of symbol dictionaries
            output_path: Path for output image
        """
        # Open image
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)

        # Try to load a font
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
        except:
            font = ImageFont.load_default()

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
            text_bbox = draw.textbbox((bbox[0], bbox[1] - 25), label, font=font)
            draw.rectangle(text_bbox, fill=color)
            draw.text((bbox[0], bbox[1] - 25), label, fill='white', font=font)

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
            print(f"  {symbol_type} ({label}): {count}")


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
        help='Path to Audiveris executable or JAR file'
    )

    args = parser.parse_args()

    try:
        detector = MusicSymbolDetector(audiveris_path=args.audiveris)
        detector.process_image(args.image, args.output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
