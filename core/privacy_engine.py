import io
import math
from typing import Dict, Any, Optional, Tuple, List
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ExifTags
import piexif

DUMMY_LOCATIONS = {
    "paris": {"name": "Eiffel Tower, Paris", "lat": 48.858372, "lon": 2.294481},
    "tokyo": {"name": "Shibuya Crossing, Tokyo", "lat": 35.659500, "lon": 139.700400},
    "london": {"name": "Big Ben, London", "lat": 51.500729, "lon": -0.124625},
    "newyork": {"name": "Times Square, New York", "lat": 40.758000, "lon": -73.985500},
    "bermuda": {"name": "Bermuda Triangle", "lat": 25.000000, "lon": -71.000000},
    "null_island": {"name": "Null Island (0°N 0°E)", "lat": 0.000000, "lon": 0.000000}
}


def _deg_to_dms_rational(deg_float: float) -> Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int]]:
    """Converts a decimal degree coordinate into degrees/minutes/seconds rational tuples for EXIF."""
    abs_deg = abs(deg_float)
    d = int(abs_deg)
    rem = (abs_deg - d) * 60
    m = int(rem)
    s = round((rem - m) * 60, 4)
    s_int = int(s * 1000)
    return ((d, 1), (m, 1), (s_int, 1000))


def inspect_image_privacy(image_bytes: bytes) -> Dict[str, Any]:
    """Inspects an image for hidden EXIF, GPS location, device fingerprint, and timestamps."""
    result: Dict[str, Any] = {
        "has_exif": False,
        "has_gps": False,
        "gps": None,
        "device": None,
        "timestamp": None,
        "privacy_score": 100,  # 100 = completely safe, 0 = high exposure
        "risk_level": "SAFE",
        "findings": []
    }

    try:
        img = Image.open(io.BytesIO(image_bytes))
    except Exception as e:
        result["findings"].append(f"Invalid image format: {str(e)}")
        return result

    raw_exif = None
    try:
        raw_exif = img.getexif()
    except Exception:
        pass

    if not raw_exif or len(raw_exif) == 0:
        result["findings"].append("Zero EXIF metadata detected. Photo is already clean.")
        return result

    result["has_exif"] = True
    result["privacy_score"] -= 20
    result["risk_level"] = "LOW"

    # Extract human-readable EXIF tags
    exif_data = {}
    for tag_id, val in raw_exif.items():
        tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
        exif_data[tag_name] = val

    # 1. Device Make & Model
    make = str(exif_data.get("Make", "")).strip()
    model = str(exif_data.get("Model", "")).strip()
    software = str(exif_data.get("Software", "")).strip()

    if make or model:
        result["device"] = {
            "make": make,
            "model": model,
            "software": software
        }
        result["privacy_score"] -= 25
        result["findings"].append(f"Device Fingerprint detected: {make} {model} ({software})".strip())

    # 2. Timestamp
    dt = str(exif_data.get("DateTime", "") or exif_data.get("DateTimeOriginal", "")).strip()
    if dt:
        result["timestamp"] = dt
        result["privacy_score"] -= 15
        result["findings"].append(f"Exact date/time recorded: {dt}")

    # 3. GPS Coordinates Check
    gps_info = None
    try:
        gps_ifd = raw_exif.get_ifd(ExifTags.IFD.GPSInfo)
        if gps_ifd:
            gps_info = gps_ifd
    except Exception:
        pass

    if gps_info:
        try:
            lat_ref = gps_info.get(1, "N")
            lat_dms = gps_info.get(2)
            lon_ref = gps_info.get(3, "E")
            lon_dms = gps_info.get(4)

            if lat_dms and lon_dms:
                lat = float(lat_dms[0]) + float(lat_dms[1]) / 60 + float(lat_dms[2]) / 3600
                if lat_ref == "S":
                    lat = -lat
                lon = float(lon_dms[0]) + float(lon_dms[1]) / 60 + float(lon_dms[2]) / 3600
                if lon_ref == "W":
                    lon = -lon

                result["has_gps"] = True
                result["gps"] = {
                    "latitude": round(lat, 6),
                    "longitude": round(lon, 6),
                    "maps_url": f"https://www.google.com/maps?q={round(lat, 6)},{round(lon, 6)}"
                }
                result["privacy_score"] -= 40
                result["risk_level"] = "CRITICAL"
                result["findings"].append(
                    f"CRITICAL: Exact GPS Location exposed ({round(lat, 6)}, {round(lon, 6)})! Anyone can find your home/place."
                )
        except Exception:
            pass

    if result["privacy_score"] < 40:
        result["risk_level"] = "CRITICAL"
    elif result["privacy_score"] < 70:
        result["risk_level"] = "MEDIUM"

    result["privacy_score"] = max(0, result["privacy_score"])
    return result


def strip_image_metadata(image_bytes: bytes, output_format: str = "JPEG") -> bytes:
    """Completely strips all EXIF, GPS, XMP, IPTC, and ICC tags from the image."""
    img = Image.open(io.BytesIO(image_bytes))
    
    # Create pure clean image copy without original metadata dicts
    data = list(img.getdata())
    clean_img = Image.new(img.mode, img.size)
    clean_img.putdata(data)

    out = io.BytesIO()
    fmt = output_format.upper()
    if fmt in ("JPG", "JPEG"):
        clean_img = clean_img.convert("RGB")
        clean_img.save(out, format="JPEG", quality=95)
    elif fmt == "PNG":
        clean_img.save(out, format="PNG", optimize=True)
    elif fmt == "WEBP":
        clean_img.save(out, format="WEBP", quality=95)
    else:
        clean_img.save(out, format=fmt)

    return out.getvalue()


