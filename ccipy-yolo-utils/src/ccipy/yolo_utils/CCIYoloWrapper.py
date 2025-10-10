"""
    Wrapper for stardist models in a way that is compatible with CCI code elsewhere
"""
    
class CCIYoloWrapper:
    
    def __init__(self,  model, model_name: str = "latest", basedir: str = 'models'):
        self.model_name = model_name
        self.basedir = basedir
        self.model = model
        
    @classmethod
    def load_model_by_name(cls, model_name: str, basedir: str = 'models') -> CCIYoloWrapper:
        return cls(yolomodel(None, name=model_name, basedir=basedir), model_name=model_name, basedir=basedir) 
    
    @classmethod
    def new_model(cls, config = stardist.models.Config2D, model_name: str = "latest", basedir: str = 'models') -> CCIYoloWrapper:
        return cls(yolomodel(config, name=model_name, basedir=basedir), model_name=model_name, basedir=basedir)
    
    
    def predict(self, img, **kwargs):
        return self.model.predict_instances(img, **kwargs)
    
    def train(self, X, Y, validation_data: Tuple[Any, Any], augmenter = None, epochs=300 **kwargs):
        X_val, Y_val = validation_data
        # self.model.train(X, Y, validation_data=validation_data, augmenter=augmenter, epochs=epochs, **kwargs)
        # self.model.optimize_thresholds(X, Y)
        #Y_val_pred = [self.model.predict_instances(x, n_tiles=self.model._guess_n_tiles(x), show_tile_progress=False)[0]
        #              for x in tqdm(X_val)]

        #taus = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
        #stats = [matching_dataset(Y_val, Y_val_pred, thresh=t, show_progress=False) for t in tqdm(taus)]
