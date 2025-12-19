import hashlib
import base64

class SimpleEncrypt:
    def __init__(self, secret):
        self.secret = secret
    
    def encrypt(self, text):
        combined = f"{text}:{self.secret}"
        return hashlib.sha256(combined.encode()).hexdigest()