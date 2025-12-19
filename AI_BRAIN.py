"""
🧠 ADVANCED AI BRAIN SYSTEM
Self-learning neural network simulation
"""

import json
import hashlib
import random
import numpy as np
from datetime import datetime
from collections import defaultdict
from pathlib import Path

class NeuralAI:
    def __init__(self):
        self.memory_path = Path("data/ai_brain.json")
        self.memory_path.parent.mkdir(exist_ok=True)
        
        self._load_brain()
        
        # AI প্যারামিটার
        self.learning_rate = 0.1
        self.memory_decay = 0.99
        self.pattern_threshold = 0.6
        
        print("🧠 AI Neural Network Initialized")
    
    def _load_brain(self):
        """ব্রেইন লোড"""
        if self.memory_path.exists():
            with open(self.memory_path, 'r', encoding='utf-8') as f:
                brain_data = json.load(f)
                self.patterns = brain_data.get("patterns", {})
                self.connections = brain_data.get("connections", {})
                self.context_memory = brain_data.get("context", {})
                self.learning_log = brain_data.get("learning", [])
        else:
            self.patterns = {}
            self.connections = {}
            self.context_memory = {}
            self.learning_log = []
    
    def _save_brain(self):
        """ব্রেইন সেভ"""
        brain_data = {
            "patterns": self.patterns,
            "connections": self.connections,
            "context": self.context_memory,
            "learning": self.learning_log[-1000:],  # শুধু শেষ 1000
            "updated": datetime.now().isoformat()
        }
        
        with open(self.memory_path, 'w', encoding='utf-8') as f:
            json.dump(brain_data, f, ensure_ascii=False, indent=2)
    
    def _text_to_vector(self, text):
        """টেক্সট থেকে ভেক্টর তৈরি"""
        words = text.lower().split()
        vector = {}
        
        for word in words:
            if len(word) > 2:  # শুধু গুরুত্বপূর্ণ শব্দ
                word_hash = hashlib.md5(word.encode()).hexdigest()[:8]
                vector[word_hash] = vector.get(word_hash, 0) + 1
        
        return vector
    
    def _cosine_similarity(self, vec1, vec2):
        """কোসাইন সাদৃশ্যতা"""
        if not vec1 or not vec2:
            return 0.0
        
        dot_product = sum(vec1.get(k, 0) * vec2.get(k, 0) for k in set(vec1) & set(vec2))
        norm1 = sum(v**2 for v in vec1.values()) ** 0.5
        norm2 = sum(v**2 for v in vec2.values()) ** 0.5
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def learn_pattern(self, question, response, user_id):
        """নতুন প্যাটার্ন শেখে"""
        q_vector = self._text_to_vector(question)
        q_hash = hashlib.md5(question.encode()).hexdigest()
        
        # নতুন প্যাটার্ন
        if q_hash not in self.patterns:
            self.patterns[q_hash] = {
                "question": question,
                "vector": q_vector,
                "responses": [response],
                "confidence": 1.0,
                "learned_from": [user_id],
                "learned_at": datetime.now().isoformat(),
                "used_count": 0,
                "success_rate": 1.0
            }
        else:
            # বিদ্যমান প্যাটার্ন আপডেট
            pattern = self.patterns[q_hash]
            
            if response not in pattern["responses"]:
                pattern["responses"].append(response)
            
            if user_id not in pattern["learned_from"]:
                pattern["learned_from"].append(user_id)
            
            pattern["confidence"] = min(1.0, pattern["confidence"] + 0.1)
        
        # কানেকশন তৈরি
        self._build_connections(q_hash, response)
        
        # লার্নিং লগ
        self.learning_log.append({
            "type": "learn",
            "question": question[:50],
            "response": response[:50],
            "user": user_id,
            "time": datetime.now().isoformat()
        })
        
        self._save_brain()
        return True
    
    def _build_connections(self, source_hash, response):
        """নিউরাল কানেকশন তৈরি"""
        resp_vector = self._text_to_vector(response)
        resp_hash = hashlib.md5(response.encode()).hexdigest()
        
        if source_hash not in self.connections:
            self.connections[source_hash] = {}
        
        # ওয়েট আপডেট
        current_weight = self.connections[source_hash].get(resp_hash, 0)
        self.connections[source_hash][resp_hash] = current_weight + 1
        
        # ডিকে রেট প্রয়োগ
        for src in list(self.connections.keys()):
            for dst in list(self.connections[src].keys()):
                self.connections[src][dst] *= self.memory_decay
                
                if self.connections[src][dst] < 0.01:
                    del self.connections[src][dst]
        
        self._save_brain()
    
    def find_response(self, question, user_id=None):
        """সেরা উত্তর খুঁজে"""
        q_vector = self._text_to_vector(question)
        
        best_match = None
        best_score = 0.0
        
        # সব প্যাটার্ন চেক
        for p_hash, pattern in self.patterns.items():
            similarity = self._cosine_similarity(q_vector, pattern["vector"])
            
            # কনফিডেন্স ফ্যাক্টর
            adjusted_score = similarity * pattern["confidence"]
            
            if adjusted_score > best_score and adjusted_score > self.pattern_threshold:
                best_score = adjusted_score
                best_match = pattern
        
        if best_match:
            # প্যাটার্ন আপডেট
            best_match["used_count"] += 1
            
            # কনটেক্সট মেমোরি
            if user_id:
                self._update_context(user_id, question, best_match["responses"][0])
            
            # রেসপন্স সিলেক্ট
            if len(best_match["responses"]) > 1:
                # ওয়েটেড র্যান্ডম সিলেকশন
                weights = []
                for resp in best_match["responses"]:
                    resp_hash = hashlib.md5(resp.encode()).hexdigest()
                    weight = self.connections.get(p_hash, {}).get(resp_hash, 1.0)
                    weights.append(weight)
                
                # নরমালাইজ ওয়েট
                total = sum(weights)
                if total > 0:
                    probs = [w/total for w in weights]
                    response_idx = np.random.choice(len(best_match["responses"]), p=probs)
                else:
                    response_idx = random.randint(0, len(best_match["responses"])-1)
                
                response = best_match["responses"][response_idx]
            else:
                response = best_match["responses"][0]
            
            # লার্নিং লগ
            self.learning_log.append({
                "type": "recall",
                "question": question[:50],
                "response": response[:50],
                "score": best_score,
                "time": datetime.now().isoformat()
            })
            
            self._save_brain()
            
            return {
                "response": response,
                "confidence": best_score,
                "source": "ai_memory",
                "pattern_used": best_match["question"][:50]
            }
        
        return None
    
    def _update_context(self, user_id, question, response):
        """কনটেক্সট মেমোরি আপডেট"""
        user_key = str(user_id)
        
        if user_key not in self.context_memory:
            self.context_memory[user_key] = []
        
        self.context_memory[user_key].append({
            "question": question,
            "response": response,
            "time": datetime.now().isoformat()
        })
        
        # শুধু শেষ 20 কনভারসেশন রাখুন
        if len(self.context_memory[user_key]) > 20:
            self.context_memory[user_key] = self.context_memory[user_key][-20:]
    
    def get_context(self, user_id):
        """ইউজার কনটেক্সট পেতে"""
        return self.context_memory.get(str(user_id), [])
    
    def get_brain_stats(self):
        """ব্রেইন স্ট্যাটিস্টিক্স"""
        return {
            "total_patterns": len(self.patterns),
            "total_connections": sum(len(v) for v in self.connections.values()),
            "learning_log_count": len(self.learning_log),
            "unique_users": len(self.context_memory),
            "avg_confidence": np.mean([p["confidence"] for p in self.patterns.values()]) 
                              if self.patterns else 0
        }

