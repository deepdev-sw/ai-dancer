from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from models.image_to_video_gen_task import ImageToVideoGenTask
from models.image_to_video_gen_config import ImageToVideoGenConfig
from models.image_gen_config import ImageGenConfig
from models.model_gen_config import ModelGenConfig
from generators import get_generator, get_model_generator, get_image_to_video_generator
from utils.file_manager import download_image, save_video_file
from database.database_manager import DatabaseManager
import httpx
import os
import time

class ImageToVideoTaskRecoveryProcessor(QThread):
    task_finished = pyqtSignal(int)
    task_failed = pyqtSignal(int, str)
    all_finished = pyqtSignal()
    
    def __init__(self, tasks_data):
        super().__init__()
        self.tasks_data = tasks_data
        self.local_db_manager = None
    
    def run(self):
        try:
            self.local_db_manager = DatabaseManager()
            self._recover_tasks()
        except Exception as e:
            print(f'任务恢复线程执行失败: {str(e)}')
        finally:
            if self.local_db_manager:
                self.local_db_manager.close()
            self.all_finished.emit()
    
    def _recover_tasks(self):
        for task_data in self.tasks_data:
            self.local_task_id = task_data['id']
            self.task_data = task_data
            try:
                self._recover_task()
            except Exception as e:
                self._handle_error(f'任务恢复失败: {str(e)}')
    
    def _recover_task(self):
        status = self.task_data.get('status')
        
        if status == ImageToVideoGenTask.STATUS_SUBMITTED:
            self._recover_from_submitted()
        elif status == ImageToVideoGenTask.STATUS_CLOTHES_PROCESSED:
            self._recover_from_clothes_processed()
        elif status == ImageToVideoGenTask.STATUS_MODEL_PROCESSED:
            self._recover_from_model_processed()
    
    def _recover_from_submitted(self):
        model_image = self.local_db_manager.get_model_image_by_id(self.task_data['model_image_id'])
        clothes_image = self.local_db_manager.get_clothes_image_by_id(self.task_data['clothes_image_id'])
        image_gen_config_dict = self.local_db_manager.get_image_gen_config_by_id(self.task_data['image_gen_config_id'])
        
        if not model_image or not clothes_image or not image_gen_config_dict:
            self._handle_error('缺少必要的数据，无法恢复任务')
            return
        
        image_gen_config = ImageGenConfig.from_dict(image_gen_config_dict)
        generator = get_generator(image_gen_config.config_type)
        
        result = generator.generate_image(image_gen_config, clothes_image['image_path'])
        
        if result:
            saved_path = download_image(result)
            
            ai_clothes_id = self.local_db_manager.add_ai_clothes(
                original_clothes_id=clothes_image['id'],
                new_image_path=saved_path
            )
            
            self.local_db_manager.update_image_to_video_gen_task(
                self.local_task_id,
                status=ImageToVideoGenTask.STATUS_CLOTHES_PROCESSED,
                ai_clothes_id=ai_clothes_id
            )
            
            self.task_data['ai_clothes_id'] = ai_clothes_id
            self._recover_from_clothes_processed()
        else:
            self._handle_error('衣服图片处理失败，未返回结果')
    
    def _recover_from_clothes_processed(self):
        ai_clothes_id = self.task_data.get('ai_clothes_id')
        if not ai_clothes_id:
            self._handle_error('缺少AI处理衣服ID，无法恢复任务')
            return
        
        ai_clothes = self.local_db_manager.get_ai_clothes_by_id(ai_clothes_id)
        model_image = self.local_db_manager.get_model_image_by_id(self.task_data['model_image_id'])
        model_gen_config_dict = self.local_db_manager.get_model_gen_config_by_id(self.task_data['model_gen_config_id'])
        
        if not ai_clothes or not model_image or not model_gen_config_dict:
            self._handle_error('缺少必要的数据，无法恢复任务')
            return
        
        model_gen_config = ModelGenConfig.from_dict(model_gen_config_dict)
        generator = get_model_generator(model_gen_config.config_type)
        
        result = generator.generate_image(
            model_gen_config, 
            model_image['image_path'], 
            ai_clothes['new_image_path']
        )
        
        if result:
            saved_path = download_image(result)
            
            dressed_model_id = self.local_db_manager.add_dressed_model(
                original_model_id=model_image['id'],
                ai_clothes_id=ai_clothes['id'],
                new_image_path=saved_path
            )
            
            self.local_db_manager.update_image_to_video_gen_task(
                self.local_task_id,
                status=ImageToVideoGenTask.STATUS_MODEL_PROCESSED,
                dressed_model_id=dressed_model_id
            )
            
            self.task_data['dressed_model_id'] = dressed_model_id
            self._recover_from_model_processed()
        else:
            self._handle_error('模特图片处理失败，未返回结果')
    
    def _recover_from_model_processed(self):
        dressed_model_id = self.task_data.get('dressed_model_id')
        
        if not dressed_model_id:
            self._handle_error('缺少模特图片ID，无法恢复')
            return
        
        external_task_id = self.task_data.get('external_task_id')
        video_gen_config_dict = self.local_db_manager.get_image_to_video_gen_config_by_id(
            self.task_data['image_to_video_gen_config_id']
        )
        
        if not video_gen_config_dict:
            self._handle_error('缺少视频生成配置，无法恢复')
            return
        
        video_gen_config = ImageToVideoGenConfig.from_dict(video_gen_config_dict)
        generator = get_image_to_video_generator(video_gen_config.config_type)
        dressed_model = self.local_db_manager.get_dressed_model_by_id(dressed_model_id)
        
        if external_task_id:
            status_result = generator.check_task_status(external_task_id, video_gen_config)
            
            if status_result.get('success'):
                status = status_result.get('status')
                
                if status == 'success':
                    self._handle_video_success(status_result, video_gen_config, dressed_model_id)
                elif status == 'failed':
                    error_msg = status_result.get('error_message', '视频生成失败')
                    self._handle_error(error_msg)
                elif status == 'processing':
                    self._poll_video_task_status(external_task_id, generator, video_gen_config, dressed_model_id)
            else:
                self._retry_video_generation(generator, video_gen_config, dressed_model)
        else:
            self._retry_video_generation(generator, video_gen_config, dressed_model)
    
    def _retry_video_generation(self, generator, video_gen_config, dressed_model):
        result = generator.generate_video(
            video_gen_config,
            dressed_model['new_image_path']
        )
        
        if result.get('success'):
            external_task_id = result.get('task_id')
            self.task_data['external_task_id'] = external_task_id
            self.local_db_manager.update_image_to_video_gen_task(
                self.local_task_id,
                external_task_id=external_task_id
            )
            self._poll_video_task_status(external_task_id, generator, video_gen_config, dressed_model['id'])
        else:
            error_msg = result.get('error_message', '视频生成任务提交失败')
            self._handle_error(error_msg)
    
    def _poll_video_task_status(self, external_task_id, generator, video_gen_config, dressed_model_id):
        time.sleep(15)
        
        status_result = generator.check_task_status(external_task_id, video_gen_config)
        
        if status_result.get('success'):
            status = status_result.get('status')
            
            if status == 'success':
                self._handle_video_success(status_result, video_gen_config, dressed_model_id)
            elif status == 'failed':
                error_msg = status_result.get('error_message', '视频生成失败')
                self._handle_error(error_msg)
            elif status == 'processing':
                self._poll_video_task_status(external_task_id, generator, video_gen_config, dressed_model_id)
    
    def _handle_video_success(self, status_result, video_gen_config, dressed_model_id):
        result_url = status_result.get('result_url')
        if result_url:
            video_data = httpx.get(result_url).content
            temp_path = os.path.join('/tmp', f'temp_video_{self.task_data.get("external_task_id")}.mp4')
            with open(temp_path, 'wb') as f:
                f.write(video_data)
            
            saved_path = save_video_file(temp_path)
            os.remove(temp_path)
            
            image_to_video_id = self.local_db_manager.add_image_to_video(
                image_to_video_gen_config_id=video_gen_config.id,
                dressed_model_id=dressed_model_id,
                video_path=saved_path
            )
            
            self.local_db_manager.update_image_to_video_gen_task(
                self.local_task_id,
                status=ImageToVideoGenTask.STATUS_VIDEO_GENERATED,
                image_to_video_id=image_to_video_id
            )
        else:
            self.local_db_manager.update_image_to_video_gen_task(
                self.local_task_id,
                status=ImageToVideoGenTask.STATUS_VIDEO_GENERATED
            )
        
        self.task_finished.emit(self.local_task_id)
    
    def _handle_error(self, error_msg):
        try:
            if self.local_db_manager:
                self.local_db_manager.update_image_to_video_gen_task(
                    self.local_task_id,
                    status=ImageToVideoGenTask.STATUS_FAILED,
                    result_desc=error_msg
                )
        except Exception as e:
            print(f'更新任务状态失败: {str(e)}')
        self.task_failed.emit(self.local_task_id, error_msg)

class TaskRecovery(QObject):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.processor = None
    
    def recover_processing_tasks(self):
        all_tasks = self.db_manager.get_all_image_to_video_gen_tasks()
        
        pending_tasks = []
        for task in all_tasks:
            status = task.get('status')
            if status not in [ImageToVideoGenTask.STATUS_FAILED, ImageToVideoGenTask.STATUS_VIDEO_GENERATED]:
                pending_tasks.append(task)
        
        if pending_tasks:
            self.processor = ImageToVideoTaskRecoveryProcessor(pending_tasks)
            self.processor.task_finished.connect(self.on_task_recovered)
            self.processor.task_failed.connect(self.on_task_recovery_failed)
            self.processor.all_finished.connect(self.on_all_tasks_finished)
            self.processor.start()
    
    @pyqtSlot(int)
    def on_task_recovered(self, task_id):
        print(f'任务 {task_id} 恢复成功')
    
    @pyqtSlot(int, str)
    def on_task_recovery_failed(self, task_id, error_msg):
        print(f'任务 {task_id} 恢复失败: {error_msg}')
    
    @pyqtSlot()
    def on_all_tasks_finished(self):
        print('所有任务恢复处理完成')