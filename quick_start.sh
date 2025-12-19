#!/bin/bash
# quick_start.sh

echo "🚀 RANA BOT SYSTEM - Quick Start"
echo "================================"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found!"
    exit 1
fi

# Create directory
mkdir -p rana_bot_system
cd rana_bot_system

echo "📁 Creating project structure..."

# Create basic files
cat > SYSTEM_CORE.py << 'EOF'
# [SYSTEM_CORE.py content from above]
EOF

cat > .env << 'EOF'
# [.env content from above]
EOF

cat > requirements.txt << 'EOF'
# [requirements.txt content from above]
EOF

# Create directories
mkdir -p data configs logs backups plugins

# Create minimal config
cat > configs/system.json << 'EOF'
{
    "name": "YOUR CRUSH ⟵o_0",
    "version": "4.0",
    "developer": "RANA (MASTER 🪓)",
    "contact": "01847634486",
    "email": "ranaeditz333@gmail.com",
    "location": "Faridpur, Dhaka, Bangladesh"
}
EOF

# Create minimal plugin
cat > plugins/01_dev_info.py << 'EOF'
"""
👤 Developer Information Plugin
"""

def on_load(system):
    print("✅ Developer Info Plugin Loaded")
    
    dev_info = {
        "name": "RANA (MASTER 🪓)",
        "bot": "YOUR CRUSH ⟵o_0",
        "contact": "01847634486",
        "email": "ranaeditz333@gmail.com",
        "telegram": "@rana_editz_00",
        "location": "Faridpur, Dhaka, Bangladesh"
    }
    
    system.dev_info = dev_info
    return dev_info

def handle_event(event_name, data):
    if event_name == "get_dev_info":
        return {
            "name": "RANA (MASTER 🪓)",
            "contact": "01847634486"
        }
    return None
EOF

echo "✅ Project created successfully!"
echo ""
echo "📋 Next Steps:"
echo "1. Edit .env file with your BOT_TOKEN"
echo "2. Install dependencies: pip install -r requirements.txt"
echo "3. Run the system: python SYSTEM_CORE.py"
echo ""
echo "📞 Support: 01847634486"
echo "👤 Developer: RANA (MASTER 🪓)"