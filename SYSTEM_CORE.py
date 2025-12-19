import json
import time
import hashlib
import random
import threading
from datetime import datetime
from pathlib import Path

class RanaSystemCore:
    def __init__(self):
        print("""
╔══════════════════════════════════╗
║     🤖 YOUR CRUSH ⟵o_0          ║
║     Developer: RANA (MASTER 🪓)  ║
║     AI Bot System v3.0          ║
╚══════════════════════════════════╝
        """)
        
        self.base_path = Path(__file__).parent
        self.data_path = self.base_path / "data"
        self.plugins_path = self.base_path / "plugins"
        
        self.data_path.mkdir(exist_ok=True)
        (self.data_path / "plugins").mkdir(exist_ok=True)
        
        self._setup_security()
        self._load_data()
        
        self.plugins = {}
        self.active_users = {}
        self.ai_memory = {}
        
        self._running = True
        
        print("✅ System Initialized")
    
    def _setup_security(self):
        """সিকিউরিটি সেটআপ"""
        security_file = self.data_path / "security.key"
        if not security_file.exists():
            key = hashlib.sha256(str(time.time()).encode()).hexdigest()
            with open(security_file, 'w') as f:
                f.write(key)
    
    def _load_data(self):
        """ডাটা লোড"""
        data_files = {
            "users": self.data_path / "users.json",
            "credits": self.data_path / "credits.json",
            "memory": self.data_path / "memory.json"
        }
        
        for key, file_path in data_files.items():
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    setattr(self, f"_{key}", json.load(f))
            else:
                setattr(self, f"_{key}", {})
    
    def _save_data(self):
        """ডাটা সেভ"""
        with open(self.data_path / "users.json", 'w', encoding='utf-8') as f:
            json.dump(self._users, f, ensure_ascii=False, indent=2)
        
        with open(self.data_path / "credits.json", 'w', encoding='utf-8') as f:
            json.dump(self._credits, f, ensure_ascii=False, indent=2)
        
        with open(self.data_path / "memory.json", 'w', encoding='utf-8') as f:
            json.dump(self._memory, f, ensure_ascii=False, indent=2)
    
    def register_user(self, user_id, bot_token, chat_id):
        """নতুন ইউজার রেজিস্টার"""
        user_key = str(user_id)
        
        self._users[user_key] = {
            "bot_token": bot_token,
            "chat_id": chat_id,
            "registered": datetime.now().isoformat(),
            "status": "active",
            "credit": 0
        }
        
        self._credits[user_key] = 0
        self._save_data()
        
        return True
    
    def add_credit(self, user_id, amount=100):
        """ক্রেডিট যোগ"""
        user_key = str(user_id)
        current = self._credits.get(user_key, 0)
        self._credits[user_key] = current + amount
        self._save_data()
        return self._credits[user_key]
    
    def use_credit(self, user_id):
        """ক্রেডিট ব্যবহার"""
        user_key = str(user_id)
        if self._credits.get(user_key, 0) > 0:
            self._credits[user_key] -= 1
            self._save_data()
            return True
        return False
    
    def get_user_info(self):
        """ইউজার ইনফো"""
        return {
            "total_users": len(self._users),
            "active": len([u for u in self._users.values() if u.get("status") == "active"]),
            "total_credit": sum(self._credits.values())
        }
    
    def broadcast_event(self, event_name, data=None):
        """ইভেন্ট ব্রডকাস্ট"""
        results = {}
        for plugin_name, plugin in self.plugins.items():
            if hasattr(plugin, 'handle_event'):
                try:
                    result = plugin.handle_event(event_name, data)
                    if result:
                        results[plugin_name] = result
                except Exception as e:
                    print(f"⚠️ Plugin {plugin_name} error: {e}")
        
        return results
    
    def run(self):
        """সিস্টেম চালান"""
        print("\n" + "="*50)
        print("🚀 SYSTEM IS RUNNING")
        print("-"*50)
        print("📁 Add .py files to 'plugins/' folder")
        print("🔄 They will auto-load immediately")
        print("="*50 + "\n")
        
        try:
            while self._running:
                time.sleep(1)
                
                # প্রতি মিনিটে সিস্টেম চেক
                if int(time.time()) % 60 == 0:
                    self._save_data()
                    
        except KeyboardInterrupt:
            print("\n🛑 Shutting down system...")
            self._save_data()
            self._running = False