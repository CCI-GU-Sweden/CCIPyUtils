"""
   Wrapper for stardist models in a way that is compatible with CCI code elsewhere
"""
from pathlib import Path
from ultralytics import YOLO


class CCIYoloWrapper:

    def __init__(self, model_name_or_path: str = "yolov8n.pt"):
        self.model_name = ""
        self.res = None
        self.model = YOLO(model_name_or_path)

    # @classmethod
    # def load_model_by_name(cls, model_name: str, basedir: str = 'models'):
    #     return cls(yolomodel(None, name=model_name, basedir=basedir), model_name=model_name, basedir=basedir)

    # @classmethod
    # def new_model(cls, config=yolo.models.Config2D, model_name: str = "latest", basedir: str = 'models'):
    #     return cls(yolomodel(config, name=model_name, basedir=basedir), model_name=model_name, basedir=basedir)

    def load_model(self, weights_path: Path):
        self.model = YOLO(weights_path)

    def predict(self, img):
        return self.model(img)

    def train(self, data_set_file: Path, image_size, batch=8, epochs=300, patience=100, ** kwargs):
        self.res = self.model.train(data=data_set_file, batch=batch, imgsz=image_size, epochs=epochs, patience=patience, **kwargs)
        return self.res
