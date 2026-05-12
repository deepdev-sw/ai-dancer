from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLineEdit, QTableWidget, QTableWidgetItem, 
                             QFileDialog, QMessageBox, QHeaderView, QDialog,
                             QLabel, QScrollArea, QComboBox, QProgressBar)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from utils.file_manager import save_image_file, delete_file
from utils.constants import ALLOWED_IMAGE_EXTENSIONS
from ui.config_dialog import ConfigSelectDialog
from generators import get_generator
import urllib.request
import tempfile
import os

class ImagePreviewDialog(QDialog):
    def __init__(self, image_url, parent=None):
        super().__init__(parent)
        self.image_url = image_url
        self.accepted_flag = False
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('图片预览')
        self.setGeometry(100, 100, 600, 500)
        
        layout = QVBoxLayout()
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        self.image_label = QLabel()
        self.load_image()
        
        scroll_area.setWidget(self.image_label)
        layout.addWidget(scroll_area)
        
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton('确认保存')
        self.ok_btn.clicked.connect(self.on_ok)
        self.cancel_btn = QPushButton('取消')
        self.cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def load_image(self):
        try:
            data = urllib.request.urlopen(self.image_url).read()
            pixmap = QPixmap()
            pixmap.loadFromData(data)
            self.image_label.setPixmap(pixmap.scaled(550, 400, aspectRatioMode=True))
        except Exception as e:
            self.image_label.setText(f'加载图片失败: {str(e)}')
    
    def on_ok(self):
        self.accepted_flag = True
        self.accept()

