import os
import base64
from generators.base_generator import BaseImageGenerator
from models.image_gen_config import ImageGenConfig

class VolcEngineImageGenerator(BaseImageGenerator):
    def generate_image(self, config, image_path=None):
        try:
            from volcenginesdkarkruntime import Ark
        except ImportError:
            raise ImportError("请先安装火山引擎SDK: pip install 'volcengine-python-sdk[ark]'")
        
        import json
        config_content = json.loads(config.config_content)
        
        api_key = config_content.get('api_key')
        model_id = config_content.get('model')
        prompt = config_content.get('prompt', '')
        size = config_content.get('size', '2K')
        output_format = config_content.get('output_format', 'jpeg')
        
        if not api_key:
            raise ValueError("配置中缺少apiKey")
        if not model_id:
            raise ValueError("配置中缺少modelId")
        if not prompt:
            raise ValueError("配置中缺少prompt")
        
        image_base64 = None
        if image_path and os.path.exists(image_path):
            image_base64 = self.image_to_base64(image_path)
        
        client = Ark(
            base_url="https://ark.cn-beijing.volces.com/api/v3",
            api_key=api_key,
        )
        
        images_response = client.images.generate(
            model=model_id,
            prompt=prompt,
            sequential_image_generation="disabled",
            response_format="url",
            size=size,
            stream=False,
            watermark=False,
            output_format=output_format,
            image=image_base64
        )
        
        if images_response.data and len(images_response.data) > 0:
            return images_response.data[0].url
        return None
    
    def image_to_base64(self, image_path):
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        ext = os.path.splitext(image_path)[1].lower()
        if ext == '.jpg' or ext == '.jpeg':
            mime_type = 'image/jpeg'
        elif ext == '.png':
            mime_type = 'image/png'
        elif ext == '.gif':
            mime_type = 'image/gif'
        elif ext == '.bmp':
            mime_type = 'image/bmp'
        else:
            mime_type = 'image/jpeg'
        
        base64_encoded = base64.b64encode(image_data).decode('utf-8')
        return f"data:{mime_type};base64,{base64_encoded}"
    
    def get_config_type(self):
        return ImageGenConfig.CONFIG_TYPE_VOLC_ENGINE