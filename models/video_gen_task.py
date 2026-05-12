class VideoGenTask:
    STATUS_PROCESSING = "processing"
    STATUS_SUCCESS = "success"
    STATUS_FAILED = "failed"
    
    def __init__(self, id=None, status=None, result_desc=None, submitted_at=None,
                 external_task_id=None, new_video_id=None, video_gen_config_id=None, 
                 original_video_id=None, dressed_model_id=None):
        self.id = id
        self.status = status
        self.result_desc = result_desc
        self.submitted_at = submitted_at
        self.external_task_id = external_task_id
        self.new_video_id = new_video_id
        self.video_gen_config_id = video_gen_config_id
        self.original_video_id = original_video_id
        self.dressed_model_id = dressed_model_id
    
    def to_dict(self):
        return {
            'id': self.id,
            'status': self.status,
            'result_desc': self.result_desc,
            'submitted_at': self.submitted_at,
            'external_task_id': self.external_task_id,
            'new_video_id': self.new_video_id,
            'video_gen_config_id': self.video_gen_config_id,
            'original_video_id': self.original_video_id,
            'dressed_model_id': self.dressed_model_id
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get('id'),
            status=data.get('status'),
            result_desc=data.get('result_desc'),
            submitted_at=data.get('submitted_at'),
            external_task_id=data.get('external_task_id'),
            new_video_id=data.get('new_video_id'),
            video_gen_config_id=data.get('video_gen_config_id'),
            original_video_id=data.get('original_video_id'),
            dressed_model_id=data.get('dressed_model_id')
        )
    
    def get_status_display(self):
        status_map = {
            self.STATUS_PROCESSING: '处理中',
            self.STATUS_SUCCESS: '成功',
            self.STATUS_FAILED: '失败'
        }
        return status_map.get(self.status, self.status)