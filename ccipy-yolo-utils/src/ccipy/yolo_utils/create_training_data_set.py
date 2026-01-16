from pathlib import Path
import glob
import shutil


def create_training_set(path_to_images: Path, path_to_vectors: Path, destination_path: Path, label_names: list[tuple[int, str]]) -> None:
    """Create a YOLO training set by copying images and annotations to the destination path.
    Args:
        path_to_images (Path): Path to the directory containing images.
        path_to_annotations (Path): Path to the directory containing annotation files.
        destination_path (Path): Path to the destination directory for the training set.
        label_names (list[tuple[int, str]]): List of tuples defining class indices and their names.
    """
    # Create destination directories
    images_dest_path = destination_path / Path("images")
    labels_dest_path = destination_path / Path("labels")
    
    images_dest_val = images_dest_path / Path("val")
    images_dest_train = images_dest_path / Path("train")
    
    labels_dest_val = labels_dest_path / Path("val")
    labels_dest_train = labels_dest_path / Path("train")
    
    images_dest_val.mkdir(parents=True, exist_ok=True)
    images_dest_train.mkdir(parents=True, exist_ok=True)
    labels_dest_val.mkdir(parents=True, exist_ok=True)
    labels_dest_train.mkdir(parents=True, exist_ok=True)

    img_exts = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp"}
    vec_exts = {".txt"}

    images = sorted([str(p) for p in path_to_images.iterdir() if p.suffix.lower() in img_exts])
    label_vectors = sorted([str(p) for p in path_to_vectors.iterdir() if p.suffix.lower() in vec_exts])

    #sort lists here!!!

    for idx, img in enumerate(images):
        if idx % 2 == 0:
            shutil.copy2(img, images_dest_train)
        else:
            shutil.copy2(img, images_dest_val)

    for idx, lbl in enumerate(label_vectors):
        if idx % 2 == 0:
            shutil.copy2(lbl, labels_dest_train)
        else:
            shutil.copy2(lbl, labels_dest_val)
        
    dataset_file = destination_path / Path("dataset.yaml")
    with open(dataset_file, 'w') as dataset_file:
        dataset_file.write("train: ./images/train/\n")
        dataset_file.write("val: ./images/val/\n")
        dataset_file.write("names:\n")
        for class_index, class_name in label_names:
            dataset_file.write(f"  {class_index}: {class_name}\n")

        dataset_file.close()
