from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QMessageBox, 
                             QHeaderView, QDialog, QLabel, QScrollArea, 
                             QComboBox, QProgressBar)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from utils.file_manager import delete_file, download_image
from models.model_gen_config import ModelGenConfig
from generators.model_volc_engine_generator import VolcEngineModelGenerator
import os
import traceback

class AiClothesTab(QWidget):
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
        self.table.setHorizontalHeaderLabels(['ID', '原衣服名称', '新图片路径', '操作', '生成新模特'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.table)
        
        self.setLayout(self.layout)
        self.load_data()
    
    def load_data(self):
        self.table.setRowCount(0)
        ai_clothes = self.db_manager.get_all_ai_clothes()
        for item in ai_clothes:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(item['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(item['original_name'] or '未知'))
            self.table.setItem(row, 2, QTableWidgetItem(item['new_image_path']))
            
            view_btn = QPushButton('查看')
            view_btn.clicked.connect(lambda _, path=item['new_image_path']: self.view_image(path))
            delete_btn = QPushButton('删除')
            delete_btn.clicked.connect(lambda _, aid=item['id'], path=item['new_image_path']: self.delete_ai_clothes(aid, path))
            
            btn_layout = QHBoxLayout()
            btn_layout.addWidget(view_btn)
            btn_layout.addWidget(delete_btn)
            btn_widget = QWidget()
            btn_widget.setLayout(btn_layout)
            self.table.setCellWidget(row, 3, btn_widget)
            
            gen_model_btn = QPushButton('生成模特')
            gen_model_btn.clicked.connect(lambda _, aid=item['id'], cid=item['original_clothes_id'], path=item['new_image_path']: 
                                         self.open_generate_dialog(aid, cid, path))
            self.table.setCellWidget(row, 4, gen_model_btn)
    
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
            image_label.setPixmap(pixmap.scaled(800, 600, Qt.KeepAspectRatio))
        else:
            image_label.setText('无法加载图片')
        
        scroll_area.setWidget(image_label)
        
        close_btn = QPushButton('关闭')
        close_btn.clicked.connect(dialog.close)
        
        dialog_layout.addWidget(scroll_area)
        dialog_layout.addWidget(close_btn)
        
        dialog.exec_()
    
    def delete_ai_clothes(self, ai_clothes_id, image_path):
        reply = QMessageBox.question(
            self, '确认删除', '确定要删除这个AI处理后的衣服吗？',
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                self.db_manager.delete_ai_clothes(ai_clothes_id)
                delete_file(image_path)
                self.load_data()
                QMessageBox.information(self, '成功', 'AI处理衣服删除成功')
            except Exception as e:
                QMessageBox.critical(self, '错误', f'删除失败: {str(e)}\n\n{traceback.format_exc()}')
    
    def open_generate_dialog(self, ai_clothes_id, clothes_id, clothes_image_path):
        dialog = GenerateModelImageDialog(self, ai_clothes_id, clothes_id, clothes_image_path, self.db_manager)
        dialog.exec_()

class GenerateModelImageDialog(QDialog):
    def __init__(self, parent, ai_clothes_id, clothes_id, clothes_image_path, db_manager):
        super().__init__(parent)
        self.parent = parent
        self.ai_clothes_id = ai_clothes_id
        self.clothes_id = clothes_id
        self.clothes_image_path = clothes_image_path
        self.db_manager = db_manager
        self.generated_image_path = None
        self.selected_model_id = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('生成新模特图片')
        self.setGeometry(100, 100, 600, 550)
        self.setModal(True)
        
        self.layout = QVBoxLayout()
        
        self.config_layout = QHBoxLayout()
        self.config_label = QLabel('选择生成配置:')
        self.config_combo = QComboBox()
        self.config_layout.addWidget(self.config_label)
        self.config_layout.addWidget(self.config_combo)
        self.layout.addLayout(self.config_layout)
        
        self.model_layout = QHBoxLayout()
        self.model_label = QLabel('选择模特图片:')
        self.model_combo = QComboBox()
        self.model_layout.addWidget(self.model_label)
        self.model_layout.addWidget(self.model_combo)
        self.layout.addLayout(self.model_layout)
        
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
        self.load_models()
    
    def load_configs(self):
        self.config_combo.clear()
        configs = self.db_manager.get_all_model_gen_configs()
        if not configs:
            QMessageBox.warning(self, '警告', '请先添加新模特图片生成配置')
            self.generate_btn.setEnabled(False)
            return
        
        for config in configs:
            self.config_combo.addItem(config['name'], config['id'])
        self.generate_btn.setEnabled(True)
    
    def load_models(self):
        self.model_combo.clear()
        models = self.db_manager.get_all_model_images()
        if not models:
            QMessageBox.warning(self, '警告', '请先添加模特图片')
            self.generate_btn.setEnabled(False)
            return
        
        for model in models:
            self.model_combo.addItem(model['name'], model['id'])
        self.generate_btn.setEnabled(True)
    
    def on_generate(self):
        config_id = self.config_combo.currentData()
        model_id = self.model_combo.currentData()
        
        if not config_id:
            QMessageBox.warning(self, '警告', '请选择生成配置')
            return
        
        if not model_id:
            QMessageBox.warning(self, '警告', '请选择模特图片')
            return
        
        self.selected_model_id = model_id
        
        model_info = self.db_manager.get_model_image_by_id(model_id)
        if not model_info:
            QMessageBox.warning(self, '警告', '模特图片不存在')
            return
        
        model_image_path = model_info['image_path']
        
        if not os.path.exists(model_image_path):
            QMessageBox.warning(self, '警告', '模特图片文件不存在')
            return
        
        if not os.path.exists(self.clothes_image_path):
            QMessageBox.warning(self, '警告', '衣服图片文件不存在')
            return
        
        config_data = self.db_manager.get_model_gen_config_by_id(config_id)
        if not config_data:
            QMessageBox.warning(self, '警告', '配置不存在')
            return
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.generate_btn.setEnabled(False)
        
        self.worker = GenerateImageWorker(config_data, model_image_path, self.clothes_image_path)
        self.worker.finished.connect(self.on_generate_finished)
        self.worker.error.connect(self.on_generate_error)
        self.worker.start()
    
    def on_generate_finished(self, image_url):
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 100)
        
        try:
            self.generated_image_path = download_image(image_url)
            pixmap = QPixmap(self.generated_image_path)
            if not pixmap.isNull():
                self.image_label.setPixmap(pixmap.scaled(400, 300, Qt.KeepAspectRatio))
                self.confirm_btn.setEnabled(True)
                QMessageBox.information(self, '成功', '图片生成成功')
            else:
                QMessageBox.warning(self, '警告', '无法加载生成的图片')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'下载图片失败: {str(e)}\n\n{traceback.format_exc()}')
        
        self.generate_btn.setEnabled(True)
    
    def on_generate_error(self, error_msg):
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 100)
        QMessageBox.critical(self, '错误', f'生成图片失败: {error_msg}')
        self.generate_btn.setEnabled(True)
    
    def on_confirm(self):
        if not self.generated_image_path or not self.selected_model_id:
            QMessageBox.warning(self, '警告', '请先生成图片')
            return
        
        try:
            self.db_manager.add_dressed_model(
                original_model_id=self.selected_model_id,
                ai_clothes_id=self.ai_clothes_id,
                new_image_path=self.generated_image_path
            )
            QMessageBox.information(self, '成功', '新模特图片保存成功')
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, '错误', f'保存失败: {str(e)}\n\n{traceback.format_exc()}')

class GenerateImageWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, config_data, model_image_path, clothes_image_path):
        super().__init__()
        self.config_data = config_data
        self.model_image_path = model_image_path
        self.clothes_image_path = clothes_image_path
    
    def run(self):
        try:
            config = ModelGenConfig.from_dict(self.config_data)
            
            generator = VolcEngineModelGenerator()
            image_url = generator.generate_image(config, self.model_image_path, self.clothes_image_path)
            
            if not image_url:
                self.error.emit('未生成图片')
                return
            
            self.finished.emit(image_url)
        except Exception as e:
            self.error.emit(f'{str(e)}\n\n{traceback.format_exc()}')