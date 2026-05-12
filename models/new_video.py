class NewVideo:
    def __init__(self, id=None, original_video_id=None, dressed_model_id=None, new_video_path=None, original_video_name=None, created_at=None):
        self.id = id
        self.original_video_id = original_video_id
        self.dressed_model_id = dressed_model_id
        self.new_video_path = new_video_path
        self.original_video_name = original_video_name
        self.created_at = created_at
    
    def to_dict(self):
        return {
            'id': self.id,
            'original_video_id': self.original_video_id,
            'dressed_model_id': self.dressed_model_id,
            'new_video_path': self.new_video_path,
            'original_video_name': self.original_video_name,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get('id'),
            original_video_id=data.get('original_video_id'),
            dressed_model_id=data.get('dressed_model_id'),
            new_video_path=data.get('new_video_path'),
            original_video_name=data.get('original_video_name'),
            created_at=data.get('created_at')
        )
