class DanceVideo:
    def __init__(self, id=None, name=None, video_path=None, created_at=None):
        self.id = id
        self.name = name
        self.video_path = video_path
        self.created_at = created_at
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'video_path': self.video_path,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            video_path=data.get('video_path'),
            created_at=data.get('created_at')
        )