class ClothesTab(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
    
    def init_ui(self):
        self.layout = QVBoxLayout()
        
        self.top_layout = QHBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText('衣服名称')
        self.browse_btn = QPushButton('浏览图片')
        self.browse_btn.clicked.connect(self.browse_image)
        self.add_btn = QPushButton('添加')
        self.add_btn.clicked.connect(self.add_clothes)
        self.top_layout.addWidget(self.name_input)
        self.top_layout.addWidget(self.browse_btn)
        self.top_layout.addWidget(self.add_btn)
        self.refresh_btn = QPushButton('刷新')
        self.refresh_btn.clicked.connect(self.load_data)
        self.top_layout.addWidget(self.refresh_btn)
        self.layout.addLayout(self.top_layout)
        
        self.path_display = QLineEdit()
        self.path_display.setReadOnly(True)
        self.path_display.setPlaceholderText('选中的图片路径')
        self.layout.addWidget(self.path_display)
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['ID', '名称', '图片路径', '操作', '生成新图'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.table)
        
        self.setLayout(self.layout)
        self.load_data()
        
        self.selected_path = None
    
    def browse_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, '选择图片文件', '', 
            f'图片文件 ({" ".join(f"*{ext}" for ext in ALLOWED_IMAGE_EXTENSIONS)})'
        )
        if file_path:
            self.selected_path = file_path
            self.path_display.setText(file_path)
    
    def add_clothes(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, '警告', '请输入衣服名称')
            return
        if not self.selected_path:
            QMessageBox.warning(self, '警告', '请选择图片文件')
            return
        
        try:
            saved_path = save_image_file(self.selected_path)
            self.db_manager.add_clothes_image(name, saved_path)
            self.name_input.clear()
            self.selected_path = None
            self.path_display.clear()
            self.load_data()
            QMessageBox.information(self, '成功', '衣服图片添加成功')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'添加失败: {str(e)}')
    
    def generate_new_clothes_image(self, clothes_id, clothes_name, image_path):
        self.open_generate_clothes_dialog(clothes_id, clothes_name, image_path)
    
    def download_image(self, url):
        try:
            data = urllib.request.urlopen(url).read()
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                f.write(data)
                return f.name
        except Exception as e:
            QMessageBox.critical(self, '错误', f'下载图片失败: {str(e)}')
            return None
    
    def load_data(self):
        self.table.setRowCount(0)
        clothes = self.db_manager.get_all_clothes_images()
        for cloth in clothes:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(cloth['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(cloth['name']))
            self.table.setItem(row, 2, QTableWidgetItem(cloth['image_path']))
            
            view_btn = QPushButton('查看')
            view_btn.clicked.connect(lambda _, path=cloth['image_path']: self.view_image(path))
            edit_btn = QPushButton('编辑')
            edit_btn.clicked.connect(lambda _, cid=cloth['id'], name=cloth['name']: self.edit_clothes(cid, name))
            delete_btn = QPushButton('删除')
            delete_btn.clicked.connect(lambda _, cid=cloth['id'], path=cloth['image_path']: self.delete_clothes(cid, path))
            
            btn_layout = QHBoxLayout()
            btn_layout.addWidget(view_btn)
            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(delete_btn)
            btn_widget = QWidget()
            btn_widget.setLayout(btn_layout)
            self.table.setCellWidget(row, 3, btn_widget)
            
            generate_btn = QPushButton('生成新图')
            generate_btn.clicked.connect(lambda _, cid=cloth['id'], name=cloth['name'], path=cloth['image_path']: self.generate_new_clothes_image(cid, name, path))
            
            gen_btn_widget = QWidget()
            gen_layout = QHBoxLayout()
            gen_layout.addWidget(generate_btn)
            gen_btn_widget.setLayout(gen_layout)
            self.table.setCellWidget(row, 4, gen_btn_widget)
    
    def edit_clothes(self, clothes_id, current_name):
        dialog = QDialog()
        dialog.setWindowTitle('编辑衣服')
        dialog_layout = QVBoxLayout(dialog)
        
        name_input = QLineEdit(current_name)
        path_display = QLineEdit()
        path_display.setReadOnly(True)
        path_display.setPlaceholderText('选中的图片路径')
        browse_btn = QPushButton('浏览新图片')
        save_btn = QPushButton('保存')
        cancel_btn = QPushButton('取消')
        
        selected_path = [None]
        
        def browse_new():
            file_path, _ = QFileDialog.getOpenFileName(
                self, '选择图片文件', '', 
                f'图片文件 ({" ".join(f"*{ext}" for ext in ALLOWED_IMAGE_EXTENSIONS)})'
            )
            if file_path:
                selected_path[0] = file_path
                path_display.setText(file_path)
        
        def save():
            new_name = name_input.text().strip()
            if not new_name:
                QMessageBox.warning(self, '警告', '请输入衣服名称')
                return
            
            try:
                if selected_path[0]:
                    old_cloth = self.db_manager.get_clothes_image_by_id(clothes_id)
                    if old_cloth:
                        delete_file(old_cloth['image_path'])
                    new_path = save_image_file(selected_path[0])
                    self.db_manager.update_clothes_image(clothes_id, new_name, new_path)
                else:
                    self.db_manager.update_clothes_image(clothes_id, new_name)
                
                self.load_data()
                dialog.close()
                QMessageBox.information(self, '成功', '衣服图片更新成功')
            except Exception as e:
                QMessageBox.critical(self, '错误', f'更新失败: {str(e)}')
        
        browse_btn.clicked.connect(browse_new)
        save_btn.clicked.connect(save)
        cancel_btn.clicked.connect(dialog.close)
        
        dialog_layout.addWidget(name_input)
        dialog_layout.addWidget(path_display)
        dialog_layout.addWidget(browse_btn)
        dialog_layout.addWidget(save_btn)
        dialog_layout.addWidget(cancel_btn)
        dialog.exec_()
    
    def delete_clothes(self, clothes_id, image_path):
        reply = QMessageBox.question(
            self, '确认删除', '确定要删除这个衣服图片吗？',
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                self.db_manager.delete_clothes_image(clothes_id)
                delete_file(image_path)
                self.load_data()
                QMessageBox.information(self, '成功', '衣服图片删除成功')
            except Exception as e:
                QMessageBox.critical(self, '错误', f'删除失败: {str(e)}')
    
    def view_image(self, image_path):
        dialog = QDialog()
        dialog.setWindowTitle('查看图片')
        dialog.setMinimumSize(600, 400)
        dialog_layout = QVBoxLayout(dialog)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        image_label = QLabel()
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            image_label.setPixmap(pixmap.scaled(800, 600, aspectRatioMode=True))
        else:
            image_label.setText('无法加载图片')
        
        scroll_area.setWidget(image_label)
        
        close_btn = QPushButton('关闭')
        close_btn.clicked.connect(dialog.close)
        
        dialog_layout.addWidget(scroll_area)
        dialog_layout.addWidget(close_btn)
        
        dialog.exec_()
    
    def open_generate_clothes_dialog(self, clothes_id, clothes_name, image_path):
        dialog = GenerateClothesImageDialog(self, clothes_id, clothes_name, image_path, self.db_manager)
        if dialog.exec_() == QDialog.Accepted:
            self.load_data()

class GenerateClothesImageDialog(QDialog):
    def __init__(self, parent, clothes_id, clothes_name, clothes_image_path, db_manager):
        super().__init__(parent)
        self.parent = parent
        self.clothes_id = clothes_id
        self.clothes_name = clothes_name
        self.clothes_image_path = clothes_image_path
        self.db_manager = db_manager
        self.generated_image_path = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('生成新衣服图片')
        self.setGeometry(100, 100, 600, 550)
        self.setModal(True)
        
        self.layout = QVBoxLayout()
        
        self.config_layout = QHBoxLayout()
        self.config_label = QLabel('选择生成配置:')
        self.config_combo = QComboBox()
        self.config_layout.addWidget(self.config_label)
        self.config_layout.addWidget(self.config_combo)
        self.layout.addLayout(self.config_layout)
        
        self.generate_btn = QPushButton('生成图片')
        self.generate_btn.clicked.connect(self.on_generate)
        self.layout.addWidget(self.generate_btn)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.layout.addWidget(self.progress_bar)
        
        self.image_label = QLabel('生成的图片将在这里显示')
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet('border: 1px solid #ccc;')
        self.image_label.setFixedSize(400, 300)
        self.layout.addWidget(self.image_label)
        
        self.btn_layout = QHBoxLayout()
        self.confirm_btn = QPushButton('确认保存')
        self.confirm_btn.clicked.connect(self.on_confirm)
        self.confirm_btn.setEnabled(False)
        self.cancel_btn = QPushButton('取消')
        self.cancel_btn.clicked.connect(self.reject)
        self.btn_layout.addWidget(self.confirm_btn)
        self.btn_layout.addWidget(self.cancel_btn)
        self.layout.addLayout(self.btn_layout)
        
        self.setLayout(self.layout)
        self.load_configs()
    
    def load_configs(self):
        self.config_combo.clear()
        configs = self.db_manager.get_all_image_gen_configs()
        if not configs:
            QMessageBox.warning(self, '警告', '请先添加衣服图片生成配置')
            self.generate_btn.setEnabled(False)
            return
        
        for config in configs:
            self.config_combo.addItem(config['name'], config['id'])
        self.generate_btn.setEnabled(True)
    
    def on_generate(self):
        config_id = self.config_combo.currentData()
        
        if not config_id:
            QMessageBox.warning(self, '警告', '请选择生成配置')
            return
        
        if not os.path.exists(self.clothes_image_path):
            QMessageBox.warning(self, '警告', '衣服图片文件不存在')
            return
        
        config_data = self.db_manager.get_image_gen_config_by_id(config_id)
        if not config_data:
            QMessageBox.warning(self, '警告', '配置不存在')
            return
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.generate_btn.setEnabled(False)
        
        self.worker = GenerateClothesWorker(config_data, self.clothes_image_path)
        self.worker.finished.connect(self.on_generate_finished)
        self.worker.error.connect(self.on_generate_error)
        self.worker.start()
    
    def on_generate_finished(self, image_url):
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 100)
        
        try:
            data = urllib.request.urlopen(image_url).read()
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                f.write(data)
                self.generated_image_path = f.name
            
            pixmap = QPixmap(self.generated_image_path)
            if not pixmap.isNull():
                self.image_label.setPixmap(pixmap.scaled(400, 300, Qt.KeepAspectRatio))
                self.confirm_btn.setEnabled(True)
                QMessageBox.information(self, '成功', '图片生成成功')
            else:
                QMessageBox.warning(self, '警告', '无法加载生成的图片')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'下载图片失败: {str(e)}')
        
        self.generate_btn.setEnabled(True)
    
    def on_generate_error(self, error_msg):
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 100)
        QMessageBox.critical(self, '错误', f'生成图片失败: {error_msg}')
        self.generate_btn.setEnabled(True)
    
    def on_confirm(self):
        if not self.generated_image_path:
            QMessageBox.warning(self, '警告', '请先生成图片')
            return
        
        try:
            saved_path = save_image_file(self.generated_image_path)
            self.db_manager.add_ai_clothes(self.clothes_id, saved_path)
            QMessageBox.information(self, '成功', '新衣服图片生成并保存成功')
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, '错误', f'保存失败: {str(e)}')

class GenerateClothesWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, config_data, clothes_image_path):
        super().__init__()
        self.config_data = config_data
        self.clothes_image_path = clothes_image_path
    
    def run(self):
        try:
            from models.image_gen_config import ImageGenConfig
            
            config = ImageGenConfig.from_dict(self.config_data)
            generator = get_generator(config.config_type)
            image_url = generator.generate_image(config, self.clothes_image_path)
            
            if not image_url:
                self.error.emit('未生成图片')
                return
            
            self.finished.emit(image_url)
        except Exception as e:
            self.error.emit(str(e))