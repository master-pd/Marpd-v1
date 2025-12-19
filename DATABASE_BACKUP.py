"""
💾 SQL DATABASE BACKUP SYSTEM
Automated database backup and restore
"""

import shutil
import gzip
import json
from datetime import datetime
from pathlib import Path

class SQLBackupSystem:
    def __init__(self, db_manager):
        self.db = db_manager
        self.backup_dir = Path("backups/sql")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self, backup_name=None):
        """SQL ডাটাবেজ ব্যাকআপ"""
        if not backup_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}"
        
        backup_path = self.backup_dir / f"{backup_name}.sql.gz"
        
        try:
            # SQLite এর জন্য বিশেষ ব্যাকআপ
            if self.db.db_type == "sqlite":
                db_path = self.db.config.get("path", "data/bot_database.db")
                
                # সরাসরি ফাইল কপি
                shutil.copy2(db_path, self.backup_dir / f"{backup_name}.db")
                
                # SQL ডাম্প তৈরি
                self._create_sqlite_dump(db_path, backup_path)
            else:
                # PostgreSQL/MySQL ডাম্প
                self._create_sql_dump(backup_path)
            
            # মেটাডাটা সেভ
            metadata = {
                "name": backup_name,
                "timestamp": datetime.now().isoformat(),
                "database_type": self.db.db_type,
                "tables": self._get_table_info(),
                "size": backup_path.stat().st_size if backup_path.exists() else 0
            }
            
            with open(self.backup_dir / f"{backup_name}.meta.json", 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print(f"✅ SQL backup created: {backup_name}")
            return backup_name
            
        except Exception as e:
            print(f"❌ Backup error: {e}")
            return None
    
    def _create_sqlite_dump(self, db_path, backup_path):
        """SQLite ডাম্প তৈরি"""
        import sqlite3
        
        conn = sqlite3.connect(db_path)
        
        with gzip.open(backup_path, 'wt', encoding='utf-8') as f:
            # টেবিল স্কিমা
            for line in conn.iterdump():
                f.write(line + '\n')
        
        conn.close()
    
    def _create_sql_dump(self, backup_path):
        """SQL ডাম্প তৈরি"""
        # PostgreSQL/MySQL এর জন্য ডাম্প লজিক
        # Note: প্রকৃত ইমপ্লিমেন্টেশনে pg_dump বা mysqldump ব্যবহার করতে হবে
        pass
    
    def _get_table_info(self):
        """টেবিল ইনফো"""
        tables = {}
        
        try:
            self.db.cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """)
            
            for table in self.db.cursor.fetchall():
                table_name = table[0]
                
                # row count
                self.db.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = self.db.cursor.fetchone()[0]
                
                tables[table_name] = {"rows": row_count}
        except:
            pass
        
        return tables
    
    def restore_backup(self, backup_name):
        """ব্যাকআপ থেকে রিস্টোর"""
        backup_file = self.backup_dir / f"{backup_name}.sql.gz"
        
        if not backup_file.exists():
            return False
        
        try:
            if self.db.db_type == "sqlite":
                # বর্তমান ডাটাবেজ ব্যাকআপ
                current_backup = self.create_backup(f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                
                # পুরোনো ডাটাবেজ ডিলিট
                db_path = self.db.config.get("path", "data/bot_database.db")
                Path(db_path).unlink(missing_ok=True)
                
                # ব্যাকআপ থেকে রিস্টোর
                self._restore_sqlite(backup_file, db_path)
            else:
                # PostgreSQL/MySQL রিস্টোর
                self._restore_sql(backup_file)
            
            print(f"✅ Database restored from: {backup_name}")
            return True
            
        except Exception as e:
            print(f"❌ Restore error: {e}")
            return False
    
    def _restore_sqlite(self, backup_file, db_path):
        """SQLite রিস্টোর"""
        import sqlite3
        
        conn = sqlite3.connect(db_path)
        
        with gzip.open(backup_file, 'rt', encoding='utf-8') as f:
            sql_dump = f.read()
        
        conn.executescript(sql_dump)
        conn.close()