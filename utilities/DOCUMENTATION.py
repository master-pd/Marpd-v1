class AutoDocumentation:
    def __init__(self, core):
        self.core = core
    
    def generate(self):
        docs = {
            "system": {
                "name": "YOUR CRUSH ⟵o_0",
                "version": "3.0",
                "developer": "RANA (MASTER 🪓)",
                "contact": "01847634486"
            },
            "plugins": list(getattr(self.core, 'plugins', {}).keys()),
            "features": [
                "Auto-loading plugins",
                "AI learning system", 
                "Credit management",
                "Multi-bot support"
            ]
        }
        return docs