#!/usr/bin/env python3
"""
Example run: feed four pallet-corner GPS points on stdin or inline.
"""
import json
import logging

from .geometry import compute_target_coordinate

EXAMPLE = [
    (52.00001, 13.00002, 45.3),
    [52.00002, 13.00050, 45.1],
    [52.00030, 13.00055, 45.4],
    [52.00029, 13.00007, 45.2],
]  # dummy data only!

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    result = compute_target_coordinate(EXAMPLE, up=10)
    print(json.dumps({"target": result}, indent=2))
