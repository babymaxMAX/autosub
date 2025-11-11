#!/usr/bin/env python3
"""Setup system fonts for subtitle styling."""

import os
import sys
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def check_system_fonts():
    """Check available system fonts."""
    print("🔍 Checking available system fonts...")
    
    # Common system font paths
    font_paths = [
        "/System/Library/Fonts/",
        "/Library/Fonts/", 
        "/Users/*/Library/Fonts/",
        "/usr/share/fonts/",
        "/usr/local/share/fonts/"
    ]
    
    available_fonts = []
    
    for path in font_paths:
        if os.path.exists(path):
            try:
                for font_file in Path(path).rglob("*.ttf"):
                    available_fonts.append(font_file.name)
                for font_file in Path(path).rglob("*.otf"):
                    available_fonts.append(font_file.name)
            except PermissionError:
                continue
    
    print(f"Found {len(available_fonts)} system fonts")
    return available_fonts

def get_font_mapping():
    """Get mapping of style names to actual system fonts."""
    # Map our style font names to common system fonts
    font_mapping = {
        "Montserrat Black": ["Montserrat-Black.ttf", "Arial-Black.ttf", "Arial Black"],
        "Roboto": ["Roboto-Regular.ttf", "Helvetica.ttc", "Arial.ttf"],
        "Open Sans": ["OpenSans-Regular.ttf", "Helvetica.ttc", "Arial.ttf"],
        "Bebas Neue": ["BebasNeue-Regular.ttf", "Impact.ttf", "Arial Black"],
        "Playfair Display": ["PlayfairDisplay-Regular.ttf", "Times.ttc", "Times New Roman"],
        "Orbitron": ["Orbitron-Regular.ttf", "Courier.ttc", "Courier New"],
        "Inter": ["Inter-Regular.ttf", "Helvetica.ttc", "Arial.ttf"],
        "Source Sans Pro": ["SourceSansPro-Regular.ttf", "Helvetica.ttc", "Arial.ttf"],
    }
    
    return font_mapping

def update_subtitle_styles():
    """Update subtitle styles with available system fonts."""
    print("🎨 Updating subtitle styles with system fonts...")
    
    font_mapping = get_font_mapping()
    available_fonts = check_system_fonts()
    
    # Update the subtitle styles file
    styles_file = project_root / "common" / "subtitle_styles.py"
    
    with open(styles_file, 'r') as f:
        content = f.read()
    
    # Replace font names with available system fonts
    for style_font, fallbacks in font_mapping.items():
        best_font = style_font  # Default to original
        
        # Find the best available font
        for fallback in fallbacks:
            if any(fallback.lower() in font.lower() for font in available_fonts):
                best_font = fallback.replace('.ttf', '').replace('.otf', '')
                break
        
        # Replace in content
        content = content.replace(f'"FontName": "{style_font}"', f'"FontName": "{best_font}"')
    
    # Write updated content
    with open(styles_file, 'w') as f:
        f.write(content)
    
    print("✅ Subtitle styles updated with system fonts")

def main():
    """Setup fonts for subtitle styling."""
    print("🔤 Setting up fonts for subtitle styling...")
    
    check_system_fonts()
    update_subtitle_styles()
    
    print("\n🎉 Font setup completed!")
    print("📝 Subtitle styles have been updated to use available system fonts.")

if __name__ == "__main__":
    main()
