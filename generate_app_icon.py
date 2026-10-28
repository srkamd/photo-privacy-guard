from PIL import Image, ImageDraw, ImageFont
import math
import os

out_dir = r"D:\Projects\photo-privacy-guard\openai_bundle\assets"
os.makedirs(out_dir, exist_ok=True)

size = (512, 512)
img = Image.new("RGBA", size, (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Background squircle
bg_box = [(16, 16), (496, 496)]
draw.rounded_rectangle(bg_box, radius=110, fill=(11, 15, 25), outline=(16, 185, 129), width=8)

# Shield Shape
shield_poly = [
    (256, 90),
    (400, 150),
    (400, 290),
    (256, 420),
    (112, 290),
    (112, 150)
]
draw.polygon(shield_poly, fill=(20, 32, 48), outline=(52, 211, 153), width=10)

# Camera lens circle in center
draw.ellipse([(196, 200), (316, 320)], fill=(16, 185, 129), outline=(255, 255, 255), width=6)
draw.ellipse([(226, 230), (286, 290)], fill=(11, 15, 25))

# Shutter reflection
draw.ellipse([(238, 242), (254, 258)], fill=(255, 255, 255))

# Lock or GPS pin symbol at bottom of shield
draw.polygon([(256, 350), (276, 390), (236, 390)], fill=(52, 211, 153))

# Save icon.png and logo.png
icon_path = os.path.join(out_dir, "icon.png")
logo_path = os.path.join(out_dir, "logo.png")
img.save(icon_path, format="PNG")
img.save(logo_path, format="PNG")
print(f"Generated icons at {icon_path}")
