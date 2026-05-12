class ImageToVideo:
    def __init__(self, id=None, image_to_video_gen_config_id=None, dressed_model_id=None, 
                 video_path=None, config_name=None, created_at=None):
        self.id = id
        self.image_to_video_gen_config_id = image_to_video_gen_config_id
        self.dressed_model_id = dressed_model_id
        self.video_path = video_path
        self.config_name = config_name
        self.created_at = created_at
    
    def to_dict(self):
        return {
            'id': self.id,
            'image_to_video_gen_config_id': self.image_to_video_gen_config_id,
            'dressed_model_id': self.dressed_model_id,
            'video_path': self.video_path,
            'config_name': self.config_name,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get('id'),
            image_to_video_gen_config_id=data.get('image_to_video_gen_config_id'),
            dressed_model_id=data.get('dressed_model_id'),
            video_path=data.get('video_path'),
            config_name=data.get('config_name'),
            created_at=data.get('created_at')
        )