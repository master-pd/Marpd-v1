"""
👤 DEVELOPER INFORMATION PLUGIN
Your personal and professional info
"""

def on_plugin_load(core):
    print("👤 Developer Info Plugin Loaded")
    
    dev_info = {
        "bot_name": "YOUR CRUSH ⟵o_0",
        "personal": {
            "name": "RANA",
            "social_name": "MASTER 🪓",
            "age": "20 years", 
            "status": "Single",
            "education": "SSC Batch 2022",
            "location": "Faridpur, Dhaka, Bangladesh"
        },
        "professional": {
            "profession": "Security Field",
            "work_type": "Experiment / Technical Operations",
            "skills": [
                "Video Editing",
                "Photo Editing", 
                "Mobile Technology",
                "Online Operations",
                "Cyber Security (Currently Learning)"
            ]
        },
        "contact": {
            "email": "ranaeditz333@gmail.com",
            "telegram_bot": "@black_lovers1_bot",
            "telegram_profile": "@rana_editz_00",
            "support_channel": "https://t.me/master_account_remover_channel",
            "phone": "01847634486"
        },
        "goals": {
            "dream": "Become a Professional Developer",
            "project": "Website (Coming Soon)"
        },
        "summary": {
            "bot": "YOUR CRUSH ⟵o_0",
            "developer": "RANA (MASTER 🪓)",
            "from": "Faridpur, Dhaka",
            "current_status": "Developer in Training",
            "learning": "Cyber Security (Ongoing)"
        }
    }
    
    # কোর সিস্টেমে ডেভেলপার ইনফো যোগ
    core.dev_info = dev_info
    print("✅ Developer information added to system")
    
    return {"plugin": "dev_info", "version": "2.0"}

def handle_event(event_name, data=None):
    if event_name == "get_dev_info":
        return get_developer_card()
    
    return None

def get_developer_card():
    """ডেভেলপার কার্ড রিটার্ন"""
    return """
╔══════════════════════════════════╗
║       🤖 YOUR CRUSH ⟵o_0        ║
╠══════════════════════════════════╣
║ 👤 Developer: RANA (MASTER 🪓)   ║
║ 🏠 Location: Faridpur, Dhaka     ║
║ 📞 Phone: 01847634486            ║
║ 📧 Email: ranaeditz333@gmail.com ║
║ 🌐 Telegram: @rana_editz_00      ║
║ 🎯 Status: Developer in Training ║
║ 📚 Learning: Cyber Security      ║
╚══════════════════════════════════╝
    """