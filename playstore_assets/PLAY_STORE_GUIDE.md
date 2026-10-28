# 📱 Google Play Store Submission Guide: Photo Privacy Guard

---

## 1. Play Store Par Knsi Build Upload Karni Hai?
Google Play Console par **`.apk` upload nahi hota** (August 2021 se Google ne new apps ke liye APK band kar diya hai).  
Wahan sirf **`.aab` (Android App Bundle)** upload hota hai.

---

## 2. `.aab` Build Kaise Milegi? (PWABuilder - 60 Seconds, 100% Free)

Microsoft aur Google ka official tool hai **[PWABuilder.com](https://www.pwabuilder.com)** jo kisi bhi web app / PWA ko certified Android App Bundle (`.aab`) mein convert karta hai.

### Steps:
1. Jab aapki app Vercel par live ho jaye (e.g. `https://photo-privacy-guard.vercel.app`):
2. Browser mein open karein: **[https://www.pwabuilder.com](https://www.pwabuilder.com)**
3. Apni Vercel app ka URL paste karein: `https://photo-privacy-guard.vercel.app` aur **"Start"** dabayein.
4. PWABuilder aapke `manifest.json` aur icons ko verify karega (Score 100% aayega kyunke humne pehle se setup kar diya hai!).
5. **"Package for Stores"** button par click karein.
6. **"Android"** select karein aur **"Generate Package"** dabayein.
7. Yeh aapko ek zip file dega jiske andar aapki **`app-release.aab`** file hogi!
8. Bas yeh file Google Play Console par upload kar dein!

---

## 3. Google Play Console Listing Details (Copy-Paste Ready)

### 🏷️ App Title (Max 30 characters):
```text
Photo Privacy Guard - EXIF Clean
```

### 📝 Short Description (Max 80 characters):
```text
Remove hidden GPS location, strip EXIF metadata & protect IDs with watermarks.
```

### 📄 Full Description (Max 4000 characters):
```text
Protect your digital privacy before sharing photos online. Every photo captured on modern smartphones contains hidden EXIF metadata—including exact GPS home coordinates, device serial numbers, camera models, and precise timestamps.

Photo Privacy Guard is a zero-trace security utility designed to inspect, strip, and protect your images before they leave your device.

🛡️ KEY PRIVACY CAPABILITIES:

1. EXIF & GPS Metadata Scanner:
Instantly detect exposed GPS latitude/longitude, altitude, camera manufacturer, shutter speed, and timestamp. View your photo's vulnerability score in seconds.

2. Ghost Mode (Dummy GPS Location Spoofer):
Rather than simply deleting GPS data (which alerts third-party platforms that metadata was scrubbed), Ghost Mode replaces your sensitive home coordinates with realistic tourist destinations (Paris, Tokyo, New York, London, Bermuda) using authentic rational DMS tags.

3. One-Click Zero-Trace Stripper:
Purge 100% of EXIF markers, GPS headers, TIFF data, and camera maker notes. Output clean, anonymized JPEG files ready for social media or messaging apps.

4. Anti-Fraud ID Watermarking:
Sharing your CNIC, Passport, Driver's License, or utility bills for KYC verification? Apply a high-contrast diagonal security grid ("FOR VERIFICATION ONLY - DO NOT REUSE") across the document. Legible for verification agents, yet completely unusable for identity fraudsters and loan scams.

🔒 ZERO-RETENTION ARCHITECTURE:
- All processing occurs with zero cloud retention.
- No login required.
- No tracking pixels or telemetry.
- Lightweight, fast, and battery-efficient.

Take back control of your location privacy. Download Photo Privacy Guard today.
```

---

## 4. Play Store Graphics (Ready in `playstore_assets/`):

| Asset | Dimensions | File Path |
|---|---|---|
| **App Icon** | 512 x 512 PNG | `playstore_assets/app_icon_512x512.png` |
| **Feature Graphic** | 1024 x 500 PNG | `playstore_assets/feature_graphic_1024x500.png` |
| **Screenshot 1** | 1080 x 1920 PNG | `playstore_assets/screenshots/screenshot_1_threat_detection.png` |
| **Screenshot 2** | 1080 x 1920 PNG | `playstore_assets/screenshots/screenshot_2_location_defense.png` |
| **Screenshot 3** | 1080 x 1920 PNG | `playstore_assets/screenshots/screenshot_3_document_shield.png` |
| **Screenshot 4** | 1080 x 1920 PNG | `playstore_assets/screenshots/screenshot_4_total_anonymity.png` |

---

## 5. Console Policy & Legal Links:

- **Privacy Policy URL:** `https://photo-privacy-guard.vercel.app/privacy`
- **Category:** Tools / Productivity
- **Content Rating:** Everyone (3+)
- **Contains Ads:** No (unless you add AdMob later)
- **Target Audience:** 18 and over / All ages
- **App Access:** All functionality is available without special access
- **Financial Features:** None
- **Government Apps:** No
