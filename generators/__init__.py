from .base_generator import BaseImageGenerator
from .volc_engine_generator import VolcEngineImageGenerator
from .base_video_generator import BaseVideoGenerator
from .wanxiang_video_generator import WanxiangVideoGenerator
from .model_image_generator import ModelImageGenerator
from .model_volc_engine_generator import VolcEngineModelGenerator
from .base_image_to_video_generator import BaseImageToVideoGenerator
from .volc_engine_image_to_video_generator import VolcEngineImageToVideoGenerator

def get_generator(config_type):
    generators = {
        VolcEngineImageGenerator().get_config_type(): VolcEngineImageGenerator
    }
    if config_type in generators:
        return generators[config_type]()
    raise ValueError(f"不支持的图片生成配置类型: {config_type}")

def get_video_generator(config_type):
    generators = {
        WanxiangVideoGenerator().get_config_type(): WanxiangVideoGenerator
    }
    if config_type in generators:
        return generators[config_type]()
    raise ValueError(f"不支持的视频生成配置类型: {config_type}")

def get_model_generator(config_type):
    generators = {
        VolcEngineModelGenerator().get_config_type(): VolcEngineModelGenerator
    }
    if config_type in generators:
        return generators[config_type]()
    raise ValueError(f"不支持的模特生成配置类型: {config_type}")

def get_image_to_video_generator(config_type):
    generators = {
        VolcEngineImageToVideoGenerator().get_config_type(): VolcEngineImageToVideoGenerator
    }
    if config_type in generators:
        return generators[config_type]()
    raise ValueError(f"不支持的图生视频配置类型: {config_type}")