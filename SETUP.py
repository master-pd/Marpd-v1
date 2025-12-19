"""
⚙️ AUTO SETUP SCRIPT
Automatically sets up the complete system
"""

import os
import sys
import json
import shutil
from pathlib import Path

def print_header():
    """হেডার প্রিন্ট"""
    print("""
╔══════════════════════════════════════╗
║    RANA BOT FACTORY - AUTO SETUP     ║
║    🤖 YOUR CRUSH ⟵o_0 v3.0          ║
║    👤 Developer: RANA (MASTER 🪓)    ║
╚══════════════════════════════════════╝
    """)

def check_requirements():
    """রিকোয়ারমেন্ট চেক"""
    print("🔍 Checking requirements...")
    
    required_modules = [
        "sys", "os", "json", "hashlib", "time", 
        "datetime", "random", "threading", "pathlib"
    ]
    
    missing = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            missing.append(module)
    
    if missing:
        print(f"\n❌ Missing modules: {', '.join(missing)}")
        return False
    
    # Optional: Check for telegram library
    try:
        import telegram
        print("✅ python-telegram-bot")
    except ImportError:
        print("⚠️ python-telegram-bot (optional)")
    
    return True

def create_directory_structure():
    """ডিরেক্টরি স্ট্রাকচার তৈরি"""
    print("\n📁 Creating directory structure...")
    
    directories = [
        "data",
        "data/plugins",
        "plugins",
        "logs",
        "backups"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ {directory}/")
    
    return True

def create_config_files():
    """কনফিগ ফাইল তৈরি"""
    print("\n⚙️ Creating configuration files...")
    
    # Default config
    default_config = {
        "system": {
            "name": "YOUR CRUSH ⟵o_0",
            "version": "3.0",
            "developer": "RANA (MASTER 🪓)",
            "contact": "01847634486"
        },
        "security": {
            "encryption_level": "high",
            "auto_backup": True,
            "backup_interval": 86400  # 24 hours
        },
        "ai": {
            "learning_enabled": True,
            "confidence_threshold": 0.6,
            "memory_size": 1000
        }
    }
    
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(default_config, f, indent=2, ensure_ascii=False)
    
    print("✅ config.json")
    
    # Create empty data files
    data_files = {
        "data/users.json": {},
        "data/credits.json": {},
        "data/ai_memory.json": {"patterns": {}, "learning": []},
        "data/ai_brain.json": {"patterns": {}, "connections": {}, "learning": []}
    }
    
    for file_path, data in data_files.items():
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ {file_path}")
    
    return True

def create_security_files():
    """সিকিউরিটি ফাইল তৈরি"""
    print("\n🔐 Creating security files...")
    
    # Security key
    import hashlib
    import time
    
    security_key = hashlib.sha256(
        f"RANA_BOT_{time.time()}_SECURE".encode()
    ).hexdigest()
    
    with open("security.key", "w") as f:
        f.write(security_key)
    
    print("✅ security.key")
    
    # Empty logs
    with open("security.log", "w") as f:
        f.write("Security Log - RANA Bot System\n")
        f.write("="*40 + "\n")
    
    print("✅ security.log")
    
    with open("system.log", "w") as f:
        f.write("System Log - YOUR CRUSH ⟵o_0 Bot\n")
        f.write("="*40 + "\n")
    
    print("✅ system.log")
    
    return True

def create_plugin_templates():
    """প্লাগইন টেম্পলেট তৈরি"""
    print("\n🧩 Creating plugin templates...")
    
    templates_dir = Path("plugin_templates")
    templates_dir.mkdir(exist_ok=True)
    
    # Basic plugin template
    basic_template = '''"""
{plugin_name} Plugin
Auto-generated plugin template
"""

def on_plugin_load(core):
    """Plugin load event"""
    print("✅ {plugin_name} plugin loaded")
    
    # Your initialization code here
    # Access core system: core.plugins, core.users, etc.
    
    return {{
        "plugin": "{plugin_name}",
        "version": "1.0",
        "author": "Your Name"
    }}

def handle_event(event_name, data=None):
    """Event handler"""
    if event_name == "test_event":
        # Handle test event
        return {{
            "handled": True,
            "plugin": "{plugin_name}",
            "result": "success"
        }}
    
    # Return None for unhandled events
    return None

def on_plugin_unload(core):
    """Plugin unload event"""
    print("👋 {plugin_name} plugin unloaded")
    # Cleanup code here
'''
    
    with open(templates_dir / "basic_plugin.py", "w", encoding="utf-8") as f:
        f.write(basic_template)
    
    print("✅ plugin_templates/basic_plugin.py")
    
    # Advanced plugin template
    advanced_template = '''"""
Advanced Plugin Template
With scheduled tasks and AI integration
"""

import threading
import time
from datetime import datetime

class AdvancedPlugin:
    def __init__(self, core):
        self.core = core
        self.running = False
        self.thread = None
        
    def start(self):
        """Start plugin"""
        self.running = True
        self.thread = threading.Thread(target=self._main_loop, daemon=True)
        self.thread.start()
        
    def stop(self):
        """Stop plugin"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
            
    def _main_loop(self):
        """Main plugin loop"""
        while self.running:
            try:
                # Your periodic tasks here
                current_time = datetime.now()
                
                # Example: Hourly task
                if current_time.minute == 0:
                    self._hourly_task()
                
            except Exception as e:
                print(f"⚠️ Plugin error: {{e}}")
            
            time.sleep(60)  # Check every minute
            
    def _hourly_task(self):
        """Example hourly task"""
        print(f"⏰ Hourly task at {{datetime.now().strftime('%H:%M')}}")
        
        # Broadcast event
        if hasattr(self.core, 'broadcast_event'):
            self.core.broadcast_event("hourly_check", {{
                "time": datetime.now().isoformat()
            }})

# Plugin interface functions
def on_plugin_load(core):
    """Load plugin"""
    print("🚀 Advanced plugin loading...")
    
    # Create plugin instance
    plugin = AdvancedPlugin(core)
    plugin.start()
    
    # Store in core
    core.advanced_plugin = plugin
    
    return {{
        "plugin": "advanced",
        "status": "running",
        "started": datetime.now().isoformat()
    }}

def handle_event(event_name, data=None):
    """Handle events"""
    # Your event handling logic here
    return None

def on_plugin_unload(core):
    """Unload plugin"""
    if hasattr(core, 'advanced_plugin'):
        core.advanced_plugin.stop()
        del core.advanced_plugin
    
    print("🛑 Advanced plugin stopped")
'''
    
    with open(templates_dir / "advanced_plugin.py", "w", encoding="utf-8") as f:
        f.write(advanced_template)
    
    print("✅ plugin_templates/advanced_plugin.py")
    
    return True

def create_readme():
    """README ফাইল তৈরি"""
    print("\n📖 Creating documentation...")
    
    readme_content = """# 🤖 YOUR CRUSH ⟵o_0 - AI Bot System

## 📋 Overview
Complete AI-powered Telegram bot system with auto-learning capabilities.

## 🚀 Quick Start

### 1. Installation
```bash
# Clone or extract files
cd rana_bot_factory

# Run setup
python SETUP.py

# Start the system
python RUN_BOT.py