"""
🎉 WELCOME MESSAGE PLUGIN
Welcome and goodbye messages
"""

import time
from datetime import datetime

def on_plugin_load(core):
    print("🎉 Welcome System Loaded")
    
    welcome_messages = {
        "bn": "🎉 স্বাগতম! আমি YOUR CRUSH ⟵o_0 বট।",
        "en": "🎉 Welcome! I'm YOUR CRUSH ⟵o_0 bot.",
        "ar": "🎉 أهلا بك! أنا بوت YOUR CRUSH ⟵o_0."
    }
    
    goodbye_messages = {
        "bn": "👋 আল্লাহ হাফেজ! আবার কথা হবে।",
        "en": "👋 Goodbye! Talk to you later.",
        "ar": "👋 مع السلامة! نتحدث لاحقًا."
    }
    
    core.welcome_msgs = welcome_messages
    core.goodbye_msgs = goodbye_messages
    
    return {"languages": list(welcome_messages.keys())}

def handle_event(event_name, data=None):
    if event_name == "user_joined":
        user_id = data.get('user_id')
        language = data.get('language', 'bn')
        
        welcome_msg = core.welcome_msgs.get(language, core.welcome_msgs['bn'])
        
        # ডেভেলপার ইনফো যোগ
        dev_info = "👤 Developer: RANA (MASTER 🪓) | 📞 01847634486"
        
        full_message = f"""
{welcome_msg}

{dev_info}

💬 আমার সাথে স্বাভাবিকভাবে কথা বলুন।
💰 ক্রেডিট সিস্টেম: ১০০ টাকা/২ মাস
🔄 নতুন ফিচার অটো-লোড হবে!
        """
        
        return {
            "event": "welcome_sent",
            "user_id": user_id,
            "message": full_message
        }
    
    elif event_name == "user_left":
        user_id = data.get('user_id')
        language = data.get('language', 'bn')
        
        goodbye_msg = core.goodbye_msgs.get(language, core.goodbye_msgs['bn'])
        
        return {
            "event": "goodbye_sent",
            "user_id": user_id,
            "message": goodbye_msg
        }
    
    return None