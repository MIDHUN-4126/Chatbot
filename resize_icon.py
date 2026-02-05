"""
Script to resize the Tamil Nadu logo for browser extension icons
"""
from PIL import Image
import os
import sys

def resize_icon(input_path, output_dir):
    """
    Resize an image to multiple sizes for browser extension
    
    Args:
        input_path: Path to the source image
        output_dir: Directory to save resized icons
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Open the source image
        print(f"Opening image: {input_path}")
        img = Image.open(input_path)
        
        # Convert to RGBA if not already (to preserve transparency)
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Define sizes needed for Chrome extension
        sizes = [16, 48, 128]
        
        for size in sizes:
            # Resize using high-quality LANCZOS resampling
            resized = img.resize((size, size), Image.Resampling.LANCZOS)
            
            # Save the resized image
            output_path = os.path.join(output_dir, f'icon-{size}.png')
            resized.save(output_path, 'PNG', optimize=True)
            print(f"✓ Created {output_path} ({size}x{size})")
        
        print("\n✓ All icons created successfully!")
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        return False

if __name__ == "__main__":
    # Use default path to Tamil Nadu logo
    input_file = r"C:\Users\Asus\OneDrive\Pictures\Tamil-Nadu-Logo.png"
    
    if not os.path.exists(input_file):
        print(f"Error: File not found: {input_file}")
        print("Please make sure the Tamil Nadu logo is saved as 'Tamil-Nadu-Logo.png' in the Pictures folder")
        exit(1)
    
    # Output directory
    output_dir = os.path.join(os.path.dirname(__file__), 'browser_extension', 'icons')
    
    print(f"Resizing image to 16x16, 48x48, and 128x128...\n")
    resize_icon(input_file, output_dir)
