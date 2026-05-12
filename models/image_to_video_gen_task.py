class ImageToVideoGenTask:
    STATUS_SUBMITTED = "submitted"
    STATUS_CLOTHES_PROCESSED = "clothes_processed"
    STATUS_MODEL_PROCESSED = "model_processed"
    STATUS_VIDEO_GENERATED = "video_generated"
    STATUS_FAILED = "failed"
    
    def __init__(self, id=None, model_image_id=None, clothes_image_id=None,
                 image_gen_config_id=None, model_gen_config_id=None, 
                 image_to_video_gen_config_id=None, ai_clothes_id=None,
                 dressed_model_id=None, image_to_video_id=None,
                 submitted_at=None, status=None, result_desc=None,
                 external_task_id=None):
        self.id = id
        self.model_image_id = model_image_id
        self.clothes_image_id = clothes_image_id
        self.image_gen_config_id = image_gen_config_id
        self.model_gen_config_id = model_gen_config_id
        self.image_to_video_gen_config_id = image_to_video_gen_config_id
        self.ai_clothes_id = ai_clothes_id
        self.dressed_model_id = dressed_model_id
        self.image_to_video_id = image_to_video_id
        self.submitted_at = submitted_at
        self.status = status
        self.result_desc = result_desc
        self.external_task_id = external_task_id
    
    def to_dict(self):
        return {
            'id': self.id,
            'model_image_id': self.model_image_id,
            'clothes_image_id': self.clothes_image_id,
            'image_gen_config_id': self.image_gen_config_id,
            'model_gen_config_id': self.model_gen_config_id,
            'image_to_video_gen_config_id': self.image_to_video_gen_config_id,
            'ai_clothes_id': self.ai_clothes_id,
            'dressed_model_id': self.dressed_model_id,
            'image_to_video_id': self.image_to_video_id,
            'submitted_at': self.submitted_at,
            'status': self.status,
            'result_desc': self.result_desc,
            'external_task_id': self.external_task_id
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get('id'),
            model_image_id=data.get('model_image_id'),
            clothes_image_id=data.get('clothes_image_id'),
            image_gen_config_id=data.get('image_gen_config_id'),
            model_gen_config_id=data.get('model_gen_config_id'),
            image_to_video_gen_config_id=data.get('image_to_video_gen_config_id'),
            ai_clothes_id=data.get('ai_clothes_id'),
            dressed_model_id=data.get('dressed_model_id'),
            image_to_video_id=data.get('image_to_video_id'),
            submitted_at=data.get('submitted_at'),
            status=data.get('status'),
            result_desc=data.get('result_desc'),
            external_task_id=data.get('external_task_id')
        )
    
    def get_status_display(self):
        status_map = {
            self.STATUS_SUBMITTED: '已提交',
            self.STATUS_CLOTHES_PROCESSED: '已处理衣服图片',
            self.STATUS_MODEL_PROCESSED: '已处理模特图片',
            self.STATUS_VIDEO_GENERATED: '已完成图生视频',
            self.STATUS_FAILED: '失败'
        }
        return status_map.get(self.status, self.status)