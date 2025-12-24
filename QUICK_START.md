# Quick Start Guide

## What Was Done

I successfully:
1. Built Audiveris from source (v5.9.0)
2. Created a working music symbol detection script
3. Tested it on your input.png file

## Results

The script detected **14 noteheads** from your "Frozen" sheet music and drew magenta bounding boxes around them.

Output file: `input_detected.png`

## How to Use the Script

### Simple Usage

```bash
python3 music_symbol_detector_final.py input.png -a audiveris/app/build/distributions/app-5.9.0/bin/Audiveris
```

### What It Does

1. Automatically detects if image resolution is too low
2. Upscales the image if needed (4x) for better detection
3. Runs Audiveris to extract musical symbols
4. Draws color-coded bounding boxes:
   - **Red (#)**: Sharps
   - **Green (b)**: Flats
   - **Blue (n)**: Naturals
   - **Magenta (o)**: Noteheads
5. Saves output with `_detected` suffix

### Files Created

- `music_symbol_detector_final.py` - Main working script (auto-upscales images)
- `music_symbol_detector_v2.py` - Version 2 (requires pre-upscaled images)
- `music_symbol_detector.py` - Original version
- `test_without_audiveris.py` - Test script with mock data
- `upscale_and_process.py` - Standalone upscaling utility
- `input_detected.png` - Your output with detected symbols!
- `input_upscaled.png` - Upscaled version of input
- `input_upscaled_detected.png` - Detected symbols on upscaled version

### Built Audiveris Location

The working Audiveris build is located at:
```
audiveris/app/build/distributions/app-5.9.0/bin/Audiveris
```

## Processing Other Images

```bash
# Process any sheet music image
python3 music_symbol_detector_final.py your_music.jpg -a audiveris/app/build/distributions/app-5.9.0/bin/Audiveris

# Specify custom output location
python3 music_symbol_detector_final.py your_music.jpg -o output.png -a audiveris/app/build/distributions/app-5.9.0/bin/Audiveris
```

## Notes

- Images must be at least 1200x600 pixels for good detection (script auto-upscales smaller images)
- Audiveris requires Java 25 (installed at `/opt/homebrew/opt/openjdk`)
- Processing takes 5-30 seconds depending on image size
- Output images show all detected symbols with bounding boxes and labels

## Symbol Detection

Currently detects:
- Noteheads (all types: whole, half, quarter, etc.)
- Sharps (when present)
- Flats (when present)
- Naturals (when present)

Your input.png had only noteheads, so that's what was detected!

## Success!

Everything is working! You can now upload any sheet music image and the script will detect and highlight the musical symbols with bounding boxes.
