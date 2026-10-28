import os
import zipfile

ROOT = r"D:\Projects\photo-privacy-guard"
BUNDLE_DIR = os.path.join(ROOT, "openai_bundle")
OUTPUT_ZIP = os.path.join(ROOT, "photo-privacy-guard-plugin.zip")

with zipfile.ZipFile(OUTPUT_ZIP, "w", zipfile.ZIP_DEFLATED) as z:
    for root_dir, dirs, files in os.walk(BUNDLE_DIR):
        for file in files:
            full_path = os.path.join(root_dir, file)
            rel_path = os.path.relpath(full_path, BUNDLE_DIR)
            z.write(full_path, rel_path)

print(f"Plugin package created at: {OUTPUT_ZIP} ({os.path.getsize(OUTPUT_ZIP)} bytes)")
