"""
Project-wide custom exceptions.
"""
class GeodesyError(RuntimeError):
    """Raised when a geodesy transform fails (e.g. bad CRS parameters)."""
