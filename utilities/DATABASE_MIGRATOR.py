"""
🔄 DATABASE MIGRATION SYSTEM
Schema migrations and data updates
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
import shutil

class DatabaseMigrator:
    def __init__(self, core):
        self.core = core
        self.migrations_dir = Path("migrations")
        self.migrations_dir.mkdir(exist_ok=True)
        
        self._load_migration_history()
        print("🔄 Database Migrator Ready")
    
    def _load_migration_history(self):
        """মাইগ্রেশন হিস্টোরি লোড"""
        history_file = self.migrations_dir / "migration_history.json"
        
        if history_file.exists():
            with open(history_file, 'r') as f:
                self.history = json.load(f)
        else:
            self.history = {
                "applied_migrations": [],
                "last_migration": None,
                "schema_version": "1.0.0"
            }
    
    def _save_migration_history(self):
        """মাইগ্রেশন হিস্টোরি সেভ"""
        history_file = self.migrations_dir / "migration_history.json"
        
        with open(history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def create_migration(self, name, description=""):
        """নতুন মাইগ্রেশন তৈরি"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        migration_id = f"{timestamp}_{name}"
        
        migration_file = self.migrations_dir / f"{migration_id}.py"
        
        template = f'''"""
Migration: {name}
Created: {datetime.now().isoformat()}
Description: {description}
"""

def up(core):
    """
    Apply migration - add your schema changes here
    """
    print(f"Applying migration: {name}")
    
    # Example: Add new field to users
    if hasattr(core, '_users'):
        for user_id, user_data in core._users.items():
            if 'migrated' not in user_data:
                user_data['migrated'] = True
    
    return True

def down(core):
    """
    Rollback migration - undo your changes here
    """
    print(f"Rolling back migration: {name}")
    
    # Example: Remove added field
    if hasattr(core, '_users'):
        for user_id, user_data in core._users.items():
            if 'migrated' in user_data:
                del user_data['migrated']
    
    return True
'''
        
        with open(migration_file, 'w', encoding='utf-8') as f:
            f.write(template)
        
        print(f"✅ Migration created: {migration_id}")
        return migration_id
    
    def apply_migration(self, migration_id):
        """মাইগ্রেশন প্রয়োগ"""
        migration_file = self.migrations_dir / f"{migration_id}.py"
        
        if not migration_file.exists():
            print(f"❌ Migration not found: {migration_id}")
            return False
        
        try:
            # মাইগ্রেশন লোড
            with open(migration_file, 'r', encoding='utf-8') as f:
                migration_code = f.read()
            
            exec_globals = {}
            exec(migration_code, exec_globals)
            
            # up() ফাংশন কল
            if 'up' in exec_globals:
                success = exec_globals['up'](self.core)
                
                if success:
                    # হিস্টোরিতে যোগ
                    self.history["applied_migrations"].append({
                        "id": migration_id,
                        "applied_at": datetime.now().isoformat(),
                        "status": "applied"
                    })
                    
                    self.history["last_migration"] = datetime.now().isoformat()
                    self._save_migration_history()
                    
                    # কোর ডাটা সেভ
                    if hasattr(self.core, '_save_data'):
                        self.core._save_data()
                    
                    print(f"✅ Migration applied: {migration_id}")
                    return True
                else:
                    print(f"❌ Migration failed: {migration_id}")
                    return False
            else:
                print(f"❌ No 'up' function in migration: {migration_id}")
                return False
                
        except Exception as e:
            print(f"❌ Migration error: {e}")
            return False
    
    def rollback_migration(self, migration_id):
        """মাইগ্রেশন রোলব্যাক"""
        migration_file = self.migrations_dir / f"{migration_id}.py"
        
        if not migration_file.exists():
            print(f"❌ Migration not found: {migration_id}")
            return False
        
        try:
            # মাইগ্রেশন লোড
            with open(migration_file, 'r', encoding='utf-8') as f:
                migration_code = f.read()
            
            exec_globals = {}
            exec(migration_code, exec_globals)
            
            # down() ফাংশন কল
            if 'down' in exec_globals:
                success = exec_globals['down'](self.core)
                
                if success:
                    # হিস্টোরি থেকে রিমুভ
                    self.history["applied_migrations"] = [
                        m for m in self.history["applied_migrations"]
                        if m["id"] != migration_id
                    ]
                    
                    self._save_migration_history()
                    
                    # কোর ডাটা সেভ
                    if hasattr(self.core, '_save_data'):
                        self.core._save_data()
                    
                    print(f"✅ Migration rolled back: {migration_id}")
                    return True
                else:
                    print(f"❌ Rollback failed: {migration_id}")
                    return False
            else:
                print(f"❌ No 'down' function in migration: {migration_id}")
                return False
                
        except Exception as e:
            print(f"❌ Rollback error: {e}")
            return False
    
    def list_migrations(self):
        """মাইগ্রেশন লিস্ট"""
        migrations = []
        
        for py_file in self.migrations_dir.glob("*.py"):
            if py_file.name == "__init__.py" or py_file.name == "migration_history.json":
                continue
            
            migration_id = py_file.stem
            applied = any(m["id"] == migration_id for m in self.history["applied_migrations"])
            
            migrations.append({
                "id": migration_id,
                "applied": applied,
                "file": py_file.name
            })
        
        return sorted(migrations, key=lambda x: x["id"], reverse=True)