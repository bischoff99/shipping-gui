#!/bin/bash

# Claude Agent Orchestrator - Productivity Setup Script
# Unified Order & Warehouse Management System

echo "Setting up Claude Agent Orchestrator productivity enhancements..."

# Create agent activation aliases
setup_aliases() {
    echo "Setting up agent activation aliases..."
    
    cat >> ~/.bashrc << 'EOF'

# Claude Agent Orchestrator Aliases
alias claude-backend="echo 'Activating Backend Architect Agent...' && cat /root/projects/SHIPPING_GUI/.claude/agents/backend-architect.md"
alias claude-frontend="echo 'Activating Frontend Expert Agent...' && cat /root/projects/SHIPPING_GUI/.claude/agents/frontend-expert.md"
alias claude-test="echo 'Activating Test Automator Agent...' && cat /root/projects/SHIPPING_GUI/.claude/agents/test-automator.md"
alias claude-review="echo 'Activating Code Reviewer Agent...' && cat /root/projects/SHIPPING_GUI/.claude/agents/code-reviewer.md"
alias claude-docs="echo 'Activating Documentation Specialist Agent...' && cat /root/projects/SHIPPING_GUI/.claude/agents/documentation-specialist.md"
alias claude-api="echo 'Activating API Integration Specialist Agent...' && cat /root/projects/SHIPPING_GUI/.claude/agents/api-integration-specialist.md"
alias claude-perf="echo 'Activating Performance Optimizer Agent...' && cat /root/projects/SHIPPING_GUI/.claude/agents/performance-optimizer.md"
alias claude-security="echo 'Activating Security Auditor Agent...' && cat /root/projects/SHIPPING_GUI/.claude/agents/security-auditor.md"

# Agent orchestrator commands
alias claude-status="echo 'Agent Status:' && ls -la /root/projects/SHIPPING_GUI/.claude/agents/ | grep -E '\\.md$'"
alias claude-help="echo 'Available Claude Agents:' && echo '  claude-backend    - Flask architecture and API integration' && echo '  claude-frontend   - UI/UX and template optimization' && echo '  claude-test       - Testing automation and coverage' && echo '  claude-review     - Code quality and security review' && echo '  claude-docs       - Documentation management' && echo '  claude-api        - External API integration' && echo '  claude-perf       - Performance optimization' && echo '  claude-security   - Security auditing and compliance'"

# Development shortcuts
alias app-start="cd /root/projects/SHIPPING_GUI && python app.py"
alias app-test="cd /root/projects/SHIPPING_GUI && pytest"
alias app-lint="cd /root/projects/SHIPPING_GUI && black . && flake8"
alias app-deps="cd /root/projects/SHIPPING_GUI && pip install -r requirements.txt"

EOF

    echo "Agent aliases added to ~/.bashrc"
}

# Setup git hooks for agent integration
setup_git_hooks() {
    echo "Setting up git hooks for agent integration..."
    
    # Pre-commit hook
    cat > /root/projects/SHIPPING_GUI/.git/hooks/pre-commit << 'EOF'
#!/bin/bash

echo "Running Claude Agent pre-commit checks..."

# Activate Code Reviewer Agent for quality checks
echo "🔍 Code Reviewer Agent: Analyzing code quality..."

# Check for Python style issues
if command -v black &> /dev/null; then
    black --check . || {
        echo "❌ Code formatting issues detected. Run 'black .' to fix."
        exit 1
    }
fi

# Check for security issues
if command -v bandit &> /dev/null; then
    bandit -r . -f json -o /tmp/bandit-report.json || {
        echo "⚠️ Security issues detected. Review bandit report."
    }
fi

# Check for test coverage
if [ -f "tests/" ]; then
    echo "🧪 Test Automator Agent: Validating test coverage..."
    pytest --cov=. --cov-report=term-missing --cov-fail-under=80 || {
        echo "❌ Test coverage below 80%. Add more tests."
        exit 1
    }
fi

echo "✅ Pre-commit checks passed"
EOF

    chmod +x /root/projects/SHIPPING_GUI/.git/hooks/pre-commit

    # Post-commit hook
    cat > /root/projects/SHIPPING_GUI/.git/hooks/post-commit << 'EOF'
#!/bin/bash

echo "Post-commit: Updating agent context..."

# Log commit for agent reference
COMMIT_HASH=$(git rev-parse HEAD)
COMMIT_MSG=$(git log -1 --pretty=%B)

cat >> /root/projects/SHIPPING_GUI/.claude/commit-log.txt << EOL
Commit: $COMMIT_HASH
Date: $(date)
Message: $COMMIT_MSG
---
EOL

echo "Agent context updated for commit $COMMIT_HASH"
EOF

    chmod +x /root/projects/SHIPPING_GUI/.git/hooks/post-commit
    
    echo "Git hooks configured successfully"
}

