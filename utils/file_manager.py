import os
import shutil
import requests
from datetime import datetime
from utils.constants import VIDEO_DIR, IMAGE_DIR, ALLOWED_VIDEO_EXTENSIONS, ALLOWED_IMAGE_EXTENSIONS

def generate_unique_filename(original_name):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    name, ext = os.path.splitext(original_name)
    return f"{name}_{timestamp}{ext}"

def save_video_file(source_path):
    if not os.path.exists(source_path):
        raise FileNotFoundError(f"文件不存在: {source_path}")
    
    ext = os.path.splitext(source_path)[1].lower()
    if ext not in ALLOWED_VIDEO_EXTENSIONS:
        raise ValueError(f"不支持的视频格式: {ext}")
    
    filename = generate_unique_filename(os.path.basename(source_path))
    dest_path = os.path.join(VIDEO_DIR, filename)
    shutil.copy2(source_path, dest_path)
    return dest_path

def save_image_file(source_path):
    if not os.path.exists(source_path):
        raise FileNotFoundError(f"文件不存在: {source_path}")
    
    ext = os.path.splitext(source_path)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValueError(f"不支持的图片格式: {ext}")
    
    filename = generate_unique_filename(os.path.basename(source_path))
    dest_path = os.path.join(IMAGE_DIR, filename)
    shutil.copy2(source_path, dest_path)
    return dest_path

def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)

def get_file_size(file_path):
    if os.path.exists(file_path):
        size = os.path.getsize(file_path)
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.2f} KB"
        else:
            return f"{size / (1024 * 1024):.2f} MB"
    return "0 B"

def download_image(url, filename=None):
    if not url:
        raise ValueError("URL不能为空")
    
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        if filename:
            ext = os.path.splitext(filename)[1].lower()
            if not ext:
                ext = '.jpg'
        else:
            ext = '.jpg'
            filename = f"generated_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
        
        dest_path = os.path.join(IMAGE_DIR, filename)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        
        with open(dest_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        return dest_path
    except requests.exceptions.RequestException as e:
        raise Exception(f"下载图片失败: {str(e)}")
