"""
🔑 LICENSE MANAGEMENT SYSTEM
Software licensing and activation
"""

import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path

class LicenseManager:
    def __init__(self, core):
        self.core = core
        self.licenses_file = Path("data/licenses.json")
        self.licenses_file.parent.mkdir(exist_ok=True)
        
        self.licenses = self._load_licenses()
        self.license_key = self._generate_system_key()
        
        print("🔑 License Manager Initialized")
    
    def _load_licenses(self):
        """লাইসেন্স লোড"""
        if self.licenses_file.exists():
            with open(self.licenses_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_licenses(self):
        """লাইসেন্স সেভ"""
        with open(self.licenses_file, 'w') as f:
            json.dump(self.licenses, f, indent=2)
    
    def _generate_system_key(self):
        """সিস্টেম কি জেনারেট"""
        import socket
        import platform
        
        system_info = {
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "processor": platform.processor(),
            "machine": platform.machine()
        }
        
        key_string = json.dumps(system_info, sort_keys=True)
        return hashlib.sha256(key_string.encode()).hexdigest()[:32]
    
    def generate_license(self, user_id, plan="basic", duration_days=30):
        """লাইসেন্স জেনারেট"""
        user_key = str(user_id)
        
        license_data = {
            "license_id": hashlib.md5(f"{user_key}_{datetime.now().timestamp()}".encode()).hexdigest(),
            "user_id": user_key,
            "plan": plan,
            "created": datetime.now().isoformat(),
            "expires": (datetime.now() + timedelta(days=duration_days)).isoformat(),
            "status": "active",
            "features": self._get_plan_features(plan),
            "max_bots": self._get_max_bots(plan),
            "signature": self._sign_license(user_key, plan)
        }
        
        self.licenses[license_data["license_id"]] = license_data
        self._save_licenses()
        
        return license_data
    
    def _get_plan_features(self, plan):
        """প্ল্যান ফিচার"""
        plans = {
            "basic": ["auto_reply", "welcome_messages", "basic_ai"],
            "premium": ["auto_reply", "welcome_messages", "advanced_ai", "media_support", "analytics"],
            "enterprise": ["all_features", "priority_support", "custom_plugins", "api_access"]
        }
        return plans.get(plan, plans["basic"])
    
    def _get_max_bots(self, plan):
        """ম্যাক্সিমাম বট"""
        limits = {
            "basic": 1,
            "premium": 3,
            "enterprise": 10
        }
        return limits.get(plan, 1)
    
    def _sign_license(self, user_id, plan):
        """লাইসেন্স সাইন"""
        data = f"{user_id}:{plan}:{self.license_key}"
        return hashlib.sha512(data.encode()).hexdigest()
    
    def validate_license(self, license_id, user_id=None):
        """লাইসেন্স ভ্যালিডেট"""
        if license_id not in self.licenses:
            return {"valid": False, "error": "License not found"}
        
        license_data = self.licenses[license_id]
        
        # ইউজার আইডি চেক
        if user_id and str(user_id) != license_data["user_id"]:
            return {"valid": False, "error": "User mismatch"}
        
        # এক্সপাইরি চেক
        expires = datetime.fromisoformat(license_data["expires"])
        if datetime.now() > expires:
            license_data["status"] = "expired"
            self._save_licenses()
            return {"valid": False, "error": "License expired"}
        
        # সিগনেচার ভ্যালিডেশন
        expected_signature = self._sign_license(license_data["user_id"], license_data["plan"])
        if license_data["signature"] != expected_signature:
            return {"valid": False, "error": "Invalid signature"}
        
        return {
            "valid": True,
            "license": license_data,
            "remaining_days": (expires - datetime.now()).days
        }
    
    def check_user_access(self, user_id, feature):
        """ইউজার একসেস চেক"""
        user_key = str(user_id)
        
        # ইউজারের লাইসেন্স খুঁজুন
        user_license = None
        for license_id, license_data in self.licenses.items():
            if license_data["user_id"] == user_key and license_data["status"] == "active":
                user_license = license_data
                break
        
        if not user_license:
            return {"access": False, "reason": "No active license"}
        
        # ফিচার চেক
        if feature in user_license["features"] or "all_features" in user_license["features"]:
            return {"access": True, "license": license_id}
        
        return {"access": False, "reason": "Feature not in plan"}
    
    def update_license(self, license_id, updates):
        """লাইসেন্স আপডেট"""
        if license_id not in self.licenses:
            return False
        
        for key, value in updates.items():
            if key in ["license_id", "signature"]:
                continue
            self.licenses[license_id][key] = value
        
        # সিগনেচার রিক্যালকুলেট
        license_data = self.licenses[license_id]
        license_data["signature"] = self._sign_license(
            license_data["user_id"], 
            license_data["plan"]
        )
        
        self._save_licenses()
        return True
    
    def revoke_license(self, license_id):
        """লাইসেন্স রিভোক"""
        if license_id in self.licenses:
            self.licenses[license_id]["status"] = "revoked"
            self._save_licenses()
            return True
        return False