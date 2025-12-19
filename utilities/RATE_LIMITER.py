import time
from collections import defaultdict

class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(list)
    
    def check(self, key, limit=10, window=60):
        current = time.time()
        self.requests[key] = [t for t in self.requests[key] if current - t < window]
        
        if len(self.requests[key]) >= limit:
            return False
        
        self.requests[key].append(current)
        return True