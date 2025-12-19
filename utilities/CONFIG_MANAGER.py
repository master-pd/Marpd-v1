"""
⚙️ CONFIGURATION MANAGER
Dynamic configuration with hot reload
"""

import json
import yaml
from pathlib import Path
import threading
import time

class ConfigManager:
    def __init__(self, core):
        self.core = core
        self.config_dir = Path("configs")
        self.config_dir.mkdir(exist_ok=True)
        
        self.configs = {}
        self.watchers = {}
        
        self._load_all_configs()
        self._start_config_watcher()
        print("⚙️ Config Manager Initialized")
    
    def _load_all_configs(self):
        """সব কনফিগ লোড"""
        config_files = list(self.config_dir.glob("*.json")) + list(self.config_dir.glob("*.yaml")) + list(self.config_dir.glob("*.yml"))
        
        for config_file in config_files:
            self._load_config_file(config_file)
    
    def _load_config_file(self, file_path):
        """একটি কনফিগ ফাইল লোড"""
        try:
            config_name = file_path.stem
            
            if file_path.suffix in ['.yaml', '.yml']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)
            else:  # .json
                with open(file_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
            
            self.configs[config_name] = config_data
            
            # কোর-এ সেট
            setattr(self.core, f"config_{config_name}", config_data)
            
            print(f"✅ Config loaded: {config_name}")
            return True
            
        except Exception as e:
            print(f"❌ Config load error {file_path}: {e}")
            return False
    
    def _start_config_watcher(self):
        """কনফিগ ওয়াচার শুরু"""
        def watcher_loop():
            file_timestamps = {}
            
            while True:
                try:
                    for config_file in self.config_dir.glob("*"):
                        current_mtime = config_file.stat().st_mtime
                        last_mtime = file_timestamps.get(config_file)
                        
                        if last_mtime and current_mtime > last_mtime:
                            print(f"🔄 Config changed: {config_file.name}")
                            self._load_config_file(config_file)
                            
                            # কনফিগ চেঞ্জ ইভেন্ট
                            if hasattr(self.core, 'broadcast_event'):
                                self.core.broadcast_event("config_changed", {
                                    "file": config_file.name,
                                    "time": time.time()
                                })
                        
                        file_timestamps[config_file] = current_mtime
                    
                except Exception as e:
                    print(f"⚠️ Config watcher error: {e}")
                
                time.sleep(5)
        
        threading.Thread(target=watcher_loop, daemon=True).start()
    
    def get_config(self, name, default=None):
        """কনফিগ পেতে"""
        return self.configs.get(name, default)
    
    def set_config(self, name, config_data):
        """কনফিগ সেট"""
        self.configs[name] = config_data
        
        # ফাইলে সেভ
        config_file = self.config_dir / f"{name}.json"
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        
        # কোর আপডেট
        setattr(self.core, f"config_{name}", config_data)
        
        return True
    
    def create_default_configs(self):
        """ডিফল্ট কনফিগ তৈরি"""
        default_configs = {
            "system": {
                "name": "YOUR CRUSH ⟵o_0",
                "version": "3.0",
                "developer": "RANA (MASTER 🪓)",
                "contact": "01847634486",
                "location": "Faridpur, Dhaka, Bangladesh"
            },
            "ai": {
                "learning_rate": 0.1,
                "confidence_threshold": 0.6,
                "max_patterns": 10000,
                "cache_size": 1000
            },
            "security": {
                "rate_limit": 10,
                "max_login_attempts": 5,
                "session_timeout": 3600,
                "encryption_level": "high"
            },
            "payment": {
                "price_per_month": 50,
                "currency": "BDT",
                "payment_methods": ["Nagad", "Bkash", "Rocket"],
                "payment_number": "01847634486",
                "receiver": "RANA (MASTER 🪓)"
            },
            "notifications": {
                "enabled": True,
                "channels": ["telegram", "email"],
                "schedule": "daily"
            }
        }
        
        for name, config_data in default_configs.items():
            self.set_config(name, config_data)
        
        print("✅ Default configs created")