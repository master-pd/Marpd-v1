"""
My Custom Feature Plugin
"""

def on_load(system):
    """Called when plugin loads"""
    print("✅ My Plugin Loaded")
    return {"name": "my_feature", "version": "1.0"}

def handle_event(event_name, data=None):
    """Handle system events"""
    if event_name == "user_message":
        # Process user message
        return {"response": "Hello from my plugin!"}
    return None