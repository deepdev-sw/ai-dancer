import httpx
import json
import os
import uuid
import oss2
from .base_video_generator import BaseVideoGenerator
from models.video_gen_config import VideoGenConfig

class WanxiangVideoGenerator(BaseVideoGenerator):
    def __init__(self):
        self.base_url = "https://dashscope.aliyuncs.com"
        self.api_key = None
    
    def _get_oss_client(self, config_content):
        access_key_id = config_content.get('aliyunAccessKeyId', '')
        access_key_secret = config_content.get('aliyunAccessKeySecret', '')
        endpoint = config_content.get('aliyunEndpoint', '')
        bucket_name = config_content.get('aliyunBucketName', '')
        
        auth = oss2.Auth(access_key_id, access_key_secret)
        return oss2.Bucket(auth, endpoint, bucket_name)
    
    def _upload_file_to_oss(self, oss_client, file_path):
        file_ext = os.path.splitext(file_path)[1]
        object_name = f"ai-dancer/{uuid.uuid4().hex}{file_ext}"
        
        oss_client.put_object_from_file(object_name, file_path)
        
        return oss_client.sign_url('GET', object_name, 3600)
    
    def generate_video(self, config, original_video_path, model_image_path):
        try:
            config_content = json.loads(config.config_content)
            api_key = config_content.get('apiKey', '')
            service_mode = config_content.get('serviceMode', 'standard')
            
            self.api_key = api_key
            
            oss_client = self._get_oss_client(config_content)
            
            video_url = self._upload_file_to_oss(oss_client, original_video_path)
            image_url = self._upload_file_to_oss(oss_client, model_image_path)
            
            headers = {
                'X-DashScope-Async': 'enable',
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            mode = service_mode
            
            payload = {
                "model": "wan2.2-animate-move",
                "input": {
                    "image_url": image_url,
                    "video_url": video_url,
                    "watermark": False
                },
                "parameters": {
                    "mode": mode
                }
            }
            
            response = httpx.post(
                f"{self.base_url}/api/v1/services/aigc/image2video/video-synthesis",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            response.raise_for_status()
            result = response.json()
            # 打印result
            print(result)
            
            output = result.get('output', {})
            task_id = output.get('task_id')
            
            if task_id:
                return {
                    'success': True,
                    'task_id': task_id,
                    'message': '任务提交成功'
                }
            else:
                return {
                    'success': False,
                    'error_message': result.get('message', '提交失败')
                }
        
        except Exception as e:
            return {
                'success': False,
                'error_message': str(e)
            }
    
    def check_task_status(self, task_id):
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}'
            }
            
            response = httpx.get(
                f"{self.base_url}/api/v1/tasks/{task_id}",
                headers=headers,
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            # 打印result
            print(result)
            
            output = result.get('output', {})
            task_status = output.get('task_status', 'UNKNOWN')
            
            status_mapping = {
                'PENDING': 'processing',
                'RUNNING': 'processing',
                'SUCCEEDED': 'success',
                'FAILED': 'failed',
                'CANCELED': 'failed',
                'UNKNOWN': 'failed'
            }
            
            status = status_mapping.get(task_status, 'unknown')
            result_url = None
            
            if status == 'success':
                results = output.get('results', {})
                result_url = results.get('video_url')
            
            return {
                'success': True,
                'status': status,
                'result_url': result_url,
                'error_message': output.get('message'),
                'progress': result.get('progress', 0)
            }
        
        except Exception as e:
            return {
                'success': False,
                'status': 'failed',
                'error_message': str(e)
            }
    
    def get_config_type(self):
        return VideoGenConfig.CONFIG_TYPE_WANXIANG_ACTION_API