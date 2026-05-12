import os
import time
import httpx
from .base_image_to_video_generator import BaseImageToVideoGenerator
from models.image_to_video_gen_config import ImageToVideoGenConfig

class VolcEngineImageToVideoGenerator(BaseImageToVideoGenerator):
    def generate_video(self, config, image_path):
        try:
            from volcenginesdkarkruntime import Ark
        except ImportError:
            raise ImportError("请先安装火山引擎SDK: pip install 'volcengine-python-sdk[ark]'")
        
        import json
        config_content = json.loads(config.config_content)
        
        api_key = config_content.get('apiKey')
        model_id = config_content.get('modelId')
        prompt = config_content.get('prompt')
        resolution = config_content.get('resolution', '720p')
        
        if not api_key:
            return {'success': False, 'error_message': '配置中缺少api_key'}
        
        client = Ark(
            base_url="https://ark.cn-beijing.volces.com/api/v3",
            api_key=api_key,
        )
        
        content = []
        if prompt:
            content.append({
                'type': 'text',
                'text': f"{prompt}"
            })
        
        if image_path and os.path.exists(image_path):
            content.append({
                'type': 'image_url',
                'image_url': {
                    'url': self._upload_image(image_path, config_content)
                }
            })
        
        resolution_map = {
            '480p': '480P',
            '720p': '720P',
            '1080p': '1080P'
        }
        
        try:
            create_result = client.content_generation.tasks.create(
                model=model_id,
                content=content,
                resolution=resolution_map.get(resolution, '720P')
            )
            # 打印create_result
            print(create_result)
            
            if create_result and hasattr(create_result, 'id'):
                return {
                    'success': True,
                    'task_id': create_result.id,
                    'message': '任务提交成功'
                }
            else:
                return {'success': False, 'error_message': '任务创建失败'}
                
        except Exception as e:
            return {'success': False, 'error_message': str(e)}
    
    def _upload_image(self, image_path, config_content):
        import base64
        
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        ext = os.path.splitext(image_path)[1].lower()
        if ext == '.jpg' or ext == '.jpeg':
            mime_type = 'image/jpeg'
        elif ext == '.png':
            mime_type = 'image/png'
        else:
            mime_type = 'image/jpeg'
        
        base64_encoded = base64.b64encode(image_data).decode('utf-8')
        return f"data:{mime_type};base64,{base64_encoded}"
    
    def check_task_status(self, task_id, video_gen_config):
        try:
            from volcenginesdkarkruntime import Ark
        except ImportError:
            return {'success': False, 'error_message': 'SDK未安装'}
        
        try:
            import json
            config_content = json.loads(video_gen_config.config_content)
            api_key = config_content.get('apiKey')
            client = Ark(
                base_url="https://ark.cn-beijing.volces.com/api/v3",
                api_key=api_key,
            )
            
            get_result = client.content_generation.tasks.get(task_id=task_id)
            # 打印get_result
            print(get_result)
            
            status = get_result.status
            
            if status == "succeeded":
                result_url = get_result.content.video_url
                return {
                    'success': True,
                    'status': 'success',
                    'result_url': result_url,
                    'error_message': None
                }
            elif status == "failed" or status == "canceled" or status == "expired":
                error_msg = get_result.error.message if hasattr(get_result, 'error') else '任务失败'
                return {
                    'success': True,
                    'status': 'failed',
                    'result_url': None,
                    'error_message': error_msg
                }
            else:
                return {
                    'success': True,
                    'status': 'processing',
                    'result_url': None,
                    'error_message': None
                }
                
        except Exception as e:
            return {'success': False, 'error_message': str(e)}
    
    def get_config_type(self):
        return ImageToVideoGenConfig.CONFIG_TYPE_VOLC_ENGINE_VIDEO_API