class AIOrchestrator:
    def __init__(self):
        self.brain = NeuralAI()
        self.response_cache = {}
        
    def process_query(self, user_id, query):
        """কোয়েরি প্রসেস"""
        # প্রথমে ক্যাশে চেক
        cache_key = f"{user_id}_{hashlib.md5(query.encode()).hexdigest()}"
        if cache_key in self.response_cache:
            return self.response_cache[cache_key]
        
        # AI ব্রেইন থেকে উত্তর খুঁজুন
        ai_response = self.brain.find_response(query, user_id)
        
        if ai_response:
            # ক্যাশে স্টোর
            self.response_cache[cache_key] = ai_response
            
            # ক্যাশে লিমিট
            if len(self.response_cache) > 1000:
                # FIFO: প্রথমেরগুলো রিমুভ
                keys = list(self.response_cache.keys())
                for key in keys[:100]:
                    del self.response_cache[key]
            
            return ai_response
        
        # উত্তর না পেলে
        return {
            "response": None,
            "confidence": 0.0,
            "source": "no_match",
            "suggestion": "আমি এই প্রশ্নের উত্তর জানি না। আপনি আমাকে শিখিয়ে দিবেন?"
        }
    
    def teach_ai(self, user_id, question, response):
        """AI কে শেখান"""
        success = self.brain.learn_pattern(question, response, user_id)
        
        if success:
            # ক্যাশে ইনভ্যালিডেট
            cache_key = f"{user_id}_{hashlib.md5(question.encode()).hexdigest()}"
            if cache_key in self.response_cache:
                del self.response_cache[cache_key]
        
        return success
    
    def get_ai_status(self):
        """AI স্ট্যাটাস"""
        stats = self.brain.get_brain_stats()
        stats["cache_size"] = len(self.response_cache)
        stats["active"] = True
        
        return stats