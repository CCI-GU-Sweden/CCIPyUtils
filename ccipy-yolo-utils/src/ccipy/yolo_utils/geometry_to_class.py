from typing import Callable
from ccipy.utils.roi_geometry import RoiGeometry

geometry_to_yolo_class = Callable[[RoiGeometry], int]


def geometry_to_class_default(geometry: RoiGeometry) -> int:
    return geometry.get_color()


def geometry_to_class_text_default(geometry: RoiGeometry) -> int:
    return int(geometry.get_text())
