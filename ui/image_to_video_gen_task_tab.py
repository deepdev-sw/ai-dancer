from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QComboBox,
                             QHeaderView, QMessageBox, QDialog, QLabel, QApplication)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QCursor
from models.image_to_video_gen_task import ImageToVideoGenTask
from ui.image_to_video_gen_dialog import ImageToVideoGenDialog

class ImageToVideoGenTaskTab(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
    
    def init_ui(self):
        self.layout = QVBoxLayout()
        
        self.top_layout = QHBoxLayout()
        
        self.add_btn = QPushButton('添加任务')
        self.add_btn.clicked.connect(self.add_task)
        
        self.status_combo = QComboBox()
        self.status_combo.addItem('全部')
        self.status_combo.addItem('已提交')
        self.status_combo.addItem('已处理衣服图片')
        self.status_combo.addItem('已处理模特图片')
        self.status_combo.addItem('已完成图生视频')
        self.status_combo.addItem('失败')
        self.status_combo.currentIndexChanged.connect(self.load_data)
        
        self.refresh_btn = QPushButton('刷新')
        self.refresh_btn.clicked.connect(self.load_data)
        
        self.top_layout.addWidget(self.add_btn)
        self.top_layout.addWidget(self.status_combo)
        self.top_layout.addWidget(self.refresh_btn)
        self.layout.addLayout(self.top_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            '模特图片名称', '衣服图片名称', '衣服抠图配置名称',
            '模特图片生成配置名称', '图生视频配置名称', '任务状态', '任务结果', 
            '图生视频路径', '查看图生视频', '操作'
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.table)
        
        self.setLayout(self.layout)
        self.load_data()
    
    def load_data(self):
        self.table.setRowCount(0)
        
        status_text = self.status_combo.currentText()
        if status_text == '全部':
            tasks = self.db_manager.get_all_image_to_video_gen_tasks()
        elif status_text == '已提交':
            tasks = self.db_manager.get_image_to_video_gen_tasks_by_status(ImageToVideoGenTask.STATUS_SUBMITTED)
        elif status_text == '已处理衣服图片':
            tasks = self.db_manager.get_image_to_video_gen_tasks_by_status(ImageToVideoGenTask.STATUS_CLOTHES_PROCESSED)
        elif status_text == '已处理模特图片':
            tasks = self.db_manager.get_image_to_video_gen_tasks_by_status(ImageToVideoGenTask.STATUS_MODEL_PROCESSED)
        elif status_text == '已完成图生视频':
            tasks = self.db_manager.get_image_to_video_gen_tasks_by_status(ImageToVideoGenTask.STATUS_VIDEO_GENERATED)
        elif status_text == '失败':
            tasks = self.db_manager.get_image_to_video_gen_tasks_by_status(ImageToVideoGenTask.STATUS_FAILED)
        else:
            tasks = []
        
        for task in tasks:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(task.get('model_image_name', '未知')))
            self.table.setItem(row, 1, QTableWidgetItem(task.get('clothes_image_name', '未知')))
            self.table.setItem(row, 2, QTableWidgetItem(task.get('image_gen_config_name', '未知')))
            self.table.setItem(row, 3, QTableWidgetItem(task.get('model_gen_config_name', '未知')))
            self.table.setItem(row, 4, QTableWidgetItem(task.get('image_to_video_gen_config_name', '未知')))
            
            status_display = self._get_status_display(task['status'])
            self.table.setItem(row, 5, QTableWidgetItem(status_display))
            
            self.table.setItem(row, 6, QTableWidgetItem(task.get('result_desc', '')))
            
            video_path = task.get('output_video_path', '')
            if video_path:
                path_label = QLabel(video_path)
                path_label.setStyleSheet('color: blue; text-decoration: underline;')
                path_label.setCursor(QCursor(Qt.PointingHandCursor))
                path_label.mousePressEvent = lambda _, p=video_path: self.copy_path(p)
                self.table.setCellWidget(row, 7, path_label)
            else:
                self.table.setItem(row, 7, QTableWidgetItem(''))
            
            view_btn = QPushButton('查看图生视频')
            view_btn.clicked.connect(lambda checked, t=task: self.view_video(t))
            is_video_generated = task['status'] == ImageToVideoGenTask.STATUS_VIDEO_GENERATED
            view_btn.setEnabled(is_video_generated)
            self.table.setCellWidget(row, 8, view_btn)
            
            delete_btn = QPushButton('删除')
            delete_btn.clicked.connect(lambda checked, t=task: self.delete_task(t))
            self.table.setCellWidget(row, 9, delete_btn)
            
            self.table.setItem(row, 10, QTableWidgetItem(str(task['id'])))
            self.table.setColumnHidden(10, True)
    
    def copy_path(self, path):
        clipboard = QApplication.clipboard()
        clipboard.setText(path)
        QMessageBox.information(self, '成功', '路径已复制到剪贴板')
    
    def _get_status_display(self, status):
        status_map = {
            ImageToVideoGenTask.STATUS_SUBMITTED: '已提交',
            ImageToVideoGenTask.STATUS_CLOTHES_PROCESSED: '已处理衣服图片',
            ImageToVideoGenTask.STATUS_MODEL_PROCESSED: '已处理模特图片',
            ImageToVideoGenTask.STATUS_VIDEO_GENERATED: '已完成图生视频',
            ImageToVideoGenTask.STATUS_FAILED: '失败'
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
        dialog = QDialog()
        dialog.setWindowTitle('视频播放')
        dialog.setMinimumSize(800, 600)
        dialog_layout = QVBoxLayout(dialog)
        
        video_widget = QVideoWidget()
        media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        media_player.setVideoOutput(video_widget)
        media_player.setMedia(QMediaContent(QUrl.fromLocalFile(video_path)))
        
        control_layout = QHBoxLayout()
        play_btn = QPushButton('播放')
        pause_btn = QPushButton('暂停')
        stop_btn = QPushButton('停止')
        close_btn = QPushButton('关闭')
        
        def play():
            media_player.play()
        
        def pause():
            media_player.pause()
        
        def stop():
            media_player.stop()
        
        def close_dialog():
            media_player.stop()
            dialog.close()
        
        def on_dialog_finished():
            media_player.stop()
        
        play_btn.clicked.connect(play)
        pause_btn.clicked.connect(pause)
        stop_btn.clicked.connect(stop)
        close_btn.clicked.connect(close_dialog)
        dialog.finished.connect(on_dialog_finished)
        
        control_layout.addWidget(play_btn)
        control_layout.addWidget(pause_btn)
        control_layout.addWidget(stop_btn)
        control_layout.addWidget(close_btn)
        
        dialog_layout.addWidget(video_widget)
        dialog_layout.addLayout(control_layout)
        
        dialog.exec_()
    
    def delete_task(self, task):
        task_id = task['id']
        reply = QMessageBox.question(self, '确认删除', f'确定要删除任务ID {task_id} 吗？',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            success = self.db_manager.delete_image_to_video_gen_task(task_id)
            if success:
                QMessageBox.information(self, '提示', '删除成功')
                self.load_data()
            else:
                QMessageBox.warning(self, '提示', '删除失败')
    
    def add_task(self):
        dialog = ImageToVideoGenDialog(self, self.db_manager)
        if dialog.exec_():
            self.load_data()