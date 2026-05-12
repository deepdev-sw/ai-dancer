from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QComboBox, QLabel, QMessageBox)
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, pyqtSlot
from models.ai_dance_video_gen_task import AiDanceVideoGenTask
from models.image_gen_config import ImageGenConfig
from models.model_gen_config import ModelGenConfig
from models.video_gen_config import VideoGenConfig
from generators import get_generator, get_model_generator, get_video_generator
from utils.file_manager import download_image, generate_unique_filename
from utils.constants import VIDEO_DIR
from database.database_manager import DatabaseManager
import httpx
import os
import traceback

class TaskProcessor(QThread):
    task_finished = pyqtSignal()
    task_failed = pyqtSignal(str)
    
    def __init__(self, task_data):
        super().__init__()
        self.task_data = task_data
        self.local_task_id = task_data['task_id']
        self.local_db_manager = None
    
    def run(self):
        try:
            self.local_db_manager = DatabaseManager()
            self._process_clothes()
        except Exception as e:
            self._handle_error(f'任务处理失败: {str(e)}\n\n{traceback.format_exc()}')
        finally:
            if self.local_db_manager:
                self.local_db_manager.close()
    
    def _process_clothes(self):
        clothes_image = self.task_data['clothes_image']
        image_config = self.task_data['image_config']
        
        image_gen_config = ImageGenConfig.from_dict(image_config)
        generator = get_generator(image_gen_config.config_type)
        
        result = generator.generate_image(image_gen_config, clothes_image['image_path'])
        
        if result:
            saved_path = download_image(result)
            
            ai_clothes_id = self.local_db_manager.add_ai_clothes(
                original_clothes_id=clothes_image['id'],
                new_image_path=saved_path
            )
            
            self.local_db_manager.update_ai_dance_video_gen_task(
                self.local_task_id,
                status=AiDanceVideoGenTask.STATUS_CLOTHES_PROCESSED,
                ai_clothes_id=ai_clothes_id
            )
            
            ai_clothes = self.local_db_manager.get_ai_clothes_by_id(ai_clothes_id)
            self._process_model(ai_clothes)
        else:
            self._handle_error('衣服图片处理失败，未返回结果')
    
    def _process_model(self, ai_clothes):
        model_image = self.task_data['model_image']
        
        task = self.local_db_manager.get_ai_dance_video_gen_task_by_id(self.local_task_id)
        model_gen_config_dict = self.local_db_manager.get_model_gen_config_by_id(task['model_gen_config_id'])
        model_gen_config = ModelGenConfig.from_dict(model_gen_config_dict)
        
        generator = get_model_generator(model_gen_config.config_type)
        
        result = generator.generate_image(
            model_gen_config, 
            model_image['image_path'], 
            ai_clothes['new_image_path']
        )
        
        if result:
            saved_path = download_image(result)
            
            dressed_model_id = self.local_db_manager.add_dressed_model(
                original_model_id=model_image['id'],
                ai_clothes_id=ai_clothes['id'],
                new_image_path=saved_path
            )
            
            self.local_db_manager.update_ai_dance_video_gen_task(
                self.local_task_id,
                status=AiDanceVideoGenTask.STATUS_MODEL_PROCESSED,
                dressed_model_id=dressed_model_id
            )
            
            dressed_model = self.local_db_manager.get_dressed_model_by_id(dressed_model_id)
            self._process_video(dressed_model)
        else:
            self._handle_error('模特图片处理失败，未返回结果')
    
    def _process_video(self, dressed_model):
        dance_video = self.task_data['dance_video']
        
        task = self.local_db_manager.get_ai_dance_video_gen_task_by_id(self.local_task_id)
        video_gen_config_dict = self.local_db_manager.get_video_gen_config_by_id(task['video_gen_config_id'])
        video_gen_config = VideoGenConfig.from_dict(video_gen_config_dict)
        
        generator = get_video_generator(video_gen_config.config_type)
        
        result = generator.generate_video(
            video_gen_config,
            dance_video['video_path'],
            dressed_model['new_image_path']
        )
        
        if result.get('success'):
            external_task_id = result.get('task_id')
            self._poll_video_task_status(external_task_id, generator, dance_video['id'], dressed_model['id'])
        else:
            error_msg = result.get('error_message', '视频生成任务提交失败')
            self._handle_error(error_msg)
    
    def _poll_video_task_status(self, external_task_id, generator, video_id, dressed_model_id):
        status_result = generator.check_task_status(external_task_id)
        
        if status_result.get('success'):
            status = status_result.get('status')
            
            if status == 'success':
                result_url = status_result.get('result_url')
                if result_url:
                    video_data = httpx.get(result_url).content
                    filename = generate_unique_filename(f'video_{external_task_id}.mp4')
                    saved_path = os.path.join(VIDEO_DIR, filename)
                    with open(saved_path, 'wb') as f:
                        f.write(video_data)
                    
                    new_video_id = self.local_db_manager.add_new_video(
                        video_id,
                        dressed_model_id,
                        saved_path
                    )
                    
                    self.local_db_manager.update_ai_dance_video_gen_task(
                        self.local_task_id,
                        status=AiDanceVideoGenTask.STATUS_VIDEO_GENERATED,
                        new_video_id=new_video_id
                    )
                else:
                    self.local_db_manager.update_ai_dance_video_gen_task(
                        self.local_task_id,
                        status=AiDanceVideoGenTask.STATUS_VIDEO_GENERATED
                    )
                
                self.task_finished.emit()
            
            elif status == 'failed':
                error_msg = status_result.get('error_message', '视频生成失败')
                self._handle_error(error_msg)
            
            elif status == 'processing':
                import time
                time.sleep(15)
                self._poll_video_task_status(external_task_id, generator, video_id, dressed_model_id)
    
    def _handle_error(self, error_msg):
        try:
            if self.local_db_manager:
                self.local_db_manager.update_ai_dance_video_gen_task(
                    self.local_task_id,
                    status=AiDanceVideoGenTask.STATUS_FAILED,
                    result_desc=error_msg
                )
        except Exception as e:
            print(f'更新任务状态失败: {str(e)}\n\n{traceback.format_exc()}')
        self.task_failed.emit(error_msg)