# Create monitoring script
setup_monitoring() {
    echo "Setting up agent performance monitoring..."
    
    cat > /root/projects/SHIPPING_GUI/.claude/monitor.py << 'EOF'
#!/usr/bin/env python3
"""
Claude Agent Orchestrator - Performance Monitor
Tracks agent effectiveness and system performance
"""

import json
import time
import psutil
import os
from datetime import datetime

class AgentMonitor:
    def __init__(self):
        self.config_path = '/root/projects/SHIPPING_GUI/.claude/agents.json'
        self.metrics_path = '/root/projects/SHIPPING_GUI/.claude/metrics.json'
        
    def collect_system_metrics(self):
        """Collect system performance metrics"""
        return {
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'process_count': len(psutil.pids())
        }
    
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
EOF

    chmod +x /root/projects/SHIPPING_GUI/.claude/monitor.py
    echo "Agent monitoring configured"
}

# Create agent validator
setup_validator() {
    echo "Setting up agent validation..."
    
    cat > /root/projects/SHIPPING_GUI/.claude/validate.py << 'EOF'
#!/usr/bin/env python3
"""
Claude Agent Orchestrator - Validation Script
Validates agent configuration and cooperative behavior
"""

import json
import os
import re
from pathlib import Path

class AgentValidator:
    def __init__(self):
        self.base_path = Path('/root/projects/SHIPPING_GUI/.claude')
        self.config_path = self.base_path / 'agents.json'
        
    def validate_config(self):
        """Validate agent configuration file"""
        if not self.config_path.exists():
            return False, "agents.json not found"
        
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON in agents.json: {e}"
        
        required_keys = ['version', 'project', 'agents', 'orchestrator']
        missing_keys = [key for key in required_keys if key not in config]
        if missing_keys:
            return False, f"Missing required keys: {missing_keys}"
        
        return True, "Configuration valid"
    
    def validate_agents(self):
        """Validate individual agent files"""
        with open(self.config_path, 'r') as f:
            config = json.load(f)
        
        results = []
        for agent_name, agent_config in config['agents'].items():
            agent_file = self.base_path / 'agents' / agent_config['file']
            
            if not agent_file.exists():
                results.append((agent_name, False, f"Agent file not found: {agent_file}"))
                continue
            
            # Validate agent file content
            with open(agent_file, 'r') as f:
                content = f.read()
            
            # Check for required sections
            required_sections = [
                'Core Responsibilities',
                'Technical Triggers', 
                'Collaboration Guidelines',
                'Response Format'
            ]
            
            missing_sections = []
            for section in required_sections:
                if section not in content:
                    missing_sections.append(section)
            
            if missing_sections:
                results.append((agent_name, False, f"Missing sections: {missing_sections}"))
            else:
                results.append((agent_name, True, "Agent valid"))
        
        return results
    
    def validate_project_integration(self):
        """Validate integration with project structure"""
        project_root = Path('/root/projects/SHIPPING_GUI')
        
        # Check for key project files
        key_files = [
            'app.py', 'routing.py', 'validation.py', 'utils.py',
            'api/veeqo_api.py', 'api/easyship_api.py',
            'templates', 'tests'
        ]
        
        missing_files = []
        for file_path in key_files:
            full_path = project_root / file_path
            if not full_path.exists():
                missing_files.append(str(file_path))
        
        if missing_files:
            return False, f"Missing project files: {missing_files}"
        
        return True, "Project integration valid"
    
    def run_validation(self):
        """Run complete validation"""
        print("Claude Agent Orchestrator - Validation Report")
        print("=" * 50)
        
        # Validate configuration
        config_valid, config_msg = self.validate_config()
        print(f"Configuration: {'✅' if config_valid else '❌'} {config_msg}")
        
        if not config_valid:
            return False
        
        # Validate agents
        print("\nAgent Validation:")
        agent_results = self.validate_agents()
        all_agents_valid = True
        
        for agent_name, valid, message in agent_results:
            print(f"  {agent_name}: {'✅' if valid else '❌'} {message}")
            if not valid:
                all_agents_valid = False
        
        # Validate project integration
        integration_valid, integration_msg = self.validate_project_integration()
        print(f"\nProject Integration: {'✅' if integration_valid else '❌'} {integration_msg}")
        
        # Overall result
        overall_valid = config_valid and all_agents_valid and integration_valid
        print(f"\nOverall Status: {'✅ VALID' if overall_valid else '❌ ISSUES FOUND'}")
        
        return overall_valid

if __name__ == "__main__":
    validator = AgentValidator()
    validator.run_validation()
EOF

    chmod +x /root/projects/SHIPPING_GUI/.claude/validate.py
    echo "Agent validator configured"
}

# Main setup execution
main() {
    setup_aliases
    setup_git_hooks
    setup_monitoring
    setup_validator
    
    echo ""
    echo "🎉 Claude Agent Orchestrator productivity setup complete!"
    echo ""
    echo "Available commands:"
    echo "  source ~/.bashrc          # Load new aliases"
    echo "  claude-help              # Show agent commands"
    echo "  claude-status            # Check agent status"
    echo "  ./.claude/validate.py    # Validate agent setup"
    echo "  ./.claude/monitor.py     # Run monitoring check"
    echo ""
}

main "$@"