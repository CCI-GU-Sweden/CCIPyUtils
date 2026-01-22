from ccipy.omero.cci_omero_connection import OmeroConnection
from ccipy.omero.omero_getter_ctx import OmeroGetterCtx
from ccipy.utils.cci_logger import CCILogger


def remove_rois_from_image(omero_conn: OmeroConnection, image_id: int) -> int:
    """Remove all ROIs from an OMERO image.
    Args:
        omero_conn (OmeroConnection): OMERO connection object.
        image_id (int): ID of the OMERO image.
    """
    with OmeroGetterCtx(omero_conn) as getter:
        rois = getter.get_rois_for_image(image_id)
        us = omero_conn.get_update_service()
        for roi in rois:
            us.deleteObject(roi)

        CCILogger.info(f"Removed {len(rois)} ROIs from image ID {image_id}.")
    return len(rois)


def remove_rois_from_dataset(omero_conn: OmeroConnection, dataset_id: int) -> int:
    """Remove all ROIs from all images in an OMERO dataset.
    Args:
        omero_conn (OmeroConnection): OMERO connection object.
        dataset_id (int): ID of the OMERO dataset.
    """
    with OmeroGetterCtx(omero_conn) as getter:
        image_ids = getter.get_image_ids_from_dataset(dataset_id)
        tot_removed = 0
        for image_id in image_ids:
            tot_removed += remove_rois_from_image(omero_conn, image_id)

        CCILogger.info(f"Removed {tot_removed} ROIs from dataset ID {dataset_id} containing {len(list(image_ids))} images.")

    return tot_removed
