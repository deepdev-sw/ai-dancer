class ModelGenConfig:
    CONFIG_TYPE_VOLC_ENGINE = "火山引擎图片生成API"
    
    def __init__(self, id=None, name=None, config_type=None, config_content=None, created_at=None):
        self.id = id
        self.name = name
        self.config_type = config_type
        self.config_content = config_content
        self.created_at = created_at
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'config_type': self.config_type,
            'config_content': self.config_content,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            config_type=data.get('config_type'),
            config_content=data.get('config_content'),
            created_at=data.get('created_at')
        )