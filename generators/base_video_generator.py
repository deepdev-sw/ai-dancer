from abc import ABC, abstractmethod

class BaseVideoGenerator(ABC):
    @abstractmethod
    def generate_video(self, config, original_video_path, model_image_path):
        """
        提交视频生成任务
        
        Args:
            config: 视频生成配置对象
            original_video_path: 原始跳舞视频路径
            model_image_path: 模特图片路径
        
        Returns:
            dict: 包含 task_id 和其他相关信息
        """
        pass
    
    @abstractmethod
    def check_task_status(self, task_id):
        """
        检查任务状态
        
        Args:
            task_id: 任务ID
        
        Returns:
            dict: 包含 status, result_url, error_message 等信息
        """
        pass
    
    @abstractmethod
    def get_config_type(self):
        """
        返回配置类型标识
        
        Returns:
            str: 配置类型标识
        """
        pass