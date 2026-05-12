from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLineEdit, QTableWidget, QTableWidgetItem, 
                             QComboBox, QMessageBox, QHeaderView, QDialog,
                             QLabel)
import json
import traceback
from models.video_gen_config import VideoGenConfig

class VideoGenConfigTab(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
    
    def init_ui(self):
        self.layout = QVBoxLayout()
        
        self.top_layout = QHBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText('配置名称')
        self.type_combo = QComboBox()
        self.type_combo.addItem(VideoGenConfig.CONFIG_TYPE_WANXIANG_ACTION_API)
        self.add_btn = QPushButton('添加配置')
        self.add_btn.clicked.connect(self.add_config)
        self.top_layout.addWidget(self.name_input)
        self.top_layout.addWidget(self.type_combo)
        self.top_layout.addWidget(self.add_btn)
        self.refresh_btn = QPushButton('刷新')
        self.refresh_btn.clicked.connect(self.load_data)
        self.top_layout.addWidget(self.refresh_btn)
        self.layout.addLayout(self.top_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['ID', '配置名称', '配置类型', '操作'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.table)
        
        self.setLayout(self.layout)
        self.load_data()
    
    def load_data(self):
        self.table.setRowCount(0)
        configs = self.db_manager.get_all_video_gen_configs()
        for config in configs:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(config['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(config['name']))
            self.table.setItem(row, 2, QTableWidgetItem(config['config_type']))
            
            edit_btn = QPushButton('编辑')
            edit_btn.clicked.connect(lambda _, cid=config['id'], name=config['name'], 
                                   ctype=config['config_type'], content=config['config_content']: 
                                   self.edit_config(cid, name, ctype, content))
            delete_btn = QPushButton('删除')
            delete_btn.clicked.connect(lambda _, cid=config['id']: self.delete_config(cid))
            
            btn_layout = QHBoxLayout()
            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(delete_btn)
            btn_widget = QWidget()
            btn_widget.setLayout(btn_layout)
            self.table.setCellWidget(row, 3, btn_widget)
    
    def add_config(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, '警告', '请输入配置名称')
            return
        
        config_type = self.type_combo.currentText()
        
        dialog = VideoConfigEditDialog(self, name=name, config_type=config_type)
        if dialog.exec_() == QDialog.Accepted:
            try:
                self.db_manager.add_video_gen_config(name, config_type, dialog.get_config_content())
                self.name_input.clear()
                self.load_data()
                QMessageBox.information(self, '成功', '配置添加成功')
            except Exception as e:
                QMessageBox.critical(self, '错误', f'添加失败: {str(e)}\n\n{traceback.format_exc()}')
    
    def edit_config(self, config_id, name, config_type, config_content):
        dialog = VideoConfigEditDialog(self, name=name, config_type=config_type, config_content=config_content)
        if dialog.exec_() == QDialog.Accepted:
            try:
                self.db_manager.update_video_gen_config(config_id, dialog.name_input.text().strip(), 
                                                      config_type, dialog.get_config_content())
                self.load_data()
                QMessageBox.information(self, '成功', '配置更新成功')
            except Exception as e:
                QMessageBox.critical(self, '错误', f'更新失败: {str(e)}\n\n{traceback.format_exc()}')
    
    def delete_config(self, config_id):
        reply = QMessageBox.question(
            self, '确认删除', '确定要删除这个配置吗？',
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                self.db_manager.delete_video_gen_config(config_id)
                self.load_data()
                QMessageBox.information(self, '成功', '配置删除成功')
            except Exception as e:
                QMessageBox.critical(self, '错误', f'删除失败: {str(e)}\n\n{traceback.format_exc()}')

class VideoConfigEditDialog(QDialog):
    def __init__(self, parent=None, name='', config_type='', config_content=''):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle('编辑视频生成配置')
        self.setGeometry(100, 100, 600, 400)
        
        layout = QVBoxLayout()
        
        self.name_input = QLineEdit(name)
        self.name_input.setPlaceholderText('配置名称')
        if not config_content:
            self.name_input.setReadOnly(True)
        layout.addWidget(QLabel('配置名称:'))
        layout.addWidget(self.name_input)
        
        layout.addWidget(QLabel('配置类型:'))
        self.type_label = QLabel(config_type)
        layout.addWidget(self.type_label)
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText('API Key')
        layout.addWidget(QLabel('API Key:'))
        layout.addWidget(self.api_key_input)
        
        self.model_id_input = QLineEdit()
        self.model_id_input.setPlaceholderText('模型ID')
        layout.addWidget(QLabel('模型ID:'))
        layout.addWidget(self.model_id_input)
        
        self.service_mode_input = QLineEdit()
        self.service_mode_input.setPlaceholderText('模型服务模式')
        layout.addWidget(QLabel('模型服务模式:'))
        layout.addWidget(self.service_mode_input)
        
        layout.addWidget(QLabel('--- 阿里云 OSS 配置 ---'))
        
        self.aliyun_access_key_id_input = QLineEdit()
        self.aliyun_access_key_id_input.setPlaceholderText('阿里云 AccessKey ID')
        layout.addWidget(QLabel('阿里云 AccessKey ID:'))
        layout.addWidget(self.aliyun_access_key_id_input)
        
        self.aliyun_access_key_secret_input = QLineEdit()
        self.aliyun_access_key_secret_input.setPlaceholderText('阿里云 AccessKey Secret')
        layout.addWidget(QLabel('阿里云 AccessKey Secret:'))
        layout.addWidget(self.aliyun_access_key_secret_input)
        
        self.aliyun_endpoint_input = QLineEdit()
        self.aliyun_endpoint_input.setPlaceholderText('阿里云 OSS Endpoint')
        layout.addWidget(QLabel('阿里云 OSS Endpoint:'))
        layout.addWidget(self.aliyun_endpoint_input)
        
        self.aliyun_bucket_name_input = QLineEdit()
        self.aliyun_bucket_name_input.setPlaceholderText('阿里云 OSS Bucket Name')
        layout.addWidget(QLabel('阿里云 OSS Bucket Name:'))
        layout.addWidget(self.aliyun_bucket_name_input)
        
        if config_content:
            try:
                data = json.loads(config_content)
                self.api_key_input.setText(data.get('apiKey', ''))
                self.model_id_input.setText(data.get('modelId', ''))
                self.service_mode_input.setText(data.get('serviceMode', ''))
                self.aliyun_access_key_id_input.setText(data.get('aliyunAccessKeyId', ''))
                self.aliyun_access_key_secret_input.setText(data.get('aliyunAccessKeySecret', ''))
                self.aliyun_endpoint_input.setText(data.get('aliyunEndpoint', ''))
                self.aliyun_bucket_name_input.setText(data.get('aliyunBucketName', ''))
            except:
                pass
        
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton('确定')
        self.ok_btn.clicked.connect(self.on_ok)
        self.cancel_btn = QPushButton('取消')
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def get_config_content(self):
        config = {
            "apiKey": self.api_key_input.text().strip(),
            "modelId": self.model_id_input.text().strip(),
            "serviceMode": self.service_mode_input.text().strip(),
            "aliyunAccessKeyId": self.aliyun_access_key_id_input.text().strip(),
            "aliyunAccessKeySecret": self.aliyun_access_key_secret_input.text().strip(),
            "aliyunEndpoint": self.aliyun_endpoint_input.text().strip(),
            "aliyunBucketName": self.aliyun_bucket_name_input.text().strip()
        }
        return json.dumps(config, indent=2, ensure_ascii=False)
    
    def on_ok(self):
        api_key = self.api_key_input.text().strip()
        model_id = self.model_id_input.text().strip()
        aliyun_access_key_id = self.aliyun_access_key_id_input.text().strip()
        aliyun_access_key_secret = self.aliyun_access_key_secret_input.text().strip()
        aliyun_endpoint = self.aliyun_endpoint_input.text().strip()
        aliyun_bucket_name = self.aliyun_bucket_name_input.text().strip()
        
        if not api_key:
            QMessageBox.warning(self, '警告', '请输入API Key')
            return
        
        if not model_id:
            QMessageBox.warning(self, '警告', '请输入模型ID')
            return
        
        if not aliyun_access_key_id:
            QMessageBox.warning(self, '警告', '请输入阿里云 AccessKey ID')
            return
        
        if not aliyun_access_key_secret:
            QMessageBox.warning(self, '警告', '请输入阿里云 AccessKey Secret')
            return
        
        if not aliyun_endpoint:
            QMessageBox.warning(self, '警告', '请输入阿里云 OSS Endpoint')
            return
        
        if not aliyun_bucket_name:
            QMessageBox.warning(self, '警告', '请输入阿里云 OSS Bucket Name')
            return
        
        self.accept()