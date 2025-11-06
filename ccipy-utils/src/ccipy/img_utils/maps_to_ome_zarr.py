
from ccipy.utils import string_utils
from pathlib import Path
import dask.array as da
import numpy as np
from ome_zarr.io import parse_url
from ome_zarr.writer import write_multiscale
import pandas as pd
#import skimage.io as skio
import imageio.v3 as iio
import xmltodict
import zarr
import zarr.storage
import zarr.creation


def find_image_pyramids(maps_proj_path: Path, pyramid_file_name: str = "pyramid.xml") -> list[Path]:
    """ Find all image pyramids in the maps project folder.
        Args: 
            maps_proj_path (Path): Path to the maps project folder.
        returns:
            List of Paths to the image pyramids found
    """
    ids = []
    for pyramidXML_path in maps_proj_path.glob(f"**/{pyramid_file_name}"):
        image_pyramid = pyramidXML_path.parents[2]
        ids.append(image_pyramid)

    return ids

def get_pyramid_data_path(pyramid_file_folder: Path, default_folder_name: str = "image_pyramid") -> tuple[Path, str]:
    """ Get the pyramid data path and image id from the pyramid file folder.
        Args:
            pyramid_file_folder (Path): Path to the folder containing the pyramid data (i.e. one of the paths from find_image_pyramid).
            default_folder_name (str): Default name of the pyramid folder.
        Returns:
            Tuple containing the pyramid data path and image id.
    """
    img_folder = pyramid_file_folder
    if img_folder.name == default_folder_name:
        img_id = img_folder.parent.name
    else:
        img_id = img_folder.name
    pyramid_data_path = list(img_folder.glob("*/data"))[0]

    return pyramid_data_path, img_id


def get_first_tile(pyramid_data_path: Path, level: int = 0, column: int = 0, expected_tile_name: str = "tile_0.tif"):
    """ Get the first tile image from the pyramid data path."""
    
    lvl_path = pyramid_data_path.joinpath(f"l_{level}", f"c_{column}")
    tile_path = lvl_path.joinpath(expected_tile_name)
    tile_img = iio.imread(tile_path)
    return tile_img


def get_channel_name(image_pyramid: Path, params_file: str = "MultiChannelParams.xml"):
    """ Get the channel name from the MultiChannelParams.xml file in the image pyramid folder."""
    
    with open(image_pyramid.joinpath(params_file), "rb") as f:
        multichannel_dict = xmltodict.parse(f, xml_attribs=True)

    ch_name = multichannel_dict["MultiChannelParameters"]["Channel"]["Name"]
    return ch_name

class PyramidMetadata:
    def __init__(self, pyramid_dict, pyramid_path: Path):
        self.n_lvl = int(pyramid_dict["root"]["imageset"]["@levels"])
        self.height = int(pyramid_dict["root"]["imageset"]["@height"])
        self.width = int(pyramid_dict["root"]["imageset"]["@width"])
        self.overlap = int(pyramid_dict["root"]["imageset"]["@tileOverlap"])
        assert(self.overlap == 0), "Currently only non-overlapping tiles are supported"
        self.res_step = float(pyramid_dict["root"]["imageset"]["@step"])
        self.tile_width = int(pyramid_dict["root"]["imageset"]["@tileWidth"])
        self.tile_height = int(pyramid_dict["root"]["imageset"]["@tileHeight"])
        self.pix_size_x = float(pyramid_dict["root"]["metadata"]["pixelsize"]["x"])
        self.pix_size_y = float(pyramid_dict["root"]["metadata"]["pixelsize"]["y"])
        url_str = pyramid_dict["root"]["imageset"]["@url"]
        self.nr_rows = int(np.ceil(self.height / self.tile_height))
        self.nr_cols = int(np.ceil(self.width / self.tile_width))
        self.pyramid_path = pyramid_path
    
        self.url = url_str
        self.level_dir_prefix, self.col_dir_prefix, self.row_image_name = url_str.split("/")
        

def read_pyramid_metadata(pyramid_data_path: Path, dict_file: str = "pyramid.xml") -> PyramidMetadata:
    """ Read the pyramid metadata from the pyramid.xml file in the pyramid data path.
        Args:
            pyramid_data_path (Path): Path to the pyramid data folder.
            dict_file (str): Name of the pyramid metadata file.
        Returns:
            PyramidMetadata object containing the metadata.
    """

    with open(pyramid_data_path.joinpath(dict_file), "rb") as f:
        pyramid_dict = xmltodict.parse(f, xml_attribs=True)

    meta = PyramidMetadata(pyramid_dict, pyramid_data_path)
    return meta


def get_col_df(col_folder: Path, pyramid_meta_data: PyramidMetadata, dtype) -> pd.DataFrame:
    
    c_name = col_folder.name
    col_tiles = [f for f in col_folder.iterdir() if f.is_file and f.name.endswith('.tif')]

    col_df = pd.DataFrame(
        columns=[
            'row_idx',
            'col_idx',
            'tif_path',
            'corner_row',
            'corner_col',
            'size_row',
            'size_col',
            'data_type'
        ]
    )
    col_df['tif_path'] = col_tiles
    col_df['col_idx'] = c_name
    col_df['data_type'] = dtype
    col_df['size_row'] = pyramid_meta_data.tile_height
    col_df['size_col'] = pyramid_meta_data.tile_width

    row_idx = []
    cor_row = []
    cor_col = []

    for val in col_tiles:
        t_name = str(val.name).split("tile_")[1].split(".")[0]
        idx = int(t_name)
        row_idx.append(idx)
        cor_row.append(idx * pyramid_meta_data.tile_height)
        cor_col.append(int(c_name) * pyramid_meta_data.tile_width)

    col_df['row_idx'] = row_idx
    col_df['corner_row'] = cor_row
    col_df['corner_col'] = cor_col

    return col_df


