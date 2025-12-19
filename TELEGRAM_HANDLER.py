"""
🤖 TELEGRAM BOT HANDLER
Telegram API integration for multi-bot support
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional
import json

# Conditional import for production
try:
    from telegram import Update, Bot
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    print("⚠️ python-telegram-bot not installed. Using mock mode.")

class TelegramBotManager:
    def __init__(self, core_system):
        self.core = core_system
        self.active_bots = {}
        self.user_bots = {}
        
        self.logger = logging.getLogger(__name__)
        
        # বট কনফিগ
        self.config = {
            "max_bots_per_user": 3,
            "message_timeout": 30,
            "retry_attempts": 3,
            "webhook_url": None  # For production
        }
    
    async def initialize_user_bot(self, user_id, bot_token, chat_id):
        """ইউজার বট ইনিশিয়ালাইজ"""
        user_key = str(user_id)
        
        if not TELEGRAM_AVAILABLE:
            self.logger.warning("Telegram lib not available. Running in simulation mode.")
            return await self._simulate_bot(user_key, bot_token, chat_id)
        
        try:
            # বট ভ্যালিডেশন
            bot = Bot(token=bot_token)
            bot_info = await bot.get_me()
            
            # অ্যাপ্লিকেশন তৈরি
            application = Application.builder().token(bot_token).build()
            
            # হ্যান্ডলার রেজিস্টার
            application.add_handler(CommandHandler("start", self._start_command))
            application.add_handler(CommandHandler("help", self._help_command))
            application.add_handler(CommandHandler("credit", self._credit_command))
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._message_handler))
            
            # ইউজার ডাটা স্টোর
            self.user_bots[user_key] = {
                "bot": bot,
                "application": application,
                "chat_id": chat_id,
                "bot_info": bot_info,
                "started_at": datetime.now().isoformat(),
                "message_count": 0,
                "is_active": True
            }
            
            # পোলিং শুরু (একটি আলাদা টাস্কে)
            asyncio.create_task(self._start_polling(application, user_key))
            
            self.logger.info(f"✅ User bot started: @{bot_info.username} for user {user_id}")
            
            return {
                "success": True,
                "bot_username": bot_info.username,
                "bot_id": bot_info.id,
                "started": True
            }
            
        except Exception as e:
            self.logger.error(f"❌ Bot initialization failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "started": False
            }
    
    async def _simulate_bot(self, user_key, bot_token, chat_id):
        """সিমুলেশন মোড"""
        self.user_bots[user_key] = {
            "bot": None,
            "application": None,
            "chat_id": chat_id,
            "bot_info": {"username": "simulation_bot", "id": 999999},
            "started_at": datetime.now().isoformat(),
            "message_count": 0,
            "is_active": True,
            "simulation": True
        }
        
        self.logger.info(f"✅ Simulation bot started for user {user_key}")
        
        return {
            "success": True,
            "bot_username": "simulation_bot",
            "bot_id": 999999,
            "started": True,
            "simulation": True
        }
    
    async def _start_polling(self, application, user_key):
        """পোলিং শুরু"""
        try:
            await application.initialize()
            await application.start()
            await application.updater.start_polling(
                poll_interval=1.0,
                timeout=10,
                allowed_updates=Update.ALL_TYPES
            )
            
            self.logger.info(f"📡 Polling started for user {user_key}")
            
        except Exception as e:
            self.logger.error(f"❌ Polling failed for {user_key}: {e}")
            if user_key in self.user_bots:
                self.user_bots[user_key]["is_active"] = False
    
    async def _start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """স্টার্ট কমান্ড"""
        user_id = update.effective_user.id
        
        welcome_message = """
🎉 স্বাগতম! আমি YOUR CRUSH ⟵o_0 বট।

 বট ইনফো: 🌚
• Developer: RANA (MASTER 🪓)
• Contact: 01847634486
• Location: Faridpur, Dhaka

💡 ফিচারসমূহ 🐻‍❄
✅ অটো রিপ্লাই
✅ AI চ্যাট
✅ সময় অনুযায়ী নোটিফিকেশন
✅ মিডিয়া সাপোর্ট

💰 **ক্রেডিট:** ১০০ টাকা / ২ মাস
        """
        
        await update.message.reply_text(welcome_message)
    
    async def _help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """হেল্প কমান্ড"""
        help_text = """


