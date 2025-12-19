"""
🌍 LANGUAGE SUPPORT PLUGIN
Multi-language support
"""

def on_plugin_load(core):
    print("🌍 Language Support Loaded")
    
    languages = {
        "bn": {
            "name": "বাংলা",
            "greeting": "স্বাগতম",
            "farewell": "বিদায়",
            "credit": "ক্রেডিট"
        },
        "en": {
            "name": "English",
            "greeting": "Welcome",
            "farewell": "Goodbye",
            "credit": "Credit"
        },
        "ar": {
            "name": "العربية",
            "greeting": "مرحبا",
            "farewell": "وداعا",
            "credit": "ائتمان"
        },
        "in": {
            "name": "हिन्दी",
            "greeting": "स्वागत है",
            "farewell": "अलविदा",
            "credit": "क्रेडिट"
        }
    }
    
    core.languages = languages
    return {"available": list(languages.keys())}

def handle_event(event_name, data=None):
    if event_name == "set_language":
        user_id = data.get('user_id')
        lang_code = data.get('language', 'bn')
        
        if lang_code in core.languages:
            lang_info = core.languages[lang_code]
            
            return {
                "language_set": True,
                "language": lang_code,
                "name": lang_info["name"],
                "message": f"ভাষা পরিবর্তন করা হয়েছে: {lang_info['name']}"
            }
        else:
            return {
                "language_set": False,
                "message": "ভাষা সাপোর্টেড নয়!"
            }
    
    elif event_name == "get_translation":
        text = data.get('text')
        from_lang = data.get('from', 'bn')
        to_lang = data.get('to', 'en')
        
        # সিম্পল ট্রান্সলেশন টেবিল
        translations = {
            "স্বাগতম": {"en": "Welcome", "ar": "مرحبا", "in": "स्वागत है"},
            "ক্রেডিট": {"en": "Credit", "ar": "ائتمان", "in": "क्रेडिट"},
            "নামাজ": {"en": "Prayer", "ar": "صلاة", "in": "नमाज"}
        }
        
        if text in translations and to_lang in translations[text]:
            return {
                "translated": True,
                "original": text,
                "translation": translations[text][to_lang],
                "from": from_lang,
                "to": to_lang
            }
        
        return {
            "translated": False,
            "message": "ট্রান্সলেশন পাওয়া যায়নি"
        }
    
    return None