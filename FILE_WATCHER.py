import time
import hashlib
from pathlib import Path
import threading

class FileIntegrityWatcher:
    def __init__(self):
        self.core_files = [
            "SYSTEM_CORE.py",
            "AUTO_LOADER.py", 
            "FILE_WATCHER.py",
            "SECURITY_VAULT.py",
            "AI_BRAIN.py",
            "TELEGRAM_HANDLER.py"
        ]
        
        self.file_hashes = {}
        self._running = True
        
        self._init_hashes()
        self._start_monitor()
        
        print("🔍 File Integrity Monitor Active")
    
    def _init_hashes(self):
        """ফাইল হ্যাশ ইনিশিয়ালাইজ"""
        for file_name in self.core_files:
            if Path(file_name).exists():
                self.file_hashes[file_name] = self._calculate_hash(file_name)
    
    def _calculate_hash(self, file_path):
        """ফাইল হ্যাশ ক্যালকুলেট"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except:
            return None
    
    def _start_monitor(self):
        """মনিটর শুরু"""
        def monitor_loop():
            while self._running:
                for file_name in self.core_files:
                    current_hash = self._calculate_hash(file_name)
                    original_hash = self.file_hashes.get(file_name)
                    
                    if original_hash and current_hash != original_hash:
                        print(f"🚨 ALERT: {file_name} has been modified!")
                        
                        # সিকিউরিটি অ্যাকশন
                        self._security_alert(file_name)
                
                time.sleep(30)  # প্রতি ৩০ সেকেন্ডে চেক
        
        threading.Thread(target=monitor_loop, daemon=True).start()
    
    def _security_alert(self, file_name):
        """সিকিউরিটি অ্যালার্ট"""
        print(f"🔒 Security breach detected in {file_name}")
        
        # লগ তৈরি
        log_msg = f"{time.ctime()}: {file_name} was modified\n"
        with open("security.log", "a") as f:
            f.write(log_msg)
    
    def stop(self):
        """মনিটর বন্ধ"""
        self._running = False