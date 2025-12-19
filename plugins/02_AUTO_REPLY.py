"""
🤖 AUTO REPLY PLUGIN
Automatic response system
"""

import time
import random
from datetime import datetime

def on_plugin_load(core):
    print("🤖 Auto Reply System Activated")
    
    # ডিফল্ট রেসপন্স
    default_responses = [
        "আমি আপনার মেসেজ পেয়েছি!",
        "শীঘ্রই রিপ্লাই দিব...",
        "এখনই উত্তর দিচ্ছি!",
        "আপনার মেসেজ প্রসেস হচ্ছে..."
    ]
    
    core.auto_reply_responses = default_responses
    return {"feature": "auto_reply"}

def handle_event(event_name, data=None):
    if event_name == "user_message":
        user_id = data.get('user_id')
        message = data.get('message', '')
        
        # ক্রেডিট চেক
        if not core.use_credit(user_id):
            return {
                "status": "no_credit",
                "message": "ক্রেডিট শেষ! পেমেন্ট করুন: 01847634486"
            }
        
        # অটো রিপ্লাই জেনারেট
        reply = generate_auto_reply(message)
        
        return {
            "status": "reply_sent",
            "reply": reply,
            "user_id": user_id
        }
    
    return None

def generate_auto_reply(message):
    """অটো রিপ্লাই জেনারেট"""
    greetings = ["হ্যালো", "হাই", "আসসালামু", "হেলো", "সালাম"]
    questions = ["কেমন", "কি", "কিভাবে", "কখন", "কোথায়"]
    
    message_lower = message.lower()
    
    # গ্রীটিং ডিটেক্ট
    for greet in greetings:
        if greet in message_lower:
            return random.choice([
                "আসসালামু আলাইকুম! কেমন আছেন?",
                "হ্যালো! আমি আপনার বট।",
                "শুভেচ্ছা! আমি আপনার ক্রাশ বট।"
            ])
    
    # কোশ্চেন ডিটেক্ট
    for q in questions:
        if q in message_lower:
            return random.choice([
                "সে বিষয়ে আমি জানি না, শিখতে চাই!",
                "আপনি আমাকে শিখিয়ে দিন এটা কী?",
                "এটা এখনও আমার শেখার তালিকায় নেই।"
            ])
    
    # ডিফল্ট রিপ্লাই
    return random.choice(core.auto_reply_responses)