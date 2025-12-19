-- Database Migration Script
-- Version: 3.0.0

-- 👤 USERS TABLE
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    settings TEXT DEFAULT '{}'
);

-- 🤖 USER BOTS TABLE
CREATE TABLE IF NOT EXISTS user_bots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    bot_token VARCHAR(255) UNIQUE NOT NULL,
    bot_username VARCHAR(255),
    chat_id BIGINT,
    is_active BOOLEAN DEFAULT 1,
    credit_balance INTEGER DEFAULT 0,
    last_payment_date TIMESTAMP,
    next_payment_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    settings TEXT DEFAULT '{}',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 💰 CREDITS TABLE
CREATE TABLE IF NOT EXISTS credits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    amount INTEGER NOT NULL,
    transaction_type VARCHAR(50),
    reference_id VARCHAR(100),
    description TEXT,
    balance_after INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 💳 PAYMENTS TABLE
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'BDT',
    method VARCHAR(50),
    transaction_id VARCHAR(100),
    sender_number VARCHAR(20),
    status VARCHAR(20) DEFAULT 'pending',
    verified_by INTEGER,
    verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 🧠 AI MEMORY TABLE
CREATE TABLE IF NOT EXISTS ai_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_hash VARCHAR(64) UNIQUE NOT NULL,
    question TEXT NOT NULL,
    response TEXT NOT NULL,
    learned_from INTEGER,
    used_count INTEGER DEFAULT 0,
    confidence DECIMAL(3, 2) DEFAULT 1.0,
    last_used TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (learned_from) REFERENCES users(id) ON DELETE SET NULL
);

-- 💬 CONVERSATIONS TABLE
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    bot_id INTEGER NOT NULL,
    message_text TEXT,
    message_type VARCHAR(20),
    response_text TEXT,
    response_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (bot_id) REFERENCES user_bots(id) ON DELETE CASCADE
);

-- ⏰ SCHEDULED MESSAGES TABLE
CREATE TABLE IF NOT EXISTS scheduled_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    bot_id INTEGER NOT NULL,
    message_text TEXT NOT NULL,
    scheduled_time TIMESTAMP NOT NULL,
    repeat_type VARCHAR(20),
    status VARCHAR(20) DEFAULT 'pending',
    sent_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (bot_id) REFERENCES user_bots(id) ON DELETE CASCADE
);

-- 🔐 AUDIT LOG TABLE
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action VARCHAR(100) NOT NULL,
    details TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- 🎯 INDEXES FOR PERFORMANCE
CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_users_status ON users(status);
CREATE INDEX IF NOT EXISTS idx_user_bots_user_id ON user_bots(user_id);
CREATE INDEX IF NOT EXISTS idx_user_bots_active ON user_bots(is_active);
CREATE INDEX IF NOT EXISTS idx_credits_user_id ON credits(user_id);
CREATE INDEX IF NOT EXISTS idx_credits_created ON credits(created_at);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);
CREATE INDEX IF NOT EXISTS idx_payments_created ON payments(created_at);
CREATE INDEX IF NOT EXISTS idx_ai_memory_hash ON ai_memory(pattern_hash);
CREATE INDEX IF NOT EXISTS idx_ai_memory_confidence ON ai_memory(confidence);
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_created ON conversations(created_at);
CREATE INDEX IF NOT EXISTS idx_scheduled_messages_time ON scheduled_messages(scheduled_time);
CREATE INDEX IF NOT EXISTS idx_scheduled_messages_status ON scheduled_messages(status);
CREATE INDEX IF NOT EXISTS idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_created ON audit_log(created_at);

-- 📊 VIEWS FOR REPORTING
CREATE VIEW IF NOT EXISTS v_user_summary AS
SELECT 
    u.id,
    u.telegram_id,
    u.username,
    u.first_name,
    u.status,
    u.created_at,
    u.last_active,
    COUNT(DISTINCT ub.id) as bot_count,
    COALESCE(SUM(ub.credit_balance), 0) as total_credits,
    COUNT(DISTINCT p.id) as payment_count,
    COALESCE(SUM(CASE WHEN p.status = 'verified' THEN p.amount ELSE 0 END), 0) as total_paid
FROM users u
LEFT JOIN user_bots ub ON u.id = ub.user_id AND ub.is_active = 1
LEFT JOIN payments p ON u.id = p.user_id
GROUP BY u.id;

CREATE VIEW IF NOT EXISTS v_daily_stats AS
SELECT
    DATE(created_at) as date,
    COUNT(DISTINCT user_id) as active_users,
    COUNT(*) as total_messages,
    SUM(CASE WHEN response_text IS NOT NULL THEN 1 ELSE 0 END) as responded_messages,
    COUNT(DISTINCT bot_id) as active_bots
FROM conversations
GROUP BY DATE(created_at);

-- 🔄 TRIGGERS FOR DATA INTEGRITY
CREATE TRIGGER IF NOT EXISTS trg_update_last_active
AFTER INSERT ON conversations
FOR EACH ROW
BEGIN
    UPDATE users 
    SET last_active = CURRENT_TIMESTAMP 
    WHERE id = NEW.user_id;
END;

CREATE TRIGGER IF NOT EXISTS trg_credit_check
BEFORE INSERT ON conversations
FOR EACH ROW
WHEN (SELECT credit_balance FROM user_bots WHERE id = NEW.bot_id) <= 0
BEGIN
    SELECT RAISE(ABORT, 'Insufficient credits');
END;

-- 🗑️ CLEANUP OLD DATA (90 days)
CREATE TRIGGER IF NOT EXISTS trg_cleanup_conversations
AFTER INSERT ON conversations
BEGIN
    DELETE FROM conversations 
    WHERE created_at < datetime('now', '-90 days');
END;

-- Version tracking
CREATE TABLE IF NOT EXISTS db_version (
    version VARCHAR(20) PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

INSERT OR IGNORE INTO db_version (version, description) 
VALUES ('3.0.0', 'Initial database schema');