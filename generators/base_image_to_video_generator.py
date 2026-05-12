from abc import ABC, abstractmethod

class BaseImageToVideoGenerator(ABC):
    @abstractmethod
    def generate_video(self, config, image_path):
        pass
    
    @abstractmethod
    def check_task_status(self, task_id, video_gen_config):
        pass
    
    @abstractmethod
    def get_config_type(self):
        pass