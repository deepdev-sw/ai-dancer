import sys
import subprocess
import traceback
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLineEdit, QTableWidget, QTableWidgetItem, 
                             QFileDialog, QMessageBox, QHeaderView)
from PyQt5.QtGui import QIcon
from utils.file_manager import save_video_file, delete_file, get_file_size
from utils.constants import ALLOWED_VIDEO_EXTENSIONS

class VideoTab(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
    
    def init_ui(self):
        self.layout = QVBoxLayout()
        
        self.top_layout = QHBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText('视频名称')
        self.browse_btn = QPushButton('浏览视频')
        self.browse_btn.clicked.connect(self.browse_video)
        self.add_btn = QPushButton('添加')
        self.add_btn.clicked.connect(self.add_video)
        self.top_layout.addWidget(self.name_input)
        self.top_layout.addWidget(self.browse_btn)
        self.top_layout.addWidget(self.add_btn)
        self.refresh_btn = QPushButton('刷新')
        self.refresh_btn.clicked.connect(self.load_data)
        self.top_layout.addWidget(self.refresh_btn)
        self.layout.addLayout(self.top_layout)
        
        self.path_display = QLineEdit()
        self.path_display.setReadOnly(True)
        self.path_display.setPlaceholderText('选中的视频路径')
        self.layout.addWidget(self.path_display)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['ID', '名称', '视频路径', '操作'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.table)
        
        self.setLayout(self.layout)
        self.load_data()
        
        self.selected_path = None
    
    def browse_video(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, '选择视频文件', '', 
            f'视频文件 ({" ".join(f"*{ext}" for ext in ALLOWED_VIDEO_EXTENSIONS)})'
        )
        if file_path:
            self.selected_path = file_path
            self.path_display.setText(file_path)
    
    def add_video(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, '警告', '请输入视频名称')
            return
        if not self.selected_path:
            QMessageBox.warning(self, '警告', '请选择视频文件')
            return
        
        try:
            saved_path = save_video_file(self.selected_path)
            self.db_manager.add_dance_video(name, saved_path)
            self.name_input.clear()
            self.selected_path = None
            self.path_display.clear()
            self.load_data()
            QMessageBox.information(self, '成功', '视频添加成功')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'添加失败: {str(e)}\n\n{traceback.format_exc()}')
    
    def load_data(self):
        self.table.setRowCount(0)
        videos = self.db_manager.get_all_dance_videos()
        for video in videos:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(video['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(video['name']))
            self.table.setItem(row, 2, QTableWidgetItem(video['video_path']))
            
            view_btn = QPushButton('播放')
            view_btn.clicked.connect(lambda _, path=video['video_path']: self.play_video(path))
            edit_btn = QPushButton('编辑')
            edit_btn.clicked.connect(lambda _, vid=video['id'], name=video['name']: self.edit_video(vid, name))
            delete_btn = QPushButton('删除')
            delete_btn.clicked.connect(lambda _, vid=video['id'], path=video['video_path']: self.delete_video(vid, path))
            
            btn_layout = QHBoxLayout()
            btn_layout.addWidget(view_btn)
            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(delete_btn)
            btn_widget = QWidget()
            btn_widget.setLayout(btn_layout)
            self.table.setCellWidget(row, 3, btn_widget)
    
    def edit_video(self, video_id, current_name):
        dialog = QDialog()
        dialog.setWindowTitle('编辑视频')
        dialog_layout = QVBoxLayout(dialog)
        
        name_input = QLineEdit(current_name)
        path_display = QLineEdit()
        path_display.setReadOnly(True)
        path_display.setPlaceholderText('选中的视频路径')
        browse_btn = QPushButton('浏览新视频')
        save_btn = QPushButton('保存')
        cancel_btn = QPushButton('取消')
        
        selected_path = [None]
        
        def browse_new():
            file_path, _ = QFileDialog.getOpenFileName(
                self, '选择视频文件', '', 
                f'视频文件 ({" ".join(f"*{ext}" for ext in ALLOWED_VIDEO_EXTENSIONS)})'
            )
            if file_path:
                selected_path[0] = file_path
                path_display.setText(file_path)
        
        def save():
            new_name = name_input.text().strip()
            if not new_name:
                QMessageBox.warning(self, '警告', '请输入视频名称')
                return
            
            try:
                if selected_path[0]:
                    old_video = self.db_manager.get_dance_video_by_id(video_id)
                    if old_video:
                        delete_file(old_video['video_path'])
                    new_path = save_video_file(selected_path[0])
                    self.db_manager.update_dance_video(video_id, new_name, new_path)
                else:
                    self.db_manager.update_dance_video(video_id, new_name)
                
                self.load_data()
                dialog.close()
                QMessageBox.information(self, '成功', '视频更新成功')
            except Exception as e:
                QMessageBox.critical(self, '错误', f'更新失败: {str(e)}\n\n{traceback.format_exc()}')
        
        browse_btn.clicked.connect(browse_new)
        save_btn.clicked.connect(save)
        cancel_btn.clicked.connect(dialog.close)
        
        dialog_layout.addWidget(name_input)
        dialog_layout.addWidget(path_display)
        dialog_layout.addWidget(browse_btn)
        dialog_layout.addWidget(save_btn)
        dialog_layout.addWidget(cancel_btn)
        dialog.exec_()
    
    def delete_video(self, video_id, video_path):
        reply = QMessageBox.question(
            self, '确认删除', '确定要删除这个视频吗？',
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                self.db_manager.delete_dance_video(video_id)
                delete_file(video_path)
                self.load_data()
                QMessageBox.information(self, '成功', '视频删除成功')
            except Exception as e:
                QMessageBox.critical(self, '错误', f'删除失败: {str(e)}\n\n{traceback.format_exc()}')
    
    def play_video(self, video_path):
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
