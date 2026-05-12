import sys
import time
from PyQt5.QtCore import pyqtSignal, QObject


class LogManager(QObject):
    log_added = pyqtSignal(str)
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LogManager, cls).__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        super().__init__()
        self.log_buffer = []
        self.max_buffer_size = 1000
    
    def _format_log(self, level, message):
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        return f"[{timestamp}] [{level}] {message}"
    
    def debug(self, message):
        log = self._format_log('DEBUG', message)
        self._add_log(log)
    
    def info(self, message):
        log = self._format_log('INFO', message)
        self._add_log(log)
    
    def warning(self, message):
        log = self._format_log('WARNING', message)
        self._add_log(log)
    
    def error(self, message):
        log = self._format_log('ERROR', message)
        self._add_log(log)
    
    def critical(self, message):
        log = self._format_log('CRITICAL', message)
        self._add_log(log)
    
    def _add_log(self, log):
        self.log_buffer.append(log)
        if len(self.log_buffer) > self.max_buffer_size:
            self.log_buffer.pop(0)
        self.log_added.emit(log)
        print(log)
    
    def get_all_logs(self):
        return self.log_buffer
    
    def clear_logs(self):
        self.log_buffer.clear()


log_manager = LogManager()