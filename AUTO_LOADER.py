import importlib.util
import sys
import time
from pathlib import Path
import threading

class AutoPluginLoader:
    def __init__(self, core_system):
        self.core = core_system
        self.plugins_dir = Path("plugins")
        self.plugins_dir.mkdir(exist_ok=True)
        
        self.loaded_plugins = {}
        self.watch_thread = None
        
        self._load_existing_plugins()
        self._start_watcher()
        
        print("🔄 Auto-Loader Ready")
    
    def _load_existing_plugins(self):
        """বিদ্যমান প্লাগইন লোড"""
        for py_file in self.plugins_dir.glob("*.py"):
            if py_file.name.startswith("__"):
                continue
            self._load_plugin(py_file)
    
    def _load_plugin(self, file_path):
        """একটি প্লাগইন লোড"""
        try:
            plugin_name = file_path.stem
            
            # মডিউল স্পেসিফিকেশন তৈরি
            spec = importlib.util.spec_from_file_location(plugin_name, file_path)
            module = importlib.util.module_from_spec(spec)
            
            # কোর সিস্টেম যোগ
            module.core = self.core
            module.plugin_name = plugin_name
            
            # এক্সিকিউট
            spec.loader.exec_module(module)
            
            # প্লাগইন রেজিস্ট্রেশন
            self.loaded_plugins[plugin_name] = module
            self.core.plugins[plugin_name] = module
            
            # লোড ইভেন্ট
            if hasattr(module, 'on_plugin_load'):
                module.on_plugin_load(self.core)
            
            print(f"✅ Plugin loaded: {plugin_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to load {file_path.name}: {e}")
            return False
    
    def _start_watcher(self):
        """ফাইল ওয়াচার শুরু"""
        def watch_loop():
            known_files = set(self.loaded_plugins.keys())
            
            while True:
                try:
                    current_files = set(p.stem for p in self.plugins_dir.glob("*.py") 
                                      if not p.name.startswith("__"))
                    
                    # নতুন ফাইল চেক
                    new_files = current_files - known_files
                    for file_stem in new_files:
                        file_path = self.plugins_dir / f"{file_stem}.py"
                        if self._load_plugin(file_path):
                            print(f"🎉 New plugin auto-loaded: {file_stem}")
                    
                    # মুছে ফেলা ফাইল চেক
                    removed_files = known_files - current_files
                    for file_stem in removed_files:
                        if file_stem in self.loaded_plugins:
                            plugin = self.loaded_plugins[file_stem]
                            if hasattr(plugin, 'on_plugin_unload'):
                                plugin.on_plugin_unload(self.core)
                            
                            del self.loaded_plugins[file_stem]
                            if file_stem in self.core.plugins:
                                del self.core.plugins[file_stem]
                            
                            print(f"🗑️ Plugin removed: {file_stem}")
                    
                    known_files = current_files
                    
                except Exception as e:
                    print(f"⚠️ Watcher error: {e}")
                
                time.sleep(5)  # প্রতি ৫ সেকেন্ডে চেক
        
        self.watch_thread = threading.Thread(target=watch_loop, daemon=True)
        self.watch_thread.start()
        print("👁️ File watcher started")