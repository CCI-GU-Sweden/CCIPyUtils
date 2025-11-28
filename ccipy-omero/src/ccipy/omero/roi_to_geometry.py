from ccipy.utils.roi_geometry import RoiEllipse, RoiPolygon, RoiRectangle, RoiGeometry, RoiPoint
from omero.model import RectangleI, EllipseI, PointI, LabelI, MaskI, LineI, PolygonI, PolylineI, Roi, Shape
from ccipy.utils.cci_logger import CCILogger
import re

INSIGHT_POINT_LIST_RE = re.compile(r'points\[([^\]]+)\]')


def roi_to_geometry(shape: Shape) -> RoiGeometry | None:
    text_value = ""
    if shape.getTextValue():
        text_value = shape.getTextValue().getValue()

    if isinstance(shape, RectangleI):
        x_coord = shape.getX().getValue()
        y_coord = shape.getY().getValue()
        width = shape.getWidth().getValue()
        height = shape.getHeight().getValue()
        return RoiRectangle(x_coord, y_coord, width, height, text_value)
    
    if isinstance(shape, EllipseI):
        x_coord = shape.getX().getValue()
        y_coord = shape.getY().getValue()
        radius_x = shape.getRadiusX().getValue()
        radius_y = shape.getRadiusY().getValue()
        return RoiEllipse(x_coord, y_coord, radius_x * 2, radius_y * 2, text_value)
    
    if isinstance(shape, PolygonI):
        point_list = shape.getPoints().getValue()
        match = INSIGHT_POINT_LIST_RE.search(point_list)
        if match is not None:
            point_list = match.group(1)

        point_list = point_list.split(' ')
        
        point_list = [map(float, point.split(',')) for point in point_list]
        point_list = [RoiPoint(x, y) for x, y in point_list]
        
        return RoiPolygon(point_list)

    if isinstance(shape, (PointI, LabelI, MaskI, LineI, PolylineI)):
        # Currently not supported shapes
        CCILogger.warning(f"Shape type {type(shape)} is not supported for conversion to RoiGeometry.")
        return None


def rois_to_geometries(rois: list[Roi]) -> list[RoiGeometry]:
    geometries = []
    for roi in rois:
        for shape in roi.copyShapes():
            geometry = roi_to_geometry(shape)
            if geometry is not None:
                geometries.append(geometry)
    return geometries
