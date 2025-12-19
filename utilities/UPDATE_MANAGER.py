"""
🔄 AUTO UPDATE MANAGER
Automatic updates and version management
"""

import json
import hashlib
import subprocess
from datetime import datetime
from pathlib import Path
import sys
import threading

class UpdateManager:
    def __init__(self, core):
        self.core = core
        self.update_dir = Path("updates")
        self.update_dir.mkdir(exist_ok=True)
        
        self.current_version = "3.0.0"
        self.available_updates = []
        self.update_in_progress = False
        
        self._check_for_updates()
        print("🔄 Update Manager Ready")
    
    def _check_for_updates(self):
        """আপডেট চেক"""
        # This would check a remote server
        # For now, use local update files
        
        update_files = list(self.update_dir.glob("update_*.json"))
        
        for update_file in update_files:
            try:
                with open(update_file, 'r') as f:
                    update_info = json.load(f)
                
                if self._is_newer_version(update_info.get("version", "")):
                    self.available_updates.append(update_info)
                    
            except Exception as e:
                print(f"⚠️ Update file error {update_file}: {e}")
    
    def _is_newer_version(self, version):
        """নতুন ভার্সন চেক"""
        current_parts = list(map(int, self.current_version.split(".")))
        new_parts = list(map(int, version.split(".")))
        
        return new_parts > current_parts
    
    def apply_update(self, update_file):
        """আপডেট প্রয়োগ"""
        if self.update_in_progress:
            return {"success": False, "error": "Update already in progress"}
        
        self.update_in_progress = True
        
        try:
            update_path = self.update_dir / update_file
            
            if not update_path.exists():
                return {"success": False, "error": "Update file not found"}
            
            with open(update_path, 'r') as f:
                update_info = json.load(f)
            
            print(f"🔄 Applying update: {update_info.get('name', 'Unknown')}")
            
            # ব্যাকআপ তৈরি
            backup_result = self._create_backup()
            
            # আপডেট স্ক্রিপ্ট এক্সিকিউট
            if "script" in update_info:
                script_success = self._execute_update_script(update_info["script"])
                
                if not script_success:
                    # ব্যাকআপ থেকে রিস্টোর
                    self._restore_from_backup(backup_result)
                    return {"success": False, "error": "Update script failed"}
            
            # ভার্সন আপডেট
            self.current_version = update_info.get("version", self.current_version)
            
            # আপডেট লগ
            self._log_update(update_info, True)
            
            # আপডেটেড ফাইলস লিস্ট থেকে রিমুভ
            self.available_updates = [u for u in self.available_updates if u.get("file") != update_file]
            
            print(f"✅ Update applied: {update_info.get('version')}")
            
            return {
                "success": True,
                "version": update_info.get("version"),
                "changes": update_info.get("changes", [])
            }
            
        except Exception as e:
            print(f"❌ Update error: {e}")
            return {"success": False, "error": str(e)}
        
        finally:
            self.update_in_progress = False
    
    def _create_backup(self):
        """ব্যাকআপ তৈরি"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"pre_update_{timestamp}"
        
        try:
            import shutil
            import tempfile
            
            temp_dir = tempfile.mkdtemp()
            backup_path = Path(temp_dir) / backup_name
            
            # গুরুত্বপূর্ণ ফাইল কপি
            important_files = [
                "SYSTEM_CORE.py",
                "AUTO_LOADER.py",
                "plugins/",
                "data/"
            ]
            
            for item in important_files:
                source = Path(item)
                if source.exists():
                    if source.is_dir():
                        shutil.copytree(source, backup_path / source.name)
                    else:
                        shutil.copy2(source, backup_path / source.name)
            
            return {
                "success": True,
                "backup_path": str(backup_path),
                "timestamp": timestamp
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _execute_update_script(self, script_content):
        """আপডেট স্ক্রিপ্ট এক্সিকিউট"""
        try:
            # স্ক্রিপ্ট ফাইল তৈরি
            script_file = self.update_dir / "temp_update_script.py"
            
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            # এক্সিকিউট
            result = subprocess.run(
                [sys.executable, str(script_file)],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # টেম্প ফাইল ডিলিট
            script_file.unlink(missing_ok=True)
            
            if result.returncode == 0:
                print(f"✅ Update script executed successfully")
                return True
            else:
                print(f"❌ Update script failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Script execution error: {e}")
            return False
    
    def _restore_from_backup(self, backup_info):
        """ব্যাকআপ থেকে রিস্টোর"""
        if not backup_info.get("success"):
            print("❌ No backup available for restore")
            return False
        
        print("🔄 Restoring from backup...")
        # Restore logic here
        return True
    
    def _log_update(self, update_info, success):
        """আপডেট লগ"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "version": update_info.get("version"),
            "name": update_info.get("name", ""),
            "success": success,
            "file": update_info.get("file", "")
        }
        
        log_file = Path("update_log.json")
        
        logs = []
        if log_file.exists():
            with open(log_file, 'r') as f:
                logs = json.load(f)
        
        logs.append(log_entry)
        
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)