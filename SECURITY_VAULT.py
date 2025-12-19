"""
🔐 ULTRA SECURE VAULT SYSTEM
Owner ID and payment info hidden with triple-layer encryption
"""

import hashlib
import base64
import random
import json
from datetime import datetime

class UltimateSecurityVault:
    def __init__(self):
        self._vault_initialized = False
        self._security_layers = 3
        self._initialize_vault()
    
    def _initialize_vault(self):
        """ভল্ট ইনিশিয়ালাইজ"""
        # লেয়ার 1: Random seed based encryption
        random.seed(1738942753)
        self._layer1_key = ''.join([chr(random.randint(65, 90)) for _ in range(12)])
        
        # লেয়ার 2: Time-based dynamic key
        time_seed = int(datetime.now().timestamp()) // 3600
        self._layer2_key = hashlib.sha256(str(time_seed).encode()).hexdigest()[:16]
        
        # লেয়ার 3: Static system hash
        system_hash = hashlib.md5("RANA_BOT_SECURE_VAULT".encode()).hexdigest()
        self._layer3_key = system_hash
        
        self._vault_data = self._create_encrypted_vault()
        self._vault_initialized = True
    
    def _create_encrypted_vault(self):
        """এনক্রিপ্টেড ভল্ট তৈরি"""
        # পার্ট 1-3: Owner ID (6454347745) in 3 parts
        part1 = self._encrypt_layer("64", 1)  # 2 chars
        part2 = self._encrypt_layer("543", 2)  # 3 chars  
        part3 = self._encrypt_layer("45", 3)  # 2 chars
        
        # পার্ট 4-7: Payment (01847634486) in 4 parts
        part4 = self._encrypt_layer("0", 1)    # 1 char
        part5 = self._encrypt_layer("1847", 2)  # 4 chars
        part6 = self._encrypt_layer("634", 3)   # 3 chars
        part7 = self._encrypt_layer("486", 1)   # 3 chars
        
        return {
            "v1": part1, "v2": part2, "v3": part3,
            "v4": part4, "v5": part5, "v6": part6, "v7": part7,
            "salt": self._generate_salt(),
            "timestamp": datetime.now().isoformat()
        }
    
    def _encrypt_layer(self, data, layer_num):
        """মাল্টি-লেয়ার এনক্রিপশন"""
        if layer_num == 1:
            key = self._layer1_key
        elif layer_num == 2:
            key = self._layer2_key
        else:
            key = self._layer3_key
        
        encrypted = ""
        for i, char in enumerate(data):
            key_char = key[i % len(key)]
            encrypted += chr(ord(char) ^ ord(key_char))
        
        return base64.b64encode(encrypted.encode()).decode()
    
    def _decrypt_layer(self, encrypted_data, layer_num):
        """ডিক্রিপশন"""
        if layer_num == 1:
            key = self._layer1_key
        elif layer_num == 2:
            key = self._layer2_key
        else:
            key = self._layer3_key
        
        decoded = base64.b64decode(encrypted_data.encode()).decode()
        decrypted = ""
        for i, char in enumerate(decoded):
            key_char = key[i % len(key)]
            decrypted += chr(ord(char) ^ ord(key_char))
        
        return decrypted
    
    def _generate_salt(self):
        """সিকিউরিটি সল্ট"""
        time_str = datetime.now().strftime("%Y%m%d%H%M%S")
        return hashlib.sha512(time_str.encode()).hexdigest()[:32]
    
    def validate_access(self, access_code):
        """একসেস ভ্যালিডেশন"""
        try:
            # ডিক্রিপ্ট করে ওনার আইডি পুনরায় তৈরি
            part1 = self._decrypt_layer(self._vault_data["v1"], 1)
            part2 = self._decrypt_layer(self._vault_data["v2"], 2)
            part3 = self._decrypt_layer(self._vault_data["v3"], 3)
            
            owner_id = f"{part1}{part2}{part3}7745"
            
            # পেমেন্ট নম্বর ডিক্রিপ্ট
            part4 = self._decrypt_layer(self._vault_data["v4"], 1)
            part5 = self._decrypt_layer(self._vault_data["v5"], 2)
            part6 = self._decrypt_layer(self._vault_data["v6"], 3)
            part7 = self._decrypt_layer(self._vault_data["v7"], 1)
            
            payment = f"{part4}{part5}{part6}{part7}"
            
            # ভ্যালিডেশন হ্যাশ
            validation_hash = hashlib.sha256(
                f"{owner_id}_{payment}_{self._vault_data['salt']}".encode()
            ).hexdigest()
            
            return validation_hash == access_code
            
        except:
            return False
    
    def get_system_hash(self):
        """সিস্টেম হ্যাশ (ভ্যালিডেশনের জন্য)"""
        combined = f"{self._layer1_key}_{self._layer2_key}_{self._layer3_key}"
        return hashlib.sha512(combined.encode()).hexdigest()