import sqlite3
import os
from datetime import datetime
from utils.constants import DATABASE_PATH

class DatabaseManager:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self._connect()
        self._create_tables()
    
    def _connect(self):
        os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
    
    def _create_tables(self):
        create_dance_videos = '''
            CREATE TABLE IF NOT EXISTS dance_videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                video_path TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        '''
        
        create_model_images = '''
            CREATE TABLE IF NOT EXISTS model_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                image_path TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        '''
        
        create_clothes_images = '''
            CREATE TABLE IF NOT EXISTS clothes_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                image_path TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        '''
        
        create_ai_clothes = '''
            CREATE TABLE IF NOT EXISTS ai_clothes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_clothes_id INTEGER NOT NULL,
                new_image_path TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (original_clothes_id) REFERENCES clothes_images(id)
            )
        '''
        
        create_dressed_models = '''
            CREATE TABLE IF NOT EXISTS dressed_models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_model_id INTEGER NOT NULL,
                ai_clothes_id INTEGER NOT NULL,
                new_image_path TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (original_model_id) REFERENCES model_images(id),
                FOREIGN KEY (ai_clothes_id) REFERENCES ai_clothes(id)
            )
        '''
        
        create_new_videos = '''
            CREATE TABLE IF NOT EXISTS new_videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_video_id INTEGER NOT NULL,
                dressed_model_id INTEGER NOT NULL,
                new_video_path TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (original_video_id) REFERENCES dance_videos(id),
                FOREIGN KEY (dressed_model_id) REFERENCES dressed_models(id)
            )
        '''
        
        create_image_gen_configs = '''
            CREATE TABLE IF NOT EXISTS image_gen_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                config_type TEXT NOT NULL,
                config_content TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        '''
        
        create_model_gen_configs = '''
            CREATE TABLE IF NOT EXISTS model_gen_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                config_type TEXT NOT NULL,
                config_content TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        '''
        
        create_video_gen_configs = '''
            CREATE TABLE IF NOT EXISTS video_gen_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                config_type TEXT NOT NULL,
                config_content TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        '''
        
        create_image_to_video_gen_configs = '''
            CREATE TABLE IF NOT EXISTS image_to_video_gen_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                config_type TEXT NOT NULL,
                config_content TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        '''
        
        create_video_gen_tasks = '''
            CREATE TABLE IF NOT EXISTS video_gen_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                status TEXT NOT NULL,
                result_desc TEXT,
                submitted_at TEXT NOT NULL,
                external_task_id TEXT,
                new_video_id INTEGER,
                video_gen_config_id INTEGER NOT NULL,
                original_video_id INTEGER NOT NULL,
                dressed_model_id INTEGER NOT NULL,
                FOREIGN KEY (new_video_id) REFERENCES new_videos(id),
                FOREIGN KEY (video_gen_config_id) REFERENCES video_gen_configs(id),
                FOREIGN KEY (original_video_id) REFERENCES dance_videos(id),
                FOREIGN KEY (dressed_model_id) REFERENCES dressed_models(id)
            )
        '''
        
        create_ai_dance_video_gen_tasks = '''
            CREATE TABLE IF NOT EXISTS ai_dance_video_gen_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dance_video_id INTEGER NOT NULL,
                model_image_id INTEGER NOT NULL,
                clothes_image_id INTEGER NOT NULL,
                image_gen_config_id INTEGER NOT NULL,
                model_gen_config_id INTEGER NOT NULL,
                video_gen_config_id INTEGER NOT NULL,
                ai_clothes_id INTEGER,
                dressed_model_id INTEGER,
                new_video_id INTEGER,
                submitted_at TEXT NOT NULL,
                status TEXT NOT NULL,
                result_desc TEXT,
                FOREIGN KEY (dance_video_id) REFERENCES dance_videos(id),
                FOREIGN KEY (model_image_id) REFERENCES model_images(id),
                FOREIGN KEY (clothes_image_id) REFERENCES clothes_images(id),
                FOREIGN KEY (image_gen_config_id) REFERENCES image_gen_configs(id),
                FOREIGN KEY (model_gen_config_id) REFERENCES model_gen_configs(id),
                FOREIGN KEY (video_gen_config_id) REFERENCES video_gen_configs(id),
                FOREIGN KEY (ai_clothes_id) REFERENCES ai_clothes(id),
                FOREIGN KEY (dressed_model_id) REFERENCES dressed_models(id),
                FOREIGN KEY (new_video_id) REFERENCES new_videos(id)
            )
        '''
        
        create_image_to_videos = '''
            CREATE TABLE IF NOT EXISTS image_to_videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_to_video_gen_config_id INTEGER NOT NULL,
                dressed_model_id INTEGER NOT NULL,
                video_path TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (image_to_video_gen_config_id) REFERENCES image_to_video_gen_configs(id),
                FOREIGN KEY (dressed_model_id) REFERENCES dressed_models(id)
            )
        '''
        
        create_image_to_video_gen_tasks = '''
            CREATE TABLE IF NOT EXISTS image_to_video_gen_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_image_id INTEGER NOT NULL,
                clothes_image_id INTEGER NOT NULL,
                image_gen_config_id INTEGER NOT NULL,
                model_gen_config_id INTEGER NOT NULL,
                image_to_video_gen_config_id INTEGER NOT NULL,
                ai_clothes_id INTEGER,
                dressed_model_id INTEGER,
                image_to_video_id INTEGER,
                submitted_at TEXT NOT NULL,
                status TEXT NOT NULL,
                result_desc TEXT,
                external_task_id TEXT,
                FOREIGN KEY (model_image_id) REFERENCES model_images(id),
                FOREIGN KEY (clothes_image_id) REFERENCES clothes_images(id),
                FOREIGN KEY (image_gen_config_id) REFERENCES image_gen_configs(id),
                FOREIGN KEY (model_gen_config_id) REFERENCES model_gen_configs(id),
                FOREIGN KEY (image_to_video_gen_config_id) REFERENCES image_to_video_gen_configs(id),
                FOREIGN KEY (ai_clothes_id) REFERENCES ai_clothes(id),
                FOREIGN KEY (dressed_model_id) REFERENCES dressed_models(id),
                FOREIGN KEY (image_to_video_id) REFERENCES image_to_videos(id)
            )
        '''
        
        tables = [
            create_dance_videos,
            create_model_images,
            create_clothes_images,
            create_ai_clothes,
            create_dressed_models,
            create_new_videos,
            create_image_gen_configs,
            create_model_gen_configs,
            create_video_gen_configs,
            create_image_to_video_gen_configs,
            create_video_gen_tasks,
            create_ai_dance_video_gen_tasks,
            create_image_to_videos,
            create_image_to_video_gen_tasks
        ]
        
        for table in tables:
            self.cursor.execute(table)
        self.conn.commit()
    
    def _get_timestamp(self):
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def add_dance_video(self, name, video_path):
        sql = 'INSERT INTO dance_videos (name, video_path, created_at) VALUES (?, ?, ?)'
        self.cursor.execute(sql, (name, video_path, self._get_timestamp()))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_all_dance_videos(self):
        self.cursor.execute('SELECT * FROM dance_videos ORDER BY created_at DESC')
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_dance_video_by_id(self, video_id):
        self.cursor.execute('SELECT * FROM dance_videos WHERE id = ?', (video_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def update_dance_video(self, video_id, name=None, video_path=None):
        updates = []
        params = []
        
        if name is not None:
            updates.append('name = ?')
            params.append(name)
        if video_path is not None:
            updates.append('video_path = ?')
            params.append(video_path)
        
        if not updates:
            return False
        
        params.append(video_id)
        sql = f'UPDATE dance_videos SET {", ".join(updates)} WHERE id = ?'
        self.cursor.execute(sql, params)
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def delete_dance_video(self, video_id):
        self.cursor.execute('DELETE FROM dance_videos WHERE id = ?', (video_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def add_model_image(self, name, image_path):
        sql = 'INSERT INTO model_images (name, image_path, created_at) VALUES (?, ?, ?)'
        self.cursor.execute(sql, (name, image_path, self._get_timestamp()))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_all_model_images(self):
        self.cursor.execute('SELECT * FROM model_images ORDER BY created_at DESC')
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_model_image_by_id(self, image_id):
        self.cursor.execute('SELECT * FROM model_images WHERE id = ?', (image_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def update_model_image(self, image_id, name=None, image_path=None):
        updates = []
        params = []
        
        if name is not None:
            updates.append('name = ?')
            params.append(name)
        if image_path is not None:
            updates.append('image_path = ?')
            params.append(image_path)
        
        if not updates:
            return False
        
        params.append(image_id)
        sql = f'UPDATE model_images SET {", ".join(updates)} WHERE id = ?'
        self.cursor.execute(sql, params)
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def delete_model_image(self, image_id):
        self.cursor.execute('DELETE FROM model_images WHERE id = ?', (image_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def add_clothes_image(self, name, image_path):
        sql = 'INSERT INTO clothes_images (name, image_path, created_at) VALUES (?, ?, ?)'
        self.cursor.execute(sql, (name, image_path, self._get_timestamp()))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_all_clothes_images(self):
        self.cursor.execute('SELECT * FROM clothes_images ORDER BY created_at DESC')
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_clothes_image_by_id(self, image_id):
        self.cursor.execute('SELECT * FROM clothes_images WHERE id = ?', (image_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def update_clothes_image(self, image_id, name=None, image_path=None):
        updates = []
        params = []
        
        if name is not None:
            updates.append('name = ?')
            params.append(name)
        if image_path is not None:
            updates.append('image_path = ?')
            params.append(image_path)
        
        if not updates:
            return False
        
        params.append(image_id)
        sql = f'UPDATE clothes_images SET {", ".join(updates)} WHERE id = ?'
        self.cursor.execute(sql, params)
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def delete_clothes_image(self, image_id):
        self.cursor.execute('DELETE FROM clothes_images WHERE id = ?', (image_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def add_ai_clothes(self, original_clothes_id, new_image_path):
        sql = 'INSERT INTO ai_clothes (original_clothes_id, new_image_path, created_at) VALUES (?, ?, ?)'
        self.cursor.execute(sql, (original_clothes_id, new_image_path, self._get_timestamp()))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_all_ai_clothes(self):
        sql = '''
            SELECT ac.*, ci.name as original_name 
            FROM ai_clothes ac 
            LEFT JOIN clothes_images ci ON ac.original_clothes_id = ci.id 
            ORDER BY ac.created_at DESC
        '''
        self.cursor.execute(sql)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_ai_clothes_by_id(self, ai_clothes_id):
        sql = '''
            SELECT ac.*, ci.name as original_name 
            FROM ai_clothes ac 
            LEFT JOIN clothes_images ci ON ac.original_clothes_id = ci.id 
            WHERE ac.id = ?
        '''
        self.cursor.execute(sql, (ai_clothes_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def delete_ai_clothes(self, ai_clothes_id):
        self.cursor.execute('DELETE FROM ai_clothes WHERE id = ?', (ai_clothes_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def add_dressed_model(self, original_model_id, ai_clothes_id, new_image_path):
        sql = 'INSERT INTO dressed_models (original_model_id, ai_clothes_id, new_image_path, created_at) VALUES (?, ?, ?, ?)'
        self.cursor.execute(sql, (original_model_id, ai_clothes_id, new_image_path, self._get_timestamp()))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_all_dressed_models(self):
        sql = '''
            SELECT dm.*, mi.name as original_model_name, ac.id as ai_clothes_id
            FROM dressed_models dm 
            LEFT JOIN model_images mi ON dm.original_model_id = mi.id 
            LEFT JOIN ai_clothes ac ON dm.ai_clothes_id = ac.id 
            ORDER BY dm.created_at DESC
        '''
        self.cursor.execute(sql)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_dressed_model_by_id(self, dressed_model_id):
        sql = '''
            SELECT dm.*, mi.name as original_model_name, ac.id as ai_clothes_id
            FROM dressed_models dm 
            LEFT JOIN model_images mi ON dm.original_model_id = mi.id 
            LEFT JOIN ai_clothes ac ON dm.ai_clothes_id = ac.id 
            WHERE dm.id = ?
        '''
        self.cursor.execute(sql, (dressed_model_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def delete_dressed_model(self, dressed_model_id):
        self.cursor.execute('DELETE FROM dressed_models WHERE id = ?', (dressed_model_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def add_new_video(self, original_video_id, dressed_model_id, new_video_path):
        sql = 'INSERT INTO new_videos (original_video_id, dressed_model_id, new_video_path, created_at) VALUES (?, ?, ?, ?)'
        self.cursor.execute(sql, (original_video_id, dressed_model_id, new_video_path, self._get_timestamp()))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_all_new_videos(self):
        sql = '''
            SELECT nv.*, dv.name as original_video_name, dm.id as dressed_model_id
            FROM new_videos nv 
            LEFT JOIN dance_videos dv ON nv.original_video_id = dv.id 
            LEFT JOIN dressed_models dm ON nv.dressed_model_id = dm.id 
            ORDER BY nv.created_at DESC
        '''
        self.cursor.execute(sql)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_new_video_by_id(self, video_id):
        sql = '''
            SELECT nv.*, dv.name as original_video_name, dm.id as dressed_model_id
            FROM new_videos nv 
            LEFT JOIN dance_videos dv ON nv.original_video_id = dv.id 
            LEFT JOIN dressed_models dm ON nv.dressed_model_id = dm.id 
            WHERE nv.id = ?
        '''
        self.cursor.execute(sql, (video_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def delete_new_video(self, video_id):
        self.cursor.execute('DELETE FROM new_videos WHERE id = ?', (video_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def add_image_gen_config(self, name, config_type, config_content):
        sql = 'INSERT INTO image_gen_configs (name, config_type, config_content, created_at) VALUES (?, ?, ?, ?)'
        self.cursor.execute(sql, (name, config_type, config_content, self._get_timestamp()))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_all_image_gen_configs(self):
        self.cursor.execute('SELECT * FROM image_gen_configs ORDER BY created_at DESC')
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_image_gen_config_by_id(self, config_id):
        self.cursor.execute('SELECT * FROM image_gen_configs WHERE id = ?', (config_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def update_image_gen_config(self, config_id, name=None, config_type=None, config_content=None):
        updates = []
        params = []
        
        if name is not None:
            updates.append('name = ?')
            params.append(name)
        if config_type is not None:
            updates.append('config_type = ?')
            params.append(config_type)
        if config_content is not None:
            updates.append('config_content = ?')
            params.append(config_content)
        
        if not updates:
            return False
        
        params.append(config_id)
        sql = f'UPDATE image_gen_configs SET {", ".join(updates)} WHERE id = ?'
        self.cursor.execute(sql, params)
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def delete_image_gen_config(self, config_id):
        self.cursor.execute('DELETE FROM image_gen_configs WHERE id = ?', (config_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def add_model_gen_config(self, name, config_type, config_content):
        sql = 'INSERT INTO model_gen_configs (name, config_type, config_content, created_at) VALUES (?, ?, ?, ?)'
        self.cursor.execute(sql, (name, config_type, config_content, self._get_timestamp()))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_all_model_gen_configs(self):
        self.cursor.execute('SELECT * FROM model_gen_configs ORDER BY created_at DESC')
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_model_gen_config_by_id(self, config_id):
        self.cursor.execute('SELECT * FROM model_gen_configs WHERE id = ?', (config_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def update_model_gen_config(self, config_id, name=None, config_type=None, config_content=None):
        updates = []
        params = []
        
        if name is not None:
            updates.append('name = ?')
            params.append(name)
        if config_type is not None:
            updates.append('config_type = ?')
            params.append(config_type)
        if config_content is not None:
            updates.append('config_content = ?')
            params.append(config_content)
        
        if not updates:
            return False
        
        params.append(config_id)
        sql = f'UPDATE model_gen_configs SET {", ".join(updates)} WHERE id = ?'
        self.cursor.execute(sql, params)
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def delete_model_gen_config(self, config_id):
        self.cursor.execute('DELETE FROM model_gen_configs WHERE id = ?', (config_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def add_video_gen_config(self, name, config_type, config_content):
        sql = 'INSERT INTO video_gen_configs (name, config_type, config_content, created_at) VALUES (?, ?, ?, ?)'
        self.cursor.execute(sql, (name, config_type, config_content, self._get_timestamp()))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_all_video_gen_configs(self):
        self.cursor.execute('SELECT * FROM video_gen_configs ORDER BY created_at DESC')
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_video_gen_config_by_id(self, config_id):
        self.cursor.execute('SELECT * FROM video_gen_configs WHERE id = ?', (config_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def update_video_gen_config(self, config_id, name=None, config_type=None, config_content=None):
        updates = []
        params = []
        
        if name is not None:
            updates.append('name = ?')
            params.append(name)
        if config_type is not None:
            updates.append('config_type = ?')
            params.append(config_type)
        if config_content is not None:
            updates.append('config_content = ?')
            params.append(config_content)
        
        if not updates:
            return False
        
        params.append(config_id)
        sql = f'UPDATE video_gen_configs SET {", ".join(updates)} WHERE id = ?'
        self.cursor.execute(sql, params)
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def delete_video_gen_config(self, config_id):
        self.cursor.execute('DELETE FROM video_gen_configs WHERE id = ?', (config_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def add_image_to_video_gen_config(self, name, config_type, config_content):
        sql = 'INSERT INTO image_to_video_gen_configs (name, config_type, config_content, created_at) VALUES (?, ?, ?, ?)'
        self.cursor.execute(sql, (name, config_type, config_content, self._get_timestamp()))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_all_image_to_video_gen_configs(self):
        self.cursor.execute('SELECT * FROM image_to_video_gen_configs ORDER BY created_at DESC')
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_image_to_video_gen_config_by_id(self, config_id):
        self.cursor.execute('SELECT * FROM image_to_video_gen_configs WHERE id = ?', (config_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def update_image_to_video_gen_config(self, config_id, name=None, config_type=None, config_content=None):
        updates = []
        params = []
        
        if name is not None:
            updates.append('name = ?')
            params.append(name)
        if config_type is not None:
            updates.append('config_type = ?')
            params.append(config_type)
        if config_content is not None:
            updates.append('config_content = ?')
            params.append(config_content)
        
        if not updates:
            return False
        
        params.append(config_id)
        sql = f'UPDATE image_to_video_gen_configs SET {", ".join(updates)} WHERE id = ?'
        self.cursor.execute(sql, params)
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def delete_image_to_video_gen_config(self, config_id):
        self.cursor.execute('DELETE FROM image_to_video_gen_configs WHERE id = ?', (config_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def add_video_gen_task(self, status, video_gen_config_id, original_video_id, 
                           dressed_model_id, result_desc=None, external_task_id=None, new_video_id=None):
        sql = '''
            INSERT INTO video_gen_tasks 
            (status, result_desc, submitted_at, external_task_id, new_video_id, 
             video_gen_config_id, original_video_id, dressed_model_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        self.cursor.execute(sql, (status, result_desc, self._get_timestamp(), 
                                  external_task_id, new_video_id, 
                                  video_gen_config_id, original_video_id, dressed_model_id))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_all_video_gen_tasks(self):
        sql = '''
            SELECT vgt.*, vgc.name as config_name, dv.name as video_name, dm.new_image_path as model_image
            FROM video_gen_tasks vgt
            LEFT JOIN video_gen_configs vgc ON vgt.video_gen_config_id = vgc.id
            LEFT JOIN dance_videos dv ON vgt.original_video_id = dv.id
            LEFT JOIN dressed_models dm ON vgt.dressed_model_id = dm.id
            ORDER BY vgt.submitted_at DESC
        '''
        self.cursor.execute(sql)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_video_gen_task_by_id(self, task_id):
        sql = '''
            SELECT vgt.*, vgc.name as config_name, dv.name as video_name, dm.new_image_path as model_image
            FROM video_gen_tasks vgt
            LEFT JOIN video_gen_configs vgc ON vgt.video_gen_config_id = vgc.id
            LEFT JOIN dance_videos dv ON vgt.original_video_id = dv.id
            LEFT JOIN dressed_models dm ON vgt.dressed_model_id = dm.id
            WHERE vgt.id = ?
        '''
        self.cursor.execute(sql, (task_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def get_video_gen_tasks_by_status(self, status):
        sql = '''
            SELECT vgt.*, vgc.name as config_name, dv.name as video_name, dm.new_image_path as model_image
            FROM video_gen_tasks vgt
            LEFT JOIN video_gen_configs vgc ON vgt.video_gen_config_id = vgc.id
            LEFT JOIN dance_videos dv ON vgt.original_video_id = dv.id
            LEFT JOIN dressed_models dm ON vgt.dressed_model_id = dm.id
            WHERE vgt.status = ?
            ORDER BY vgt.submitted_at DESC
        '''
        self.cursor.execute(sql, (status,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def update_video_gen_task(self, task_id, status=None, result_desc=None, 
                              external_task_id=None, new_video_id=None):
        updates = []
        params = []
        
        if status is not None:
            updates.append('status = ?')
            params.append(status)
        if result_desc is not None:
            updates.append('result_desc = ?')
            params.append(result_desc)
        if external_task_id is not None:
            updates.append('external_task_id = ?')
            params.append(external_task_id)
        if new_video_id is not None:
            updates.append('new_video_id = ?')
            params.append(new_video_id)
        
        if not updates:
            return False
        
        params.append(task_id)
        sql = f'UPDATE video_gen_tasks SET {", ".join(updates)} WHERE id = ?'
        self.cursor.execute(sql, params)
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def delete_video_gen_task(self, task_id):
        self.cursor.execute('DELETE FROM video_gen_tasks WHERE id = ?', (task_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def add_ai_dance_video_gen_task(self, dance_video_id, model_image_id, clothes_image_id,
                                    image_gen_config_id, model_gen_config_id, video_gen_config_id,
                                    status, result_desc=None, ai_clothes_id=None, 
                                    dressed_model_id=None, new_video_id=None):
        sql = '''
            INSERT INTO ai_dance_video_gen_tasks 
            (dance_video_id, model_image_id, clothes_image_id, image_gen_config_id, 
             model_gen_config_id, video_gen_config_id, ai_clothes_id, dressed_model_id, 
             new_video_id, submitted_at, status, result_desc)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        self.cursor.execute(sql, (dance_video_id, model_image_id, clothes_image_id, 
                                  image_gen_config_id, model_gen_config_id, video_gen_config_id,
                                  ai_clothes_id, dressed_model_id, new_video_id,
                                  self._get_timestamp(), status, result_desc))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_all_ai_dance_video_gen_tasks(self):
        sql = '''
            SELECT advt.*, dv.name as dance_video_name, mi.name as model_image_name,
                   ci.name as clothes_image_name, igc.name as image_gen_config_name,
                   mgc.name as model_gen_config_name, vgc.name as video_gen_config_name,
                   nv.new_video_path as output_video_path
            FROM ai_dance_video_gen_tasks advt
            LEFT JOIN dance_videos dv ON advt.dance_video_id = dv.id
            LEFT JOIN model_images mi ON advt.model_image_id = mi.id
            LEFT JOIN clothes_images ci ON advt.clothes_image_id = ci.id
            LEFT JOIN image_gen_configs igc ON advt.image_gen_config_id = igc.id
            LEFT JOIN model_gen_configs mgc ON advt.model_gen_config_id = mgc.id
            LEFT JOIN video_gen_configs vgc ON advt.video_gen_config_id = vgc.id
            LEFT JOIN new_videos nv ON advt.new_video_id = nv.id
            ORDER BY advt.submitted_at DESC
        '''
        self.cursor.execute(sql)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_ai_dance_video_gen_task_by_id(self, task_id):
        sql = '''
            SELECT advt.*, dv.name as dance_video_name, mi.name as model_image_name,
                   ci.name as clothes_image_name, igc.name as image_gen_config_name,
                   mgc.name as model_gen_config_name, vgc.name as video_gen_config_name,
                   nv.new_video_path as output_video_path
            FROM ai_dance_video_gen_tasks advt
            LEFT JOIN dance_videos dv ON advt.dance_video_id = dv.id
            LEFT JOIN model_images mi ON advt.model_image_id = mi.id
            LEFT JOIN clothes_images ci ON advt.clothes_image_id = ci.id
            LEFT JOIN image_gen_configs igc ON advt.image_gen_config_id = igc.id
            LEFT JOIN model_gen_configs mgc ON advt.model_gen_config_id = mgc.id
            LEFT JOIN video_gen_configs vgc ON advt.video_gen_config_id = vgc.id
            LEFT JOIN new_videos nv ON advt.new_video_id = nv.id
            WHERE advt.id = ?
        '''
        self.cursor.execute(sql, (task_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def get_ai_dance_video_gen_tasks_by_status(self, status):
        sql = '''
            SELECT advt.*, dv.name as dance_video_name, mi.name as model_image_name,
                   ci.name as clothes_image_name, igc.name as image_gen_config_name,
                   mgc.name as model_gen_config_name, vgc.name as video_gen_config_name,
                   nv.new_video_path as output_video_path
            FROM ai_dance_video_gen_tasks advt
            LEFT JOIN dance_videos dv ON advt.dance_video_id = dv.id
            LEFT JOIN model_images mi ON advt.model_image_id = mi.id
            LEFT JOIN clothes_images ci ON advt.clothes_image_id = ci.id
            LEFT JOIN image_gen_configs igc ON advt.image_gen_config_id = igc.id
            LEFT JOIN model_gen_configs mgc ON advt.model_gen_config_id = mgc.id
            LEFT JOIN video_gen_configs vgc ON advt.video_gen_config_id = vgc.id
            LEFT JOIN new_videos nv ON advt.new_video_id = nv.id
            WHERE advt.status = ?
            ORDER BY advt.submitted_at DESC
        '''
        self.cursor.execute(sql, (status,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def update_ai_dance_video_gen_task(self, task_id, status=None, result_desc=None,
                                       ai_clothes_id=None, dressed_model_id=None, new_video_id=None):
        updates = []
        params = []
        
        if status is not None:
            updates.append('status = ?')
            params.append(status)
        if result_desc is not None:
            updates.append('result_desc = ?')
            params.append(result_desc)
        if ai_clothes_id is not None:
            updates.append('ai_clothes_id = ?')
            params.append(ai_clothes_id)
        if dressed_model_id is not None:
            updates.append('dressed_model_id = ?')
            params.append(dressed_model_id)
        if new_video_id is not None:
            updates.append('new_video_id = ?')
            params.append(new_video_id)
        
        if not updates:
            return False
        
        params.append(task_id)
        sql = f'UPDATE ai_dance_video_gen_tasks SET {", ".join(updates)} WHERE id = ?'
        self.cursor.execute(sql, params)
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def delete_ai_dance_video_gen_task(self, task_id):
        self.cursor.execute('DELETE FROM ai_dance_video_gen_tasks WHERE id = ?', (task_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def add_image_to_video(self, image_to_video_gen_config_id, dressed_model_id, video_path):
        sql = '''
            INSERT INTO image_to_videos 
            (image_to_video_gen_config_id, dressed_model_id, video_path, created_at) 
            VALUES (?, ?, ?, ?)
        '''
        self.cursor.execute(sql, (image_to_video_gen_config_id, dressed_model_id, video_path, self._get_timestamp()))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_all_image_to_videos(self):
        sql = '''
            SELECT iv.*, itvc.name as config_name
            FROM image_to_videos iv
            LEFT JOIN image_to_video_gen_configs itvc ON iv.image_to_video_gen_config_id = itvc.id
            ORDER BY iv.created_at DESC
        '''
        self.cursor.execute(sql)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_image_to_video_by_id(self, video_id):
        sql = '''
            SELECT iv.*, itvc.name as config_name
            FROM image_to_videos iv
            LEFT JOIN image_to_video_gen_configs itvc ON iv.image_to_video_gen_config_id = itvc.id
            WHERE iv.id = ?
        '''
        self.cursor.execute(sql, (video_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def delete_image_to_video(self, video_id):
        self.cursor.execute('DELETE FROM image_to_videos WHERE id = ?', (video_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def add_image_to_video_gen_task(self, model_image_id, clothes_image_id,
                                    image_gen_config_id, model_gen_config_id,
                                    image_to_video_gen_config_id, status,
                                    result_desc=None, ai_clothes_id=None,
                                    dressed_model_id=None, image_to_video_id=None,
                                    external_task_id=None):
        sql = '''
            INSERT INTO image_to_video_gen_tasks 
            (model_image_id, clothes_image_id, image_gen_config_id, 
             model_gen_config_id, image_to_video_gen_config_id, ai_clothes_id,
             dressed_model_id, image_to_video_id, submitted_at, status, result_desc,
             external_task_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        self.cursor.execute(sql, (model_image_id, clothes_image_id, image_gen_config_id,
                                  model_gen_config_id, image_to_video_gen_config_id,
                                  ai_clothes_id, dressed_model_id, image_to_video_id,
                                  self._get_timestamp(), status, result_desc,
                                  external_task_id))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_all_image_to_video_gen_tasks(self):
        sql = '''
            SELECT itvt.*, mi.name as model_image_name,
                   ci.name as clothes_image_name, igc.name as image_gen_config_name,
                   mgc.name as model_gen_config_name, itvc.name as image_to_video_gen_config_name,
                   iv.video_path as output_video_path
            FROM image_to_video_gen_tasks itvt
            LEFT JOIN model_images mi ON itvt.model_image_id = mi.id
            LEFT JOIN clothes_images ci ON itvt.clothes_image_id = ci.id
            LEFT JOIN image_gen_configs igc ON itvt.image_gen_config_id = igc.id
            LEFT JOIN model_gen_configs mgc ON itvt.model_gen_config_id = mgc.id
            LEFT JOIN image_to_video_gen_configs itvc ON itvt.image_to_video_gen_config_id = itvc.id
            LEFT JOIN image_to_videos iv ON itvt.image_to_video_id = iv.id
            ORDER BY itvt.submitted_at DESC
        '''
        self.cursor.execute(sql)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_image_to_video_gen_task_by_id(self, task_id):
        sql = '''
            SELECT itvt.*, mi.name as model_image_name,
                   ci.name as clothes_image_name, igc.name as image_gen_config_name,
                   mgc.name as model_gen_config_name, itvc.name as image_to_video_gen_config_name,
                   iv.video_path as output_video_path
            FROM image_to_video_gen_tasks itvt
            LEFT JOIN model_images mi ON itvt.model_image_id = mi.id
            LEFT JOIN clothes_images ci ON itvt.clothes_image_id = ci.id
            LEFT JOIN image_gen_configs igc ON itvt.image_gen_config_id = igc.id
            LEFT JOIN model_gen_configs mgc ON itvt.model_gen_config_id = mgc.id
            LEFT JOIN image_to_video_gen_configs itvc ON itvt.image_to_video_gen_config_id = itvc.id
            LEFT JOIN image_to_videos iv ON itvt.image_to_video_id = iv.id
            WHERE itvt.id = ?
        '''
        self.cursor.execute(sql, (task_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def get_image_to_video_gen_tasks_by_status(self, status):
        sql = '''
            SELECT itvt.*, mi.name as model_image_name,
                   ci.name as clothes_image_name, igc.name as image_gen_config_name,
                   mgc.name as model_gen_config_name, itvc.name as image_to_video_gen_config_name,
                   iv.video_path as output_video_path
            FROM image_to_video_gen_tasks itvt
            LEFT JOIN model_images mi ON itvt.model_image_id = mi.id
            LEFT JOIN clothes_images ci ON itvt.clothes_image_id = ci.id
            LEFT JOIN image_gen_configs igc ON itvt.image_gen_config_id = igc.id
            LEFT JOIN model_gen_configs mgc ON itvt.model_gen_config_id = mgc.id
            LEFT JOIN image_to_video_gen_configs itvc ON itvt.image_to_video_gen_config_id = itvc.id
            LEFT JOIN image_to_videos iv ON itvt.image_to_video_id = iv.id
            WHERE itvt.status = ?
            ORDER BY itvt.submitted_at DESC
        '''
        self.cursor.execute(sql, (status,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def update_image_to_video_gen_task(self, task_id, status=None, result_desc=None,
                                       ai_clothes_id=None, dressed_model_id=None, 
                                       image_to_video_id=None, external_task_id=None):
        updates = []
        params = []
        
        if status is not None:
            updates.append('status = ?')
            params.append(status)
        if result_desc is not None:
            updates.append('result_desc = ?')
            params.append(result_desc)
        if ai_clothes_id is not None:
            updates.append('ai_clothes_id = ?')
            params.append(ai_clothes_id)
        if dressed_model_id is not None:
            updates.append('dressed_model_id = ?')
            params.append(dressed_model_id)
        if image_to_video_id is not None:
            updates.append('image_to_video_id = ?')
            params.append(image_to_video_id)
        if external_task_id is not None:
            updates.append('external_task_id = ?')
            params.append(external_task_id)
        
        if not updates:
            return False
        
        params.append(task_id)
        sql = f'UPDATE image_to_video_gen_tasks SET {", ".join(updates)} WHERE id = ?'
        self.cursor.execute(sql, params)
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def delete_image_to_video_gen_task(self, task_id):
        self.cursor.execute('DELETE FROM image_to_video_gen_tasks WHERE id = ?', (task_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def close(self):
        if self.conn:
            self.conn.close()
