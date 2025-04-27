"""
Plane-fit utilities + “10 m back & 4 m up” solver.
"""
from __future__ import annotations

import numpy as np
from numpy.linalg import svd, norm
import logging

from geodesy import geodetic_to_enu, enu_to_geodetic

BACK_DISTANCE_METRES: float = 10.0
UP_DISTANCE_METRES: float = 4.0


def fit_plane_normal(points_enu: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Fit a plane through points and return its centroid and (unit) normal.

    :param points_enu: (N, 3) ENU points assumed roughly coplanar.
    :returns: (centroid, normal) – each (3,) nd-array.
    """
    centroid = points_enu.mean(axis=0)
    uu, _, vt = svd(points_enu - centroid)
    normal = vt[-1]           # eigen-vector w/ smallest eigen-value
    normal /= norm(normal)    # ensure |n| = 1
    # Decide orientation: we want the “away from pallets” side (–Y if ambiguous)
    if normal[1] > 0:         # points north; flip so it points south
        normal = -normal
    return centroid, normal


def compute_target_coordinate(
    corner_points_gps: list[list[float]],
    back: float = BACK_DISTANCE_METRES,
    up: float = UP_DISTANCE_METRES,
) -> list[float]:
    """
    Main business function: return GPS of the inspection/hover point.

    Steps
    -----
    1.  Use the centroid of the corners as the local ENU origin.
    2.  Convert corners → ENU, overwrite z with average (coplanar assumption).
    3.  Fit plane, take its normal, step `back` m along it.
    4.  Add +`up` m on ENU-Z.
    5.  Convert back to geodetic.

    :param corner_points_gps: list[[lat, lon, alt]], four pallet corners.
    :param back: metres to retreat from pallet plane.
    :param up: metres to rise vertically.
    :returns: [lat, lon, alt] of target point.
    """
    pts = np.asarray(corner_points_gps, dtype=float)
    origin = pts.mean(axis=0)
    logging.info(f"Origin: {origin=}")

    enu = geodetic_to_enu(pts, origin)
    logging.debug("ENU points:\n%s", enu)
    enu[:, 2] = enu[:, 2].mean()        # flatten onto common z plane
    print("ENU points (flattened):\n", enu)

    centroid, normal = fit_plane_normal(enu)
    print("Centroid: ", centroid)
    print("Normal: ", normal)
    target_enu = centroid - back * normal
    target_enu[2] += up                # rise
    print("Target ENU: ", target_enu)

    return enu_to_geodetic(target_enu.reshape(1, 3), origin)[0].tolist()
