"""
🖼️ MEDIA HANDLER PLUGIN
Photo and video support
"""

def on_plugin_load(core):
    print("🖼️ Media Handler Loaded")
    
    supported_formats = {
        "images": [".jpg", ".jpeg", ".png", ".gif"],
        "videos": [".mp4", ".avi", ".mov", ".mkv"],
        "documents": [".pdf", ".doc", ".txt"]
    }
    
    core.media_formats = supported_formats
    return {"formats": supported_formats}

def handle_event(event_name, data=None):
    if event_name == "media_received":
        file_type = data.get('type')
        file_size = data.get('size', 0)
        user_id = data.get('user_id')
        
        # ফাইল সাইজ চেক (10MB লিমিট)
        max_size = 10 * 1024 * 1024  # 10MB
        
        if file_size > max_size:
            return {
                "status": "error",
                "message": "ফাইল সাইজ বেশি! সর্বোচ্চ 10MB",
                "max_size": "10MB"
            }
        
        # ফাইল টাইপ ভ্যালিডেশন
        if file_type in ["photo", "image"]:
            response_msg = "ছবি রিসিভ হয়েছে! প্রসেস হচ্ছে..."
        elif file_type in ["video", "movie"]:
            response_msg = "ভিডিও রিসিভ হয়েছে! প্রসেস হচ্ছে..."
        else:
            response_msg = "ফাইল রিসিভ হয়েছে!"
        
        return {
            "status": "success",
            "message": response_msg,
            "user_id": user_id,
            "file_type": file_type
        }
    
    elif event_name == "media_processed":
        user_id = data.get('user_id')
        result = data.get('result')
        
        return {
            "processed": True,
            "user_id": user_id,
            "result": result
        }
    
    return None