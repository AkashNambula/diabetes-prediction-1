from PIL import Image, ImageDraw, ImageFilter
import random
import math

def create_diabetes_theme_background(filename="diabetes_bg_v2.png"):
    # Create image (Full HD)
    width, height = 1920, 1080
    
    # 1. Base: Professional Gradient (Medical Blue -> White)
    base_color_start = (255, 255, 255)   # White
    base_color_end = (230, 242, 255)     # Very Light Blue
    
    img = Image.new('RGB', (width, height), base_color_start)
    draw = ImageDraw.Draw(img)
    
    # Gradient background
    for y in range(height):
        r = int(base_color_start[0] + (base_color_end[0] - base_color_start[0]) * y / height)
        g = int(base_color_start[1] + (base_color_end[1] - base_color_start[1]) * y / height)
        b = int(base_color_start[2] + (base_color_end[2] - base_color_start[2]) * y / height)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Create an overlay for transparency
    overlay = Image.new('RGBA', (width, height), (0,0,0,0))
    overlay_draw = ImageDraw.Draw(overlay)

    # 2. THE BLUE CIRCLE (Universal Diabetes Symbol)
    # Large, offset to the right to not interfere with login form
    circle_color = (0, 119, 182, 30) # Medical Blue with low opacity
    center_x, center_y = int(width * 0.75), int(height * 0.5)
    radius = 350
    thickness = 50
    overlay_draw.ellipse((center_x - radius, center_y - radius, center_x + radius, center_y + radius), 
                         outline=circle_color, width=thickness)

    # 3. PREDICTION GRAPH (Symbolizing "Prevention/Monitoring")
    # A smooth curve or meaningful line chart in the background
    points = []
    start_x = 0
    end_x = width
    step = 20
    
    # Generate a "healthy trend" curve
    for x in range(start_x, end_x, step):
        # Sine wave with some randomness
        normalized_x = x / width
        y = height * 0.6 + math.sin(normalized_x * 10) * 100 - (normalized_x * 200) 
        points.append((x, y))
        
    # Draw the graph line
    overlay_draw.line(points, fill=(72, 202, 228, 40), width=15) # Light Cyan line
    
    # Add dots on the line
    for p in points[::5]: # Every 5th point
        r = 8
        overlay_draw.ellipse((p[0]-r, p[1]-r, p[0]+r, p[1]+r), fill=(0, 150, 199, 60))

    # 4. MEDICAL ICONS / GLUCOSE DROPS (Abstract)
    # Draw abstract drops (circles with triangular tops) or just circles
    for _ in range(10):
        x = random.randint(0, width // 2) # Keep to the left/background
        y = random.randint(0, height)
        r = random.randint(10, 30)
        # Drop shape (circle)
        overlay_draw.ellipse((x-r, y-r, x+r, y+r), fill=(200, 230, 255, 100))

    # 5. Composite and Blur
    # We blur the overlay slightly so it looks like a background
    # But keep the circle relatively sharp
    img = img.convert("RGBA")
    img = Image.alpha_composite(img, overlay)
    
    # Save
    img.save(filename)
    print(f"Generated {filename}")

if __name__ == "__main__":
    create_diabetes_theme_background()
