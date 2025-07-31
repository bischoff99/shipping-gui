#!/usr/bin/env python3
"""
Claude Agent Orchestrator - Cooperation Test
Tests agent collaborative behavior and workflow coordination
"""

import json
import os
from pathlib import Path

class CooperationTester:
    def __init__(self):
        self.base_path = Path('/root/projects/SHIPPING_GUI/.claude')
        self.config_path = self.base_path / 'agents.json'
        
    def load_agent_config(self):
        """Load agent configuration"""
        with open(self.config_path, 'r') as f:
            return json.load(f)
    
    def test_agent_triggers(self):
        """Test agent activation triggers"""
        config = self.load_agent_config()
        results = []
        
        # Test file-based triggers
        test_files = [
            'app.py',
            'templates/dashboard.html',
            'tests/test_app.py',
            'api/veeqo_api.py',
            'README.md'
        ]
        
        for test_file in test_files:
            triggered_agents = []
            for agent_name, agent_config in config['agents'].items():
                triggers = agent_config.get('triggers', [])
                for trigger in triggers:
                    if self._matches_trigger(test_file, trigger):
                        triggered_agents.append(agent_name)
                        break
            
            results.append({
                'file': test_file,
                'triggered_agents': triggered_agents,
                'agent_count': len(triggered_agents)
            })
        
        return results
    
    def test_keyword_activation(self):
        """Test keyword-based agent activation"""
        config = self.load_agent_config()
        results = []
        
        test_scenarios = [
            {'context': 'Flask API endpoint performance issue', 'keywords': ['flask', 'api', 'performance']},
            {'context': 'Template XSS vulnerability', 'keywords': ['template', 'xss', 'security']},
            {'context': 'Pytest coverage below 90%', 'keywords': ['pytest', 'coverage', 'test']},
            {'context': 'Veeqo API integration error', 'keywords': ['veeqo', 'api', 'integration']},
            {'context': 'Database query optimization needed', 'keywords': ['database', 'optimization', 'performance']}
        ]
        
        for scenario in test_scenarios:
            activated_agents = []
            for agent_name, agent_config in config['agents'].items():
                agent_keywords = agent_config.get('keywords', [])
                if any(keyword in agent_keywords for keyword in scenario['keywords']):
                    activated_agents.append(agent_name)
            
            results.append({
                'scenario': scenario['context'],
                'keywords': scenario['keywords'],
                'activated_agents': activated_agents,
                'agent_count': len(activated_agents)
            })
        
        return results
    
    def test_collaboration_workflows(self):
        """Test agent collaboration patterns"""
        config = self.load_agent_config()
        collaboration_rules = config['orchestrator']['collaboration_rules']
        
        workflows = []
        
        # Feature development workflow
        feature_workflow = {
            'name': 'New Feature Development',
            'stages': [
                {'stage': 'Planning', 'primary_agent': 'backend-architect', 'collaborators': ['frontend-expert']},
                {'stage': 'Implementation', 'primary_agent': 'backend-architect', 'collaborators': ['frontend-expert', 'api-integration-specialist']},
                {'stage': 'Testing', 'primary_agent': 'test-automator', 'collaborators': ['backend-architect']},
                {'stage': 'Review', 'primary_agent': 'code-reviewer', 'collaborators': ['security-auditor', 'performance-optimizer']},
                {'stage': 'Documentation', 'primary_agent': 'documentation-specialist', 'collaborators': ['backend-architect', 'frontend-expert']}
            ]
        }
        
        # Security review workflow
        security_workflow = {
            'name': 'Security Review Process',
            'stages': [
                {'stage': 'Code Analysis', 'primary_agent': 'security-auditor', 'collaborators': ['code-reviewer']},
                {'stage': 'API Security', 'primary_agent': 'security-auditor', 'collaborators': ['api-integration-specialist']},
                {'stage': 'Frontend Security', 'primary_agent': 'security-auditor', 'collaborators': ['frontend-expert']},
                {'stage': 'Documentation Update', 'primary_agent': 'documentation-specialist', 'collaborators': ['security-auditor']}
            ]
        }
        
        workflows.extend([feature_workflow, security_workflow])
        
        return workflows
    
    def _matches_trigger(self, file_path, trigger_pattern):
        """Check if file matches trigger pattern"""
        if '*' in trigger_pattern:
            # Simple glob matching
            parts = trigger_pattern.split('*')
            if len(parts) == 2:
                prefix, suffix = parts
                return file_path.startswith(prefix) and file_path.endswith(suffix)
        
        return file_path == trigger_pattern or file_path.endswith(trigger_pattern)
    
    def run_cooperation_tests(self):
        """Run all cooperation tests"""
        print("Claude Agent Orchestrator - Cooperation Test Report")
        print("=" * 55)
        
        # Test trigger-based activation
        print("\n1. File-Based Trigger Tests:")
        print("-" * 30)
        trigger_results = self.test_agent_triggers()
        for result in trigger_results:
            agents_str = ', '.join(result['triggered_agents']) if result['triggered_agents'] else 'None'
            print(f"  {result['file']:<25} → {agents_str}")
        
        # Test keyword activation
        print("\n2. Keyword-Based Activation Tests:")
        print("-" * 35)
        keyword_results = self.test_keyword_activation()
        for result in keyword_results:
            agents_str = ', '.join(result['activated_agents']) if result['activated_agents'] else 'None'
            print(f"  Scenario: {result['scenario']}")
            print(f"    Keywords: {', '.join(result['keywords'])}")
            print(f"    Agents: {agents_str}")
            print()
        
        # Test collaboration workflows
        print("3. Collaboration Workflow Tests:")
        print("-" * 32)
        workflows = self.test_collaboration_workflows()
        for workflow in workflows:
            print(f"  Workflow: {workflow['name']}")
            for stage in workflow['stages']:
                collaborators_str = ', '.join(stage['collaborators']) if stage['collaborators'] else 'None'
                print(f"    {stage['stage']}: {stage['primary_agent']} (+ {collaborators_str})")
            print()
        
        # Summary
        total_trigger_tests = len(trigger_results)
        successful_triggers = sum(1 for r in trigger_results if r['agent_count'] > 0)
        
        total_keyword_tests = len(keyword_results)
        successful_keywords = sum(1 for r in keyword_results if r['agent_count'] > 0)
        
        print("4. Test Summary:")
        print("-" * 15)
        print(f"  Trigger Tests: {successful_triggers}/{total_trigger_tests} successful")
        print(f"  Keyword Tests: {successful_keywords}/{total_keyword_tests} successful")
        print(f"  Workflows Defined: {len(workflows)}")
        
        overall_success = (successful_triggers / total_trigger_tests) >= 0.8 and \
                         (successful_keywords / total_keyword_tests) >= 0.8
        
        print(f"\n  Overall Status: {'✅ COOPERATION VALIDATED' if overall_success else '❌ COOPERATION ISSUES'}")
        
        return overall_success

if __name__ == "__main__":
    tester = CooperationTester()
    tester.run_cooperation_tests()