class AiDanceVideoGenDialog(QDialog):
    def __init__(self, parent=None, db_manager=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle('创建AI跳舞视频生成任务')
        self.setGeometry(100, 100, 600, 400)
        self.local_task_id = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel('选择跳舞视频:'))
        self.video_combo = QComboBox()
        self.video_combo.addItem('选择视频')
        videos = self.db_manager.get_all_dance_videos()
        for video in videos:
            self.video_combo.addItem(f"{video['id']} - {video['name']}", video)
        layout.addWidget(self.video_combo)
        
        layout.addWidget(QLabel('选择模特图片:'))
        self.model_combo = QComboBox()
        self.model_combo.addItem('选择模特图片')
        models = self.db_manager.get_all_model_images()
        for model in models:
            self.model_combo.addItem(f"{model['id']} - {model['name']}", model)
        layout.addWidget(self.model_combo)
        
        layout.addWidget(QLabel('选择衣服图片:'))
        self.clothes_combo = QComboBox()
        self.clothes_combo.addItem('选择衣服图片')
        clothes = self.db_manager.get_all_clothes_images()
        for cloth in clothes:
            self.clothes_combo.addItem(f"{cloth['id']} - {cloth['name']}", cloth)
        layout.addWidget(self.clothes_combo)
        
        layout.addWidget(QLabel('选择衣服抠图配置:'))
        self.image_config_combo = QComboBox()
        self.image_config_combo.addItem('选择配置')
        configs = self.db_manager.get_all_image_gen_configs()
        for config in configs:
            self.image_config_combo.addItem(f"{config['id']} - {config['name']}", config)
        layout.addWidget(self.image_config_combo)
        
        layout.addWidget(QLabel('选择模特生成配置:'))
        self.model_config_combo = QComboBox()
        self.model_config_combo.addItem('选择配置')
        configs = self.db_manager.get_all_model_gen_configs()
        for config in configs:
            self.model_config_combo.addItem(f"{config['id']} - {config['name']}", config)
        layout.addWidget(self.model_config_combo)
        
        layout.addWidget(QLabel('选择视频生成配置:'))
        self.video_config_combo = QComboBox()
        self.video_config_combo.addItem('选择配置')
        configs = self.db_manager.get_all_video_gen_configs()
        for config in configs:
            self.video_config_combo.addItem(f"{config['id']} - {config['name']}", config)
        layout.addWidget(self.video_config_combo)
        
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton('确定')
        self.ok_btn.clicked.connect(self.on_ok)
        self.cancel_btn = QPushButton('取消')
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def on_ok(self):
        video_index = self.video_combo.currentIndex()
        model_index = self.model_combo.currentIndex()
        clothes_index = self.clothes_combo.currentIndex()
        image_config_index = self.image_config_combo.currentIndex()
        model_config_index = self.model_config_combo.currentIndex()
        video_config_index = self.video_config_combo.currentIndex()
        
        if video_index == 0:
            QMessageBox.warning(self, '警告', '请选择跳舞视频')
            return
        if model_index == 0:
            QMessageBox.warning(self, '警告', '请选择模特图片')
            return
        if clothes_index == 0:
            QMessageBox.warning(self, '警告', '请选择衣服图片')
            return
        if image_config_index == 0:
            QMessageBox.warning(self, '警告', '请选择衣服抠图配置')
            return
        if model_config_index == 0:
            QMessageBox.warning(self, '警告', '请选择模特生成配置')
            return
        if video_config_index == 0:
            QMessageBox.warning(self, '警告', '请选择视频生成配置')
            return
        
        selected_video = self.video_combo.itemData(video_index)
        selected_model = self.model_combo.itemData(model_index)
        selected_clothes = self.clothes_combo.itemData(clothes_index)
        selected_image_config = self.image_config_combo.itemData(image_config_index)
        selected_model_config = self.model_config_combo.itemData(model_config_index)
        selected_video_config = self.video_config_combo.itemData(video_config_index)
        
        self.local_task_id = self.db_manager.add_ai_dance_video_gen_task(
            dance_video_id=selected_video['id'],
            model_image_id=selected_model['id'],
            clothes_image_id=selected_clothes['id'],
            image_gen_config_id=selected_image_config['id'],
            model_gen_config_id=selected_model_config['id'],
            video_gen_config_id=selected_video_config['id'],
            status=AiDanceVideoGenTask.STATUS_SUBMITTED
        )
        
        QMessageBox.information(self, '成功', '任务已提交，后台处理中...')
        self.accept()
        
        task_data = {
            'task_id': self.local_task_id,
            'dance_video': selected_video,
            'model_image': selected_model,
            'clothes_image': selected_clothes,
            'image_config': selected_image_config,
            'model_config': selected_model_config,
            'video_config': selected_video_config
        }
        
        self.task_processor = TaskProcessor(task_data)
        self.task_processor.task_finished.connect(self.on_task_finished)
        self.task_processor.task_failed.connect(self.on_task_failed)
        self.task_processor.start()
    
    @pyqtSlot()
    def on_task_finished(self):
        print('任务处理完成')
    
    @pyqtSlot(str)
    def on_task_failed(self, error_msg):
        print(f'任务处理失败: {error_msg}')