from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QComboBox, QLabel, QMessageBox)
from PyQt5.QtCore import QTimer
from models.video_gen_config import VideoGenConfig
from generators import get_video_generator
from models.video_gen_task import VideoGenTask
from utils.file_manager import save_video_file
import httpx
import os
import traceback

class VideoGenDialog(QDialog):
    def __init__(self, parent=None, db_manager=None, dressed_model_id=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.dressed_model_id = dressed_model_id
        self.setWindowTitle('生成新跳舞视频')
        self.setGeometry(100, 100, 500, 300)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel('选择视频生成配置:'))
        self.config_combo = QComboBox()
        self.config_combo.addItem('选择配置')
        configs = self.db_manager.get_all_video_gen_configs()
        for config in configs:
            self.config_combo.addItem(f"{config['id']} - {config['name']}", config)
        layout.addWidget(self.config_combo)
        
        layout.addWidget(QLabel('选择跳舞视频:'))
        self.video_combo = QComboBox()
        self.video_combo.addItem('选择视频')
        videos = self.db_manager.get_all_dance_videos()
        for video in videos:
            self.video_combo.addItem(f"{video['id']} - {video['name']}", video)
        layout.addWidget(self.video_combo)
        
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
        config_index = self.config_combo.currentIndex()
        video_index = self.video_combo.currentIndex()
        
        if config_index == 0:
            QMessageBox.warning(self, '警告', '请选择视频生成配置')
            return
        if video_index == 0:
            QMessageBox.warning(self, '警告', '请选择跳舞视频')
            return
        
        selected_config = self.config_combo.itemData(config_index)
        selected_video = self.video_combo.itemData(video_index)
        
        video_gen_config = VideoGenConfig.from_dict(selected_config)
        
        dressed_model = self.db_manager.get_dressed_model_by_id(self.dressed_model_id)
        if not dressed_model:
            QMessageBox.warning(self, '警告', '无法获取模特图片信息')
            return
        
        original_video_path = selected_video['video_path']
        model_image_path = dressed_model['new_image_path']
        
        try:
            generator = get_video_generator(video_gen_config.config_type)
            
            result = generator.generate_video(
                video_gen_config, 
                original_video_path, 
                model_image_path
            )
            
            if result.get('success'):
                task_id = self.db_manager.add_video_gen_task(
                    status=VideoGenTask.STATUS_PROCESSING,
                    video_gen_config_id=video_gen_config.id,
                    original_video_id=selected_video['id'],
                    dressed_model_id=self.dressed_model_id,
                    external_task_id=result.get('task_id')
                )
                
                self._poll_task_status(task_id, result.get('task_id'), generator, 
                                      video_gen_config.id, selected_video['id'])
                
                QMessageBox.information(self, '成功', '视频生成任务已提交')
                self.accept()
            else:
                error_msg = result.get('error_message', '未知错误')
                self.db_manager.add_video_gen_task(
                    status=VideoGenTask.STATUS_FAILED,
                    video_gen_config_id=video_gen_config.id,
                    original_video_id=selected_video['id'],
                    dressed_model_id=self.dressed_model_id,
                    result_desc=error_msg
                )
                QMessageBox.critical(self, '错误', f'提交失败: {error_msg}')
        
        except Exception as e:
            QMessageBox.critical(self, '错误', f'生成视频失败: {str(e)}\n\n{traceback.format_exc()}')
    
    def _poll_task_status(self, local_task_id, external_task_id, generator, 
                          config_id, video_id):
        self._poll_timer = QTimer()
        self._poll_timer.setSingleShot(True)
        self._poll_timer.timeout.connect(lambda: self._check_task_status(
            local_task_id, external_task_id, generator, config_id, video_id))
        self._check_task_status(local_task_id, external_task_id, generator, 
                               config_id, video_id)
        
    def _check_task_status(self, local_task_id, external_task_id, generator, 
                          config_id, video_id):
        try:
            status_result = generator.check_task_status(external_task_id)
            
            if status_result.get('success'):
                status = status_result.get('status')
                
                if status == 'success':
                    result_url = status_result.get('result_url')
                    if result_url:
                        video_data = httpx.get(result_url).content
                        temp_path = os.path.join('/tmp', f'temp_video_{external_task_id}.mp4')
                        with open(temp_path, 'wb') as f:
                            f.write(video_data)
                        
                        saved_path = save_video_file(temp_path)
                        os.remove(temp_path)
                        
                        new_video_id = self.db_manager.add_new_video(
                            video_id,
                            self.dressed_model_id,
                            saved_path
                        )
                        
                        self.db_manager.update_video_gen_task(
                            local_task_id,
                            status=VideoGenTask.STATUS_SUCCESS,
                            new_video_id=new_video_id
                        )
                    else:
                        self.db_manager.update_video_gen_task(
                            local_task_id,
                            status=VideoGenTask.STATUS_SUCCESS
                        )
                
                elif status == 'failed':
                    error_msg = status_result.get('error_message', '任务失败')
                    self.db_manager.update_video_gen_task(
                        local_task_id,
                        status=VideoGenTask.STATUS_FAILED,
                        result_desc=error_msg
                    )
                
                elif status == 'processing':
                    self._poll_timer.start(15000)
                
        except Exception as e:
            self.db_manager.update_video_gen_task(
                local_task_id,
                status=VideoGenTask.STATUS_FAILED,
                result_desc=str(e)
            )