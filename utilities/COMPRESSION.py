import gzip
import json

class DataCompressor:
    @staticmethod
    def compress(data):
        return gzip.compress(json.dumps(data).encode())
    
    @staticmethod  
    def decompress(compressed):
        return json.loads(gzip.decompress(compressed).decode())