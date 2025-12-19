"""
🕌 PRAYER TIMES PLUGIN
Namaz and Azan notifications
"""

import time
from datetime import datetime

prayer_schedule = {
    "fajr": {"time": "5:30", "message": "ফজরের আজান হয়েছে, নামাজ পড়ুন।"},
    "dhuhr": {"time": "12:30", "message": "জোহরের আজান হয়েছে, নামাজ পড়ুন।"},
    "asr": {"time": "16:00", "message": "আসরের আজান হয়েছে, নামাজ পড়ুন।"},
    "maghrib": {"time": "18:00", "message": "মাগরিবের আজান হয়েছে, নামাজ পড়ুন।"},
    "isha": {"time": "19:30", "message": "ইশার আজান হয়েছে, নামাজ পড়ুন।"}
}

def on_plugin_load(core):
    print("🕌 Prayer Times Plugin Loaded")
    
    # শিডিউলার শুরু
    start_prayer_notifier()
    
    return {"prayers": list(prayer_schedule.keys())}

def start_prayer_notifier():
    """নামাজ নোটিফায়ার শুরু"""
    import threading
    
    def notifier_loop():
        notified_today = []
        
        while True:
            now = datetime.now()
            current_time = now.strftime("%H:%M")
            
            for prayer, info in prayer_schedule.items():
                prayer_time = info["time"]
                
                if current_time == prayer_time and prayer not in notified_today:
                    print(f"🕌 {prayer.upper()}: {info['message']}")
                    
                    # ব্রডকাস্ট ইভেন্ট
                    if hasattr(core, 'broadcast_event'):
                        core.broadcast_event("prayer_time", {
                            "prayer": prayer,
                            "time": prayer_time,
                            "message": info["message"]
                        })
                    
                    notified_today.append(prayer)
            
            # দিন শেষে রিসেট
            if now.hour == 23 and now.minute == 59:
                notified_today = []
            
            time.sleep(60)  # প্রতি মিনিটে চেক
    
    threading.Thread(target=notifier_loop, daemon=True).start()
    print("⏰ Prayer notifier started")

def handle_event(event_name, data=None):
    if event_name == "prayer_time":
        prayer = data.get('prayer')
        message = data.get('message', '')
        
        # অ্যাকটিভ ইউজারদের কাছে পাঠান
        active_count = len(core.active_users)
        
        return {
            "prayer": prayer,
            "message": message,
            "users_notified": active_count
        }
    
    return None