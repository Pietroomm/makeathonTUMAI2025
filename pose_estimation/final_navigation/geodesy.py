"""
Geodetic ( lat, lon, alt ) ↔ local-ENU helpers.

All heavy lifting is done once here so geometry.py can stay vector-math-only.
"""
from __future__ import annotations

import numpy as np
from pyproj import Transformer
import logging

from .exceptions import GeodesyError

# Re-use one transformer pair across calls (thread-safe in PyProj ≥3.2).
_TO_ECEF = Transformer.from_crs("epsg:4979", "epsg:4978", always_xy=True)
_FROM_ECEF = Transformer.from_crs("epsg:4978", "epsg:4979", always_xy=True)


def _geodetic_to_ecef(lat: float, lon: float, alt: float) -> np.ndarray:
    """Internal helper: single-point geodetic → ECEF."""
    try:
        x, y, z = _TO_ECEF.transform(lon, lat, alt)  # note lon/lat order
        logging.info(f"Geodetic coordinates: {lat=}, {lon=}, {alt=} got converted to ECEF: {x=}, {y=}, {z=}")
    except Exception as exc:  # noqa: E501
        raise GeodesyError(
            f"Cannot convert ({lat=}, {lon=}, {alt=}) to ECEF"
        ) from exc
    return np.array([x, y, z])


def _ecef_to_geodetic(x: float, y: float, z: float) -> np.ndarray:
    """Internal helper: single-point ECEF → geodetic."""
    try:
        lon, lat, alt = _FROM_ECEF.transform(x, y, z)
        logging.info(f"ECEF coordinates: {x=}, {y=}, {z=} got converted to Geodetic: {lat=}, {lon=}, {alt=}")
    except Exception as exc:
        raise GeodesyError(f"Cannot convert ECEF ({x}, {y}, {z}) to geodetic") from exc
    return np.array([lat, lon, alt])


def geodetic_to_enu(
    points: np.ndarray, origin: np.ndarray
) -> np.ndarray:
    """
    Convert an array of geodetic coordinates to local ENU.

    :param points: (N, 3) array of [lat, lon, alt] (° , ° , m).
    :param origin: (3,) array – local origin [lat0, lon0, alt0] (deg, deg, m).
    :returns: (N, 3) ENU coordinates (m) relative to origin.
    """
    # Pre-compute ECEF of origin + rotation matrix
    x0, y0, z0 = _geodetic_to_ecef(*origin)
    lat0, lon0, _ = np.radians(origin)

    sin_lat, cos_lat = np.sin(lat0), np.cos(lat0)
    sin_lon, cos_lon = np.sin(lon0), np.cos(lon0)

    rot = np.array(
        [
            [-sin_lon, cos_lon, 0.0],
            [-sin_lat * cos_lon, -sin_lat * sin_lon, cos_lat],
            [cos_lat * cos_lon, cos_lat * sin_lon, sin_lat],
        ]
    )

    ecef_pts = np.vstack([_geodetic_to_ecef(*p) for p in points])
    d = ecef_pts - np.array([x0, y0, z0])
    return (rot @ d.T).T  # shape (N, 3)


def enu_to_geodetic(
    enu: np.ndarray, origin: np.ndarray
) -> np.ndarray:
    """
    Convert ENU coordinates back to geodetic.

    :param enu: (N, 3) ENU array (m).
    :param origin: (3,) geodetic origin used earlier.
    :returns: (N, 3) array of [lat, lon, alt].
    """
    x0, y0, z0 = _geodetic_to_ecef(*origin)
    lat0, lon0, _ = np.radians(origin)

    sin_lat, cos_lat = np.sin(lat0), np.cos(lat0)
    sin_lon, cos_lon = np.sin(lon0), np.cos(lon0)

    rot_T = np.array(
        [
            [-sin_lon, -sin_lat * cos_lon, cos_lat * cos_lon],
            [cos_lon, -sin_lat * sin_lon, cos_lat * sin_lon],
            [0.0, cos_lat, sin_lat],
        ]
    )

    ecef_origin = np.array([x0, y0, z0])  # ⬅️ 3-vector
    ecef_delta = (rot_T @ enu.T).T
    ecef = ecef_origin + ecef_delta  # ✅ add all three
    return np.vstack([_ecef_to_geodetic(*row) for row in ecef])
