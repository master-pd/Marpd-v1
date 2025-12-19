"""
⏰ ADVANCED TASK SCHEDULER
Cron-like task scheduling
"""

import schedule
import time
import threading
from datetime import datetime
import json

class TaskScheduler:
    def __init__(self, core):
        self.core = core
        self.tasks = {}
        self.running = False
        self.scheduler_thread = None
        print("⏰ Task Scheduler Initialized")
    
    def add_task(self, task_id, schedule_time, callback, args=None, kwargs=None):
        """টাস্ক যোগ"""
        task = {
            "id": task_id,
            "schedule": schedule_time,
            "callback": callback,
            "args": args or (),
            "kwargs": kwargs or {},
            "created": datetime.now().isoformat(),
            "last_run": None,
            "run_count": 0,
            "enabled": True
        }
        
        self.tasks[task_id] = task
        
        # Schedule-এ রেজিস্টার
        if ":" in schedule_time:
            # Specific time (HH:MM)
            schedule.every().day.at(schedule_time).do(
                self._execute_task, task_id
            ).tag(task_id)
        elif schedule_time.startswith("every_"):
            # Interval-based
            parts = schedule_time.split("_")
            if len(parts) == 2:
                interval = int(parts[1])
                schedule.every(interval).seconds.do(
                    self._execute_task, task_id
                ).tag(task_id)
        
        return task_id
    
    def _execute_task(self, task_id):
        """টাস্ক এক্সিকিউট"""
        if task_id not in self.tasks:
            return
        
        task = self.tasks[task_id]
        
        if not task["enabled"]:
            return
        
        try:
            # ক্যালব্যাক কল
            result = task["callback"](*task["args"], **task["kwargs"])
            
            # টাস্ক আপডেট
            task["last_run"] = datetime.now().isoformat()
            task["run_count"] += 1
            
            # রেজাল্ট লগ
            self._log_task_result(task_id, result)
            
            return result
            
        except Exception as e:
            self._log_task_error(task_id, str(e))
    
    def _log_task_result(self, task_id, result):
        """টাস্ক রেজাল্ট লগ"""
        log_entry = {
            "task_id": task_id,
            "timestamp": datetime.now().isoformat(),
            "result": str(result)[:200] if result else None,
            "status": "success"
        }
        
        with open("task_logs.json", "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def _log_task_error(self, task_id, error):
        """টাস্ক এরর লগ"""
        log_entry = {
            "task_id": task_id,
            "timestamp": datetime.now().isoformat(),
            "error": error,
            "status": "failed"
        }
        
        with open("task_errors.json", "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def start(self):
        """স্লিপার শুরু"""
        if self.running:
            return
        
        self.running = True
        
        def run_scheduler():
            while self.running:
                schedule.run_pending()
                time.sleep(1)
        
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        print("✅ Task Scheduler Started")
    
    def stop(self):
        """স্টপ"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        print("🛑 Task Scheduler Stopped")
    
    def get_task_status(self, task_id=None):
        """টাস্ক স্ট্যাটাস"""
        if task_id:
            return self.tasks.get(task_id)
        else:
            return {
                "total_tasks": len(self.tasks),
                "active_tasks": len([t for t in self.tasks.values() if t["enabled"]]),
                "tasks": list(self.tasks.keys())
            }