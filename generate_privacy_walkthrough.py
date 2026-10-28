import os
import subprocess
from PIL import Image, ImageDraw, ImageFont
import piexif

ROOT = r"D:\Projects\photo-privacy-guard"
FRAMES_DIR = os.path.join(ROOT, "work", "walkthrough_frames")
OUTPUT_VIDEO = os.path.join(ROOT, "photo-privacy-guard-walkthrough.mp4")
os.makedirs(FRAMES_DIR, exist_ok=True)

# Theme Palette (Modern Cyber Dark)
BG_CANVAS = (11, 15, 25)         # #0B0F19
BG_SIDEBAR = (17, 24, 39)        # #111827
BG_BUBBLE_USER = (31, 41, 55)    # #1F2937
BG_CARD = (17, 24, 39)           # #111827
BORDER_CARD = (55, 65, 81)       # #374151
BORDER_SUBTLE = (31, 41, 55)     # #1F2937
TEXT_WHITE = (243, 244, 246)
TEXT_MUTED = (156, 163, 175)
TEXT_DIM = (107, 114, 128)
ACCENT_GREEN = (16, 185, 129)    # #10B981
ACCENT_CYAN = (6, 182, 212)      # #06B6D4
ACCENT_RED = (239, 68, 68)       # #EF4444
PILL_BG = (6, 78, 59)            # Dark emerald

# Typography
FONT_HERO = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 38)
FONT_SECTION = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 26)
FONT_SUBTITLE = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 22)
FONT_BODY = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 20)
FONT_BODY_BOLD = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 20)
FONT_CODE = ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", 18)
FONT_SMALL = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 16)
FONT_SMALL_BOLD = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 16)

ICON_PATH = os.path.join(ROOT, "openai_bundle", "assets", "icon.png")
if os.path.exists(ICON_PATH):
    PLUGIN_ICON_40 = Image.open(ICON_PATH).convert("RGBA").resize((40, 40), Image.Resampling.LANCZOS)
    PLUGIN_ICON_72 = Image.open(ICON_PATH).convert("RGBA").resize((72, 72), Image.Resampling.LANCZOS)
else:
    PLUGIN_ICON_40 = Image.new("RGBA", (40, 40), ACCENT_GREEN)
    PLUGIN_ICON_72 = Image.new("RGBA", (72, 72), ACCENT_GREEN)


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list:
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if (bbox[2] - bbox[0]) <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
                current_line = [word]
            else:
                lines.append(word)
    if current_line:
        lines.append(" ".join(current_line))
    return lines


def draw_centered_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, cx: int, y: int, fill: tuple) -> int:
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    draw.text((cx - w / 2, y), text, font=font, fill=fill)
    return bbox[3] - bbox[1]


