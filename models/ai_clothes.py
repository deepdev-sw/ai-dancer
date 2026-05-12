class AiClothes:
    def __init__(self, id=None, original_clothes_id=None, new_image_path=None, original_name=None, created_at=None):
        self.id = id
        self.original_clothes_id = original_clothes_id
        self.new_image_path = new_image_path
        self.original_name = original_name
        self.created_at = created_at
    
    def to_dict(self):
        return {
            'id': self.id,
            'original_clothes_id': self.original_clothes_id,
            'new_image_path': self.new_image_path,
            'original_name': self.original_name,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get('id'),
            original_clothes_id=data.get('original_clothes_id'),
            new_image_path=data.get('new_image_path'),
            original_name=data.get('original_name'),
            created_at=data.get('created_at')
        )
