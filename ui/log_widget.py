from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, 
                             QPushButton, QHBoxLayout, QSplitter)
from PyQt5.QtCore import Qt
from utils.log_manager import log_manager


class LogWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.connect_logs()
    
    def init_ui(self):
        self.layout = QVBoxLayout(self)
        
        self.button_layout = QHBoxLayout()
        
        self.clear_button = QPushButton('清空日志')
        self.clear_button.clicked.connect(self.clear_logs)
        self.button_layout.addWidget(self.clear_button)
        
        self.button_layout.addStretch()
        
        self.layout.addLayout(self.button_layout)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
            }
        """)
        self.layout.addWidget(self.log_text)
    
    def connect_logs(self):
        log_manager.log_added.connect(self.add_log)
        for log in log_manager.get_all_logs():
            self.add_log(log)
    
    def add_log(self, log):
        self.log_text.append(log)
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
    
    def clear_logs(self):
        self.log_text.clear()
        log_manager.clear_logs()