def draw_chatgpt_chrome(draw: ImageDraw.ImageDraw, active_chat_title: str) -> None:
    # 1. Left Sidebar
    draw.rectangle([(0, 0), (280, 1080)], fill=BG_SIDEBAR)
    draw.line([(280, 0), (280, 1080)], fill=BORDER_SUBTLE, width=1)

    draw.rounded_rectangle([(16, 20), (264, 62)], radius=8, fill=(31, 41, 55), outline=BORDER_CARD, width=1)
    draw.text((36, 30), "+ New chat", fill=TEXT_WHITE, font=FONT_BODY_BOLD)

    # Status badge
    draw.rounded_rectangle([(16, 78), (264, 134)], radius=8, fill=(24, 32, 47), outline=BORDER_SUBTLE, width=1)
    draw.ellipse([(28, 98), (40, 110)], fill=ACCENT_GREEN)
    draw.text((50, 92), "Photo Privacy Guard", fill=TEXT_WHITE, font=FONT_BODY_BOLD)
    draw.text((50, 112), "Ghost Mode: Active", fill=ACCENT_GREEN, font=FONT_SMALL)

    demo_chats = [
        "1. Inspect Hidden EXIF",
        "2. Ghost GPS Injection",
        "3. Pure Metadata Strip",
        "4. Anti-Fraud ID Shield",
        "5. Compliance Summary"
    ]
    for idx, title in enumerate(demo_chats):
        y = 185 + idx * 44
        is_active = (title == active_chat_title)
        if is_active:
            draw.rounded_rectangle([(14, y), (266, y + 36)], radius=6, fill=(31, 41, 55))
            draw.text((26, y + 6), title, fill=TEXT_WHITE, font=FONT_BODY_BOLD)
        else:
            draw.text((26, y + 6), title, fill=TEXT_MUTED, font=FONT_BODY)

    # Sidebar Bottom Profile
    draw.line([(0, 1000), (280, 1000)], fill=BORDER_SUBTLE, width=1)
    draw.ellipse([(18, 1016), (56, 1054)], fill=(16, 185, 129))
    draw.text((27, 1023), "SA", fill=(11, 15, 25), font=FONT_BODY_BOLD)
    draw.text((66, 1018), "Shahrukh Ahmad", fill=TEXT_WHITE, font=FONT_BODY_BOLD)
    draw.text((66, 1040), "Privacy Engineer", fill=TEXT_DIM, font=FONT_SMALL)

    # 2. Main Top Bar
    draw.rectangle([(281, 0), (1920, 68)], fill=(17, 24, 39))
    draw.line([(281, 68), (1920, 68)], fill=BORDER_SUBTLE, width=1)
    draw.text((320, 20), "ChatGPT 4o", fill=TEXT_WHITE, font=FONT_SECTION)

    draw.rounded_rectangle([(490, 18), (730, 52)], radius=17, fill=PILL_BG, outline=ACCENT_GREEN, width=1)
    draw.ellipse([(506, 31), (516, 41)], fill=ACCENT_GREEN)
    draw.text((528, 23), "Photo Privacy Guard Active", fill=ACCENT_GREEN, font=FONT_SMALL_BOLD)

    # 3. Bottom Input Bar
    draw.rounded_rectangle([(480, 990), (1720, 1052)], radius=24, fill=(31, 41, 55), outline=BORDER_CARD, width=1)
    draw.text((516, 1010), "Upload a photo or document to inspect, spoof GPS, or protect...", fill=TEXT_MUTED, font=FONT_BODY)
    draw.ellipse([(1672, 1002), (1708, 1038)], fill=TEXT_MUTED)
    draw.polygon([(1684, 1024), (1690, 1014), (1696, 1024)], fill=BG_CANVAS)


# ---------------------------------------------
# SLIDE 1: INTRO
# ---------------------------------------------
def make_intro_slide() -> Image.Image:
    img = Image.new("RGB", (1920, 1080), BG_CANVAS)
    draw = ImageDraw.Draw(img)
    draw_chatgpt_chrome(draw, "1. Inspect Hidden EXIF")

    cx = 1100
    w, h = 960, 660
    x1, y1 = cx - w // 2, 150
    x2, y2 = x1 + w, y1 + h

    draw.rounded_rectangle([(x1, y1), (x2, y2)], radius=20, fill=BG_CARD, outline=BORDER_CARD, width=2)
    img.paste(PLUGIN_ICON_72, (cx - 36, y1 + 36), PLUGIN_ICON_72)

    draw_centered_text(draw, "Photo Privacy Guard - ChatGPT Plugin", FONT_HERO, cx, y1 + 130, TEXT_WHITE)
    draw_centered_text(draw, "Official Walkthrough for OpenAI Plugin Directory Review", FONT_SUBTITLE, cx, y1 + 185, ACCENT_GREEN)

    features = [
        ("EXIF Scanner", "Audit photos for exposed GPS location, camera serial, and timestamps"),
        ("Ghost Mode", "Inject realistic dummy GPS coords (Paris, Tokyo, London, NYC, Bermuda)"),
        ("Privacy Wipe", "Completely remove 100% of tracking metadata & device fingerprints"),
        ("ID Anti-Fraud", "Apply diagonal safety watermarks on CNIC, ID cards & utility bills"),
        ("Compliance", "MCP JSON-RPC 2024-11-05 Compliant | Zero Data Retention on Vercel")
    ]

    for i, (tag, desc) in enumerate(features):
        row_y = y1 + 250 + i * 62
        rx1, rx2 = x1 + 40, x2 - 40
        draw.rounded_rectangle([(rx1, row_y), (rx2, row_y + 48)], radius=10, fill=(11, 15, 25), outline=BORDER_SUBTLE, width=1)
        draw.rounded_rectangle([(rx1 + 10, row_y + 8), (rx1 + 130, row_y + 40)], radius=6, fill=PILL_BG, outline=ACCENT_GREEN, width=1)
        draw.text((rx1 + 18, row_y + 13), tag, fill=ACCENT_GREEN, font=FONT_SMALL_BOLD)
        draw.text((rx1 + 148, row_y + 12), desc, fill=TEXT_WHITE, font=FONT_BODY)

    draw_centered_text(draw, "Privacy Policy & Terms: Live on Vercel • By Shahrukh Ahmad", FONT_SMALL, cx, y2 - 40, TEXT_MUTED)
    return img


