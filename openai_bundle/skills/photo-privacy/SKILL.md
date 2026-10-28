---
name: photo-privacy
description: Inspect image metadata, strip EXIF and GPS tracking data, inject realistic dummy GPS coordinates (Ghost Mode), and add anti-fraud verification watermarks across sensitive documents and ID cards. Trigger whenever the user uploads or asks to inspect, sanitize, clean, or protect photos, documents, or screenshots.
---
# Instructions
When a user provides an image or asks about photo privacy:
1. **Inspection:** Use `inspect_photo_privacy` to audit for exposed GPS coordinates, camera model, and timestamp. Warn the user if their home or exact location is visible.
2. **Ghost Mode (Dummy GPS):** If the user wants to keep metadata looking authentic without revealing their real location, call `spoof_photo_location` with presets like Paris, Tokyo, London, NYC, or Bermuda.
3. **Pure Clean:** If the user wants all metadata removed, call `strip_photo_metadata`.
4. **Anti-Fraud ID Protection:** If the user shares an ID card, CNIC, or utility bill, call `add_anti_fraud_watermark` with text like "FOR VERIFICATION ONLY - DO NOT REUSE" to prevent identity fraud.
5. Render the result image inline and provide instructions.
