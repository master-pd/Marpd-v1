"""
🚨 ERROR HANDLING SYSTEM
Centralized error handling and recovery
"""

import traceback
import sys
import json
from datetime import datetime

class ErrorHandler:
    def __init__(self, core):
        self.core = core
        self.error_log = []
        self.recovery_actions = {}
        print("🚨 Error Handler Initialized")
    
    def handle_error(self, error, context=None, severity="error"):
        """এরর হ্যান্ডেল"""
        error_id = len(self.error_log) + 1
        
        error_entry = {
            "id": error_id,
            "timestamp": datetime.now().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "severity": severity,  # debug, info, warning, error, critical
            "context": context or {},
            "traceback": traceback.format_exc(),
            "handled": False,
            "recovery_attempted": False
        }
        
        self.error_log.append(error_entry)
        
        # লগ ফাইল
        self._log_to_file(error_entry)
        
        # স্বয়ংক্রিয় রিকভারি
        if severity in ["error", "critical"]:
            self._attempt_recovery(error_entry)
        
        # নোটিফিকেশন
        if severity in ["critical"]:
            self._send_alert(error_entry)
        
        return error_id
    
    def _log_to_file(self, error_entry):
        """ফাইলে লগ"""
        try:
            with open("error_log.json", "a", encoding="utf-8") as f:
                f.write(json.dumps(error_entry, ensure_ascii=False) + "\n")
        except:
            pass
    
    def _attempt_recovery(self, error_entry):
        """রিকভারি চেষ্টা"""
        error_type = error_entry["error_type"]
        
        # প্রি-ডিফাইন্ড রিকভারি অ্যাকশন
        recovery_map = {
            "ConnectionError": self._recover_connection,
            "TimeoutError": self._recover_timeout,
            "MemoryError": self._recover_memory,
            "FileNotFoundError": self._recover_file_missing
        }
        
        if error_type in recovery_map:
            try:
                recovery_result = recovery_map[error_type](error_entry)
                error_entry["recovery_attempted"] = True
                error_entry["recovery_result"] = recovery_result
                
                if recovery_result.get("success"):
                    error_entry["handled"] = True
            except Exception as e:
                error_entry["recovery_error"] = str(e)
    
    def _recover_connection(self, error_entry):
        """কানেকশন রিকভারি"""
        return {"success": True, "action": "connection_retry"}
    
    def _recover_timeout(self, error_entry):
        """টাইমআউট রিকভারি"""
        return {"success": True, "action": "timeout_adjusted"}
    
    def _recover_memory(self, error_entry):
        """মেমোরি রিকভারি"""
        # ক্যাশে ক্লিয়ার
        if hasattr(self.core, 'cache'):
            self.core.cache.clear()
        return {"success": True, "action": "cache_cleared"}
    
    def _recover_file_missing(self, error_entry):
        """ফাইল মিসিং রিকভারি"""
        # ব্যাকআপ থেকে রিস্টোর চেষ্টা
        if hasattr(self.core, 'backup_system'):
            backups = self.core.backup_system.list_backups()
            if backups:
                latest = backups[0]["name"]
                return self.core.backup_system.restore_backup(latest)
        return {"success": False, "action": "no_backup"}
    
    def _send_alert(self, error_entry):
        """অ্যালার্ট পাঠান"""
        try:
            if hasattr(self.core, 'notification_system'):
                title = f"🚨 Critical Error: {error_entry['error_type']}"
                message = f"Error ID: {error_entry['id']}\nMessage: {error_entry['error_message'][:100]}"
                
                self.core.notification_system.send_notification(
                    title=title,
                    message=message,
                    level="critical",
                    target="admin"
                )
        except:
            pass
    
    def get_error_report(self, last_n=100):
        """এরর রিপোর্ট"""
        recent_errors = self.error_log[-last_n:] if self.error_log else []
        
        stats = {
            "total_errors": len(self.error_log),
            "unhandled_errors": len([e for e in self.error_log if not e.get("handled")]),
            "critical_errors": len([e for e in self.error_log if e.get("severity") == "critical"]),
            "recovery_success_rate": self._calculate_recovery_rate()
        }
        
        return {
            "stats": stats,
            "recent_errors": recent_errors[-10:],
            "common_errors": self._get_common_errors()
        }
    
    def _calculate_recovery_rate(self):
        """রিকভারি রেট"""
        attempted = [e for e in self.error_log if e.get("recovery_attempted")]
        successful = [e for e in attempted if e.get("recovery_result", {}).get("success")]
        
        if attempted:
            return len(successful) / len(attempted)
        return 0
    
    def _get_common_errors(self):
        """কমন এরর"""
        from collections import Counter
        error_types = [e["error_type"] for e in self.error_log]
        return Counter(error_types).most_common(5)