from abc import ABC, abstractmethod

class ModelImageGenerator(ABC):
    @abstractmethod
    def generate_image(self, config, model_image_path, clothes_image_path):
        pass
    
    @abstractmethod
    def get_config_type(self):
        pass