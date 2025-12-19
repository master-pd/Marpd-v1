import os
import sys

class DeploymentHelper:
    @staticmethod
    def check_requirements():
        required = ['requests', 'python-telegram-bot']
        missing = []
        
        for package in required:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                missing.append(package)
        
        return missing
    
    @staticmethod
    def setup_directories():
        dirs = ['data', 'plugins', 'logs', 'backups']
        for d in dirs:
            os.makedirs(d, exist_ok=True)