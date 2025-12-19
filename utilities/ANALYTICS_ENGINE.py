"""
📈 ANALYTICS ENGINE
User behavior analysis and insights
"""

import json
import time
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

class AnalyticsEngine:
    def __init__(self, core):
        self.core = core
        self.user_behavior = defaultdict(list)
        self.system_metrics = []
        self.report_cache = {}
        print("📈 Analytics Engine Started")
    
    def track_user_action(self, user_id, action, data=None):
        """ইউজার অ্যাকশন ট্র্যাক"""
        timestamp = datetime.now().isoformat()
        
        log_entry = {
            "user_id": str(user_id),
            "action": action,
            "data": data or {},
            "timestamp": timestamp
        }
        
        self.user_behavior[str(user_id)].append(log_entry)
        
        # মেমোরি ম্যানেজমেন্ট
        if len(self.user_behavior[str(user_id)]) > 1000:
            self.user_behavior[str(user_id)] = self.user_behavior[str(user_id)][-500:]
    
    def get_user_insights(self, user_id):
        """ইউজার ইনসাইটস"""
        user_key = str(user_id)
        
        if user_key not in self.user_behavior:
            return {"error": "No data available"}
        
        actions = self.user_behavior[user_key]
        
        # শেষ 30 দিনের ডাটা
        month_ago = datetime.now() - timedelta(days=30)
        recent_actions = [
            a for a in actions 
            if datetime.fromisoformat(a['timestamp']) > month_ago
        ]
        
        if not recent_actions:
            return {"error": "No recent activity"}
        
        # অ্যাকশন কাউন্ট
        action_counts = defaultdict(int)
        for action in recent_actions:
            action_counts[action['action']] += 1
        
        # সক্রিয় দিন
        active_days = set()
        for action in recent_actions:
            date = datetime.fromisoformat(action['timestamp']).date()
            active_days.add(date)
        
        # পিক সময়
        hours = [datetime.fromisoformat(a['timestamp']).hour for a in recent_actions]
        if hours:
            peak_hour = statistics.mode(hours)
        else:
            peak_hour = None
        
        return {
            "total_actions": len(recent_actions),
            "active_days": len(active_days),
            "avg_daily_actions": len(recent_actions) / max(len(active_days), 1),
            "peak_hour": peak_hour,
            "top_actions": dict(sorted(action_counts.items(), key=lambda x: x[1], reverse=True)[:5]),
            "last_active": recent_actions[-1]['timestamp'] if recent_actions else None
        }
    
    def generate_system_report(self, period="daily"):
        """সিস্টেম রিপোর্ট জেনারেট"""
        cache_key = f"{period}_{datetime.now().strftime('%Y%m%d')}"
        
        if cache_key in self.report_cache:
            return self.report_cache[cache_key]
        
        if period == "daily":
            start_time = datetime.now() - timedelta(days=1)
        elif period == "weekly":
            start_time = datetime.now() - timedelta(days=7)
        else:  # monthly
            start_time = datetime.now() - timedelta(days=30)
        
        report = {
            "period": period,
            "start_date": start_time.isoformat(),
            "end_date": datetime.now().isoformat(),
            "user_growth": self._calculate_user_growth(start_time),
            "engagement": self._calculate_engagement(start_time),
            "revenue": self._calculate_revenue(start_time),
            "ai_performance": self._calculate_ai_performance(start_time),
            "system_health": self._calculate_system_health()
        }
        
        self.report_cache[cache_key] = report
        return report
    
    def _calculate_user_growth(self, since):
        """ইউজার গ্রোথ"""
        # ইমপ্লিমেন্টেশন
        return {"new_users": 0, "growth_rate": 0}
    
    def _calculate_engagement(self, since):
        """এনগেজমেন্ট"""
        # ইমপ্লিমেন্টেশন
        return {"active_users": 0, "messages_per_user": 0}
    
    def _calculate_revenue(self, since):
        """রেভিনিউ"""
        # ইমপ্লিমেন্টেশন
        return {"total": 0, "projected": 0}
    
    def _calculate_ai_performance(self, since):
        """AI পারফরমেন্স"""
        # ইমপ্লিমেন্টেশন
        return {"accuracy": 0, "response_time": 0}
    
    def _calculate_system_health(self):
        """সিস্টেম হেল্থ"""
        # ইমপ্লিমেন্টেশন
        return {"uptime": 100, "error_rate": 0}