from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QMessageBox, 
                             QHeaderView, QDialog)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl
import os

class ImageToVideoTab(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
    
    def init_ui(self):
        self.layout = QVBoxLayout()
        
        self.top_layout = QHBoxLayout()
        self.refresh_btn = QPushButton('刷新')
        self.refresh_btn.clicked.connect(self.load_data)
        self.top_layout.addWidget(self.refresh_btn)
        self.layout.addLayout(self.top_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['图生视频路径', '图生视频生成配置名称', '查看视频', '删除'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.table)
        
        self.setLayout(self.layout)
        self.load_data()
    
    def load_data(self):
        self.table.setRowCount(0)
        image_to_videos = self.db_manager.get_all_image_to_videos()
        for item in image_to_videos:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(item['video_path']))
            self.table.setItem(row, 1, QTableWidgetItem(item['config_name'] or '未知'))
            
            view_btn = QPushButton('查看视频')
            view_btn.clicked.connect(lambda _, path=item['video_path']: self.play_video(path))
            
            delete_btn = QPushButton('删除')
            delete_btn.clicked.connect(lambda _, vid=item['id'], path=item['video_path']: self.delete_image_to_video(vid, path))
            
            btn_layout = QHBoxLayout()
            btn_layout.addWidget(view_btn)
            btn_layout.addWidget(delete_btn)
            btn_widget = QWidget()
            btn_widget.setLayout(btn_layout)
            self.table.setCellWidget(row, 2, btn_widget)
            
            self.table.setCellWidget(row, 3, delete_btn)
    
    def play_video(self, video_path):
        if not os.path.exists(video_path):
            QMessageBox.warning(self, '警告', '视频文件不存在')
            return
        
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
    
    def delete_image_to_video(self, video_id, video_path):
        reply = QMessageBox.question(
            self, '确认删除', '确定要删除这个图生视频吗？',
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                self.db_manager.delete_image_to_video(video_id)
                if os.path.exists(video_path):
                    os.remove(video_path)
                self.load_data()
                QMessageBox.information(self, '成功', '图生视频删除成功')
            except Exception as e:
                QMessageBox.critical(self, '错误', f'删除失败: {str(e)}')