from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, text, filename):
    # Create a new image with a white background
    image = Image.new('RGB', (size, size), 'white')
    draw = ImageDraw.Draw(image)
    
    # Try to load a font, fallback to default if not available
    try:
        font_size = size // 4
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    # Calculate text position to center it
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    
    # Draw the text
    draw.text((x, y), text, fill='black', font=font)
    
    # Save the image
    image.save(filename)

def main():
    # Create the icons
    create_icon(192, "ICMP", "logo192.png")
    create_icon(512, "ICMP", "logo512.png")
    
    # Create favicon (32x32)
    favicon = Image.new('RGB', (32, 32), 'white')
    draw = ImageDraw.Draw(favicon)
    draw.text((8, 8), "I", fill='black')
    favicon.save("favicon.ico", format='ICO')
    
    print("Static files generated successfully!")

if __name__ == "__main__":
    main()