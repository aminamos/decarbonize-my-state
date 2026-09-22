"""Fetch satellite images for power plants missing one.

Usage:
    python scripts/fetch_plant_images.py <final/power_plants.json> <image_dir> [limit]

Replaces fetch_map_images.py: the Google Static Maps key in that script is
dead (HTTP 403). Uses the Esri World Imagery export endpoint (no key
required) at the same 800x800 size and ~zoom-16 framing as the existing
images, then draws a marker pin with PIL.
"""

import io
import json
import os
import sys
import urllib.request
import math

from PIL import Image, ImageDraw

SIZE = 800
# ~zoom-16, 400px viewport ~= 955 m span at mid-latitudes
HALF_LAT_DEG = 0.0043


def bbox_for(lat, lon):
    half_lon = HALF_LAT_DEG / math.cos(math.radians(lat))
    return f"{lon - half_lon},{lat - HALF_LAT_DEG},{lon + half_lon},{lat + HALF_LAT_DEG}"


def fetch(lat, lon):
    url = (
        "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/"
        "MapServer/export?bbox=" + bbox_for(lat, lon) +
        "&bboxSR=4326&imageSR=4326&size=800,800&format=png32&f=image"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return Image.open(io.BytesIO(r.read())).convert("RGBA")


def draw_pin(im):
    d = ImageDraw.Draw(im)
    cx, cy = SIZE // 2, SIZE // 2 - 40
    # teardrop: circle + triangle point below, Google-pin-like
    d.polygon([(cx - 26, cy + 12), (cx + 26, cy + 12), (cx, cy + 92)],
            fill=(222, 66, 60, 255))
    d.ellipse([cx - 40, cy - 40, cx + 40, cy + 40], fill=(222, 66, 60, 255))
    d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=(140, 20, 15, 255))
    return im


if __name__ == "__main__":
    plants_path, img_dir = sys.argv[1], sys.argv[2]
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else None
    data = json.load(open(plants_path))

    needed = []
    for node in data:
        for p in node["power_plants"]:
            fn = os.path.join(img_dir, f"{node['state']}-{p['slug']}.png")
            if not os.path.exists(fn):
                needed.append((fn, float(p["Latitude"]), float(p["Longitude"])))
    if limit:
        needed = needed[:limit]
    print(f"{len(needed)} images to fetch")

    for i, (fn, lat, lon) in enumerate(needed):
        try:
            im = draw_pin(fetch(lat, lon))
            im.convert("RGB").save(fn, "PNG")
        except Exception as e:
            print(f"  FAILED {fn}: {e}")
            continue
        if (i + 1) % 50 == 0:
            print(f"  {i + 1}/{len(needed)}")
    print("done")
