import sys
from PyQt5.QtWidgets import (QMainWindow, QApplication, QTabWidget, QWidget, 
                             QVBoxLayout, QLabel, QStatusBar)
from database.database_manager import DatabaseManager
from ui.video_tab import VideoTab
from ui.model_tab import ModelTab
from ui.clothes_tab import ClothesTab
from ui.ai_clothes_tab import AiClothesTab
from ui.dressed_model_tab import DressedModelTab
from ui.new_video_tab import NewVideoTab
from ui.image_gen_config_tab import ImageGenConfigTab
from ui.model_gen_config_tab import ModelGenConfigTab
from ui.video_gen_config_tab import VideoGenConfigTab
from ui.image_to_video_gen_config_tab import ImageToVideoGenConfigTab
from ui.video_gen_task_tab import VideoGenTaskTab
from ui.ai_dance_video_gen_task_tab import AiDanceVideoGenTaskTab
from ui.image_to_video_tab import ImageToVideoTab
from ui.image_to_video_gen_task_tab import ImageToVideoGenTaskTab
from utils.task_recovery import TaskRecovery

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self._recover_processing_tasks()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('AI换衣视频生成软件')
        self.setGeometry(100, 100, 1200, 800)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        self.tab_widget = QTabWidget()
        
        self.video_tab = VideoTab(self.db_manager)
        self.model_tab = ModelTab(self.db_manager)
        self.clothes_tab = ClothesTab(self.db_manager)
        self.image_gen_config_tab = ImageGenConfigTab(self.db_manager)
        self.model_gen_config_tab = ModelGenConfigTab(self.db_manager)
        self.video_gen_config_tab = VideoGenConfigTab(self.db_manager)
        self.image_to_video_gen_config_tab = ImageToVideoGenConfigTab(self.db_manager)
        self.ai_clothes_tab = AiClothesTab(self.db_manager)
        self.dressed_model_tab = DressedModelTab(self.db_manager)
        self.new_video_tab = NewVideoTab(self.db_manager)
        self.video_gen_task_tab = VideoGenTaskTab(self.db_manager)
        self.ai_dance_video_gen_task_tab = AiDanceVideoGenTaskTab(self.db_manager)
        self.image_to_video_tab = ImageToVideoTab(self.db_manager)
        self.image_to_video_gen_task_tab = ImageToVideoGenTaskTab(self.db_manager)
        
        self.tab_widget.addTab(self.video_tab, '跳舞视频')
        self.tab_widget.addTab(self.model_tab, '模特图片')
        self.tab_widget.addTab(self.clothes_tab, '衣服图片')
        self.tab_widget.addTab(self.image_gen_config_tab, '衣服抠图配置')
        self.tab_widget.addTab(self.model_gen_config_tab, '模特生成配置')
        self.tab_widget.addTab(self.video_gen_config_tab, '视频生成配置')
        self.tab_widget.addTab(self.image_to_video_gen_config_tab, '图生视频配置')
        self.tab_widget.addTab(self.ai_clothes_tab, 'AI处理衣服')
        self.tab_widget.addTab(self.dressed_model_tab, '穿新衣服模特')
        self.tab_widget.addTab(self.image_to_video_tab, '图生视频')
        self.tab_widget.addTab(self.new_video_tab, '生成视频')
        self.tab_widget.addTab(self.video_gen_task_tab, '视频生成任务')
        self.tab_widget.addTab(self.ai_dance_video_gen_task_tab, 'AI跳舞视频生成任务')
        self.tab_widget.addTab(self.image_to_video_gen_task_tab, '图生视频生成任务')
        
        self.layout.addWidget(self.tab_widget)
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage('欢迎使用AI换衣视频生成软件')
    
    def _recover_processing_tasks(self):
        task_recovery = TaskRecovery(self.db_manager)
        task_recovery.recover_processing_tasks()
    
    def closeEvent(self, event):
        # self.db_manager.close()
        event.accept()