••||ʕ⁠ʔ0_o➜ কমান্ডসমূহ 
/start - বট শুরু করুন
/help - এই মেসেজ 
/credit - ক্রেডিট চেক 
/status - বট স্ট্যাটাস 

••||ʕ⁠ʔ0_o➜ ফিচার
• স্বাভাবিকভাবে কথা বলুন
• ছবি/ভিডিও পাঠান
• সময় অনুযায়ী মেসেজ পাবেন

••||ʕ⁠ʔ0_o➜ সাপোর্ট
📞 01847634486
📧 ranaeditz333@gmail.com
👤 @rana_editz_00
        """
        
        await update.message.reply_text(help_text)
    
    async def _credit_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """ক্রেডিট কমান্ড"""
        user_id = update.effective_user.id
        user_key = str(user_id)
        
        # ইউজার খুঁজুন
        for uid, bot_data in self.user_bots.items():
            if str(bot_data["chat_id"]) == user_key:
                # ক্রেডিট চেক
                credit = self.core._credits.get(uid, 0)
                
                if credit <= 0:
                    message = f"""
••||ʕ⁠ʔ0_o➜ ক্রেডিট শেষ!

💰 ২ মাসের প্যাকেজ: ১০০ টাকা
📞 পেমেন্ট: 01847634486
👤 গ্রহীতা: RANA (MASTER 🪓)

পেমেন্টের পর প্রুফ পাঠান।
                    """
                else:
                    message = f"""
💰 **ক্রেডিট ব্যালেন্স:**

✅ বাকি: {credit} বার
💡 প্রতি বার মেসেজে ১ ক্রেডিট খরচ

{"⚠️ ক্রেডিট কম! শীঘ্রই রিচার্জ করুন।" if credit <= 10 else "✅ পর্যাপ্ত ক্রেডিট আছে।"}
                    """
                
                await update.message.reply_text(message)
                return
        
        await update.message.reply_text("❌ ইউজার পাওয়া যায়নি!")
    
    async def _message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """মেসেজ হ্যান্ডলার"""
        user_id = update.effective_user.id
        message_text = update.message.text
        message_id = update.message.message_id
        
        # ইউজার আইডি খুঁজুন
        user_key = None
        for uid, bot_data in self.user_bots.items():
            if str(bot_data["chat_id"]) == str(user_id):
                user_key = uid
                break
        
        if not user_key:
            await update.message.reply_text("❌ আনঅথোরাইজ্ড একসেস!")
            return
        
        # ক্রেডিট চেক
        if not self.core.use_credit(user_key):
            payment_msg = """
••||ʕ⁠ʔ0_o➜ ক্রেডিট শেষ!

💰 প্যাকেজ: ১০০ টাকা / ২ মাস
📞 নম্বর: 01847634486
👤 গ্রহীতা: RANA (MASTER 🪓)

