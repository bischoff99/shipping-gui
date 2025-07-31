"""
MCP (Model Context Protocol) Integration Service

This module provides integration with all MCP servers for enhanced development
and AI-powered features in the SHIPPING_GUI application.
"""

import os
import subprocess
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import requests
from flask import current_app

logger = logging.getLogger(__name__)


class MCPServerStatus:
    """Represents the status of an MCP server"""
    
    def __init__(self, name: str, command: str, connected: bool = False, 
                 last_check: Optional[datetime] = None, error: Optional[str] = None):
        self.name = name
        self.command = command
        self.connected = connected
        self.last_check = last_check or datetime.now()
        self.error = error
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "command": self.command,
            "connected": self.connected,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "error": self.error
        }


class MCPIntegration:
    """Main MCP integration service"""
    
    def __init__(self):
        self.servers: Dict[str, MCPServerStatus] = {}
        self.last_health_check: Optional[datetime] = None
        self._initialize_servers()
    
    def _initialize_servers(self):
        """Initialize known MCP servers"""
        known_servers = {
            "python-debug": "Python debugging with mcp-pdb",
            "filesystem": "File operations in /root/projects", 
            "github": "Git and GitHub operations",
            "sequential-thinking": "Step-by-step planning assistance",
            "hf-spaces": "Hugging Face integration"
        }
        
        for name, description in known_servers.items():
            self.servers[name] = MCPServerStatus(
                name=name,
                command=description,
                connected=False
            )
    
    def check_claude_availability(self) -> bool:
        """Check if Claude Code CLI is available"""
        try:
            result = subprocess.run(
                ["claude", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            return False
    
    def get_mcp_server_list(self) -> List[Dict[str, Any]]:
        """Get list of MCP servers from Claude Code"""
        try:
            result = subprocess.run(
                ["claude", "mcp", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Parse the output to extract server information
                return self._parse_mcp_list_output(result.stdout)
            else:
                logger.error(f"Failed to get MCP server list: {result.stderr}")
                return []
                
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError) as e:
            logger.error(f"Error getting MCP server list: {e}")
            return []
    
    def _parse_mcp_list_output(self, output: str) -> List[Dict[str, Any]]:
        """Parse the output from 'claude mcp list' command"""
        servers = []
        lines = output.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if ':' in line and ('✓' in line or '✗' in line):
                # Parse line format: "server-name: command - ✓ Connected" or "✗ Failed"
                parts = line.split(':')
                if len(parts) >= 2:
                    name = parts[0].strip()
                    rest = ':'.join(parts[1:]).strip()
                    
                    connected = '✓' in rest
                    error = None if connected else "Connection failed"
                    
                    # Extract command (everything before the status indicator)
                    if ' - ✓' in rest:
                        command = rest.split(' - ✓')[0].strip()
                    elif ' - ✗' in rest:
                        command = rest.split(' - ✗')[0].strip()
                    else:
                        command = rest
                    
                    servers.append({
                        "name": name,
                        "command": command,
                        "connected": connected,
                        "error": error,
                        "last_check": datetime.now().isoformat()
                    })
        
        return servers
    
    def update_server_status(self):
        """Update the status of all MCP servers"""
        if not self.check_claude_availability():
            logger.warning("Claude Code CLI not available, cannot check MCP servers")
            return
        
        server_list = self.get_mcp_server_list()
        self.last_health_check = datetime.now()
        
        # Update server statuses
        for server_info in server_list:
            name = server_info["name"]
            if name in self.servers:
                self.servers[name].connected = server_info["connected"]
                self.servers[name].error = server_info.get("error")
                self.servers[name].last_check = datetime.now()
            else:
                # Add newly discovered server
                self.servers[name] = MCPServerStatus(
                    name=name,
                    command=server_info["command"],
                    connected=server_info["connected"],
                    error=server_info.get("error")
                )
    
    def get_server_status(self, server_name: str) -> Optional[MCPServerStatus]:
        """Get status of a specific MCP server"""
        return self.servers.get(server_name)
    
    def get_all_servers_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all MCP servers"""
        return {name: server.to_dict() for name, server in self.servers.items()}
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get overall health summary of MCP integration"""
        total_servers = len(self.servers)
        connected_servers = sum(1 for server in self.servers.values() if server.connected)
        
        return {
            "total_servers": total_servers,
            "connected_servers": connected_servers,
            "disconnected_servers": total_servers - connected_servers,
            "health_percentage": (connected_servers / total_servers * 100) if total_servers > 0 else 0,
            "last_check": self.last_health_check.isoformat() if self.last_health_check else None,
            "claude_available": self.check_claude_availability(),
            "status": "healthy" if connected_servers == total_servers else "degraded" if connected_servers > 0 else "down"
        }
    
    def execute_debug_session(self, script_path: str, breakpoint_line: Optional[int] = None) -> Dict[str, Any]:
        """Execute a debug session using python-debug MCP server"""
        if not self.servers.get("python-debug", MCPServerStatus("", "", False)).connected:
            return {"error": "Python debug MCP server not available"}
        
        try:
            # This would integrate with the actual MCP server
            # For now, return a placeholder response
            return {
                "status": "debug_session_started",
                "script": script_path,
                "breakpoint": breakpoint_line,
                "message": "Debug session would be started with mcp-pdb"
            }
        except Exception as e:
            logger.error(f"Error starting debug session: {e}")
            return {"error": str(e)}
    
    def get_ai_suggestions(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get AI-powered suggestions using Hugging Face MCP"""
        if not self.servers.get("hf-spaces", MCPServerStatus("", "", False)).connected:
            return {"error": "Hugging Face MCP server not available"}
        
        try:
            # This would integrate with the actual HF MCP server
            # For now, return a placeholder response
            return {
                "suggestions": [
                    "Consider adding input validation for customer data",
                    "Optimize database queries for better performance",
                    "Add retry logic for API calls"
                ],
                "confidence": 0.85,
                "model": "claude-3-sonnet",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting AI suggestions: {e}")
            return {"error": str(e)}
    
    def create_development_plan(self, task_description: str) -> Dict[str, Any]:
        """Create a development plan using sequential-thinking MCP"""
        if not self.servers.get("sequential-thinking", MCPServerStatus("", "", False)).connected:
            return {"error": "Sequential thinking MCP server not available"}
        
        try:
            # This would integrate with the actual sequential-thinking MCP server
            # For now, return a placeholder response
            steps = [
                "Analyze the current implementation",
                "Identify areas for improvement",
                "Design the solution architecture", 
                "Implement the changes incrementally",
                "Test the implementation",
                "Deploy and monitor"
            ]
            
            return {
                "task": task_description,
                "steps": steps,
                "estimated_time": "2-4 hours",
                "complexity": "medium",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error creating development plan: {e}")
            return {"error": str(e)}


# Global MCP integration instance
mcp_integration = MCPIntegration()


def get_mcp_integration() -> MCPIntegration:
    """Get the global MCP integration instance"""
    return mcp_integration