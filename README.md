# 🚀 makeathonTUMAI2025

## Overview

Our solution enables **autonomous drone navigation** for detecting palettes and QR codes using:
- Object detection (YOLO),
- 3D pose estimation from GPS metadata,
- KMZ file generation for **waypoint navigation**.


---

## Folder Structure

### `/object_detection`
- Detects and labels palettes using a **YOLO model**.
- Extracts **bounding box coordinates** for further 3D pose estimation.

### `/pose_estimation`
- Triangulates **GPS coordinates** from bounding box detections and image metadata.
- Estimates **3D positions** of detected palettes.
- Fits **two parallel lines** across palettes.

### `/kmz_file_generation`
- Generates **KMZ** route files based on triangulated coordinates.
- Prepares waypoints for flight path execution.

### `/output_kmz`
- Stores generated **KMZ files** ready for uploading to the drone navigation system.

---

## Pipeline Summary

1. **Object Detection** → detect palettes and barcodes with YOLO.
2. **Pose Estimation** → triangulate GPS positions from detections and image metadata, and fit parallel lines from the bounding boxes palettes.
3. **KMZ Generation** → create waypoint files and execute flight plan.


---

## Notes

- Pictures are taken with a distance of 10 m and a height of 5 m. 

---


