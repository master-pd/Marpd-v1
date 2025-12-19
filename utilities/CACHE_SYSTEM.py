"""
💾 INTELLIGENT CACHE SYSTEM
LRU cache with auto-expiration
"""

import time
from collections import OrderedDict

class SmartCache:
    def __init__(self, max_size=1000, ttl=3600):
        self.cache = OrderedDict()
        self.max_size = max_size
        self.ttl = ttl  # Time to live in seconds
        self.hits = 0
        self.misses = 0
    
    def get(self, key):
        """ভ্যালু পেতে"""
        if key not in self.cache:
            self.misses += 1
            return None
        
        value, timestamp = self.cache[key]
        
        # TTL চেক
        if time.time() - timestamp > self.ttl:
            del self.cache[key]
            self.misses += 1
            return None
        
        # LRU: শেষে নিয়ে যান
        self.cache.move_to_end(key)
        self.hits += 1
        return value
    
    def set(self, key, value):
        """ভ্যালু সেট"""
        if len(self.cache) >= self.max_size:
            # LRU: প্রথম আইটেম রিমুভ
            self.cache.popitem(last=False)
        
        self.cache[key] = (value, time.time())
    
    def delete(self, key):
        """ভ্যালু ডিলিট"""
        if key in self.cache:
            del self.cache[key]
            return True
        return False
    
    def clear(self):
        """ক্যাশে ক্লিয়ার"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
    
    def stats(self):
        """স্ট্যাটিস্টিক্স"""
        return {
            "size": len(self.cache),
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": self.hits / (self.hits + self.misses) if (self.hits + self.misses) > 0 else 0,
            "max_size": self.max_size
        }