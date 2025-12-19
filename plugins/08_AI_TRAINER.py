"""
🎓 AI TRAINER PLUGIN
Machine learning system
"""

import json
import hashlib
from datetime import datetime

def on_plugin_load(core):
    print("🎓 AI Trainer Plugin Loaded")
    
    # AI মেমোরি ফাইল
    memory_file = core.data_path / "ai_memory.json"
    if not memory_file.exists():
        with open(memory_file, 'w', encoding='utf-8') as f:
            json.dump({"patterns": {}, "learning": []}, f, ensure_ascii=False)
    
    return {"ai": "training_system"}

def handle_event(event_name, data=None):
    if event_name == "user_message":
        user_id = data.get('user_id')
        message = data.get('message')
        
        # প্রথমে AI মেমোরি চেক
        response = check_ai_memory(message)
        
        if response:
            return {
                "source": "ai_memory",
                "response": response
            }
        
        # না পেলে ট্রেনিং এর জন্য প্রস্তুত
        return {
            "source": "need_training",
            "message": message,
            "user_id": user_id
        }
    
    elif event_name == "train_ai":
        question = data.get('question')
        answer = data.get('answer')
        user_id = data.get('user_id')
        
        # AI কে শেখান
        result = train_ai_model(question, answer, user_id)
        
        return {
            "trained": True,
            "question": question,
            "answer": answer,
            "user": user_id
        }
    
    return None

def check_ai_memory(message):
    """AI মেমোরি চেক"""
    try:
        memory_file = core.data_path / "ai_memory.json"
        with open(memory_file, 'r', encoding='utf-8') as f:
            memory = json.load(f)
        
        message_hash = hashlib.md5(message.encode()).hexdigest()
        
        if message_hash in memory["patterns"]:
            pattern = memory["patterns"][message_hash]
            return pattern["responses"][0] if pattern["responses"] else None
        
    except:
        pass
    
    return None

def train_ai_model(question, answer, user_id):
    """AI মডেল ট্রেন"""
    try:
        memory_file = core.data_path / "ai_memory.json"
        
        with open(memory_file, 'r', encoding='utf-8') as f:
            memory = json.load(f)
        
        question_hash = hashlib.md5(question.encode()).hexdigest()
        
        if question_hash not in memory["patterns"]:
            memory["patterns"][question_hash] = {
                "question": question,
                "responses": [answer],
                "learned_from": user_id,
                "learned_at": datetime.now().isoformat(),
                "used_count": 0
            }
        else:
            if answer not in memory["patterns"][question_hash]["responses"]:
                memory["patterns"][question_hash]["responses"].append(answer)
        
        memory["learning"].append({
            "question": question,
            "answer": answer,
            "user": user_id,
            "time": datetime.now().isoformat()
        })
        
        # শুধু সর্বশেষ 1000 টি লার্নিং রাখুন
        if len(memory["learning"]) > 1000:
            memory["learning"] = memory["learning"][-1000:]
        
        with open(memory_file, 'w', encoding='utf-8') as f:
            json.dump(memory, f, ensure_ascii=False, indent=2)
        
        return True
        
    except Exception as e:
        print(f"❌ AI Training error: {e}")
        return False