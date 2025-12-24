# Installing Audiveris on macOS

Since you're on macOS (arm64 - Apple Silicon), follow these steps:

## Option 1: Direct Download (RECOMMENDED)

1. **Download Audiveris 5.9.0 for macOS arm64:**

   Visit this URL in your browser:
   ```
   https://github.com/Audiveris/audiveris/releases/tag/5.9.0
   ```

2. **In the Assets section, download:**
   - `Audiveris-5.9.0-arm64.dmg` (for Apple Silicon M1/M2/M3)
   - OR if you have Intel Mac: `Audiveris-5.9.0-x86_64.dmg`

3. **Install:**
   - Open the downloaded `.dmg` file
   - Drag Audiveris to your Applications folder
   - Right-click and select "Open" the first time (to bypass Gatekeeper)

4. **Verify Installation:**
   ```bash
   ls -la /Applications/Audiveris.app
   ```

## Option 2: Command Line Download

Try this direct download command:

```bash
# For Apple Silicon (M1/M2/M3)
cd ~/Downloads
curl -L "https://github.com/Audiveris/audiveris/releases/download/5.9.0/Audiveris-5.9.0-arm64.dmg" -o Audiveris.dmg

# Mount and install
open Audiveris.dmg
# Then drag to Applications folder
```

## Option 3: Build from Source

If the DMG doesn't work, you can build from source:

```bash
# Install prerequisites
brew install git openjdk@17 gradle

# Clone repository
cd ~/Desktop
git clone https://github.com/Audiveris/audiveris.git
cd audiveris

# Build
./gradlew build

# The JAR file will be in: build/libs/Audiveris-5.9.0.jar
```

## After Installation

Once installed, the script will automatically find Audiveris at:
- `/Applications/Audiveris.app/Contents/MacOS/Audiveris`

Or you can specify the path manually:
```bash
python music_symbol_detector.py input.png -a /Applications/Audiveris.app/Contents/MacOS/Audiveris
```

## Quick Test

After installing, test that it works:
```bash
/Applications/Audiveris.app/Contents/MacOS/Audiveris --help
```

## If You Get "Can't Open" Error

macOS may block the app. To fix:
1. Go to System Settings > Privacy & Security
2. Scroll down and click "Open Anyway" next to the Audiveris message
3. Or run: `xattr -cr /Applications/Audiveris.app`