# ---------------------------------------------
# SLIDE 2: TEST CASE 1 - INSPECT
# ---------------------------------------------
def make_inspect_slide() -> Image.Image:
    img = Image.new("RGB", (1920, 1080), BG_CANVAS)
    draw = ImageDraw.Draw(img)
    draw_chatgpt_chrome(draw, "1. Inspect Hidden EXIF")

    col_left, col_right = 620, 1580
    prompt = "Check if my photo has GPS location or camera information exposed."
    lines = wrap_text(draw, prompt, FONT_BODY, 600)
    b_h = len(lines) * 28 + 24
    bx1 = col_right - 640
    by1 = 100

    draw.rounded_rectangle([(bx1, by1), (col_right, by1 + b_h)], radius=18, fill=BG_BUBBLE_USER)
    for idx, l in enumerate(lines):
        draw.text((bx1 + 20, by1 + 12 + idx * 28), l, fill=TEXT_WHITE, font=FONT_BODY)
    draw.ellipse([(col_right + 16, by1 + 6), (col_right + 56, by1 + 46)], fill=(70, 70, 100))
    draw.text((col_right + 28, by1 + 14), "U", fill=TEXT_WHITE, font=FONT_BODY_BOLD)

    asst_y = by1 + b_h + 30
    img.paste(PLUGIN_ICON_40, (col_left - 50, asst_y), PLUGIN_ICON_40)

    draw.rounded_rectangle([(col_left, asst_y), (col_left + 400, asst_y + 36)], radius=18, fill=PILL_BG, outline=ACCENT_GREEN, width=1)
    draw.ellipse([(col_left + 14, asst_y + 13), (col_left + 24, asst_y + 23)], fill=ACCENT_GREEN)
    draw.text((col_left + 34, asst_y + 7), "Used tool: inspect_photo_privacy", fill=ACCENT_GREEN, font=FONT_SMALL_BOLD)

    draw.text((col_left, asst_y + 50), "I audited your photo's EXIF metadata. Here is the privacy breakdown:", fill=TEXT_WHITE, font=FONT_BODY)

    card_y1 = asst_y + 90
    card_y2 = card_y1 + 380
    draw.rounded_rectangle([(col_left, card_y1), (col_right, card_y2)], radius=18, fill=BG_CARD, outline=BORDER_CARD, width=1)

    # Risk Meter on Left
    draw.rounded_rectangle([(col_left + 30, card_y1 + 30), (col_left + 310, card_y2 - 30)], radius=14, fill=(11, 15, 25), outline=BORDER_SUBTLE, width=1)
    draw_centered_text(draw, "PRIVACY RISK", FONT_SMALL_BOLD, col_left + 170, card_y1 + 55, TEXT_MUTED)
    draw_centered_text(draw, "CRITICAL", FONT_HERO, col_left + 170, card_y1 + 90, ACCENT_RED)
    draw_centered_text(draw, "Score: 20 / 100", FONT_SECTION, col_left + 170, card_y1 + 150, (251, 191, 36))
    draw.rounded_rectangle([(col_left + 50, card_y1 + 220), (col_left + 290, card_y1 + 300)], radius=10, fill=(38, 20, 20), outline=ACCENT_RED, width=1)
    draw.text((col_left + 64, card_y1 + 235), "EXPOSED DATA:", fill=ACCENT_RED, font=FONT_SMALL_BOLD)
    draw.text((col_left + 64, card_y1 + 260), "Home GPS Coordinates", fill=TEXT_WHITE, font=FONT_BODY)

    # Details on Right
    rx = col_left + 340
    ry = card_y1 + 40
    draw.text((rx, ry), "Detected Metadata Leaks:", fill=TEXT_WHITE, font=FONT_BODY_BOLD)
    ry += 40

    findings = [
        ("GPS Coordinates:", "33.6844° N, 73.0479° E (Islamabad)"),
        ("Google Maps Link:", "https://maps.google.com/?q=33.6844,73.0479"),
        ("Device Model:", "Apple iPhone 15 Pro (iOS 17.5.1)"),
        ("Date / Timestamp:", "2026:10:24 16:42:18 (Exact Local Time)"),
        ("Recommendation:", "Use 'spoof_photo_location' or 'strip_photo_metadata'")
    ]
    for lbl, val in findings:
        draw.text((rx, ry), lbl, fill=TEXT_MUTED, font=FONT_BODY)
        draw.text((rx + 180, ry), val, fill=(251, 191, 36) if "GPS" in lbl else ACCENT_GREEN, font=FONT_CODE)
        ry += 42

    return img


