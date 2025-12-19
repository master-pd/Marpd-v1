import time
import json
from datetime import datetime
from pathlib import Path
import threading
import sys

class SystemMonitor:
    def __init__(self, core_system):
        self.core = core_system
        self.metrics = {}
        self.alerts = []
        
        self._start_monitoring()
        
        print("📊 System Monitor Activated")
    
    def _start_monitoring(self):
        """মনিটরিং শুরু"""
        def monitoring_loop():
            while True:
                try:
                    self._collect_metrics()
                    self._check_alerts()
                    self._log_metrics()
                except Exception as e:
                    print(f"⚠️ Monitoring error: {e}")
                
                time.sleep(60)  # প্রতি মিনিটে
        
        threading.Thread(target=monitoring_loop, daemon=True).start()
    
    def _collect_metrics(self):
        """মেট্রিক্স সংগ্রহ"""
        current_time = datetime.now()
        
        # সিস্টেম মেট্রিক্স
        self.metrics = {
            "timestamp": current_time.isoformat(),
            "system": {
                "uptime": self._get_uptime(),
                "memory_usage": self._get_memory_usage(),
                "cpu_usage": self._get_cpu_usage(),
                "disk_usage": self._get_disk_usage()
            },
            "users": {
                "total": len(getattr(self.core, '_users', {})),
                "active": len([u for u in getattr(self.core, '_users', {}).values() 
                             if u.get("status") == "active"]),
                "new_today": self._count_new_users_today()
            },
            "ai": {
                "patterns": len(getattr(self.core.ai_orchestrator.brain, 'patterns', {})) 
                          if hasattr(self.core, 'ai_orchestrator') else 0,
                "learning_rate": self._get_ai_learning_rate(),
                "accuracy": self._get_ai_accuracy()
            },
            "plugins": {
                "total": len(getattr(self.core, 'plugins', {})),
                "loaded": sum(1 for p in getattr(self.core, 'plugins', {}).values() 
                            if hasattr(p, 'handle_event'))
            },
            "performance": {
                "response_time": self._get_avg_response_time(),
                "error_rate": self._get_error_rate(),
                "throughput": self._get_throughput()
            },
            "financial": {
                "total_credits": sum(getattr(self.core, '_credits', {}).values()),
                "revenue_today": self._get_revenue_today(),
                "active_subscriptions": self._count_active_subscriptions()
            }
        }
    
    def _get_uptime(self):
        """সিস্টেম আপটাইম"""
        if hasattr(self.core, '_start_time'):
            return time.time() - self.core._start_time
        return 0
    
    def _get_memory_usage(self):
        """মেমোরি ব্যবহার"""
        try:
            import psutil
            return psutil.virtual_memory().percent
        except:
            return 0
    
    def _get_cpu_usage(self):
        """CPU ব্যবহার"""
        try:
            import psutil
            return psutil.cpu_percent(interval=1)
        except:
            return 0
    
    def _get_disk_usage(self):
        """ডিস্ক ব্যবহার"""
        try:
            import psutil
            return psutil.disk_usage('/').percent
        except:
            return 0
    
    def _count_new_users_today(self):
        """আজকের নতুন ইউজার"""
        try:
            today = datetime.now().date()
            count = 0
            
            for user_data in getattr(self.core, '_users', {}).values():
                if 'registered' in user_data:
                    reg_date = datetime.fromisoformat(user_data['registered']).date()
                    if reg_date == today:
                        count += 1
            
            return count
        except:
            return 0
    
    def _get_ai_learning_rate(self):
        """AI লার্নিং রেট"""
        try:
            if hasattr(self.core, 'ai_orchestrator'):
                brain = self.core.ai_orchestrator.brain
                if hasattr(brain, 'learning_log'):
                    # শেষ 24 ঘণ্টার লার্নিং কাউন্ট
                    day_ago = time.time() - 86400
                    recent_learnings = [
                        log for log in brain.learning_log
                        if datetime.fromisoformat(log.get('time', '2000-01-01')).timestamp() > day_ago
                    ]
                    return len(recent_learnings)
            return 0
        except:
            return 0
    
    def _get_ai_accuracy(self):
        """AI এক্যুরেসি"""
        try:
            if hasattr(self.core, 'ai_orchestrator'):
                patterns = self.core.ai_orchestrator.brain.patterns
                if patterns:
                    avg_confidence = sum(p.get('confidence', 0) for p in patterns.values()) / len(patterns)
                    return round(avg_confidence * 100, 2)
            return 0
        except:
            return 0
    
    def _get_avg_response_time(self):
        """গড় রেসপন্স টাইম"""
        # মক ডাটা - প্রকৃত ইমপ্লিমেন্টেশনে API কল টাইম ট্র্যাক করতে হবে
        return 0.5
    
    def _get_error_rate(self):
        """এরর রেট"""
        # মক ডাটা
        return 0.02
    
    def _get_throughput(self):
        """থ্রুপুট"""
        try:
            if hasattr(self.core, 'telegram_orchestrator'):
                total_messages = sum(
                    b.get('message_count', 0) 
                    for b in self.core.telegram_orchestrator.manager.user_bots.values()
                )
                
                if self._get_uptime() > 0:
                    return total_messages / (self._get_uptime() / 3600)  # প্রতি ঘণ্টায়
            return 0
        except:
            return 0
    
    def _get_revenue_today(self):
        """আজকের আয়"""
        # মক ডাটা - প্রকৃত পেমেন্ট সিস্টেমের সাথে ইন্টিগ্রেট করতে হবে
        return 0
    
    def _count_active_subscriptions(self):
        """অ্যাকটিভ সাবস্ক্রিপশন"""
        try:
            count = 0
            for user_id, credit in getattr(self.core, '_credits', {}).items():
                if credit > 0:
                    count += 1
            return count
        except:
            return 0
    
    def _check_alerts(self):
        """অ্যালার্ট চেক"""
        alerts = []
        
        # CPU উচ্চ ব্যবহার
        if self.metrics["system"]["cpu_usage"] > 80:
            alerts.append({
                "level": "warning",
                "type": "high_cpu",
                "message": f"CPU usage high: {self.metrics['system']['cpu_usage']}%",
                "time": datetime.now().isoformat()
            })
        
        # মেমোরি উচ্চ ব্যবহার
        if self.metrics["system"]["memory_usage"] > 85:
            alerts.append({
                "level": "warning",
                "type": "high_memory",
                "message": f"Memory usage high: {self.metrics['system']['memory_usage']}%",
                "time": datetime.now().isoformat()
            })
        
        # এরর রেট বেশি
        if self.metrics["performance"]["error_rate"] > 0.1:
            alerts.append({
                "level": "error",
                "type": "high_error_rate",
                "message": f"Error rate high: {self.metrics['performance']['error_rate']*100}%",
                "time": datetime.now().isoformat()
            })
        
        # AI এক্যুরেসি কম
        if self.metrics["ai"]["accuracy"] < 50:
            alerts.append({
                "level": "warning",
                "type": "low_ai_accuracy",
                "message": f"AI accuracy low: {self.metrics['ai']['accuracy']}%",
                "time": datetime.now().isoformat()
            })
        
        # নতুন অ্যালার্ট যোগ
        for alert in alerts:
            if alert not in self.alerts:
                self.alerts.append(alert)
                print(f"🚨 {alert['level'].upper()}: {alert['message']}")
        
        # পুরোনো অ্যালার্ট (24+ ঘণ্টা) রিমুভ
        current_time = time.time()
        self.alerts = [
            alert for alert in self.alerts
            if current_time - datetime.fromisoformat(alert['time']).timestamp() < 86400
        ]
    
    def _log_metrics(self):
        """মেট্রিক্স লগ"""
        log_file = Path("logs/metrics.log")
        log_file.parent.mkdir(exist_ok=True)
        
        with open(log_file, "a") as f:
            f.write(json.dumps(self.metrics) + "\n")
    
    def get_dashboard_data(self):
        """ড্যাশবোর্ড ডাটা"""
        return {
            "metrics": self.metrics,
            "alerts": self.alerts[-10:],  # শেষ 10 অ্যালার্ট
            "summary": self._get_summary()
        }
    
    def _get_summary(self):
        """সারাংশ"""
        return {
            "system_health": self._calculate_health_score(),
            "user_growth": self._calculate_growth_rate(),
            "ai_progress": self._calculate_ai_progress(),
            "financial_health": self._calculate_financial_health()
        }
    
    def _calculate_health_score(self):
        """হেল্থ স্কোর ক্যালকুলেট"""
        scores = []
        
        # CPU স্কোর
        cpu_usage = self.metrics["system"]["cpu_usage"]
        cpu_score = max(0, 100 - cpu_usage)
        scores.append(cpu_score)
        
        # মেমোরি স্কোর
        mem_usage = self.metrics["system"]["memory_usage"]
        mem_score = max(0, 100 - mem_usage)
        scores.append(mem_score)
        
        # এরর রেট স্কোর
        error_rate = self.metrics["performance"]["error_rate"]
        error_score = max(0, 100 - (error_rate * 1000))
        scores.append(error_score)
        
        # গড় স্কোর
        return sum(scores) / len(scores) if scores else 0
    
    def _calculate_growth_rate(self):
        """গ্রোথ রেট"""
        total_users = self.metrics["users"]["total"]
        new_today = self.metrics["users"]["new_today"]
        
        if total_users > 0:
            return (new_today / total_users) * 100
        return 0
    
    def _calculate_ai_progress(self):
        """AI প্রোগ্রেস"""
        patterns = self.metrics["ai"]["patterns"]
        accuracy = self.metrics["ai"]["accuracy"]
        
        # কমপ্লেক্স স্কোরিং (প্যাটার্ন কাউন্ট + এক্যুরেসি)
        return min(100, (patterns * 0.1) + (accuracy * 0.5))
    
    def _calculate_financial_health(self):
        """ফাইন্যান্সিয়াল হেল্থ"""
        active_subs = self.metrics["financial"]["active_subscriptions"]
        total_credits = self.metrics["financial"]["total_credits"]
        
        # সিম্পল স্কোরিং
        score = min(100, (active_subs * 10) + (total_credits * 0.1))
        return score
    
    def generate_report(self, report_type="daily"):
        """রিপোর্ট জেনারেট"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = Path(f"logs/report_{report_type}_{timestamp}.json")
        
        report_data = {
            "generated_at": datetime.now().isoformat(),
            "type": report_type,
            "metrics": self.metrics,
            "alerts": self.alerts,
            "summary": self._get_summary(),
            "recommendations": self._generate_recommendations()
        }
        
        with open(report_file, "w") as f:
            json.dump(report_data, f, indent=2)
        
        print(f"📄 Report generated: {report_file.name}")
        return report_file.name
    
    def _generate_recommendations(self):
        """রেকমেন্ডেশন জেনারেট"""
        recs = []
        
        # CPU রেকমেন্ডেশন
        if self.metrics["system"]["cpu_usage"] > 70:
            recs.append("Optimize plugin performance to reduce CPU usage")
        
        # মেমোরি রেকমেন্ডেশন
        if self.metrics["system"]["memory_usage"] > 75:
            recs.append("Consider implementing data cleanup for AI memory")
        
        # AI রেকমেন্ডেশন
        if self.metrics["ai"]["accuracy"] < 60:
            recs.append("Train AI with more diverse conversation patterns")
        
        # ইউজার গ্রোথ রেকমেন্ডেশন
        if self.metrics["users"]["new_today"] < 1:
            recs.append("Consider marketing/promotion for user growth")
        
        return recs
    
    def display_dashboard(self):
        """ড্যাশবোর্ড ডিসপ্লে"""
        data = self.get_dashboard_data()
        
        print("\n" + "="*60)
        print("📊 RANA BOT SYSTEM - LIVE DASHBOARD")
        print("="*60)
        
        print(f"\n⏰ Last Updated: {data['metrics']['timestamp'][11:19]}")
        
        print(f"\n🔧 SYSTEM HEALTH: {data['summary']['system_health']:.1f}/100")
        print(f"👥 USERS: {data['metrics']['users']['total']} total, {data['metrics']['users']['active']} active")
        print(f"🧠 AI: {data['metrics']['ai']['patterns']} patterns, {data['metrics']['ai']['accuracy']}% accuracy")
        print(f"🧩 PLUGINS: {data['metrics']['plugins']['loaded']}/{data['metrics']['plugins']['total']} loaded")
        
        print(f"\n💰 FINANCIAL:")
        print(f"  • Active Subscriptions: {data['metrics']['financial']['active_subscriptions']}")
        print(f"  • Total Credits: {data['metrics']['financial']['total_credits']}")
        
        print(f"\n⚡ PERFORMANCE:")
        print(f"  • CPU: {data['metrics']['system']['cpu_usage']}%")
        print(f"  • Memory: {data['metrics']['system']['memory_usage']}%")
        print(f"  • Error Rate: {data['metrics']['performance']['error_rate']*100:.1f}%")
        
        if data['alerts']:
            print(f"\n🚨 ACTIVE ALERTS ({len(data['alerts'])}):")
            for alert in data['alerts'][:3]:  # সর্বোচ্চ 3 টি
                print(f"  • [{alert['level'].upper()}] {alert['message']}")
        
        print("\n" + "="*60)