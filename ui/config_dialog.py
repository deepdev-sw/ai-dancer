from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QListWidget, QListWidgetItem, QMessageBox, QLabel)
from models.image_gen_config import ImageGenConfig

class ConfigSelectDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.selected_config = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('选择衣服抠图配置')
        self.setGeometry(100, 100, 500, 400)
        
        layout = QVBoxLayout()
        
        label = QLabel('请选择一个衣服抠图配置：')
        layout.addWidget(label)
        
        self.config_list = QListWidget()
        self.load_configs()
        layout.addWidget(self.config_list)
        
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton('确定')
        self.ok_btn.clicked.connect(self.on_ok)
        self.cancel_btn = QPushButton('取消')
        self.cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def load_configs(self):
        self.config_list.clear()
        configs = self.db_manager.get_all_image_gen_configs()
        for config in configs:
            item = QListWidgetItem(f"{config['name']} ({config['config_type']})")
            item.setData(1, config['id'])
            self.config_list.addItem(item)
    
    def on_ok(self):
        selected_items = self.config_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, '警告', '请选择一个配置')
            return
        
        selected_item = selected_items[0]
        config_id = selected_item.data(1)
        config_data = self.db_manager.get_image_gen_config_by_id(config_id)
        if config_data:
            self.selected_config = ImageGenConfig.from_dict(config_data)
            self.accept()
        else:
            QMessageBox.error(self, '错误', '配置不存在')