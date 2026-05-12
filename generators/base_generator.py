from abc import ABC, abstractmethod

class BaseImageGenerator(ABC):
    @abstractmethod
    def generate_image(self, config, image_path=None):
        pass
    
    @abstractmethod
    def get_config_type(self):
        pass