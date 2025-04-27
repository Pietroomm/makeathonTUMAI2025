"""
Tiny demo that writes a 3-waypoint mission at kml_mission.config.OUTPUT_PATH
and prints the resulting path – ready for Google Earth or DJI Pilot 2.
"""

from writer import Waypoint, build_kmz
from utils import *
from config import OUTPUT_DIR, ROOT

if __name__ == "__main__":
    # Three quick test points around Munich
    IMAGES_BASE = ["DJI_20250424192950_0001_V.jpeg", "DJI_20250424192951_0003_V.jpeg", "DJI_20250424192952_0004_V.jpeg"]
    IMAGES_PATHS = [f"{str(ROOT)}/dev_data/dev_data/{img}" for img in IMAGES_BASE]
    # demo_waypoints = [
    #     Waypoint(longitude=12.18, latitude=49.1, altitude=450, height=40, heading=0, pitch=-90),
    #     Waypoint(longitude=11.5680, latitude=48.1420, altitude=450, height=50, heading=120, pitch=-45),
    #     Waypoint(longitude=11.5655, latitude=48.1435, altitude=450, height=45, heading=240, pitch=-60),
    # ]
    wp = []
    for i, img_p in enumerate(IMAGES_PATHS):
        lat, lon, alt = get_exif_location(img_p)
        wp.append(Waypoint(longitude=lon + 0.001*i, latitude=lat + 0.001*i, altitude=alt + 2*i, height=40, heading=0, pitch=0))
    final_kmz = build_kmz(wp)
    print(f"🎉  KMZ ready: {final_kmz.resolve()}")