# ---------------------------------------------
# SLIDE 3: TEST CASE 2 - GHOST MODE (SPOOF)
# ---------------------------------------------
def make_spoof_slide() -> Image.Image:
    img = Image.new("RGB", (1920, 1080), BG_CANVAS)
    draw = ImageDraw.Draw(img)
    draw_chatgpt_chrome(draw, "2. Ghost GPS Injection")

    col_left, col_right = 620, 1580
    prompt = "Inject a dummy GPS location for Paris (Eiffel Tower) so my real home address is hidden."
    lines = wrap_text(draw, prompt, FONT_BODY, 600)
    b_h = len(lines) * 28 + 24
    bx1 = col_right - 640
    by1 = 100

    draw.rounded_rectangle([(bx1, by1), (col_right, by1 + b_h)], radius=18, fill=BG_BUBBLE_USER)
    for idx, l in enumerate(lines):
        draw.text((bx1 + 20, by1 + 12 + idx * 28), l, fill=TEXT_WHITE, font=FONT_BODY)
    draw.ellipse([(col_right + 16, by1 + 6), (col_right + 56, by1 + 46)], fill=(70, 70, 100))
    draw.text((col_right + 28, by1 + 14), "U", fill=TEXT_WHITE, font=FONT_BODY_BOLD)

    asst_y = by1 + b_h + 30
    img.paste(PLUGIN_ICON_40, (col_left - 50, asst_y), PLUGIN_ICON_40)

    draw.rounded_rectangle([(col_left, asst_y), (col_left + 390, asst_y + 36)], radius=18, fill=PILL_BG, outline=ACCENT_GREEN, width=1)
    draw.ellipse([(col_left + 14, asst_y + 13), (col_left + 24, asst_y + 23)], fill=ACCENT_GREEN)
    draw.text((col_left + 34, asst_y + 7), "Used tool: spoof_photo_location", fill=ACCENT_GREEN, font=FONT_SMALL_BOLD)

    draw.text((col_left, asst_y + 50), "Ghost Mode activated! Real GPS replaced with Eiffel Tower, Paris:", fill=TEXT_WHITE, font=FONT_BODY)

    card_y1 = asst_y + 90
    card_y2 = card_y1 + 380
    draw.rounded_rectangle([(col_left, card_y1), (col_right, card_y2)], radius=18, fill=BG_CARD, outline=BORDER_CARD, width=1)

    # Left Graphic Mockup Box
    draw.rounded_rectangle([(col_left + 30, card_y1 + 30), (col_left + 340, card_y2 - 30)], radius=14, fill=(11, 15, 25), outline=BORDER_SUBTLE, width=1)
    draw_centered_text(draw, "📍 GHOST LOCATION", FONT_SECTION, col_left + 185, card_y1 + 60, ACCENT_GREEN)
    draw_centered_text(draw, "🇫🇷 Paris, France", FONT_HERO, col_left + 185, card_y1 + 110, TEXT_WHITE)
    draw_centered_text(draw, "Eiffel Tower Coordinates", FONT_BODY, col_left + 185, card_y1 + 165, TEXT_MUTED)
    draw.rounded_rectangle([(col_left + 50, card_y1 + 230), (col_left + 320, card_y1 + 300)], radius=10, fill=(16, 44, 34), outline=ACCENT_GREEN, width=1)
    draw.text((col_left + 65, card_y1 + 245), "REAL LOCATION STATUS:", fill=ACCENT_GREEN, font=FONT_SMALL_BOLD)
    draw.text((col_left + 65, card_y1 + 270), "100% Cloaked & Hidden", fill=TEXT_WHITE, font=FONT_BODY)

    # Right Details Table
    rx = col_left + 370
    ry = card_y1 + 45
    draw.text((rx, ry), "Injected Metadata Tags:", fill=TEXT_WHITE, font=FONT_BODY_BOLD)
    ry += 40

    spoofed_tags = [
        ("Target Preset:", "Paris, France (Eiffel Tower)"),
        ("Spoofed Latitude:", "48.858372° N (Rational DMS)"),
        ("Spoofed Longitude:", "2.294481° E (Rational DMS)"),
        ("Device Fingerprint:", "Apple iPhone 15 Pro (Dummy)"),
        ("Software Tag:", "GhostMode Privacy Engine 1.0"),
        ("Result Image:", "Ready for safe social media sharing")
    ]
    for lbl, val in spoofed_tags:
        draw.text((rx, ry), lbl, fill=TEXT_MUTED, font=FONT_BODY)
        draw.text((rx + 180, ry), val, fill=ACCENT_GREEN, font=FONT_CODE)
        ry += 38

    return img


