"""
🔔 NOTIFICATION SYSTEM
Push notifications and alerts
"""

import asyncio
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import json

class NotificationManager:
    def __init__(self, core):
        self.core = core
        self.notifications = []
        self.subscribers = {}
        print("🔔 Notification System Ready")
    
    def add_subscriber(self, user_id, channels):
        """সাবস্ক্রাইবার যোগ"""
        user_key = str(user_id)
        self.subscribers[user_key] = channels
        return True
    
    def send_notification(self, title, message, level="info", target=None):
        """নোটিফিকেশন পাঠান"""
        notification = {
            "id": len(self.notifications) + 1,
            "title": title,
            "message": message,
            "level": level,  # info, warning, error, critical
            "timestamp": datetime.now().isoformat(),
            "read": False
        }
        
        self.notifications.append(notification)
        
        # টার্গেটেড নোটিফিকেশন
        if target == "all":
            self._broadcast_to_all(notification)
        elif target and str(target) in self.subscribers:
            self._send_to_user(target, notification)
        
        return notification["id"]
    
    def _broadcast_to_all(self, notification):
        """সবাইকে ব্রডকাস্ট"""
        # লগ হিসেবে সংরক্ষণ
        with open("notifications.log", "a") as f:
            f.write(json.dumps(notification) + "\n")
    
    def _send_to_user(self, user_id, notification):
        """নির্দিষ্ট ইউজারকে পাঠান"""
        user_key = str(user_id)
        if user_key in self.subscribers:
            channels = self.subscribers[user_key]
            
            if "telegram" in channels:
                self._send_telegram(user_id, notification)
            
            if "email" in channels:
                self._send_email(user_id, notification)
    
    def _send_telegram(self, user_id, notification):
        """টেলিগ্রামে পাঠান"""
        try:
            if hasattr(self.core, 'telegram_orchestrator'):
                message = f"🔔 {notification['title']}\n\n{notification['message']}"
                self.core.telegram_orchestrator.send_user_message(user_id, message)
        except:
            pass
    
    def _send_email(self, user_id, notification):
        """ইমেইল পাঠান"""
        # ইমেইল কনফিগ
        email_config = getattr(self.core, 'email_config', {})
        
        if not email_config:
            return
        
        try:
            msg = MIMEText(notification['message'])
            msg['Subject'] = notification['title']
            msg['From'] = email_config.get('from')
            msg['To'] = self._get_user_email(user_id)
            
            with smtplib.SMTP(email_config.get('smtp_server'), email_config.get('smtp_port')) as server:
                server.starttls()
                server.login(email_config.get('username'), email_config.get('password'))
                server.send_message(msg)
        except:
            pass
    
    def _get_user_email(self, user_id):
        """ইউজার ইমেইল পেতে"""
        # ইউজার প্রোফাইল থেকে ইমেইল
        return ""