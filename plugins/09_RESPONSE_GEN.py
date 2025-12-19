"""
💬 RESPONSE GENERATOR PLUGIN
Smart response generation
"""

import random

def on_plugin_load(core):
    print("💬 Response Generator Loaded")
    
    response_templates = {
        "greeting": [
            "আসসালামু আলাইকুম!",
            "হ্যালো! কেমন আছেন?",
            "শুভেচ্ছা! আমি YOUR CRUSH বট।"
        ],
        "farewell": [
            "আল্লাহ হাফেজ!",
            "বিদায়! আবার কথা হবে।",
            "শুভ রাত্রি! ভালো থাকবেন।"
        ],
        "thanks": [
            "আপনাকেও ধন্যবাদ!",
            "কোনো সমস্যা নেই!",
            "খুশি হলাম সাহায্য করতে পেরে!"
        ],
        "unknown": [
            "মাফ করবেন, বুঝতে পারছি না।",
            "এটা এখনও শিখিনি!",
            "আপনি আমাকে শিখিয়ে দিন?"
        ]
    }
    
    core.response_templates = response_templates
    return {"templates": list(response_templates.keys())}

def handle_event(event_name, data=None):
    if event_name == "generate_response":
        context = data.get('context', 'unknown')
        user_id = data.get('user_id')
        
        # প্রাসঙ্গিক রেসপন্স নির্বাচন
        if context in core.response_templates:
            responses = core.response_templates[context]
        else:
            responses = core.response_templates["unknown"]
        
        selected_response = random.choice(responses)
        
        # ডেভেলপার সিগনেচার যোগ
        if context != "unknown":
            signature = "\n\n🤖 YOUR CRUSH ⟵o_0\n👤 Developer: RANA"
            selected_response += signature
        
        return {
            "response": selected_response,
            "context": context,
            "user_id": user_id
        }
    
    elif event_name == "analyze_message":
        message = data.get('message', '').lower()
        
        # মেসেজ অ্যানালাইসিস
        if any(word in message for word in ["হ্যালো", "হাই", "সালাম"]):
            context = "greeting"
        elif any(word in message for word in ["বিদায়", "বাই", "হাফেজ"]):
            context = "farewell"
        elif any(word in message for word in ["ধন্যবাদ", "থ্যাংকস", "শুকরিয়া"]):
            context = "thanks"
        else:
            context = "unknown"
        
        return {
            "analyzed": True,
            "context": context,
            "message": message
        }
    
    return None