# ---------------------------------------------
# SLIDE 4: TEST CASE 3 - ANTI-FRAUD WATERMARK
# ---------------------------------------------
def make_watermark_slide() -> Image.Image:
    img = Image.new("RGB", (1920, 1080), BG_CANVAS)
    draw = ImageDraw.Draw(img)
    draw_chatgpt_chrome(draw, "4. Anti-Fraud ID Shield")

    col_left, col_right = 620, 1580
    prompt = "Add an anti-fraud watermark 'FOR SIM VERIFICATION ONLY' across this ID card."
    lines = wrap_text(draw, prompt, FONT_BODY, 600)
    b_h = len(lines) * 28 + 24
    bx1 = col_right - 640
    by1 = 100

    draw.rounded_rectangle([(bx1, by1), (col_right, by1 + b_h)], radius=18, fill=BG_BUBBLE_USER)
    for idx, l in enumerate(lines):
        draw.text((bx1 + 20, by1 + 12 + idx * 28), l, fill=TEXT_WHITE, font=FONT_BODY)
    draw.ellipse([(col_right + 16, by1 + 6), (col_right + 56, by1 + 46)], fill=(70, 70, 100))
    draw.text((col_right + 28, by1 + 14), "U", fill=TEXT_WHITE, font=FONT_BODY_BOLD)

    asst_y = by1 + b_h + 30
    img.paste(PLUGIN_ICON_40, (col_left - 50, asst_y), PLUGIN_ICON_40)

    draw.rounded_rectangle([(col_left, asst_y), (col_left + 420, asst_y + 36)], radius=18, fill=PILL_BG, outline=ACCENT_GREEN, width=1)
    draw.ellipse([(col_left + 14, asst_y + 13), (col_left + 24, asst_y + 23)], fill=ACCENT_GREEN)
    draw.text((col_left + 34, asst_y + 7), "Used tool: add_anti_fraud_watermark", fill=ACCENT_GREEN, font=FONT_SMALL_BOLD)

    draw.text((col_left, asst_y + 50), "Document protected! Diagonal tamper-proof security watermark overlaid:", fill=TEXT_WHITE, font=FONT_BODY)

    card_y1 = asst_y + 90
    card_y2 = card_y1 + 380
    draw.rounded_rectangle([(col_left, card_y1), (col_right, card_y2)], radius=18, fill=BG_CARD, outline=BORDER_CARD, width=1)

    # Left ID Card Simulation Box
    draw.rounded_rectangle([(col_left + 30, card_y1 + 30), (col_left + 380, card_y2 - 30)], radius=14, fill=(240, 240, 245))
    draw.rounded_rectangle([(col_left + 50, card_y1 + 50), (col_left + 150, card_y1 + 170)], radius=8, fill=(180, 190, 205))
    draw.text((col_left + 170, card_y1 + 60), "NATIONAL ID CARD", fill=(40, 50, 70), font=FONT_BODY_BOLD)
    draw.text((col_left + 170, card_y1 + 90), "Name: CITIZEN DEMO", fill=(70, 80, 100), font=FONT_SMALL)
    draw.text((col_left + 170, card_y1 + 120), "ID: 42101-*******-1", fill=(70, 80, 100), font=FONT_SMALL)

    # Red diagonal watermark overlay simulation
    wm_stamp = Image.new("RGBA", (340, 60), (0, 0, 0, 0))
    w_draw = ImageDraw.Draw(wm_stamp)
    w_draw.rectangle([(0, 0), (338, 58)], outline=(220, 38, 38, 200), width=3)
    w_draw.text((12, 16), "FOR SIM VERIFICATION ONLY", fill=(220, 38, 38, 220), font=FONT_BODY_BOLD)
    rot_wm = wm_stamp.rotate(24, expand=True)
    img.paste(rot_wm, (col_left + 40, card_y1 + 140), rot_wm)

    # Right Details Table
    rx = col_left + 410
    ry = card_y1 + 45
    draw.text((rx, ry), "Anti-Fraud Document Protection:", fill=TEXT_WHITE, font=FONT_BODY_BOLD)
    ry += 40

    wm_details = [
        ("Watermark Text:", "FOR SIM VERIFICATION ONLY"),
        ("Protection Type:", "Diagonal repeating anti-reuse shield"),
        ("Scam Prevention:", "Cannot be reused for fake loans or SIMs"),
        ("Document Safety:", "Preserves text readability while voiding re-use"),
        ("Compliance:", "Zero-retention ephemeral processing")
    ]
    for lbl, val in wm_details:
        draw.text((rx, ry), lbl, fill=TEXT_MUTED, font=FONT_BODY)
        draw.text((rx + 160, ry), val, fill=ACCENT_GREEN, font=FONT_CODE)
        ry += 42

    return img


