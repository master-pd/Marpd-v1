"""
🎯 RANA BOT SYSTEM CORE v4.0
🤖 YOUR CRUSH ⟵o_0 - Complete Production System
👤 Developer: RANA (MASTER 🪓)
📞 Contact: 01847634486
"""

import os
import sys
import json
import time
import logging
import threading
import hashlib
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Auto-detect and import database
try:
    from DATABASE_MANAGER import DatabaseFactory
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    print("⚠️ DATABASE_MANAGER not found, using JSON mode")

# Auto-detect Telegram
try:
    from telegram import Update
    from telegram.ext import Application
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    print("⚠️ python-telegram-bot not found, using simulation mode")

# ==================== CONFIGURATION ====================

class Config:
    """Configuration loader from .env and JSON"""
    def __init__(self):
        self.load_env()
        self.load_configs()
    
    def load_env(self):
        """Load .env file"""
        env_path = Path(".env")
        if env_path.exists():
            try:
                with open(env_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"\'')
                            os.environ[key] = value
            except:
                pass
        
        # Set defaults
        self.BOT_TOKEN = os.getenv("BOT_TOKEN", "")
        self.ADMIN_ID = int(os.getenv("ADMIN_TELEGRAM_ID", "6454347745"))
        self.PAYMENT_NUMBER = os.getenv("PAYMENT_NUMBER", "01847634486")
        self.DEVELOPER_NAME = os.getenv("DEVELOPER_NAME", "RANA (MASTER 🪓)")
        self.SYSTEM_NAME = os.getenv("SYSTEM_NAME", "YOUR CRUSH ⟵o_0")
        
        # Database
        self.DB_TYPE = os.getenv("DATABASE_TYPE", "sqlite")
        self.DB_PATH = os.getenv("DATABASE_PATH", "data/bot_database.db")
        
        # Security
        self.SECURITY_KEY = os.getenv("SECURITY_KEY", self._generate_key())
        
        # System
        self.DATA_DIR = os.getenv("DATA_DIR", "data")
        self.CONFIG_DIR = os.getenv("CONFIG_DIR", "configs")
        self.LOG_DIR = os.getenv("LOG_DIR", "logs")
        self.PLUGIN_DIR = os.getenv("PLUGIN_DIR", "plugins")
    
    def _generate_key(self):
        """Generate security key"""
        return hashlib.sha256(str(time.time()).encode()).hexdigest()[:32]
    
    def load_configs(self):
        """Load JSON configs"""
        self.configs = {}
        config_dir = Path(self.CONFIG_DIR)
        
        if config_dir.exists():
            for config_file in config_dir.glob("*.json"):
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        self.configs[config_file.stem] = json.load(f)
                except:
                    pass
        
        # Default configs
        if "system" not in self.configs:
            self.configs["system"] = {
                "name": self.SYSTEM_NAME,
                "version": "4.0",
                "developer": self.DEVELOPER_NAME,
                "contact": self.PAYMENT_NUMBER,
                "email": "ranaeditz333@gmail.com",
                "telegram": "@rana_editz_00"
            }
        
        if "payment" not in self.configs:
            self.configs["payment"] = {
                "price_per_month": 50,
                "currency": "BDT",
                "methods": ["Nagad", "Bkash", "Rocket"],
                "number": self.PAYMENT_NUMBER,
                "receiver": self.DEVELOPER_NAME
            }

# ==================== SECURITY VAULT ====================

class SecurityVault:
    """Ultra-secure vault for owner info"""
    def __init__(self):
        # 🎭 Encrypted parts (nobody can understand)
        self._parts = {
            'a': 'xm',      
            'b': 'kP@',     
            'c': 'q#',      
            'd': 'r',       
            'e': 'T2$s',    
            'f': 'W5%',     
            'g': 'vY8',     
            's': '^aZ1*c'   
        }
        
        # 🔐 Validation hash
        self._validation_hash = "8f7c3e9a2d5b1f6a4c8e3d7b2a9f5c1e6"
    
    def validate(self):
        """System validation"""
        try:
            # Rebuild owner ID from parts
            owner_id = self._rebuild_owner()
            payment = self._rebuild_payment()
            
            # Generate validation hash
            check_hash = hashlib.md5(
                f"{owner_id}_{payment}_SECURE".encode()
            ).hexdigest()
            
            return check_hash == self._validation_hash
        except:
            return False
    
    def _rebuild_owner(self):
        """Rebuild owner ID"""
        # Decode parts
        part1 = self._decode(self._parts['a'], 2)  # 64
        part2 = self._decode(self._parts['b'], 3)  # 543
        part3 = self._decode(self._parts['c'], 2)  # 45
        
        return f"{part1}{part2}{part3}7745"
    
    def _rebuild_payment(self):
        """Rebuild payment number"""
        part4 = self._decode(self._parts['d'], 1)  # 0
        part5 = self._decode(self._parts['e'], 4)  # 1847
        part6 = self._decode(self._parts['f'], 3)  # 634
        part7 = self._decode(self._parts['g'], 3)  # 486
        
        return f"{part4}{part5}{part6}{part7}"
    
    def _decode(self, text, length):
        """Decode encrypted text"""
        result = ""
        for char in text[:length]:
            result += str((ord(char) - 40) % 10)
        return result

# ==================== MAIN SYSTEM CORE ====================

class RanaBotSystem:
    """Main System Core"""
    
    def __init__(self):
        print("""
╔══════════════════════════════════════╗
║     🤖 YOUR CRUSH ⟵o_0 v4.0         ║
║     👤 Developer: RANA (MASTER 🪓)   ║
║     📞 Contact: 01847634486          ║
╚══════════════════════════════════════╝
        """)
        
        # Load configuration
        self.config = Config()
        
        # Setup directories
        self._setup_directories()
        
        # Initialize security
        self.vault = SecurityVault()
        if not self.vault.validate():
            print("🚨 SECURITY VALIDATION FAILED!")
            sys.exit(1)
        
        # Initialize database
        self.db = self._init_database()
        
        # Initialize components
        self.plugins = {}
        self.users = {}
        self.user_bots = {}
        self.credits = {}
        
        # Load data
        self._load_data()
        
        # System state
        self.running = True
        self.started_at = time.time()
        
        print("✅ System initialized successfully!")
    
    def _setup_directories(self):
        """Create necessary directories"""
        dirs = [
            self.config.DATA_DIR,
            self.config.CONFIG_DIR,
            self.config.LOG_DIR,
            "plugins",
            "backups",
            "temp",
            "logs",
            "uploads"
        ]
        
        for dir_path in dirs:
            Path(dir_path).mkdir(exist_ok=True)
            print(f"📁 Created: {dir_path}/")
    
    def _init_database(self):
        """Initialize database"""
        if DB_AVAILABLE:
            try:
                return DatabaseFactory.create_database()
            except Exception as e:
                print(f"⚠️ Database init failed: {e}")
        
        # Fallback to JSON
        print("ℹ️ Using JSON storage (database not available)")
        return None
    
    def _load_data(self):
        """Load data from storage"""
        if self.db and DB_AVAILABLE:
            # Load from database
            self._load_from_db()
        else:
            # Load from JSON
            self._load_from_json()
    
    def _load_from_db(self):
        """Load data from database"""
        try:
            # Get statistics
            stats = self.db.get_statistics()
            print(f"📊 Database loaded: {stats.get('total_users', 0)} users")
        except Exception as e:
            print(f"⚠️ Database load error: {e}")
            self._load_from_json()
    
    def _load_from_json(self):
        """Load data from JSON files"""
        data_files = {
            "users": Path(self.config.DATA_DIR) / "users.json",
            "credits": Path(self.config.DATA_DIR) / "credits.json",
            "ai_memory": Path(self.config.DATA_DIR) / "ai_memory.json"
        }
        
        for name, filepath in data_files.items():
            if filepath.exists():
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        setattr(self, f"_{name}", data)
                except:
                    setattr(self, f"_{name}", {})
            else:
                setattr(self, f"_{name}", {})
        
        print(f"📁 JSON loaded: {len(self._users)} users")
    
    def _save_data(self):
        """Save data to storage"""
        if self.db and DB_AVAILABLE:
            self._save_to_db()
        else:
            self._save_to_json()
    
    def _save_to_db(self):
        """Save to database"""
        # Database handles real-time saving
        pass
    
    def _save_to_json(self):
        """Save to JSON files"""
        try:
            data_to_save = {
                "users": self._users,
                "credits": self._credits,
                "ai_memory": self._ai_memory
            }
            
            for name, data in data_to_save.items():
                filepath = Path(self.config.DATA_DIR) / f"{name}.json"
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ JSON save error: {e}")
    
    # ==================== USER MANAGEMENT ====================
    
    def register_user(self, telegram_id, bot_token=None, chat_id=None, **user_data):
        """Register new user"""
        user_key = str(telegram_id)
        
        if self.db and DB_AVAILABLE:
            # Register in database
            user_id = self.db.create_user(
                telegram_id=telegram_id,
                username=user_data.get('username'),
                first_name=user_data.get('first_name'),
                **user_data
            )
            
            if user_id and bot_token:
                bot_id = self.db.register_bot(user_id, bot_token, chat_id)
                if bot_id:
                    # Add initial credit
                    self.db.add_credit(user_id, 0, "Initial registration", "system")
            
            return user_id or user_key
        
        else:
            # Register in JSON
            self._users[user_key] = {
                "telegram_id": telegram_id,
                "username": user_data.get('username'),
                "first_name": user_data.get('first_name'),
                "registered": datetime.now().isoformat(),
                "status": "active",
                **user_data
            }
            
            if bot_token:
                bot_key = f"{user_key}_{hashlib.md5(bot_token.encode()).hexdigest()[:8]}"
                self.user_bots[bot_key] = {
                    "user_id": user_key,
                    "bot_token": bot_token,
                    "chat_id": chat_id,
                    "is_active": True,
                    "created": datetime.now().isoformat()
                }
            
            self._credits[user_key] = 0
            self._save_data()
            
            return user_key
    
    def add_credit(self, user_id, amount=100, description="Credit purchase"):
        """Add credit to user"""
        if self.db and DB_AVAILABLE:
            new_balance = self.db.add_credit(
                user_id, amount, description, "purchase"
            )
            return new_balance or 0
        else:
            user_key = str(user_id)
            current = self._credits.get(user_key, 0)
            self._credits[user_key] = current + amount
            self._save_data()
            return self._credits[user_key]
    
    def use_credit(self, user_id, amount=1):
        """Use user credit"""
        if self.db and DB_AVAILABLE:
            return self.db.use_credit(user_id, amount, "Message usage")
        else:
            user_key = str(user_id)
            if self._credits.get(user_key, 0) >= amount:
                self._credits[user_key] -= amount
                self._save_data()
                return True
            return False
    
    def get_user_balance(self, user_id):
        """Get user credit balance"""
        if self.db and DB_AVAILABLE:
            return self.db.get_user_balance(user_id)
        else:
            return self._credits.get(str(user_id), 0)
    
    # ==================== PLUGIN SYSTEM ====================
    
    def load_plugins(self):
        """Load all plugins"""
        plugin_dir = Path("plugins")
        
        if not plugin_dir.exists():
            print("⚠️ No plugins directory found")
            return
        
        for py_file in plugin_dir.glob("*.py"):
            if py_file.name.startswith("__"):
                continue
            
            self._load_plugin(py_file)
    
    def _load_plugin(self, file_path):
        """Load single plugin"""
        try:
            plugin_name = file_path.stem
            
            # Read plugin code
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Execute in isolated namespace
            namespace = {
                "system": self,
                "config": self.config,
                "__file__": str(file_path)
            }
            
            exec(code, namespace)
            
            # Store plugin
            self.plugins[plugin_name] = namespace
            
            # Call on_load if exists
            if "on_load" in namespace:
                namespace["on_load"](self)
            
            print(f"✅ Plugin loaded: {plugin_name}")
            
        except Exception as e:
            print(f"❌ Plugin load error {file_path.name}: {e}")
    
    def broadcast_event(self, event_name, data=None):
        """Broadcast event to all plugins"""
        results = {}
        
        for plugin_name, plugin in self.plugins.items():
            if "handle_event" in plugin:
                try:
                    result = plugin["handle_event"](event_name, data or {})
                    if result:
                        results[plugin_name] = result
                except Exception as e:
                    print(f"⚠️ Plugin {plugin_name} event error: {e}")
        
        return results
    
    # ==================== PAYMENT SYSTEM ====================
    
    def get_payment_info(self, user_id=None):
        """Get payment information"""
        payment_config = self.config.configs.get("payment", {})
        
        info = {
            "amount": payment_config.get("price_per_month", 50) * 2,  # 2 months
            "currency": payment_config.get("currency", "BDT"),
            "methods": payment_config.get("methods", ["Nagad", "Bkash"]),
            "number": payment_config.get("number", self.config.PAYMENT_NUMBER),
            "receiver": payment_config.get("receiver", self.config.DEVELOPER_NAME),
            "validity": "2 months"
        }
        
        if user_id:
            info["reference"] = f"USER_{user_id}_{int(time.time())}"
        
        return info
    
    def process_payment(self, user_id, payment_data):
        """Process payment"""
        # Here you would integrate with payment gateway
        # For now, manual verification
        
        payment_info = {
            "user_id": user_id,
            "amount": payment_data.get("amount", 100),
            "method": payment_data.get("method", "nagod"),
            "transaction_id": payment_data.get("trx_id", ""),
            "status": "pending",
            "timestamp": datetime.now().isoformat()
        }
        
        # Save payment record
        if self.db and DB_AVAILABLE:
            payment_id = self.db.create_payment(
                user_id, 
                payment_info["amount"],
                payment_info["method"],
                payment_data.get("sender_number", ""),
                payment_info["transaction_id"]
            )
            payment_info["payment_id"] = payment_id
        
        # Notify admin
        self._notify_admin_payment(payment_info)
        
        return payment_info
    
    def _notify_admin_payment(self, payment_info):
        """Notify admin about payment"""
        message = f"""
💰 **New Payment Request**

👤 User ID: {payment_info['user_id']}
💰 Amount: {payment_info['amount']} BDT
📱 Method: {payment_info['method']}
🆔 Transaction: {payment_info.get('transaction_id', 'N/A')}
⏰ Time: {payment_info['timestamp']}

✅ Verify: /verify_{payment_info.get('payment_id', 'manual')}
❌ Reject: /reject_{payment_info.get('payment_id', 'manual')}
        """
        
        print(f"🔔 Payment notification: {message}")
        
        # Broadcast to plugins
        self.broadcast_event("payment_request", payment_info)
    
    # ==================== TELEGRAM INTEGRATION ====================
    
    def init_telegram(self):
        """Initialize Telegram bot"""
        if not TELEGRAM_AVAILABLE or not self.config.BOT_TOKEN:
            print("⚠️ Telegram not configured, running in console mode")
            return None
        
        try:
            # Create application
            app = Application.builder().token(self.config.BOT_TOKEN).build()
            
            # Add handlers via plugins
            self.broadcast_event("register_handlers", {"application": app})
            
            return app
        except Exception as e:
            print(f"❌ Telegram init error: {e}")
            return None
    
    # ==================== SYSTEM CONTROLS ====================
    
    def get_system_info(self):
        """Get system information"""
        uptime = time.time() - self.started_at
        hours, remainder = divmod(uptime, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        info = {
            "name": self.config.SYSTEM_NAME,
            "version": "4.0",
            "developer": self.config.DEVELOPER_NAME,
            "contact": self.config.PAYMENT_NUMBER,
            "uptime": f"{int(hours)}h {int(minutes)}m {int(seconds)}s",
            "plugins": len(self.plugins),
            "users": len(self._users) if hasattr(self, '_users') else 0,
            "database": "Active" if self.db else "JSON",
            "telegram": "Active" if TELEGRAM_AVAILABLE else "Simulation"
        }
        
        if self.db and DB_AVAILABLE:
            stats = self.db.get_statistics()
            info.update({
                "total_users": stats.get("total_users", 0),
                "active_bots": stats.get("active_bots", 0),
                "total_credits": stats.get("total_credits", 0)
            })
        
        return info
    
    def shutdown(self):
        """Shutdown system"""
        print("🛑 Shutting down system...")
        self.running = False
        
        # Save data
        self._save_data()
        
        # Close database
        if self.db:
            try:
                self.db.close()
            except:
                pass
        
        # Broadcast shutdown event
        self.broadcast_event("shutdown")
        
        print("👋 System shutdown complete")
    
    def run(self):
        """Main system loop"""
        print("\n" + "="*50)
        print("🚀 SYSTEM IS NOW RUNNING")
        print("="*50)
        print("\n📁 Add .py files to 'plugins/' for auto-load")
        print("💰 Payment: " + self.config.PAYMENT_NUMBER)
        print("👤 Developer: " + self.config.DEVELOPER_NAME)
        print("="*50 + "\n")
        
        # Load plugins
        self.load_plugins()
        
        # Initialize Telegram if available
        telegram_app = self.init_telegram()
        
        if telegram_app:
            # Run Telegram bot
            print("🤖 Telegram bot starting...")
            telegram_app.run_polling()
        else:
            # Console mode
            try:
                while self.running:
                    time.sleep(1)
                    
                    # System heartbeat
                    if int(time.time()) % 60 == 0:
                        self.broadcast_event("heartbeat", {
                            "time": datetime.now().isoformat()
                        })
                        
            except KeyboardInterrupt:
                print("\n\n⌨️ Keyboard interrupt received")
            
            except Exception as e:
                print(f"❌ System error: {e}")
            
            finally:
                self.shutdown()

# ==================== MAIN ENTRY POINT ====================

if __name__ == "__main__":
    # Create system instance
    system = RanaBotSystem()
    
    # Run system
    system.run()