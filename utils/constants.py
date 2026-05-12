import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, 'data')
VIDEO_DIR = os.path.join(DATA_DIR, 'videos')
IMAGE_DIR = os.path.join(DATA_DIR, 'images')
DATABASE_PATH = os.path.join(DATA_DIR, 'ai_dancer.db')

ALLOWED_VIDEO_EXTENSIONS = ('.mp4', '.avi', '.mov', '.mkv')
ALLOWED_IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')
