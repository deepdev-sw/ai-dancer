import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QComboBox,
                             QHeaderView, QMessageBox)
from models.ai_dance_video_gen_task import AiDanceVideoGenTask
from ui.ai_dance_video_gen_dialog import AiDanceVideoGenDialog

class AiDanceVideoGenTaskTab(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
    
    def init_ui(self):
        self.layout = QVBoxLayout()
        
        self.top_layout = QHBoxLayout()
        
        self.status_combo = QComboBox()
        self.status_combo.addItem('全部')
        self.status_combo.addItem('已提交')
        self.status_combo.addItem('已处理衣服图片')
        self.status_combo.addItem('已处理模特图片')
        self.status_combo.addItem('已生成新视频')
        self.status_combo.addItem('失败')
        self.status_combo.currentIndexChanged.connect(self.load_data)
        
        self.add_btn = QPushButton('生成任务')
        self.add_btn.clicked.connect(self.add_task)
        
        self.refresh_btn = QPushButton('刷新')
        self.refresh_btn.clicked.connect(self.load_data)
        
        self.top_layout.addWidget(self.status_combo)
        self.top_layout.addWidget(self.add_btn)
        self.top_layout.addWidget(self.refresh_btn)
        self.layout.addLayout(self.top_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            '跳舞视频名称', '模特图片名称', '衣服图片名称', '衣服抠图配置名称',
            '模特图片生成配置名称', '视频生成配置名称', '任务状态', '任务结果', '查看视频'
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.table)
        
        self.setLayout(self.layout)
        self.load_data()
    
    def add_task(self):
        dialog = AiDanceVideoGenDialog(self, self.db_manager)
        if dialog.exec_():
            self.load_data()
    
    def load_data(self):
        self.table.setRowCount(0)
        
        status_text = self.status_combo.currentText()
        if status_text == '全部':
            tasks = self.db_manager.get_all_ai_dance_video_gen_tasks()
        elif status_text == '已提交':
            tasks = self.db_manager.get_ai_dance_video_gen_tasks_by_status(AiDanceVideoGenTask.STATUS_SUBMITTED)
        elif status_text == '已处理衣服图片':
            tasks = self.db_manager.get_ai_dance_video_gen_tasks_by_status(AiDanceVideoGenTask.STATUS_CLOTHES_PROCESSED)
        elif status_text == '已处理模特图片':
            tasks = self.db_manager.get_ai_dance_video_gen_tasks_by_status(AiDanceVideoGenTask.STATUS_MODEL_PROCESSED)
        elif status_text == '已生成新视频':
            tasks = self.db_manager.get_ai_dance_video_gen_tasks_by_status(AiDanceVideoGenTask.STATUS_VIDEO_GENERATED)
        elif status_text == '失败':
            tasks = self.db_manager.get_ai_dance_video_gen_tasks_by_status(AiDanceVideoGenTask.STATUS_FAILED)
        else:
            tasks = []
        
        for task in tasks:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(task.get('dance_video_name', '未知')))
            self.table.setItem(row, 1, QTableWidgetItem(task.get('model_image_name', '未知')))
            self.table.setItem(row, 2, QTableWidgetItem(task.get('clothes_image_name', '未知')))
            self.table.setItem(row, 3, QTableWidgetItem(task.get('image_gen_config_name', '未知')))
            self.table.setItem(row, 4, QTableWidgetItem(task.get('model_gen_config_name', '未知')))
            self.table.setItem(row, 5, QTableWidgetItem(task.get('video_gen_config_name', '未知')))
            
            status_display = self._get_status_display(task['status'])
            self.table.setItem(row, 6, QTableWidgetItem(status_display))
            
            self.table.setItem(row, 7, QTableWidgetItem(task.get('result_desc', '')))
            
            view_btn = QPushButton('查看视频')
            view_btn.clicked.connect(lambda checked, t=task: self.view_video(t))
            is_video_generated = task['status'] == AiDanceVideoGenTask.STATUS_VIDEO_GENERATED
            view_btn.setEnabled(is_video_generated)
            self.table.setCellWidget(row, 8, view_btn)
            
            self.table.setItem(row, 9, QTableWidgetItem(str(task['id'])))
            self.table.setColumnHidden(9, True)
    
    def _get_status_display(self, status):
        status_map = {
            AiDanceVideoGenTask.STATUS_SUBMITTED: '已提交',
            AiDanceVideoGenTask.STATUS_CLOTHES_PROCESSED: '已处理衣服图片',
            AiDanceVideoGenTask.STATUS_MODEL_PROCESSED: '已处理模特图片',
            AiDanceVideoGenTask.STATUS_VIDEO_GENERATED: '已生成新视频',
            AiDanceVideoGenTask.STATUS_FAILED: '失败'
        }
        return status_map.get(status, status)
    
    def view_video(self, task):
        video_path = task.get('output_video_path')
        if video_path:
            import os
            if os.path.exists(video_path):
                self.play_video(video_path)
            else:
                QMessageBox.warning(self, '提示', '视频文件不存在')
        else:
            QMessageBox.warning(self, '提示', '视频路径为空')
    
    def play_video(self, video_path):
        import os
        import subprocess
        
        try:
            if os.name == 'nt':
                os.startfile(video_path)
            elif os.name == 'posix':
                if sys.platform == 'darwin':
                    subprocess.run(['open', video_path])
                else:
                    subprocess.run(['xdg-open', video_path])
        except Exception as e:
            QMessageBox.warning(self, '播放失败', f'无法打开视频文件: {str(e)}')