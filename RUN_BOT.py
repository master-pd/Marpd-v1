#!/usr/bin/env python3
"""
🚀 RANA AI BOT - MAIN RUNNER
YOUR CRUSH ⟵o_0 Bot System
"""

import sys
import time
from pathlib import Path

print("""
╔══════════════════════════════════════╗
║    🤖 YOUR CRUSH ⟵o_0 BOT v3.0      ║
║    Developer: RANA (MASTER 🪓)       ║
║    Location: Faridpur, Dhaka         ║
║    Contact: 01847634486              ║
╚══════════════════════════════════════╝
""")

# সিস্টেম চেক
required_files = [
    "SYSTEM_CORE.py",
    "AUTO_LOADER.py",
    "plugins/"
]

print("🔍 System check...")
for file in required_files:
    if Path(file).exists():
        print(f"✅ {file}")
    else:
        print(f"❌ {file} not found!")
        sys.exit(1)

# ইমপোর্ট
print("\n📦 Loading modules...")
from SYSTEM_CORE import RanaSystemCore
from AUTO_LOADER import AutoPluginLoader
from FILE_WATCHER import FileIntegrityWatcher

try:
    # সিস্টেম শুরু
    print("🚀 Starting system...")
    
    # ১. কোর সিস্টেম
    core = RanaSystemCore()
    
    # ২. অটো লোডার
    loader = AutoPluginLoader(core)
    
    # ৩. ফাইল মনিটর
    watcher = FileIntegrityWatcher()
    
    print("\n" + "="*50)
    print("🎉 SYSTEM READY TO USE!")
    print("="*50)
    print("\n📁 To add new features:")
    print("   1. Create .py file in 'plugins/' folder")
    print("   2. Save it")
    print("   3. It will auto-load immediately!")
    print("\n⚡ Current plugins:", len(core.plugins))
    
    # সিস্টেম চালান
    core.run()
    
except KeyboardInterrupt:
    print("\n\n🛑 Shutdown requested...")
    
except Exception as e:
    print(f"\n❌ System error: {e}")
    
finally:
    print("\n👋 Goodbye! - RANA (MASTER 🪓)")
    print("📞 Contact: 01847634486")