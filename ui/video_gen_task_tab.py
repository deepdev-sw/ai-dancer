from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QComboBox,
                             QHeaderView)
from models.video_gen_task import VideoGenTask

class VideoGenTaskTab(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
    
    def init_ui(self):
        self.layout = QVBoxLayout()
        
        self.top_layout = QHBoxLayout()
        
        self.status_combo = QComboBox()
        self.status_combo.addItem('全部')
        self.status_combo.addItem('处理中')
        self.status_combo.addItem('成功')
        self.status_combo.addItem('失败')
        self.status_combo.currentIndexChanged.connect(self.load_data)
        
        self.refresh_btn = QPushButton('刷新')
        self.refresh_btn.clicked.connect(self.load_data)
        
        self.top_layout.addWidget(self.status_combo)
        self.top_layout.addWidget(self.refresh_btn)
        self.layout.addLayout(self.top_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['ID', '状态', '配置名称', '视频名称', '提交时间', '任务结果'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.table)
        
        self.setLayout(self.layout)
        self.load_data()
    
    def load_data(self):
        self.table.setRowCount(0)
        
        status_text = self.status_combo.currentText()
        if status_text == '全部':
            tasks = self.db_manager.get_all_video_gen_tasks()
        elif status_text == '处理中':
            tasks = self.db_manager.get_video_gen_tasks_by_status(VideoGenTask.STATUS_PROCESSING)
        elif status_text == '成功':
            tasks = self.db_manager.get_video_gen_tasks_by_status(VideoGenTask.STATUS_SUCCESS)
        elif status_text == '失败':
            tasks = self.db_manager.get_video_gen_tasks_by_status(VideoGenTask.STATUS_FAILED)
        else:
            tasks = []
        
        for task in tasks:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(task['id'])))
            
            status_display = self._get_status_display(task['status'])
            self.table.setItem(row, 1, QTableWidgetItem(status_display))
            
            self.table.setItem(row, 2, QTableWidgetItem(task.get('config_name', '未知')))
            self.table.setItem(row, 3, QTableWidgetItem(task.get('video_name', '未知')))
            self.table.setItem(row, 4, QTableWidgetItem(task.get('submitted_at', '')))
            self.table.setItem(row, 5, QTableWidgetItem(task.get('result_desc', '')))
    
    def _get_status_display(self, status):
        status_map = {
            VideoGenTask.STATUS_PROCESSING: '处理中',
            VideoGenTask.STATUS_SUCCESS: '成功',
            VideoGenTask.STATUS_FAILED: '失败'
        }
        return status_map.get(status, status)
    
    