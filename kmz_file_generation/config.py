from pathlib import Path
import logging

# Set logger config
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

# General
ROOT: Path = Path(__file__).parent
logging.info(f"ROOT directory: {ROOT}")

#: Folder or absolute file where the finished KMZ will be written
OUTPUT_DIR: Path = Path("output")
KMZ_NAME: str = "mission.kmz"

#: The name that will appear in <wpml:author>
AUTHOR: str = "Peter Schiekofer"

# WGS-84 lon,lat,ellipsoid height of the launch site
TAKEOFF_REF_POINT: str = "49.099386,12.181031,465.520000"
logging.info(f"TAKEOFF_REF_POINT: {TAKEOFF_REF_POINT}")

# Default arguments
SPEED = 10
logging.info(f"Default speed: {SPEED}")