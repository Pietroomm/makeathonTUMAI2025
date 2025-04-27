"""
Functions that turn Python data → KML text → file on disk.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from string import Template
from typing import List
import zipfile

from config import *
import templates as T


def _epoch_ms() -> str:
    """
    Current UTC time in Unix epoch milliseconds.
    """
    return str(int(time.time_ns() // 1_000_000))


def _substitute(block: str, mapping: dict[str, str]) -> str:
    """
    Convenience wrapper around :pyclass:`string.Template`.

    :param block:  Raw XML with $PLACEHOLDER$ markers.
    :param mapping:  ``{"PLACEHOLDER": "value", ...}``
    :returns:  XML with placeholders filled in.
    """
    return Template(block).safe_substitute(mapping)


@dataclass
class Waypoint:
    """
    Container for waypoint data.

    :param longitude:   WGS-84 longitude  (decimal degrees)
    :param latitude:   WGS-84 latitude   (decimal degrees)
    :param altitude:   WGS-84 altitude   (ellipsoid height, metres)
    :param height: Height above ground (metres)
    :param heading: Aircraft yaw at that point (deg, 0° = North)
    :param pitch:  Gimbal pitch     (deg, –90° = straight down)
    """
    longitude: float
    latitude: float
    altitude: float
    height: float = 10
    heading: float = 0
    pitch: float = -90


def build_template_kml(waypoint: Waypoint, index: int) -> str:
    """
    Render a single ``<Placemark>…`` block.

    :param waypoint: :class:`Waypoint` instance.
    :param index:    Zero-based waypoint index.
    :returns:        XML string.
    """
    mapping = {
        "LONGITUDE": waypoint.longitude,
        "LATITUDE": waypoint.latitude,
        "ALTITUDE": waypoint.altitude,
        "INDEX": index,
        "HEIGHT": waypoint.height,
        "ACTION_GROUP_ID": index,          # keep id == index for clarity
        "HEADING": waypoint.heading,
        "PITCH": waypoint.pitch,
    }
    return _substitute(T.WAYPOINT_BLOCK, mapping)

def build_wpml_waypoint_xml(waypoint: Waypoint, index: int) -> str:
    """
    Render one WPML Placemark (the WPML schema calls this “waypoint node”).

    executeHeight is approximated as *take-off ellipsoid height + AGL*.
    """
    mapping = {
        "LONGITUDE": waypoint.longitude,
        "LATITUDE": waypoint.latitude,
        "INDEX": index,
        "ALTITUDE": waypoint.altitude,
        "HEADING": waypoint.heading,
    }
    return _substitute(T.WPML_WAYPOINT_BLOCK, mapping)

def decimal_to_dms(decimal: float, is_lat: bool = True) -> str:
    """
    Convert a decimal degree value to DMS (degrees, minutes, seconds) format.

    :param decimal: The decimal degree value.
    :param is_lat:  True if the value is latitude (N/S), False for longitude (E/W).
    :returns: A string in the format "D° M' S" H", e.g. "48° 8' 24.840"N"
    """
    # Determine hemisphere and work with absolute value
    if is_lat:
        hemisphere = "N" if decimal >= 0 else "S"
    else:
        hemisphere = "E" if decimal >= 0 else "W"

    abs_val = abs(decimal)
    degrees = int(abs_val)
    minutes_full = (abs_val - degrees) * 60
    minutes = int(minutes_full)
    seconds = (minutes_full - minutes) * 60

    return f"{degrees}° {minutes}' {seconds:.3f}\"{hemisphere}"


def floats_to_dms(lon: float, lat: float) -> str:
    """
    Convert float longitude and latitude into a DMS formatted coordinate string.

    :param lon: The longitude value in decimal degrees.
    :param lat: The latitude value in decimal degrees.
    :returns: A formatted string with both coordinates in DMS, e.g.
              "Lon: 11° 34' 3.000\"E, Lat: 48° 8' 24.000\"N"
    """
    lon_dms = decimal_to_dms(lon, is_lat=False)
    lat_dms = decimal_to_dms(lat, is_lat=True)
    return f"Lon: {lon_dms}, Lat: {lat_dms}"


def build_kml(waypoints: List[Waypoint],
              output: Path | str,
              author: str = AUTHOR,
              takeoff_ref_point: str = TAKEOFF_REF_POINT) -> Path:
    """
    Create a full DJI-Pilot-compatible KML and write it to *output*.

    :param waypoints:  Sequence of :class:`Waypoint` objects.
    :param output:     Where to write the finished file.
    :param author:     Name inserted into <wpml:author>.
    :param takeoff_ref_point:  ``lon,lat,ellipsoidHeight`` (comma separated).
    :returns:          Path to the written file.
    """
    # 1) Substitute header + missionConfig blocks
    common_xml_block = _substitute(T.COMMON_BLOCK,
                             {"AUTHOR": author,
                              "CREATE_TIME": _epoch_ms(),
                              "UPDATE_TIME": _epoch_ms(),
                                "TAKEOFF_REF_POINT": takeoff_ref_point})

    # 2) Build every waypoint’s XML
    wpt_xml_list = []
    for idx, wpt in enumerate(waypoints):
        dms_coord = floats_to_dms(wpt.longitude, wpt.latitude)
        print(f"Waypoint {idx} DMS coordinates: {dms_coord}")
        print(f"Waypoint altitude: {wpt.altitude}m")
        wpt_xml_list.append(build_template_kml(wpt, idx))
    wpt_xml = "\n".join(wpt_xml_list)

    # 3) Assemble the full KML skeleton
    full_kml = _substitute(
        T.KML_TEMPLATE,
        {
            "COMMON_BLOCK": common_xml_block,
            "COORD_SYS_BLOCK": T.COORD_SYS_BLOCK,
            "WAYPOINTS": wpt_xml
        }
    )

    # 4) Write to disk
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(full_kml, encoding="utf-8")

    return output_path

def build_wpml(waypoints: List[Waypoint], folder: Path) -> Path:
    """
    Create *waylines.wpml* inside *folder* and return its path.
    """
    wpml_wpts = "\n".join(
        build_wpml_waypoint_xml(wpt, idx) for idx, wpt in enumerate(waypoints)
    )

    full_wpml = _substitute(
        T.WPML_TEMPLATE,
        {
            "MISSION_CONFIG_BLOCK": T.WPML_MISSION_CONFIG_BLOCK,
            "WAYPOINTS": wpml_wpts,
        }
    )

    wpml_path = folder / "waylines.wpml"
    wpml_path.write_text(full_wpml, encoding="utf-8")
    return wpml_path

def build_kmz(waypoints: List[Waypoint]) -> Path:
    """
    Generate *template.kml* + *waylines.wpml*, zip them, and return
    the path of the resulting KMZ archive.

    The output layout is:
        OUTPUT_DIR / KMZ_NAME(zip archive → .kmz)
        OUTPUT_DIR / wpmz / template.kml
        OUTPUT_DIR / wpmz / waylines.wpml
    """
    # 1) Prepare working folder
    work_dir = OUTPUT_DIR / "wpmz"
    work_dir.mkdir(parents=True, exist_ok=True)

    # 2) Build the template.kml (same logic as before, just new name)
    kml_path = build_kml(
        waypoints,
        output=work_dir / "template.kml",
        author=AUTHOR,
        takeoff_ref_point=TAKEOFF_REF_POINT,
    )

    # 3) Build waylines.wpml
    wpml_path = build_wpml(waypoints, work_dir)

    # 4) Zip → KMZ
    kmz_path = OUTPUT_DIR / KMZ_NAME
    with zipfile.ZipFile(kmz_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(kml_path, arcname="wpmz/template.kml")
        zf.write(wpml_path, arcname="wpmz/waylines.wpml")

    return kmz_path