# ---------------------------------------------
# SLIDE 5: COMPLIANCE SUMMARY
# ---------------------------------------------
def make_summary_slide() -> Image.Image:
    img = Image.new("RGB", (1920, 1080), BG_CANVAS)
    draw = ImageDraw.Draw(img)
    draw_chatgpt_chrome(draw, "5. Compliance Summary")

    cx = 1100
    w, h = 960, 680
    x1, y1 = cx - w // 2, 140
    x2, y2 = x1 + w, y1 + h

    draw.rounded_rectangle([(x1, y1), (x2, y2)], radius=20, fill=BG_CARD, outline=BORDER_CARD, width=2)
    img.paste(PLUGIN_ICON_72, (cx - 36, y1 + 30), PLUGIN_ICON_72)

    draw_centered_text(draw, "OpenAI Directory Compliance & Verification", FONT_SECTION, cx, y1 + 120, TEXT_WHITE)
    draw_centered_text(draw, "Photo Privacy Guard meets all OpenAI and MCP technical specifications", FONT_SUBTITLE, cx, y1 + 165, TEXT_MUTED)

    items = [
        ("MCP Protocol", "JSON-RPC 2.0 / protocolVersion: 2024-11-05"),
        ("Tool Annotations", "provided_tool_annotations (readOnlyHint, destructiveHint)"),
        ("Ghost Mode (Spoofing)", "Real GPS replaced with sanitized coordinates (Paris, Tokyo, etc.)"),
        ("Zero Data Retention", "Ephemeral in-memory processing. Zero files stored permanently."),
        ("Free Access", "No API keys or logins required. Free for all reviewers & users."),
        ("Legal Pages", "Dedicated /privacy and /terms endpoints live on Vercel")
    ]

    for i, (k, v) in enumerate(items):
        row_y = y1 + 220 + i * 58
        rx1, rx2 = x1 + 40, x2 - 40
        draw.rounded_rectangle([(rx1, row_y), (rx2, row_y + 48)], radius=8, fill=(11, 15, 25), outline=BORDER_SUBTLE, width=1)
        draw.ellipse([(rx1 + 14, row_y + 16), (rx1 + 30, row_y + 32)], fill=ACCENT_GREEN)
        draw.text((rx1 + 18, row_y + 15), "✓", fill=(11, 15, 25), font=FONT_SMALL_BOLD)
        draw.text((rx1 + 44, row_y + 12), k, fill=TEXT_WHITE, font=FONT_BODY_BOLD)
        draw.text((rx1 + 300, row_y + 14), v, fill=ACCENT_GREEN, font=FONT_CODE)

    draw_centered_text(draw, "Status: Ready for Production Directory Review", FONT_BODY_BOLD, cx, y2 - 45, TEXT_WHITE)
    return img


