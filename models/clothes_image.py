class ClothesImage:
    def __init__(self, id=None, name=None, image_path=None, created_at=None):
        self.id = id
        self.name = name
        self.image_path = image_path
        self.created_at = created_at
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'image_path': self.image_path,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            image_path=data.get('image_path'),
            created_at=data.get('created_at')
        )
