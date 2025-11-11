#!/usr/bin/env python3
"""Download popular fonts for subtitle styling."""

import os
import sys
import requests
import zipfile
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

FONTS_DIR = project_root / "fonts"
FONTS_DIR.mkdir(exist_ok=True)

# Popular fonts for video subtitles
FONT_URLS = {
    # Google Fonts - free and high quality
    "Montserrat": "https://fonts.google.com/download?family=Montserrat",
    "Roboto": "https://fonts.google.com/download?family=Roboto", 
    "Open Sans": "https://fonts.google.com/download?family=Open%20Sans",
    "Inter": "https://fonts.google.com/download?family=Inter",
    "Source Sans Pro": "https://fonts.google.com/download?family=Source%20Sans%20Pro",
    "Playfair Display": "https://fonts.google.com/download?family=Playfair%20Display",
    "Bebas Neue": "https://fonts.google.com/download?family=Bebas%20Neue",
    "Orbitron": "https://fonts.google.com/download?family=Orbitron",
}

def download_font(name: str, url: str):
    """Download and extract a font family."""
    print(f"Downloading {name}...")
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        zip_path = FONTS_DIR / f"{name.replace(' ', '_')}.zip"
        
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Extract fonts
        font_dir = FONTS_DIR / name.replace(' ', '_')
        font_dir.mkdir(exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(font_dir)
        
        # Remove zip file
        zip_path.unlink()
        
        print(f"✅ {name} downloaded successfully")
        
    except Exception as e:
        print(f"❌ Failed to download {name}: {e}")

def main():
    """Download all fonts."""
    print("🔤 Downloading modern fonts for subtitles...")
    
    for name, url in FONT_URLS.items():
        download_font(name, url)
    
    print("\n🎉 Font download completed!")
    print(f"Fonts saved to: {FONTS_DIR}")
    
    # List downloaded fonts
    print("\n📁 Downloaded fonts:")
    for font_dir in FONTS_DIR.iterdir():
        if font_dir.is_dir():
            ttf_files = list(font_dir.glob("*.ttf"))
            otf_files = list(font_dir.glob("*.otf"))
            print(f"  • {font_dir.name}: {len(ttf_files + otf_files)} files")

if __name__ == "__main__":
    main()
