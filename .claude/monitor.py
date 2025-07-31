#!/usr/bin/env python3
"""
Claude Agent Orchestrator - Performance Monitor
Tracks agent effectiveness and system performance
"""

import json
import time
import os
from datetime import datetime

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

class AgentMonitor:
    def __init__(self):
        self.config_path = '/root/projects/SHIPPING_GUI/.claude/agents.json'
        self.metrics_path = '/root/projects/SHIPPING_GUI/.claude/metrics.json'
        
    def collect_system_metrics(self):
        """Collect system performance metrics"""
        metrics = {
            'timestamp': datetime.now().isoformat()
        }
        
        if PSUTIL_AVAILABLE:
            metrics.update({
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent,
                'process_count': len(psutil.pids())
            })
        else:
            # Basic system info without psutil
            metrics.update({
                'cpu_percent': 'N/A',
                'memory_percent': 'N/A', 
                'disk_usage': 'N/A',
                'process_count': 'N/A',
                'note': 'Install psutil for detailed system metrics'
            })
            
        return metrics
    
    def collect_agent_metrics(self):
        """Collect agent-specific metrics"""
        with open(self.config_path, 'r') as f:
            config = json.load(f)
        
        agent_metrics = {}
        for agent_name, agent_config in config['agents'].items():
            agent_path = f"/root/projects/SHIPPING_GUI/.claude/agents/{agent_config['file']}"
            if os.path.exists(agent_path):
                stat = os.stat(agent_path)
                agent_metrics[agent_name] = {
                    'last_modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'size_bytes': stat.st_size,
                    'active': agent_config.get('active', False),
                    'priority': agent_config.get('priority', 'medium')
                }
        
        return agent_metrics
    
    def save_metrics(self, metrics):
        """Save metrics to file"""
        try:
            with open(self.metrics_path, 'r') as f:
                all_metrics = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            all_metrics = []
        
        all_metrics.append(metrics)
        
        # Keep only last 1000 entries
        if len(all_metrics) > 1000:
            all_metrics = all_metrics[-1000:]
        
        with open(self.metrics_path, 'w') as f:
            json.dump(all_metrics, f, indent=2)
    
    def run_monitoring_check(self):
        """Run complete monitoring check"""
        metrics = {
            'system': self.collect_system_metrics(),
            'agents': self.collect_agent_metrics()
        }
        
        self.save_metrics(metrics)
        print(f"Monitoring check completed at {metrics['system']['timestamp']}")
        return metrics

if __name__ == "__main__":
    monitor = AgentMonitor()
    monitor.run_monitoring_check()