def spoof_image_location(
    image_bytes: bytes,
    preset: str = "paris",
    custom_lat: Optional[float] = None,
    custom_lon: Optional[float] = None,
    dummy_make: str = "Apple",
    dummy_model: str = "iPhone 15 Pro",
    dummy_datetime: str = "2026:10:28 12:00:00"
) -> Tuple[bytes, Dict[str, Any]]:
    """Replaces real metadata with realistic dummy GPS coordinates and dummy device fingerprint."""
    if custom_lat is not None and custom_lon is not None:
        target_lat = float(custom_lat)
        target_lon = float(custom_lon)
        loc_name = f"Custom ({round(target_lat, 4)}, {round(target_lon, 4)})"
    else:
        preset_info = DUMMY_LOCATIONS.get(preset.lower(), DUMMY_LOCATIONS["paris"])
        target_lat = preset_info["lat"]
        target_lon = preset_info["lon"]
        loc_name = preset_info["name"]

    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    lat_dms = _deg_to_dms_rational(target_lat)
    lon_dms = _deg_to_dms_rational(target_lon)
    lat_ref = b"N" if target_lat >= 0 else b"S"
    lon_ref = b"E" if target_lon >= 0 else b"W"

    gps_ifd = {
        piexif.GPSIFD.GPSVersionID: (2, 3, 0, 0),
        piexif.GPSIFD.GPSLatitudeRef: lat_ref,
        piexif.GPSIFD.GPSLatitude: lat_dms,
        piexif.GPSIFD.GPSLongitudeRef: lon_ref,
        piexif.GPSIFD.GPSLongitude: lon_dms,
        piexif.GPSIFD.GPSAltitude: (15, 1),
    }

    zeroth_ifd = {
        piexif.ImageIFD.Make: dummy_make.encode("utf-8"),
        piexif.ImageIFD.Model: dummy_model.encode("utf-8"),
        piexif.ImageIFD.DateTime: dummy_datetime.encode("utf-8"),
        piexif.ImageIFD.Software: b"GhostMode Privacy Engine 1.0"
    }

    exif_ifd = {
        piexif.ExifIFD.DateTimeOriginal: dummy_datetime.encode("utf-8"),
        piexif.ExifIFD.DateTimeDigitized: dummy_datetime.encode("utf-8")
    }

    exif_dict = {
        "0th": zeroth_ifd,
        "Exif": exif_ifd,
        "GPS": gps_ifd,
        "1st": {},
        "thumbnail": None
    }

    exif_bytes = piexif.dump(exif_dict)
    out = io.BytesIO()
    img.save(out, format="JPEG", quality=95, exif=exif_bytes)

    info = {
        "spoofed_location": loc_name,
        "latitude": target_lat,
        "longitude": target_lon,
        "device": f"{dummy_make} {dummy_model}",
        "maps_url": f"https://www.google.com/maps?q={target_lat},{target_lon}"
    }
    return out.getvalue(), info


def add_anti_fraud_watermark(
    image_bytes: bytes,
    watermark_text: str = "FOR VERIFICATION ONLY - DO NOT REUSE",
    opacity: int = 140,
    color_rgb: Tuple[int, int, int] = (220, 38, 38)
) -> bytes:
    """Adds a prominent diagonal repeating anti-fraud watermark across ID documents or receipts."""
    base_img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    w, h = base_img.size

    # Watermark layer
    watermark_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark_layer)

    font_size = max(24, int(w / 24))
    try:
        font = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()

    fill_rgba = (color_rgb[0], color_rgb[1], color_rgb[2], opacity)

    # Diagonal text rotation overlay
    text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
    tw = text_bbox[2] - text_bbox[0]
    th = text_bbox[3] - text_bbox[1]

    stamp = Image.new("RGBA", (tw + 40, th + 20), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(stamp)
    s_draw.rectangle([(0, 0), (tw + 38, th + 18)], outline=fill_rgba, width=2)
    s_draw.text((20, 10), watermark_text, fill=fill_rgba, font=font)
    rotated_stamp = stamp.rotate(30, expand=True, resample=Image.Resampling.BICUBIC)

    rw, rh = rotated_stamp.size
    for x in range(-50, w + 100, rw + 80):
        for y in range(-50, h + 100, rh + 80):
            watermark_layer.paste(rotated_stamp, (x, y), rotated_stamp)

    combined = Image.alpha_composite(base_img, watermark_layer).convert("RGB")
    out = io.BytesIO()
    combined.save(out, format="JPEG", quality=95)
    return out.getvalue()


def redact_image_box(
    image_bytes: bytes,
    boxes: List[Tuple[int, int, int, int]],
    mode: str = "blackout"
) -> bytes:
    """Redacts (blackout or blur) specified bounding boxes [(x1, y1, x2, y2)] in the image."""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    draw = ImageDraw.Draw(img)

    for (x1, y1, x2, y2) in boxes:
        x_min, x_max = min(x1, x2), max(x1, x2)
        y_min, y_max = min(y1, y2), max(y1, y2)

        if mode == "blur":
            box_crop = img.crop((x_min, y_min, x_max, y_max))
            blurred = box_crop.filter(ImageFilter.GaussianBlur(radius=25))
            img.paste(blurred, (x_min, y_min))
        else:
            # Clean black censor bar with subtle border
            draw.rectangle([(x_min, y_min), (x_max, y_max)], fill=(0, 0, 0))

    out = io.BytesIO()
    img.save(out, format="JPEG", quality=95)
    return out.getvalue()
