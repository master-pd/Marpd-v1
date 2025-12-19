"""
🌐 API INTEGRATION SYSTEM
External API calls and webhook handling
"""

import requests
import json
import hashlib
import time
from datetime import datetime

class APIHandler:
    def __init__(self, core):
        self.core = core
        self.rate_limit = {}
        self.cache = {}
        print("🌐 API Handler Initialized")
    
    def call_api(self, endpoint, method="GET", data=None, headers=None):
        """API কল"""
        try:
            url = endpoint
            
            default_headers = {
                "User-Agent": "RANA-Bot-System/3.0",
                "Content-Type": "application/json"
            }
            
            if headers:
                default_headers.update(headers)
            
            if method == "GET":
                response = requests.get(url, headers=default_headers, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=data, headers=default_headers, timeout=10)
            else:
                return {"error": "Invalid method"}
            
            # Rate limit tracking
            self._track_rate_limit(endpoint)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"API error: {response.status_code}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def _track_rate_limit(self, endpoint):
        """রেট লিমিট ট্র্যাক"""
        current_minute = int(time.time() / 60)
        
        if endpoint not in self.rate_limit:
            self.rate_limit[endpoint] = {}
        
        if current_minute not in self.rate_limit[endpoint]:
            self.rate_limit[endpoint][current_minute] = 0
        
        self.rate_limit[endpoint][current_minute] += 1
        
        # পুরোনো ডাটা ক্লিনআপ
        old_keys = [k for k in self.rate_limit[endpoint].keys() if k < current_minute - 10]
        for key in old_keys:
            del self.rate_limit[endpoint][key]