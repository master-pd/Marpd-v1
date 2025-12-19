import re

class Validator:
    @staticmethod
    def is_valid_email(email):
        return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email) is not None
    
    @staticmethod
    def is_valid_phone(phone):
        return re.match(r'^\+?[0-9]{10,15}$', phone) is not None