import time
from datetime import datetime

class MaintenanceMode:
    def __init__(self, core):
        self.core = core
        self.active = False
    
    def enable(self, reason="System maintenance"):
        self.active = True
        self.reason = reason
        self.start_time = datetime.now()
        return True
    
    def disable(self):
        self.active = False
        return True