পেমেন্টের পর প্রুফ পাঠান এই চ্যাটে।
            """
            await update.message.reply_text(payment_msg)
            return
        
        # কোর ইভেন্ট ট্রিগার
        event_data = {
            "user_id": user_key,
            "message": message_text,
            "message_id": message_id,
            "chat_id": update.effective_chat.id,
            "timestamp": datetime.now().isoformat()
        }
        
        # প্লাগইন ইভেন্ট ব্রডকাস্ট
        responses = self.core.broadcast_event("telegram_message", event_data)
        
        # AI প্রসেসিং
        ai_response = None
        if hasattr(self.core, 'ai_orchestrator'):
            ai_result = self.core.ai_orchestrator.process_query(user_key, message_text)
            if ai_result.get("response"):
                ai_response = ai_result["response"]
        
        # রেসপন্স পাঠান
        if ai_response:
            await update.message.reply_text(ai_response)
        elif responses:
            # প্রথম ভ্যালিড রেসপন্স পাঠান
            for plugin_name, response in responses.items():
                if response and isinstance(response, dict) and response.get("message"):
                    await update.message.reply_text(response["message"])
                    break
        else:
            # ডিফল্ট রেসপন্স
            default_responses = [
                "আপনার মেসেজ পেয়েছি!",
                "প্রসেস করছি...",
                "শীঘ্রই উত্তর দিচ্ছি!"
            ]
            import random
            await update.message.reply_text(random.choice(default_responses))
        
        # মেসেজ কাউন্ট আপডেট
        if user_key in self.user_bots:
            self.user_bots[user_key]["message_count"] += 1
    
    async def send_message(self, user_id, message, parse_mode="HTML"):
        """ইউজারকে মেসেজ পাঠান"""
        user_key = str(user_id)
        
        if user_key in self.user_bots and self.user_bots[user_key]["is_active"]:
            bot_data = self.user_bots[user_key]
            
            try:
                if bot_data.get("simulation"):
                    self.logger.info(f"📨 [SIM] Message to {user_id}: {message[:50]}...")
                    return True
                
                await bot_data["bot"].send_message(
                    chat_id=bot_data["chat_id"],
                    text=message,
                    parse_mode=parse_mode
                )
                return True
                
            except Exception as e:
                self.logger.error(f"❌ Send message failed: {e}")
                return False
        
        return False
    
    def get_bot_status(self, user_id):
        """বট স্ট্যাটাস"""
        user_key = str(user_id)
        
        if user_key in self.user_bots:
            bot_data = self.user_bots[user_key]
            
            return {
                "active": bot_data["is_active"],
                "bot_username": bot_data["bot_info"]["username"],
                "message_count": bot_data["message_count"],
                "started_at": bot_data["started_at"],
                "simulation": bot_data.get("simulation", False)
            }
        
        return None
    
    def stop_user_bot(self, user_id):
        """ইউজার বট বন্ধ"""
        user_key = str(user_id)
        
        if user_key in self.user_bots:
            bot_data = self.user_bots[user_key]
            bot_data["is_active"] = False
            
            # অ্যাপ্লিকেশন বন্ধ (যদি থাকে)
            if bot_data["application"] and not bot_data.get("simulation"):
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        loop.create_task(bot_data["application"].stop())
                except:
                    pass
            
            del self.user_bots[user_key]
            return True
        
        return False

class TelegramOrchestrator:
    def __init__(self, core_system):
        self.core = core_system
        self.manager = TelegramBotManager(core_system)
        
        # Event loop for async operations
        self.loop = None
        self._init_event_loop()
    
    def _init_event_loop(self):
        """ইভেন্ট লুপ ইনিশিয়ালাইজ"""
        try:
            self.loop = asyncio.get_event_loop()
        except RuntimeError:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
    
    def register_user_bot(self, user_id, bot_token, chat_id):
        """ইউজার বট রেজিস্টার"""
        if not self.loop:
            self._init_event_loop()
        
        try:
            # Run async function in event loop
            result = self.loop.run_until_complete(
                self.manager.initialize_user_bot(user_id, bot_token, chat_id)
            )
            
            # Core-এ ইউজার রেজিস্টার
            if result.get("success"):
                self.core.register_user(user_id, bot_token, chat_id)
            
            return result
            
        except Exception as e:
            print(f"❌ Bot registration error: {e}")
            return {"success": False, "error": str(e)}
    
    def send_user_message(self, user_id, message):
        """ইউজারকে মেসেজ পাঠান"""
        if not self.loop:
            return False
        
        try:
            return self.loop.run_until_complete(
                self.manager.send_message(user_id, message)
            )
        except:
            return False
    
    def broadcast_message(self, message, user_filter=None):
        """ব্রডকাস্ট মেসেজ"""
        sent_count = 0
        
        for user_key, bot_data in self.manager.user_bots.items():
            if bot_data["is_active"]:
                if user_filter and not user_filter(user_key):
                    continue
                
                try:
                    success = self.send_user_message(int(user_key), message)
                    if success:
                        sent_count += 1
                except:
                    pass
        
        return sent_count
    
    def get_all_bots_status(self):
        """সব বটের স্ট্যাটাস"""
        status_report = {
            "total_bots": len(self.manager.user_bots),
            "active_bots": len([b for b in self.manager.user_bots.values() if b["is_active"]]),
            "total_messages": sum(b["message_count"] for b in self.manager.user_bots.values()),
            "bots": {}
        }
        
        for user_key, bot_data in self.manager.user_bots.items():
            status_report["bots"][user_key] = {
                "active": bot_data["is_active"],
                "username": bot_data["bot_info"]["username"],
                "messages": bot_data["message_count"],
                "since": bot_data["started_at"]
            }
        
        return status_report