def rm_tree(pth):
    pth = Path(pth)
    for child in pth.glob('*'):
        if child.is_file():
            child.unlink()
        else:
            rm_tree(child)
    pth.rmdir()


def mean_dtype(arr, **kwargs):
    return np.mean(arr, **kwargs).astype(arr.dtype)


def store_zarr_image(output_dir: Path, img_id: str, pyramid_meta_data: PyramidMetadata, channel_name: str, res_dtype, remove_if_exists: bool = False):
    """ Store the image pyramid as an OME-Zarr file.
        Args:
            output_dir (Path): Path to the output directory.
            img_id (str): Image ID.
            pyramid_meta_data (PyramidMetadata): Pyramid metadata object.
            channel_name (str): Channel name.
            res_dtype: Data type of the resulting image.
            remove_if_exists (bool): Whether to remove the existing OME-Zarr file if it exists.
    """
    z0_path = output_dir.joinpath(f"./{img_id}.zarr")
    
    if z0_path.exists():
        if remove_if_exists:
            rm_tree(z0_path)
        else:
            raise FileExistsError(f"The path {z0_path} already exists. Set remove_if_exists to True to remove it.")
            

    store = zarr.storage.LocalStore(z0_path)
    
    chunk_size_width = pyramid_meta_data.tile_width
    chunk_size_height = pyramid_meta_data.tile_height
    total_col = pyramid_meta_data.nr_cols * pyramid_meta_data.tile_width
    total_row = pyramid_meta_data.nr_rows * pyramid_meta_data.tile_height
    z = zarr.creation.open_array(
        store=store,
        mode="a",
        shape=(total_row, total_col),
        chunks=(chunk_size_height, chunk_size_width),
        dtype=res_dtype,
    )

    

    level_dir_path_str = string_utils.format_by_order(pyramid_meta_data.level_dir_prefix, [pyramid_meta_data.n_lvl - 1])
    
    level_path = pyramid_meta_data.pyramid_path.joinpath(level_dir_path_str)
    for col in range(pyramid_meta_data.nr_cols):
        col_dir_path_str = string_utils.format_by_order(pyramid_meta_data.col_dir_prefix, [col])
        col_folder = level_path.joinpath(col_dir_path_str)
        for row in range(pyramid_meta_data.nr_rows):
            row_dir_path_str = string_utils.format_by_order(pyramid_meta_data.row_image_name, [row])
            tif_path = col_folder.joinpath(row_dir_path_str)
            tmp_img = iio.imread(tif_path)

            row_1 = row * pyramid_meta_data.tile_height
            row_2 = row_1 + pyramid_meta_data.tile_height
            col_1 = col * pyramid_meta_data.tile_width
            col_2 = col_1 + pyramid_meta_data.tile_width
            z[row_1:row_2, col_1:col_2] = tmp_img

# it is still not quite clear to me why, but we need to rechunk de data at this stage
# if not zarr writting later on will fail
    d0 = da.from_zarr(store).rechunk(chunk_size_height,chunk_size_width)
    d1 = da.coarsen(mean_dtype, d0, {0:2,1:2}).rechunk(int(chunk_size_height/2),int(chunk_size_width/2))
    d2 = da.coarsen(mean_dtype, d0, {0:4,1:4}).rechunk(int(chunk_size_height/2),int(chunk_size_width/2))
    d3 = da.coarsen(mean_dtype, d0, {0:8,1:8}).rechunk(int(chunk_size_height/2),int(chunk_size_width/2))

# I can probably build this programmatically, for the moment I take a shortcut. 
# This assumes an image with full resolution and one downscale by 2x2
# here I assume that the original scale was in m but I am not sure

    initial_pix_size = float(pyramid_meta_data.pix_size_x) / 1e-9
    initial_pix_unit = 'nanometer'
    coordtfs = [
            [{'type': 'scale', 'scale': [initial_pix_size,initial_pix_size]},
            {'type': 'translation', 'translation': [0, 0]}],
            [{'type': 'scale', 'scale': [initial_pix_size*2,initial_pix_size*2]},
            {'type': 'translation', 'translation': [0, 0]}],
            [{'type': 'scale', 'scale': [initial_pix_size*4,initial_pix_size*4]},
            {'type': 'translation', 'translation': [0, 0]}],
            [{'type': 'scale', 'scale': [initial_pix_size*8,initial_pix_size*8]},
            {'type': 'translation', 'translation': [0, 0]}],
            ]
    axes = [{'name': 'y', 'type': 'space', 'unit': initial_pix_unit},
            {'name': 'x', 'type': 'space', 'unit': initial_pix_unit}]

    path = output_dir / (img_id+"-ome.zarr")

    if path.exists():
        rm_tree(path)

    zarr_loc = parse_url(path, mode='w')
    if zarr_loc is None:
        raise FileNotFoundError(f"Could not create zarr location at path: {path}")
    
    store = zarr_loc.store
    root = zarr.group(store=store)

    # Use OME write multiscale;
    write_multiscale([d0, d1, d2, d3],
            group=root, axes=axes, coordinate_transformations=coordtfs
            )
    # add omero metadata: the napari ome-zarr plugin uses this to pass rendering
    # options to napari.
    root.attrs['omero'] = {
            'channels': [{
                    'color': 'ffffff',
                    'label': channel_name,
                    'active': True,
                    'window': {
                    'end': int(d0.max().compute()),
                    'max': 65535,
                    'start': int(d0.min().compute()),
                    'min': 0,
                    }
                    }]
            }

    if z0_path.exists() and remove_if_exists:
        rm_tree(z0_path)