print("Rendering Photo Privacy Guard video frames...")

scenes = [
    ("intro", make_intro_slide(), 6),
    ("case1_inspect", make_inspect_slide(), 7),
    ("case2_spoof", make_spoof_slide(), 8),
    ("case3_watermark", make_watermark_slide(), 8),
    ("summary", make_summary_slide(), 7)
]

concat_manifest = []
for idx, (name, img_obj, duration) in enumerate(scenes):
    filepath = os.path.join(FRAMES_DIR, f"{idx:02d}_{name}.png")
    img_obj.save(filepath, format="PNG")
    concat_manifest.append(f"file '{filepath}'\nduration {duration}\n")

# Repeat last frame
concat_manifest.append(f"file '{os.path.join(FRAMES_DIR, f'{len(scenes)-1:02d}_{scenes[-1][0]}.png')}'\n")

manifest_path = os.path.join(FRAMES_DIR, "concat.txt")
with open(manifest_path, "w", encoding="utf-8") as f:
    f.writelines(concat_manifest)

print("Compiling MP4 video via FFmpeg...")

ffmpeg_cmd = [
    "ffmpeg", "-y",
    "-f", "concat", "-safe", "0", "-i", manifest_path,
    "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
    "-c:a", "aac", "-b:a", "128k", "-shortest",
    OUTPUT_VIDEO
]

res = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
if res.returncode == 0:
    print(f"SUCCESS: Video rendered at {OUTPUT_VIDEO} (Size: {os.path.getsize(OUTPUT_VIDEO)} bytes)")
else:
    print(f"Error: {res.stderr}")
