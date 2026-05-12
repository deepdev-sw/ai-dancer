import os

BASE_DIR = os.getcwd()
from utils.log_manager import log_manager
log_manager.info(f"BASE_DIR: {BASE_DIR}")

DATA_DIR = os.path.join(BASE_DIR, 'data')
log_manager.info(f"DATA_DIR: {DATA_DIR}")

VIDEO_DIR = os.path.join(DATA_DIR, 'videos')
IMAGE_DIR = os.path.join(DATA_DIR, 'images')

# 自动创建目录
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)
DATABASE_PATH = os.path.join(DATA_DIR, 'ai_dancer.db')

ALLOWED_VIDEO_EXTENSIONS = ('.mp4', '.avi', '.mov', '.mkv')
ALLOWED_IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')
