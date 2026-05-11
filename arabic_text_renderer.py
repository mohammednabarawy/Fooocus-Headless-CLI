import os
import argparse
import urllib.request
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

def get_font_path(font_path="C:\\Windows\\Fonts\\arial.ttf"):
    if not os.path.exists(font_path):
        # Fallback to segoe ui if arial is missing
        if os.path.exists("C:\\Windows\\Fonts\\segoeui.ttf"):
            return "C:\\Windows\\Fonts\\segoeui.ttf"
        raise FileNotFoundError(f"Could not find font at {font_path}")
    return font_path

def render_arabic_text(text, output_path, width, height, font_path="C:\\Windows\\Fonts\\arial.ttf", padding=50):
    font_path = get_font_path(font_path)
    
    # 1. Reshape the text to connect Arabic letters properly
    reshaped_text = arabic_reshaper.reshape(text)
    
    # 2. Fix the direction (right-to-left)
    bidi_text = get_display(reshaped_text)
    
    # Create black image
    img = Image.new('RGB', (width, height), color='black')
    draw = ImageDraw.Draw(img)
    
    # Start with a reasonable max font size and scale down
    font_size = height // 3
    font = ImageFont.truetype(font_path, font_size)
    
    # Calculate bounding box
    bbox = draw.textbbox((0, 0), bidi_text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    
    # Scale down until it fits with padding
    while (text_w > width - padding * 2 or text_h > height - padding * 2) and font_size > 10:
        font_size -= 2
        font = ImageFont.truetype(font_path, font_size)
        bbox = draw.textbbox((0, 0), bidi_text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
    
    # Calculate centered position
    x = (width - text_w) / 2 - bbox[0]
    y = (height - text_h) / 2 - bbox[1]
    
    # Draw text (white on black)
    draw.text((x, y), bidi_text, font=font, fill='white')
    
    img.save(output_path)
    print(f"Text reference image saved to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate an image with centered Arabic text for ControlNet.")
    parser.add_argument("--text", type=str, required=True, help="The Arabic text to render")
    parser.add_argument("--output", type=str, default="arabic_reference.png", help="Output image path")
    parser.add_argument("--width", type=int, default=1152, help="Image width")
    parser.add_argument("--height", type=int, default=896, help="Image height")
    
    args = parser.parse_args()
    render_arabic_text(args.text, args.output, args.width, args.height)
