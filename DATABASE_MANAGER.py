"""
🗄️ SQL DATABASE MANAGER
PostgreSQL/MySQL/SQLite3 integration
"""

import sqlite3
import psycopg2
import mysql.connector
import json
from datetime import datetime
from pathlib import Path

class DatabaseManager:
    def __init__(self, db_type="sqlite", config=None):
        self.db_type = db_type.lower()
        self.config = config or {}
        self.connection = None
        self.cursor = None
        
        self._init_database()
        print(f"🗄️ Database Manager Initialized ({db_type})")
    
    def _init_database(self):
        """ডাটাবেজ ইনিশিয়ালাইজ"""
        if self.db_type == "sqlite":
            self._init_sqlite()
        elif self.db_type == "postgresql":
            self._init_postgresql()
        elif self.db_type == "mysql":
            self._init_mysql()
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")
        
        # টেবিল তৈরি
        self._create_tables()
    
    def _init_sqlite(self):
        """SQLite3 কানেকশন"""
        db_path = self.config.get("path", "data/bot_database.db")
        Path("data").mkdir(exist_ok=True)
        
        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
    
    def _init_postgresql(self):
        """PostgreSQL কানেকশন"""
        conn_params = {
            "host": self.config.get("host", "localhost"),
            "port": self.config.get("port", 5432),
            "database": self.config.get("database", "rana_bot"),
            "user": self.config.get("user", "postgres"),
            "password": self.config.get("password", ""),
        }
        
        self.connection = psycopg2.connect(**conn_params)
        self.cursor = self.connection.cursor()
    
    def _init_mysql(self):
        """MySQL কানেকশন"""
        conn_params = {
            "host": self.config.get("host", "localhost"),
            "port": self.config.get("port", 3306),
            "database": self.config.get("database", "rana_bot"),
            "user": self.config.get("user", "root"),
            "password": self.config.get("password", ""),
        }
        
        self.connection = mysql.connector.connect(**conn_params)
        self.cursor = self.connection.cursor(dictionary=True)
    
    def _create_tables(self):
        """সব টেবিল তৈরি"""
        
        # 👤 USERS টেবিল
        users_table = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT UNIQUE NOT NULL,
            username VARCHAR(255),
            first_name VARCHAR(255),
            last_name VARCHAR(255),
            phone VARCHAR(20),
            email VARCHAR(255),
            language VARCHAR(10) DEFAULT 'bn',
            status VARCHAR(20) DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP,
            settings JSONB DEFAULT '{}'
        );
        """
        
        # 🤖 USER_BOTS টেবিল
        user_bots_table = """
        CREATE TABLE IF NOT EXISTS user_bots (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            bot_token VARCHAR(255) UNIQUE NOT NULL,
            bot_username VARCHAR(255),
            chat_id BIGINT,
            is_active BOOLEAN DEFAULT TRUE,
            credit_balance INTEGER DEFAULT 0,
            last_payment_date TIMESTAMP,
            next_payment_date TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            settings JSONB DEFAULT '{}'
        );
        """
        
        # 💰 CREDITS টেবিল
        credits_table = """
        CREATE TABLE IF NOT EXISTS credits (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            amount INTEGER NOT NULL,
            transaction_type VARCHAR(50), -- 'purchase', 'usage', 'bonus', 'refund'
            reference_id VARCHAR(100),
            description TEXT,
            balance_after INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # 💳 PAYMENTS টেবিল
        payments_table = """
        CREATE TABLE IF NOT EXISTS payments (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            amount DECIMAL(10, 2) NOT NULL,
            currency VARCHAR(10) DEFAULT 'BDT',
            method VARCHAR(50), -- 'nagad', 'bkash', 'rocket'
            transaction_id VARCHAR(100),
            sender_number VARCHAR(20),
            status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'verified', 'rejected'
            verified_by INTEGER,
            verified_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # 🧠 AI_MEMORY টেবিল
        ai_memory_table = """
        CREATE TABLE IF NOT EXISTS ai_memory (
            id SERIAL PRIMARY KEY,
            pattern_hash VARCHAR(64) UNIQUE NOT NULL,
            question TEXT NOT NULL,
            response TEXT NOT NULL,
            learned_from INTEGER REFERENCES users(id),
            used_count INTEGER DEFAULT 0,
            confidence DECIMAL(3, 2) DEFAULT 1.0,
            last_used TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # 💬 CONVERSATIONS টেবিল
        conversations_table = """
        CREATE TABLE IF NOT EXISTS conversations (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            bot_id INTEGER REFERENCES user_bots(id) ON DELETE CASCADE,
            message_text TEXT,
            message_type VARCHAR(20), -- 'text', 'photo', 'video', 'document'
            response_text TEXT,
            response_time_ms INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # ⏰ SCHEDULED_MESSAGES টেবিল
        scheduled_messages_table = """
        CREATE TABLE IF NOT EXISTS scheduled_messages (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            bot_id INTEGER REFERENCES user_bots(id) ON DELETE CASCADE,
            message_text TEXT NOT NULL,
            scheduled_time TIMESTAMP NOT NULL,
            repeat_type VARCHAR(20), -- 'once', 'daily', 'weekly', 'monthly'
            status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'sent', 'failed'
            sent_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # 🔐 AUDIT_LOG টেবিল
        audit_log_table = """
        CREATE TABLE IF NOT EXISTS audit_log (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            action VARCHAR(100) NOT NULL,
            details JSONB,
            ip_address VARCHAR(45),
            user_agent TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # সব টেবিল এক্সিকিউট
        tables = [
            users_table, user_bots_table, credits_table, 
            payments_table, ai_memory_table, conversations_table,
            scheduled_messages_table, audit_log_table
        ]
        
        for table_sql in tables:
            try:
                self.cursor.execute(table_sql)
            except Exception as e:
                print(f"⚠️ Table creation error: {e}")
        
        self.connection.commit()
        print("✅ Database tables created")
    
    # 👤 USER OPERATIONS
    def create_user(self, telegram_id, username=None, first_name=None, **kwargs):
        """নতুন ইউজার তৈরি"""
        sql = """
        INSERT INTO users (telegram_id, username, first_name, last_name, phone, email, settings)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        
        try:
            self.cursor.execute(sql, (
                telegram_id, username, first_name,
                kwargs.get('last_name'), kwargs.get('phone'),
                kwargs.get('email'), json.dumps(kwargs.get('settings', {}))
            ))
            
            user_id = self.cursor.fetchone()[0]
            self.connection.commit()
            
            # অডিট লগ
            self.log_audit(user_id, "user_created", {"telegram_id": telegram_id})
            
            return user_id
        except Exception as e:
            print(f"❌ User creation error: {e}")
            return None
    
    def get_user(self, identifier, by="telegram_id"):
        """ইউজার খুঁজে বের করুন"""
        if by == "telegram_id":
            sql = "SELECT * FROM users WHERE telegram_id = %s"
        elif by == "id":
            sql = "SELECT * FROM users WHERE id = %s"
        elif by == "username":
            sql = "SELECT * FROM users WHERE username = %s"
        else:
            return None
        
        try:
            self.cursor.execute(sql, (identifier,))
            result = self.cursor.fetchone()
            
            if result and self.db_type == "sqlite":
                return dict(result)
            return result
        except:
            return None
    
    def update_user(self, user_id, **updates):
        """ইউজার আপডেট"""
        if not updates:
            return False
        
        set_clause = ", ".join([f"{k} = %s" for k in updates.keys()])
        sql = f"UPDATE users SET {set_clause} WHERE id = %s"
        
        try:
            self.cursor.execute(sql, (*updates.values(), user_id))
            self.connection.commit()
            
            self.log_audit(user_id, "user_updated", updates)
            return True
        except Exception as e:
            print(f"❌ User update error: {e}")
            return False
    
    # 🤖 BOT OPERATIONS
    def register_bot(self, user_id, bot_token, chat_id, bot_username=None):
        """ইউজার বট রেজিস্টার"""
        sql = """
        INSERT INTO user_bots (user_id, bot_token, chat_id, bot_username)
        VALUES (%s, %s, %s, %s)
        RETURNING id
        """
        
        try:
            self.cursor.execute(sql, (user_id, bot_token, chat_id, bot_username))
            bot_id = self.cursor.fetchone()[0]
            self.connection.commit()
            
            self.log_audit(user_id, "bot_registered", {"bot_id": bot_id})
            return bot_id
        except Exception as e:
            print(f"❌ Bot registration error: {e}")
            return None
    
    def get_user_bots(self, user_id):
        """ইউজারের সব বট"""
        sql = """
        SELECT * FROM user_bots 
        WHERE user_id = %s AND is_active = TRUE
        ORDER BY created_at DESC
        """
        
        try:
            self.cursor.execute(sql, (user_id,))
            results = self.cursor.fetchall()
            
            if self.db_type == "sqlite":
                return [dict(row) for row in results]
            return results
        except:
            return []
    
    # 💰 CREDIT OPERATIONS
    def add_credit(self, user_id, amount, description="", transaction_type="purchase", reference_id=""):
        """ক্রেডিট যোগ"""
        # প্রথমে কারেন্ট ব্যালেন্স নিন
        current_balance = self.get_user_balance(user_id)
        new_balance = current_balance + amount
        
        sql = """
        INSERT INTO credits (user_id, amount, transaction_type, reference_id, description, balance_after)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        try:
            self.cursor.execute(sql, (
                user_id, amount, transaction_type, 
                reference_id, description, new_balance
            ))
            
            # user_bots টেবিল আপডেট
            update_sql = """
            UPDATE user_bots 
            SET credit_balance = %s, last_payment_date = CURRENT_TIMESTAMP
            WHERE user_id = %s AND is_active = TRUE
            """
            
            self.cursor.execute(update_sql, (new_balance, user_id))
            self.connection.commit()
            
            self.log_audit(user_id, "credit_added", {
                "amount": amount, 
                "new_balance": new_balance,
                "type": transaction_type
            })
            
            return new_balance
        except Exception as e:
            print(f"❌ Credit add error: {e}")
            return current_balance
    
    def use_credit(self, user_id, amount=1, description="Message sent"):
        """ক্রেডিট ব্যবহার"""
        current_balance = self.get_user_balance(user_id)
        
        if current_balance < amount:
            return False
        
        new_balance = current_balance - amount
        
        sql = """
        INSERT INTO credits (user_id, amount, transaction_type, description, balance_after)
        VALUES (%s, %s, %s, %s, %s)
        """
        
        try:
            self.cursor.execute(sql, (
                user_id, -amount, "usage", description, new_balance
            ))
            
            # ব্যালেন্স আপডেট
            update_sql = "UPDATE user_bots SET credit_balance = %s WHERE user_id = %s"
            self.cursor.execute(update_sql, (new_balance, user_id))
            self.connection.commit()
            
            return True
        except Exception as e:
            print(f"❌ Credit usage error: {e}")
            return False
    
    def get_user_balance(self, user_id):
        """ইউজার ব্যালেন্স"""
        sql = "SELECT credit_balance FROM user_bots WHERE user_id = %s AND is_active = TRUE"
        
        try:
            self.cursor.execute(sql, (user_id,))
            result = self.cursor.fetchone()
            
            if result:
                if self.db_type == "sqlite":
                    return result["credit_balance"]
                return result[0]
            return 0
        except:
            return 0
    
    # 💳 PAYMENT OPERATIONS
    def create_payment(self, user_id, amount, method="nagad", sender_number="", transaction_id=""):
        """পেমেন্ট রেকর্ড তৈরি"""
        sql = """
        INSERT INTO payments (user_id, amount, method, sender_number, transaction_id)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
        """
        
        try:
            self.cursor.execute(sql, (
                user_id, amount, method, sender_number, transaction_id
            ))
            
            payment_id = self.cursor.fetchone()[0]
            self.connection.commit()
            
            self.log_audit(user_id, "payment_created", {
                "payment_id": payment_id,
                "amount": amount,
                "method": method
            })
            
            return payment_id
        except Exception as e:
            print(f"❌ Payment creation error: {e}")
            return None
    
    def verify_payment(self, payment_id, verified_by, status="verified"):
        """পেমেন্ট ভেরিফাই"""
        sql = """
        UPDATE payments 
        SET status = %s, verified_by = %s, verified_at = CURRENT_TIMESTAMP
        WHERE id = %s
        """
        
        try:
            self.cursor.execute(sql, (status, verified_by, payment_id))
            
            if status == "verified":
                # ক্রেডিট যোগ
                payment = self.get_payment(payment_id)
                if payment:
                    user_id = payment["user_id"]
                    amount = int(payment["amount"] * 100)  # টাকায় রূপান্তর
                    
                    self.add_credit(
                        user_id, amount, 
                        "Payment verified", "purchase", 
                        f"PAYMENT_{payment_id}"
                    )
            
            self.connection.commit()
            
            self.log_audit(verified_by, "payment_verified", {
                "payment_id": payment_id,
                "status": status
            })
            
            return True
        except Exception as e:
            print(f"❌ Payment verification error: {e}")
            return False
    
    def get_payment(self, payment_id):
        """পেমেন্ট ডিটেইলস"""
        sql = "SELECT * FROM payments WHERE id = %s"
        
        try:
            self.cursor.execute(sql, (payment_id,))
            result = self.cursor.fetchone()
            
            if result and self.db_type == "sqlite":
                return dict(result)
            return result
        except:
            return None
    
    # 🧠 AI MEMORY OPERATIONS
    def save_ai_pattern(self, question, response, user_id=None):
        """AI প্যাটার্ন সেভ"""
        import hashlib
        pattern_hash = hashlib.sha256(question.encode()).hexdigest()
        
        sql = """
        INSERT INTO ai_memory (pattern_hash, question, response, learned_from)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (pattern_hash) 
        DO UPDATE SET used_count = ai_memory.used_count + 1, last_used = CURRENT_TIMESTAMP
        RETURNING id
        """
        
        try:
            self.cursor.execute(sql, (pattern_hash, question, response, user_id))
            pattern_id = self.cursor.fetchone()[0]
            self.connection.commit()
            return pattern_id
        except Exception as e:
            print(f"❌ AI pattern save error: {e}")
            return None
    
    def find_ai_pattern(self, question):
        """AI প্যাটার্ন খুঁজুন"""
        import hashlib
        pattern_hash = hashlib.sha256(question.encode()).hexdigest()
        
        sql = """
        SELECT * FROM ai_memory 
        WHERE pattern_hash = %s
        ORDER BY confidence DESC, used_count DESC
        LIMIT 1
        """
        
        try:
            self.cursor.execute(sql, (pattern_hash,))
            result = self.cursor.fetchone()
            
            if result:
                if self.db_type == "sqlite":
                    result = dict(result)
                return result
            return None
        except:
            return None
    
    def increment_ai_usage(self, pattern_id):
        """AI ব্যবহার কাউন্ট বাড়ান"""
        sql = "UPDATE ai_memory SET used_count = used_count + 1 WHERE id = %s"
        
        try:
            self.cursor.execute(sql, (pattern_id,))
            self.connection.commit()
            return True
        except:
            return False
    
    # 💬 CONVERSATION LOGGING
    def log_conversation(self, user_id, bot_id, message_text, response_text=None, message_type="text"):
        """কনভারসেশন লগ"""
        sql = """
        INSERT INTO conversations (user_id, bot_id, message_text, response_text, message_type)
        VALUES (%s, %s, %s, %s, %s)
        """
        
        try:
            self.cursor.execute(sql, (
                user_id, bot_id, message_text, response_text, message_type
            ))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"❌ Conversation log error: {e}")
            return False
    
    def get_user_conversations(self, user_id, limit=50):
        """ইউজারের কনভারসেশন হিস্টরি"""
        sql = """
        SELECT * FROM conversations 
        WHERE user_id = %s 
        ORDER BY created_at DESC 
        LIMIT %s
        """
        
        try:
            self.cursor.execute(sql, (user_id, limit))
            results = self.cursor.fetchall()
            
            if self.db_type == "sqlite":
                return [dict(row) for row in results]
            return results
        except:
            return []
    
    # ⏰ SCHEDULED MESSAGES
    def schedule_message(self, user_id, bot_id, message_text, scheduled_time, repeat_type="once"):
        """মেসেজ শিডিউল"""
        sql = """
        INSERT INTO scheduled_messages (user_id, bot_id, message_text, scheduled_time, repeat_type)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
        """
        
        try:
            self.cursor.execute(sql, (
                user_id, bot_id, message_text, scheduled_time, repeat_type
            ))
            
            message_id = self.cursor.fetchone()[0]
            self.connection.commit()
            
            return message_id
        except Exception as e:
            print(f"❌ Schedule message error: {e}")
            return None
    
    def get_pending_messages(self):
        """পেন্ডিং মেসেজগুলো"""
        sql = """
        SELECT * FROM scheduled_messages 
        WHERE status = 'pending' AND scheduled_time <= CURRENT_TIMESTAMP
        ORDER BY scheduled_time ASC
        LIMIT 100
        """
        
        try:
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            
            if self.db_type == "sqlite":
                return [dict(row) for row in results]
            return results
        except:
            return []
    
    def mark_message_sent(self, message_id):
        """মেসেজ সেন্ট মার্ক"""
        sql = """
        UPDATE scheduled_messages 
        SET status = 'sent', sent_at = CURRENT_TIMESTAMP
        WHERE id = %s
        """
        
        try:
            self.cursor.execute(sql, (message_id,))
            self.connection.commit()
            return True
        except:
            return False
    
    # 🔐 AUDIT LOGGING
    def log_audit(self, user_id, action, details=None, ip_address=None, user_agent=None):
        """অডিট লগ"""
        sql = """
        INSERT INTO audit_log (user_id, action, details, ip_address, user_agent)
        VALUES (%s, %s, %s, %s, %s)
        """
        
        try:
            self.cursor.execute(sql, (
                user_id, action, json.dumps(details or {}), 
                ip_address, user_agent
            ))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"❌ Audit log error: {e}")
            return False
    
    def get_audit_logs(self, user_id=None, limit=100):
        """অডিট লগ নিন"""
        if user_id:
            sql = "SELECT * FROM audit_log WHERE user_id = %s ORDER BY created_at DESC LIMIT %s"
            params = (user_id, limit)
        else:
            sql = "SELECT * FROM audit_log ORDER BY created_at DESC LIMIT %s"
            params = (limit,)
        
        try:
            self.cursor.execute(sql, params)
            results = self.cursor.fetchall()
            
            if self.db_type == "sqlite":
                return [dict(row) for row in results]
            return results
        except:
            return []
    
    # 📊 STATISTICS
    def get_statistics(self):
        """সিস্টেম স্ট্যাটিস্টিক্স"""
        stats = {}
        
        queries = {
            "total_users": "SELECT COUNT(*) FROM users",
            "active_users": "SELECT COUNT(*) FROM users WHERE status = 'active'",
            "total_bots": "SELECT COUNT(*) FROM user_bots",
            "active_bots": "SELECT COUNT(*) FROM user_bots WHERE is_active = TRUE",
            "total_credits": "SELECT SUM(credit_balance) FROM user_bots",
            "total_messages": "SELECT COUNT(*) FROM conversations",
            "total_payments": "SELECT COUNT(*) FROM payments WHERE status = 'verified'",
            "revenue_today": """
                SELECT SUM(amount) FROM payments 
                WHERE status = 'verified' 
                AND DATE(created_at) = CURRENT_DATE
            """,
            "ai_patterns": "SELECT COUNT(*) FROM ai_memory",
            "pending_payments": "SELECT COUNT(*) FROM payments WHERE status = 'pending'"
        }
        
        for key, query in queries.items():
            try:
                self.cursor.execute(query)
                result = self.cursor.fetchone()
                stats[key] = result[0] or 0
            except:
                stats[key] = 0
        
        return stats
    
    def close(self):
        """ডাটাবেজ কানেকশন বন্ধ"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("🗄️ Database connection closed")
    
    def __del__(self):
        """ডেস্ট্রাক্টর"""
        self.close()

class DatabaseFactory:
    """ডাটাবেজ ফ্যাক্টরি - একাধিক ডাটাবেজ ম্যানেজ"""
    
    @staticmethod
    def create_database(config_path="configs/database.json"):
        """ডাটাবেজ তৈরি"""
        import json
        
        if Path(config_path).exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
        else:
            # ডিফল্ট SQLite কনফিগ
            config = {
                "type": "sqlite",
                "path": "data/bot_database.db"
            }
            
            # কনফিগ সেভ
            Path("configs").mkdir(exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
        
        return DatabaseManager(config["type"], config)