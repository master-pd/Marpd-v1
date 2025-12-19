"""
💰 CREDIT SYSTEM PLUGIN
User credit management
"""

def on_plugin_load(core):
    print("💰 Credit System Activated")
    
    # পেমেন্ট ডিটেইলস
    payment_info = {
        "amount": 100,
        "validity": "2 months",
        "method": "Nagad",
        "number": "01847634486",
        "owner": "RANA (MASTER 🪓)"
    }
    
    core.payment_info = payment_info
    return {"system": "credit_manager"}

def handle_event(event_name, data=None):
    if event_name == "check_credit":
        user_id = data.get('user_id')
        user_key = str(user_id)
        
        credit = core._credits.get(user_key, 0)
        
        if credit <= 0:
            payment_msg = f"""
⛔ আপনার ক্রেডিট শেষ!

💰 প্যাকেজ: ১০০ টাকা / ২ মাস
📞 নম্বর: {core.payment_info['number']}
👤 গ্রহীতা: {core.payment_info['owner']}
🆔 রেফারেন্স: USER_{user_id}

পেমেন্টের পর প্রুফ পাঠান।
            """
            
            return {
                "status": "no_credit",
                "message": payment_msg,
                "balance": 0
            }
        
        # লো ব্যালেন্স ওয়ার্নিং
        if credit <= 10:
            warning_msg = f"⚠️ ক্রেডিট কম! বাকি: {credit} বার"
            return {
                "status": "low_credit",
                "message": warning_msg,
                "balance": credit
            }
        
        return {
            "status": "credit_ok",
            "balance": credit
        }
    
    elif event_name == "add_credit":
        user_id = data.get('user_id')
        amount = data.get('amount', 100)
        
        new_balance = core.add_credit(user_id, amount)
        
        return {
            "status": "credit_added",
            "balance": new_balance,
            "user_id": user_id
        }
    
    elif event_name == "payment_request":
        user_id = data.get('user_id')
        
        payment_details = f"""
💳 **পেমেন্ট ডিটেইলস**

👤 গ্রহীতা: RANA (MASTER 🪓)
📞 নম্বর: 01847634486
💰 অ্যামাউন্ট: 100 টাকা
📅 ভ্যালিডিটি: 2 মাস
🆔 রেফারেন্স: PAY_{user_id}_{int(time.time())}

পেমেন্টের পর স্ক্রিনশট পাঠান।
        """
        
        return {
            "type": "payment_info",
            "details": payment_details
        }