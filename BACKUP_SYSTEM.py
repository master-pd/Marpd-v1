import json
import shutil
import hashlib
import gzip
import tarfile
from datetime import datetime
from pathlib import Path
import threading
import time

class AutoBackupSystem:
    def __init__(self, core_system):
        self.core = core_system
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        
        self.backup_interval = 86400  # 24 hours
        self.max_backups = 30  # 30 days
        
        self._running = True
        self._start_backup_scheduler()
        
        print("💾 Auto Backup System Activated")
    
    def _start_backup_scheduler(self):
        """ব্যাকআপ শিডিউলার শুরু"""
        def backup_loop():
            last_backup = 0
            
            while self._running:
                current_time = time.time()
                
                if current_time - last_backup >= self.backup_interval:
                    try:
                        self.create_backup()
                        last_backup = current_time
                    except Exception as e:
                        print(f"❌ Backup failed: {e}")
                
                # পুরোনো ব্যাকআপ ক্লিনআপ
                self._cleanup_old_backups()
                
                time.sleep(3600)  # প্রতি ঘণ্টায় চেক
        
        threading.Thread(target=backup_loop, daemon=True).start()
    
    def create_backup(self):
        """নতুন ব্যাকআপ তৈরি"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}"
        backup_path = self.backup_dir / backup_name
        
        # টেম্পোরারি ফোল্ডার তৈরি
        temp_dir = self.backup_dir / "temp_backup"
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        
        temp_dir.mkdir()
        
        try:
            # ১. ডাটা ফাইল কপি
            data_files = [
                "data/users.json",
                "data/credits.json", 
                "data/ai_memory.json",
                "data/ai_brain.json",
                "config.json",
                "security.key"
            ]
            
            for file_path in data_files:
                if Path(file_path).exists():
                    shutil.copy2(file_path, temp_dir / Path(file_path).name)
            
            # ২. প্লাগইনস ব্যাকআপ
            plugins_backup = temp_dir / "plugins_list.json"
            plugins = {}
            
            for py_file in Path("plugins").glob("*.py"):
                if py_file.name.startswith("__"):
                    continue
                
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    plugins[py_file.name] = {
                        "content": content,
                        "size": len(content),
                        "modified": py_file.stat().st_mtime
                    }
            
            with open(plugins_backup, 'w', encoding='utf-8') as f:
                json.dump(plugins, f, ensure_ascii=False, indent=2)
            
            # ৩. সিস্টেম স্ট্যাটাস
            system_status = {
                "backup_time": datetime.now().isoformat(),
                "total_users": len(self.core._users) if hasattr(self.core, '_users') else 0,
                "total_credits": sum(self.core._credits.values()) if hasattr(self.core, '_credits') else 0,
                "plugins_count": len(self.core.plugins) if hasattr(self.core, 'plugins') else 0,
                "ai_patterns": len(self.core.ai_orchestrator.brain.patterns) 
                              if hasattr(self.core, 'ai_orchestrator') else 0
            }
            
            with open(temp_dir / "system_status.json", 'w') as f:
                json.dump(system_status, f, indent=2)
            
            # ৪. কমপ্রেস করে সংরক্ষণ
            backup_file = self.backup_dir / f"{backup_name}.tar.gz"
            
            with tarfile.open(backup_file, "w:gz") as tar:
                tar.add(temp_dir, arcname=backup_name)
            
            # হ্যাশ তৈরি
            backup_hash = self._calculate_file_hash(backup_file)
            
            # মেটাডাটা
            metadata = {
                "name": backup_name,
                "timestamp": datetime.now().isoformat(),
                "size": backup_file.stat().st_size,
                "hash": backup_hash,
                "status": "completed"
            }
            
            with open(self.backup_dir / f"{backup_name}.meta.json", 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # টেম্প ক্লিনআপ
            shutil.rmtree(temp_dir)
            
            print(f"✅ Backup created: {backup_name}")
            return backup_name
            
        except Exception as e:
            print(f"❌ Backup creation error: {e}")
            
            # ক্লিনআপ
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
            
            return None
    
    def _calculate_file_hash(self, file_path):
        """ফাইল হ্যাশ ক্যালকুলেট"""
        sha256 = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        
        return sha256.hexdigest()
    
    def _cleanup_old_backups(self):
        """পুরোনো ব্যাকআপ ক্লিনআপ"""
        try:
            backup_files = []
            
            for file in self.backup_dir.glob("backup_*.tar.gz"):
                meta_file = self.backup_dir / f"{file.stem}.meta.json"
                
                if meta_file.exists():
                    with open(meta_file, 'r') as f:
                        metadata = json.load(f)
                    
                    backup_files.append({
                        "file": file,
                        "meta": meta_file,
                        "timestamp": metadata.get("timestamp"),
                        "size": file.stat().st_size
                    })
            
            # তারিখ অনুযায়ী সাজান
            backup_files.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
            # বেশি পুরোনো ব্যাকআপ ডিলিট
            if len(backup_files) > self.max_backups:
                for old_backup in backup_files[self.max_backups:]:
                    try:
                        old_backup["file"].unlink()
                        old_backup["meta"].unlink()
                        print(f"🗑️ Old backup removed: {old_backup['file'].name}")
                    except:
                        pass
                        
        except Exception as e:
            print(f"⚠️ Backup cleanup error: {e}")
    
    def list_backups(self):
        """ব্যাকআপ লিস্ট"""
        backups = []
        
        for meta_file in self.backup_dir.glob("*.meta.json"):
            with open(meta_file, 'r') as f:
                metadata = json.load(f)
            
            backups.append({
                "name": metadata.get("name"),
                "timestamp": metadata.get("timestamp"),
                "size": metadata.get("size"),
                "hash": metadata.get("hash", "")[:16] + "..."
            })
        
        return sorted(backups, key=lambda x: x["timestamp"], reverse=True)
    
    def restore_backup(self, backup_name):
        """ব্যাকআপ থেকে রিস্টোর"""
        backup_file = self.backup_dir / f"{backup_name}.tar.gz"
        meta_file = self.backup_dir / f"{backup_name}.meta.json"
        
        if not backup_file.exists() or not meta_file.exists():
            return {"success": False, "error": "Backup not found"}
        
        try:
            # মেটাডাটা চেক
            with open(meta_file, 'r') as f:
                metadata = json.load(f)
            
            # হ্যাশ ভ্যালিডেশন
            current_hash = self._calculate_file_hash(backup_file)
            if current_hash != metadata.get("hash"):
                return {"success": False, "error": "Backup corrupted"}
            
            # টেম্প এক্সট্রাক্ট
            temp_dir = self.backup_dir / "temp_restore"
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            
            temp_dir.mkdir()
            
            with tarfile.open(backup_file, "r:gz") as tar:
                tar.extractall(temp_dir)
            
            # ফাইল রিস্টোর
            backup_data_dir = temp_dir / backup_name
            
            # ডাটা ফাইল রিস্টোর
            for data_file in backup_data_dir.glob("*.json"):
                if data_file.name in ["users.json", "credits.json", "ai_memory.json", "ai_brain.json"]:
                    shutil.copy2(data_file, Path("data") / data_file.name)
            
            # কনফিগ রিস্টোর
            config_file = backup_data_dir / "config.json"
            if config_file.exists():
                shutil.copy2(config_file, "config.json")
            
            # প্লাগইন রিস্টোর
            plugins_file = backup_data_dir / "plugins_list.json"
            if plugins_file.exists():
                with open(plugins_file, 'r', encoding='utf-8') as f:
                    plugins = json.load(f)
                
                for plugin_name, plugin_data in plugins.items():
                    plugin_path = Path("plugins") / plugin_name
                    with open(plugin_path, 'w', encoding='utf-8') as f:
                        f.write(plugin_data["content"])
            
            # ক্লিনআপ
            shutil.rmtree(temp_dir)
            
            print(f"✅ Backup restored: {backup_name}")
            
            # কোর সিস্টেম রিলোড
            if hasattr(self.core, '_load_data'):
                self.core._load_data()
            
            return {
                "success": True,
                "backup": backup_name,
                "restored_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Restore error: {e}")
            
            # ক্লিনআপ
            if Path("temp_restore").exists():
                shutil.rmtree("temp_restore", ignore_errors=True)
            
            return {"success": False, "error": str(e)}
    
    def stop(self):
        """ব্যাকআপ সিস্টেম বন্ধ"""
        self._running = False
        print("💾 Backup system stopped")