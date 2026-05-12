from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QMessageBox, 
                             QHeaderView, QLabel, QDialog, QScrollArea)
from PyQt5.QtGui import QPixmap
from utils.file_manager import delete_file
from ui.video_gen_dialog import VideoGenDialog

class DressedModelTab(QWidget):
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
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['ID', '原模特名称', '新图片路径', '操作', '生成视频'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.table)
        
        self.setLayout(self.layout)
        self.load_data()
    
    def load_data(self):
        self.table.setRowCount(0)
        dressed_models = self.db_manager.get_all_dressed_models()
        for item in dressed_models:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(item['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(item['original_model_name'] or '未知'))
            self.table.setItem(row, 2, QTableWidgetItem(item['new_image_path']))
            
            view_btn = QPushButton('查看图片')
            view_btn.clicked.connect(lambda _, path=item['new_image_path']: self.view_image(path))
            
            delete_btn = QPushButton('删除')
            delete_btn.clicked.connect(lambda _, did=item['id'], path=item['new_image_path']: self.delete_dressed_model(did, path))
            
            btn_layout = QHBoxLayout()
            btn_layout.addWidget(view_btn)
            btn_layout.addWidget(delete_btn)
            btn_widget = QWidget()
            btn_widget.setLayout(btn_layout)
            self.table.setCellWidget(row, 3, btn_widget)
            
            gen_video_btn = QPushButton('生成视频')
            gen_video_btn.clicked.connect(lambda _, did=item['id']: self.generate_video(did))
            self.table.setCellWidget(row, 4, gen_video_btn)
    
    def view_image(self, image_path):
        dialog = QDialog(self)
        dialog.setWindowTitle('查看图片')
        dialog.resize(800, 600)
        
        scroll_area = QScrollArea()
        label = QLabel()
        pixmap = QPixmap(image_path)
        
        if not pixmap.isNull():
            label.setPixmap(pixmap.scaled(scroll_area.size(), aspectRatioMode=True))
            label.adjustSize()
        else:
            label.setText('无法加载图片')
        
        scroll_area.setWidget(label)
        scroll_area.setWidgetResizable(True)
        
        layout = QVBoxLayout()
        layout.addWidget(scroll_area)
        dialog.setLayout(layout)
        
        dialog.exec_()
    
    def delete_dressed_model(self, dressed_model_id, image_path):
        reply = QMessageBox.question(
            self, '确认删除', '确定要删除这个穿新衣服的模特吗？',
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                self.db_manager.delete_dressed_model(dressed_model_id)
                delete_file(image_path)
                self.load_data()
                QMessageBox.information(self, '成功', '穿新衣服模特删除成功')
            except Exception as e:
                QMessageBox.critical(self, '错误', f'删除失败: {str(e)}')
    
    def generate_video(self, dressed_model_id):
        dialog = VideoGenDialog(self, self.db_manager, dressed_model_id)
        dialog.exec_()
