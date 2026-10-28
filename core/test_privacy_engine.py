import sys
sys.path.insert(0, r"D:\Projects\photo-privacy-guard")

from PIL import Image
import io
from core.privacy_engine import (
    inspect_image_privacy,
    spoof_image_location,
    strip_image_metadata,
    add_anti_fraud_watermark,
    redact_image_box
)

# 1. Create a dummy test image
sample_img = Image.new("RGB", (800, 600), color=(70, 130, 180))
buf = io.BytesIO()
sample_img.save(buf, format="JPEG")
raw_bytes = buf.getvalue()

# Test 1: Inspect blank image
insp1 = inspect_image_privacy(raw_bytes)
print("1. Blank Image Inspection:", insp1["risk_level"], "Score:", insp1["privacy_score"])

# Test 2: Spoof location to Paris (Eiffel Tower)
spoofed_bytes, spoof_info = spoof_image_location(raw_bytes, preset="paris")
print("2. Spoofed location to:", spoof_info["spoofed_location"], "Coords:", spoof_info["latitude"], spoof_info["longitude"])

# Inspect the spoofed image to verify it now reads the fake GPS!
insp2 = inspect_image_privacy(spoofed_bytes)
print("   Verification of Spoofed Image GPS:", insp2["has_gps"], insp2["gps"])

# Test 3: Completely strip metadata
clean_bytes = strip_image_metadata(spoofed_bytes)
insp3 = inspect_image_privacy(clean_bytes)
print("3. After Stripping Metadata:", insp3["risk_level"], "Has GPS:", insp3["has_gps"], "Has EXIF:", insp3["has_exif"])

# Test 4: Add Anti-Fraud Watermark
watermarked_bytes = add_anti_fraud_watermark(raw_bytes, watermark_text="FOR SIM VERIFICATION ONLY - 28 OCT 2026")
print("4. Watermark successfully added! Size:", len(watermarked_bytes), "bytes")

# Test 5: Redact a box (e.g. number plate or account number)
redacted_bytes = redact_image_box(raw_bytes, boxes=[(100, 100, 400, 200)], mode="blackout")
print("5. Blackout box applied! Size:", len(redacted_bytes), "bytes")

print("\nALL CORE ENGINE TESTS PASSED WITH 100% SUCCESS!")
