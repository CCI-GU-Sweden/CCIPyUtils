import numpy as np
from stardist.models import StarDist2D


def get_latest_model_name(file_path="latest.mod"):
    with open(file_path, "r", encoding="utf-8") as f:
        latest_model = f.read()
    return latest_model


def save_latest_model_name(model_name, file_path="latest.mod"):
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(model_name)
        
  
def get_latest_sd_model(basedir='models', file_path="latest.mod"):
    latest_model = get_latest_model_name(file_path)
    model = StarDist2D(None, name=latest_model, basedir=basedir)
    return model

def get_sd_model(model_name, basedir='models'):
    model = StarDist2D(None, name=model_name, basedir=basedir)
    return model
    
def split_slices(vol, depth_axis=0, copy=False):
    # Move depth axis to the front so indexing is simple and returns views
    v = np.moveaxis(vol, depth_axis, 0)  # shape -> (Z, ..., ...)
    # Return views (no copy) or copies if you prefer
    return [s if not copy else s.copy() for s in v]


def random_fliprot(img, mask): 
    assert img.ndim >= mask.ndim
    axes = tuple(range(mask.ndim))
    perm = tuple(np.random.permutation(axes))
    img = img.transpose(perm + tuple(range(mask.ndim, img.ndim))) 
    mask = mask.transpose(perm) 
    for ax in axes: 
        if np.random.rand() > 0.5:
            img = np.flip(img, axis=ax)
            mask = np.flip(mask, axis=ax)
    return img, mask 

def random_intensity_change(img):
    img = img*np.random.uniform(0.6,2) + np.random.uniform(-0.2,0.2)
    return img

def to_gray(yx_or_yxc: np.ndarray) -> np.ndarray:
    """Return a 2D float32 image in YX. If RGB/RGBA, convert to luminance."""
    x = yx_or_yxc
    if x.ndim == 2:
        g = x.astype(np.float32, copy=False)
    elif x.ndim == 3 and x.shape[-1] in (3, 4):  # YX3 or YX4
        w = np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)  # sRGB luma
        g = (x[..., :3].astype(np.float32) * w).sum(axis=-1)
    else:
        raise ValueError(f"Expected 2D or 3-channel image, got {x.shape}")
    return g


def augmenter(x, y):
    """Augmentation of a single input/label image pair.
    x is an input image
    y is the corresponding ground-truth label image
    """
    x, y = random_fliprot(x, y)
    x = random_intensity_change(x)
    # add some gaussian noise
    sig = 0.02*np.random.uniform(0,1)
    x = x + sig*np.random.normal(0,1,x.shape)
    return x, y

def prune_empty_labels(images, labels):
    img_lab = [(i,l) for (i,l) in zip(images,labels) if np.max(l)>0]
    return zip(*img_lab)
