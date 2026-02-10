from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
import math

def create_diabetes_theme_background(filename="diabetes_bg_v3.png"):
    # Create image (Full HD)
    width, height = 1920, 1080
    
    # 1. Base: Professional Gradient (Medical Blue -> White)
    base_color_start = (255, 255, 255)   # White
    base_color_end = (210, 230, 250)     # Light Blue
    
    img = Image.new('RGB', (width, height), base_color_start)
    draw = ImageDraw.Draw(img)
    
    # Gradient background
    for y in range(height):
        r = int(base_color_start[0] + (base_color_end[0] - base_color_start[0]) * y / height)
        g = int(base_color_start[1] + (base_color_end[1] - base_color_start[1]) * y / height)
        b = int(base_color_start[2] + (base_color_end[2] - base_color_start[2]) * y / height)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Create an overlay for elements
    overlay = Image.new('RGBA', (width, height), (0,0,0,0))
    overlay_draw = ImageDraw.Draw(overlay)

    # 2. GLUCOSE METER (Stylized) - Left Side
    meter_x, meter_y = 300, height // 2
    meter_w, meter_h = 200, 350
    meter_color = (0, 119, 182, 40) # Medical Blue transparent
    screen_color = (255, 255, 255, 100)
    
    # Body
    overlay_draw.rounded_rectangle(
        [meter_x, meter_y - meter_h//2, meter_x + meter_w, meter_y + meter_h//2],
        radius=30, fill=meter_color, outline=(0, 119, 182, 80), width=5
    )
    # Screen
    overlay_draw.rectangle(
        [meter_x + 20, meter_y - 100, meter_x + meter_w - 20, meter_y + 50],
        fill=screen_color
    )
    
    # "100" Reading (Simulated with simple shapes/lines if font not available, or attempt default)
    # Drawing simple segments for "100"
    # 1
    overlay_draw.rectangle([meter_x + 50, meter_y - 60, meter_x + 60, meter_y + 10], fill=(50, 50, 50, 150))
    # 0
    overlay_draw.ellipse([meter_x + 70, meter_y - 60, meter_x + 110, meter_y + 10], outline=(50, 50, 50, 150), width=5)
    # 0
    overlay_draw.ellipse([meter_x + 120, meter_y - 60, meter_x + 160, meter_y + 10], outline=(50, 50, 50, 150), width=5)

    # 3. BLOOD DROP (Symbolizing Test) - Near Meter
    drop_x, drop_y = meter_x + meter_w // 2, meter_y - meter_h // 2 - 40
    drop_r = 30
    drop_color = (220, 53, 69, 60) # Crimson Red transparent
    # Draw drop shape (circle + triangle top)
    overlay_draw.ellipse([drop_x - drop_r, drop_y, drop_x + drop_r, drop_y + 2*drop_r], fill=drop_color)
    overlay_draw.polygon([
        (drop_x - drop_r + 2, drop_y + 10),
        (drop_x + drop_r - 2, drop_y + 10),
        (drop_x, drop_y - 40)
    ], fill=drop_color)

    # 4. PREDICTION GRAPH (Right Side Background)
    points = []
    start_x = width - 600
    end_x = width
    step = 20
    
    # Trend line going up then stabilizing (prediction)
    for x in range(start_x, end_x, step):
        t = (x - start_x) / 600.0
        # Curve: Logistic-like
        y = height * 0.6 - (1 / (1 + math.exp(-10 * (t - 0.5)))) * 300
        points.append((x, y))
        
    overlay_draw.line(points, fill=(0, 180, 216, 60), width=10)
    
    # Add data points
    for p in points[::6]:
        r = 8
        overlay_draw.ellipse((p[0]-r, p[1]-r, p[0]+r, p[1]+r), fill=(0, 119, 182, 80))

    # 5. DNA Double Helix (Abstract Background Pattern)
    for x in range(0, width, 100):
        y1 = height * 0.2 + math.sin(x/200) * 50
        y2 = height * 0.2 + math.sin(x/200 + 3.14) * 50
        r = 5
        overlay_draw.ellipse((x-r, y1-r, x+r, y1+r), fill=(200, 200, 200, 50))
        overlay_draw.ellipse((x-r, y2-r, x+r, y2+r), fill=(200, 200, 200, 50))

    # Final Composite and Blur
    img = img.convert("RGBA")
    img = Image.alpha_composite(img, overlay)
    img = img.filter(ImageFilter.GaussianBlur(radius=2)) # Minimal blur to keep icons recognizable but background

    # Save
    img.save(filename)
    print(f"Generated {filename}")

if __name__ == "__main__":
    create_diabetes_theme_background()
