from PIL import Image, ImageDraw, ImageFilter, ImageFont
import random
import os

def create_medical_background(filename="diabetes_background.png"):
    # Create image (1920x1080)
    width, height = 1920, 1080
    
    # 1. Base Gradient (Medical Blue to White/Light Blue)
    base_color_start = (255, 255, 255) # White
    base_color_end = (240, 248, 255)   # Light Medical Blue (AliceBlue)
    
    img = Image.new('RGB', (width, height), base_color_start)
    draw = ImageDraw.Draw(img)
    
    # Simple linear gradient (manually)
    for y in range(height):
        r = int(base_color_start[0] + (base_color_end[0] - base_color_start[0]) * y / height)
        g = int(base_color_start[1] + (base_color_end[1] - base_color_start[1]) * y / height)
        b = int(base_color_start[2] + (base_color_end[2] - base_color_start[2]) * y / height)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
        
    # 2. Draw "Diabetes Blue Circles" (Symbol of Diabetes Awareness)
    # Draw several scattered circles with soft edges
    circle_color = (0, 119, 182, 40) # Medical Blue with transparency
    
    # We need RGBA for transparency
    overlay = Image.new('RGBA', (width, height), (0,0,0,0))
    overlay_draw = ImageDraw.Draw(overlay)
    
    # Large central circle outline
    center_x, center_y = width // 2, height // 2
    radius = 300
    thickness = 40
    overlay_draw.ellipse((center_x - radius, center_y - radius, center_x + radius, center_y + radius), 
                         outline=(0, 119, 182, 30), width=thickness)
    
    # Random floating circles (representing molecules/cells abstractly)
    for _ in range(15):
        x = random.randint(0, width)
        y = random.randint(0, height)
        r = random.randint(20, 80)
        opacity = random.randint(10, 40)
        overlay_draw.ellipse((x-r, y-r, x+r, y+r), fill=(0, 119, 182, opacity))
        
    # 3. Add Medical Crosses (Subtle)
    for _ in range(8):
        x = random.randint(0, width)
        y = random.randint(0, height)
        size = random.randint(30, 60)
        opacity = random.randint(10, 30)
        c = (2, 62, 138, opacity) # Deep Blue
        
        # Horizontal bar
        overlay_draw.rectangle([x - size, y - size//4, x + size, y + size//4], fill=c)
        # Vertical bar
        overlay_draw.rectangle([x - size//4, y - size, x + size//4, y + size], fill=c)

    # 4. Blur everything for a soft background effect
    img = img.convert("RGBA")
    img = Image.alpha_composite(img, overlay)
    img = img.filter(ImageFilter.GaussianBlur(radius=5))
    
    # Save
    img.convert("RGB").save(filename)
    print(f"Generated {filename}")

if __name__ == "__main__":
    create_medical_background()
