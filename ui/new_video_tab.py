import sys
import subprocess
import traceback
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView)
from utils.file_manager import delete_file

class NewVideoTab(QWidget):
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
        self.table.setHorizontalHeaderLabels(['ID', '原视频名称', '新视频路径', '操作'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.table)
        
        self.setLayout(self.layout)
        self.load_data()
    
    def load_data(self):
        self.table.setRowCount(0)
        new_videos = self.db_manager.get_all_new_videos()
        for video in new_videos:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(video['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(video['original_video_name'] or '未知'))
            self.table.setItem(row, 2, QTableWidgetItem(video['new_video_path']))
            
            view_btn = QPushButton('查看视频')
            view_btn.clicked.connect(lambda _, path=video['new_video_path']: self.open_video(path))
            
            delete_btn = QPushButton('删除')
            delete_btn.clicked.connect(lambda _, vid=video['id'], path=video['new_video_path']: self.delete_new_video(vid, path))
            
            btn_layout = QHBoxLayout()
            btn_layout.addWidget(view_btn)
            btn_layout.addWidget(delete_btn)
            btn_widget = QWidget()
            btn_widget.setLayout(btn_layout)
            self.table.setCellWidget(row, 3, btn_widget)
    
    def open_video(self, video_path):
        import os
        
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
    
    def delete_new_video(self, video_id, video_path):
        reply = QMessageBox.question(
            self, '确认删除', '确定要删除这个生成的视频吗？',
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                self.db_manager.delete_new_video(video_id)
                delete_file(video_path)
                self.load_data()
                QMessageBox.information(self, '成功', '生成视频删除成功')
            except Exception as e:
                QMessageBox.critical(self, '错误', f'删除失败: {str(e)}\n\n{traceback.format_exc()}')
