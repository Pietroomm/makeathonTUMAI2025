from PIL import Image, ExifTags

from config import ROOT


def get_exif_location(image_path):
    """
    Extract latitude, longitude, and altitude from a JPEG image's EXIF data.

    :param image_path: Path to the JPEG image file.

    :returns: tuple (latitude: float, longitude: float, altitude: float)
              or raises ValueError if GPS data is missing.
    """
    def convert_to_degrees(value):
        """Helper function to convert GPS coordinates to degrees."""
        d, m, s = value
        return float(d) + float(m) / 60.0 + float(s) / 3600.0

    image = Image.open(image_path)
    exif_data = image._getexif()

    if exif_data is None:
        raise ValueError("No EXIF metadata found.")

    gps_info = {}

    for tag, value in exif_data.items():
        decoded = ExifTags.TAGS.get(tag, tag)
        if decoded == "GPSInfo":
            for t in value:
                sub_decoded = ExifTags.GPSTAGS.get(t, t)
                gps_info[sub_decoded] = value[t]

    if not gps_info:
        raise ValueError("No GPS data found in EXIF metadata.")

    try:
        latitude = convert_to_degrees(gps_info['GPSLatitude'])
        if gps_info['GPSLatitudeRef'] == 'S':
            latitude = -latitude

        longitude = convert_to_degrees(gps_info['GPSLongitude'])
        if gps_info['GPSLongitudeRef'] == 'W':
            longitude = -longitude

        altitude = gps_info.get('GPSAltitude', 0)
        altitude = float(altitude)

    except (KeyError, TypeError) as e:
        raise ValueError(f"Error processing GPS data: {e}")

    return latitude, longitude, altitude


# Example usage:
if __name__ == "__main__":
    img_path = f"{str(ROOT)}/dev_data/dev_data/DJI_20250424192950_0001_V.jpeg"
    try:
        lat, lon, alt = get_exif_location(img_path)
        print(f"Latitude: {lat}, Longitude: {lon}, Altitude: {alt}m")
    except ValueError as e:
        print(f"Error: {e}")