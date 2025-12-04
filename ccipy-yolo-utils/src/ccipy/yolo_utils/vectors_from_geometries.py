from pathlib import Path
from ccipy.utils.roi_geometry import RoiGeometry, RoiPoint, RoiRectangle, RoiEllipse, RoiPolygon
from ccipy.yolo_utils.geometry_to_class import geometry_to_class_text_default, geometry_to_yolo_class


def geometries_to_vectors(geometries: list[RoiGeometry], geometry_to_class: geometry_to_yolo_class = geometry_to_class_text_default) -> list[tuple[int, list[tuple[float, float]]]]:
    """Convert a list of RoiGeometry objects to vectors suitable for YOLO annotations.
    Args:
        geometries (list[RoiGeometry]): List of RoiGeometry objects.
        color_to_class (color_to_class_func, optional): Function to map colors to class indices. Defaults to colors_to_class_default.
    Returns:
        list[tuple[int, list[tuple[float, float]]]]: List of tuples containing class index and list of (x, y) points.
    """
    vectors = []
    for geometry in geometries:
        
        class_type = geometry_to_class(geometry)
        points = []
        match geometry:
            case RoiRectangle():
                points = geometry.get_point_list()
                
            case RoiEllipse():
                points = geometry.get_point_list()
                
            case RoiPolygon():
                points = geometry.get_point_list()
                
            case _:
                continue  # Unsupported geometry type
            
        vector = [(point.x, point.y) for point in points]
        vector.append(vector[0])  # Close the shape by appending the first point at the end
        vectors.append((class_type, vector))

    return vectors


def geometries_to_vectors_normalized(geometries: list[RoiGeometry], image_width: int, image_height: int, geometry_to_class: geometry_to_yolo_class = geometry_to_class_text_default) -> list[tuple[int, list[tuple[float, float]]]]:
    """Convert a list of RoiGeometry objects to normalized vectors suitable for YOLO annotations.
    Args:
        geometries (list[RoiGeometry]): List of RoiGeometry objects.
        image_width (int): Width of the image for normalization.
        image_height (int): Height of the image for normalization.
        color_to_class (color_to_class_func, optional): Function to map colors to class indices. Defaults to colors_to_class_default.
    Returns:
        list[tuple[int, list[tuple[float, float]]]]: List of tuples containing class index and list of normalized (x, y) points.
    """
    vectors = []
    for geometry in geometries:
        
        class_type = geometry_to_class(geometry)
        points = []
        match geometry:
            case RoiRectangle():
                points = geometry.get_point_list()
                
            case RoiEllipse():
                points = geometry.get_point_list()
                
            case RoiPolygon():
                points = geometry.get_point_list()
                
            case _:
                continue  # Unsupported geometry type
            
        vector = [(point.x / image_width, point.y / image_height) for point in points]
        vector.append(vector[0])  # Close the shape by appending the first point at the end
        vectors.append((class_type, vector))

    return vectors


def save_vectors_to_txt(vectors: list[tuple[int, list[tuple[float, float]]]], file_path: Path) -> None:
    """Save vectors to a text file in YOLO format.
    Args:
        vectors (list[tuple[int, list[tuple[float, float]]]]): List of tuples containing class index and list of (x, y) points.
        file_path (str): Path to the output text file. Any subdirectories must already exist.
    """
    with open(file_path, 'x') as f:
        for class_type, points in vectors:
            points_str = ' '.join(f"{x:.3f} {y:.3f}" for x, y in points)
            f.write(f"{class_type} {points_str}\n")
