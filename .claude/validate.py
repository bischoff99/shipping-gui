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
