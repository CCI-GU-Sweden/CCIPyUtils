from ccipy.utils.roi_geometry import RoiEllipse, RoiPolygon, RoiRectangle, RoiGeometry, RoiPoint
from omero.model import RectangleI, EllipseI, PointI, LabelI, MaskI, LineI, PolygonI, PolylineI, Roi, Shape
from ccipy.utils.cci_logger import CCILogger
import re

INSIGHT_POINT_LIST_RE = re.compile(r'points\[([^\]]+)\]')


def roi_to_geometry(shape: Shape) -> RoiGeometry | None:
    text_value = ""
    if shape.getTextValue():
        text_value = shape.getTextValue().getValue()

    color = shape.getStrokeColor().val 

    if isinstance(shape, RectangleI):
        x_coord = shape.getX().getValue()
        y_coord = shape.getY().getValue()
        width = shape.getWidth().getValue()
        height = shape.getHeight().getValue()
        return RoiRectangle(x_coord, y_coord, width, height, color, text_value)
    
    if isinstance(shape, EllipseI):
        x_coord = shape.getX().getValue()
        y_coord = shape.getY().getValue()
        radius_x = shape.getRadiusX().getValue()
        radius_y = shape.getRadiusY().getValue()
        return RoiEllipse(x_coord, y_coord, radius_x * 2, radius_y * 2, color, text_value)
    
    if isinstance(shape, PolygonI):
        point_list = shape.getPoints().getValue()
        match = INSIGHT_POINT_LIST_RE.search(point_list)
        if match is not None:
            point_list = match.group(1)

        point_list = point_list.split(' ')
        
        point_list = [map(float, point.split(',')) for point in point_list]
        point_list = [RoiPoint(x, y) for x, y in point_list]
        
        return RoiPolygon(point_list, color, text_value)

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


def get_roi_data(roi: Roi) -> dict:
    data = {}
    
    return data


#  for roi in rois:
#         for shape in roi.copyShapes():
#             label = unwrap(shape.getTextValue())
#             # wrap label in double quotes in case it contains comma
#             label = "" if label is None else '"%s"' % label.replace(",", ".")
#             shape_type = shape.__class__.__name__.rstrip('I').lower()
#             # If shape has no Z or T, we may go through all planes...
#             the_z = unwrap(shape.theZ)
#             z_indexes = [the_z]
#             if the_z is None and all_planes:
#                 z_indexes = range(image.getSizeZ())
#             # Same for T...
#             the_t = unwrap(shape.theT)
#             t_indexes = [the_t]
#             if the_t is None and all_planes:
#                 t_indexes = range(image.getSizeT())

#             # get pixel intensities
#             for z in z_indexes:
#                 for t in t_indexes:
#                     if z is None or t is None:
#                         stats = None
#                     else:
#                         stats = roi_service.getShapeStatsRestricted(
#                             [shape.id.val], z, t, ch_indexes)
#                     for c, ch_index in enumerate(ch_indexes):
#                         row_data = {
#                             "image_id": image.getId(),
#                             "image_name": '"%s"' % image_name,
#                             "roi_id": roi.id.val,
#                             "shape_id": shape.id.val,
#                             "type": shape_type,
#                             "text": label,
#                             "z": z + 1 if z is not None else "",
#                             "t": t + 1 if t is not None else "",
#                             "channel": ch_names[ch_index],
#                             "points": stats[0].pointsCount[c] if stats else "",
#                             "min": stats[0].min[c] if stats else "",
#                             "max": stats[0].max[c] if stats else "",
#                             "sum": stats[0].sum[c] if stats else "",
#                             "mean": stats[0].mean[c] if stats else "",
#                             "std_dev": stats[0].stdDev[c] if stats else ""
#                         }
#                         # For SPW data, add Well info...
#                         if well_id is not None:
#                             row_data['well_id'] = well_id
#                             row_data['well_row'] = well_row
#                             row_data['well_column'] = well_column
#                             row_data['well_label'] = well_label
#                         add_shape_coords(shape, row_data,
#                                          pixel_size_x, pixel_size_y,
#                                          include_points)
#                         export_data.append(row_data)

#     return export_data