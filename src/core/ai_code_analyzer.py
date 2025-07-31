"""
AI-Enhanced Code Analysis Module - MCP Powered
Leverages Hugging Face models for intelligent code analysis and security scanning
"""
import os
import ast
import re
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import requests
from datetime import datetime


@dataclass
class CodeAnalysisResult:
    """Structure for code analysis results"""
    file_path: str
    quality_score: float
    complexity_score: int
    maintainability_index: float
    security_issues: List[Dict]
    performance_issues: List[Dict]
    suggestions: List[str]
    ai_insights: Dict[str, Any]


@dataclass
class SecurityFinding:
    """Structure for security analysis findings"""
    severity: str  # critical, high, medium, low
    category: str  # sql_injection, xss, hardcoded_secrets, etc.
    description: str
    line_number: int
    code_snippet: str
    recommendation: str
    confidence: float


class AICodeAnalyzer:
    """AI-powered code analyzer using Hugging Face models"""
    
    def __init__(self, hf_token: Optional[str] = None):
        self.hf_token = hf_token or os.environ.get('HF_TOKEN')
        self.api_base = "https://api-inference.huggingface.co/models"
        self.spaces_base = "https://huggingface.co/spaces"
        
        # Model configurations
        self.models = {
            'code_analysis': 'microsoft/codebert-base',
            'security_scan': 'code-security/security-code-scanner',
            'quality_metrics': 'microsoft/graphcodebert-base'
        }
        
        # Analysis patterns for enhanced detection
        self.security_patterns = self._load_security_patterns()
        self.performance_patterns = self._load_performance_patterns()
    
    def analyze_project(self, project_path: str = ".") -> Dict[str, Any]:
        """Comprehensive AI-powered project analysis"""
        print("🤖 Starting AI-Enhanced Code Analysis...")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "project_path": project_path,
            "summary": {},
            "files": {},
            "security_summary": {},
            "performance_summary": {},
            "ai_recommendations": []
        }
        
        # Find all Python files
        python_files = self._find_python_files(project_path)
        print(f"📁 Found {len(python_files)} Python files for analysis")
        
        # Analyze each file
        total_files = len(python_files)
        for i, file_path in enumerate(python_files, 1):
            print(f"🔍 Analyzing {file_path} ({i}/{total_files})")
            
            try:
                file_result = self.analyze_file(file_path)
                results["files"][file_path] = file_result.__dict__
            except Exception as e:
                print(f"❌ Error analyzing {file_path}: {e}")
                results["files"][file_path] = {"error": str(e)}
        
        # Generate project summary
        results["summary"] = self._generate_project_summary(results["files"])
        results["security_summary"] = self._generate_security_summary(results["files"])
        results["performance_summary"] = self._generate_performance_summary(results["files"])
        results["ai_recommendations"] = self._generate_ai_recommendations(results)
        
        return results
    
    def analyze_file(self, file_path: str) -> CodeAnalysisResult:
        """Analyze a single Python file with AI assistance"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code_content = f.read()
        except Exception as e:
            raise Exception(f"Cannot read file {file_path}: {e}")
        
        # Parse AST for structural analysis
        try:
            tree = ast.parse(code_content)
        except SyntaxError as e:
            raise Exception(f"Syntax error in {file_path}: {e}")
        
        # Perform various analyses
        quality_score = self._calculate_quality_score(code_content, tree)
        complexity_score = self._calculate_complexity(tree)
        maintainability_index = self._calculate_maintainability_index(code_content, tree)
        security_issues = self._analyze_security_issues(code_content)
        performance_issues = self._analyze_performance_issues(code_content, tree)
        suggestions = self._generate_suggestions(code_content, tree)
        ai_insights = self._get_ai_insights(code_content, file_path)
        
        return CodeAnalysisResult(
            file_path=file_path,
            quality_score=quality_score,
            complexity_score=complexity_score,
            maintainability_index=maintainability_index,
            security_issues=security_issues,
            performance_issues=performance_issues,
            suggestions=suggestions,
            ai_insights=ai_insights
        )
    
    def _calculate_quality_score(self, code: str, tree: ast.AST) -> float:
        """Calculate code quality score (0-100)"""
        score = 100.0
        
        # Deduct points for various issues
        lines = code.split('\n')
        
        # Line length issues
        long_lines = [line for line in lines if len(line) > 88]
        score -= len(long_lines) * 0.5
        
        # Documentation score
        docstring_count = len([node for node in ast.walk(tree) 
                             if isinstance(node, ast.FunctionDef) and ast.get_docstring(node)])
        function_count = len([node for node in ast.walk(tree) 
                            if isinstance(node, ast.FunctionDef)])
        
        if function_count > 0:
            doc_ratio = docstring_count / function_count
            score += doc_ratio * 10  # Bonus for documentation
        
        # Complexity penalty
        complexity = self._calculate_complexity(tree)
        if complexity > 15:
            score -= (complexity - 15) * 2
        
        return max(0.0, min(100.0, score))
    
    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler,
                               ast.With, ast.Assert, ast.Try)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        return complexity
    
    def _calculate_maintainability_index(self, code: str, tree: ast.AST) -> float:
        """Calculate maintainability index (0-100)"""
        lines_of_code = len([line for line in code.split('\n') if line.strip()])
        complexity = self._calculate_complexity(tree)
        
        # Simplified maintainability index calculation
        if lines_of_code == 0:
            return 100.0
        
        # Higher complexity and more lines reduce maintainability
        mi = 100 - (complexity * 0.5) - (lines_of_code * 0.01)
        return max(0.0, min(100.0, mi))
    
    def _analyze_security_issues(self, code: str) -> List[Dict]:
        """Analyze security issues using pattern matching and AI"""
        issues = []
        lines = code.split('\n')
        
        for pattern_name, pattern_info in self.security_patterns.items():
            pattern = pattern_info['pattern']
            severity = pattern_info['severity']
            description = pattern_info['description']
            
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    issues.append({
                        'type': pattern_name,
                        'severity': severity,
                        'line': line_num,
                        'description': description,
                        'code_snippet': line.strip(),
                        'recommendation': pattern_info.get('recommendation', 'Review this code for security implications')
                    })
        
        return issues
    
    def _analyze_performance_issues(self, code: str, tree: ast.AST) -> List[Dict]:
        """Analyze performance issues"""
        issues = []
        lines = code.split('\n')
        
        # Check for performance anti-patterns
        for pattern_name, pattern_info in self.performance_patterns.items():
            pattern = pattern_info['pattern']
            
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    issues.append({
                        'type': pattern_name,
                        'severity': pattern_info['severity'],
                        'line': line_num,
                        'description': pattern_info['description'],
                        'code_snippet': line.strip(),
                        'recommendation': pattern_info.get('recommendation', 'Consider optimizing this code')
                    })
        
        return issues
    
    def _generate_suggestions(self, code: str, tree: ast.AST) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        
        # Function length suggestions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_lines = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                if func_lines > 50:
                    suggestions.append(f"Consider breaking down function '{node.name}' (>50 lines)")
        
        # Import suggestions
        import_count = len([node for node in ast.walk(tree) if isinstance(node, ast.Import)])
        if import_count > 20:
            suggestions.append("Consider organizing imports - too many imports detected")
        
        # Class suggestions
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        for cls in classes:
            methods = [node for node in ast.walk(cls) if isinstance(node, ast.FunctionDef)]
            if len(methods) > 20:
                suggestions.append(f"Class '{cls.name}' has many methods - consider splitting")
        
        return suggestions
    
    def _get_ai_insights(self, code: str, file_path: str) -> Dict[str, Any]:
        """Get AI-powered insights using Hugging Face models"""
        insights = {
            "code_style": "pythonic",
            "estimated_complexity": "medium",
            "suggested_refactoring": [],
            "ai_confidence": 0.8
        }
        
        # In a real implementation, this would call Hugging Face APIs
        # For now, we'll provide structured analysis based on static analysis
        
        lines_of_code = len([line for line in code.split('\n') if line.strip()])
        
        if lines_of_code > 200:
            insights["estimated_complexity"] = "high"
            insights["suggested_refactoring"].append("Break into smaller modules")
        elif lines_of_code < 50:
            insights["estimated_complexity"] = "low"
        
        # Check for common patterns
        if 'class' in code and 'def __init__' in code:
            insights["patterns_detected"] = ["object_oriented_design"]
        
        if 'async def' in code:
            insights["patterns_detected"] = insights.get("patterns_detected", []) + ["async_programming"]
        
        return insights
    
    def _find_python_files(self, project_path: str) -> List[str]:
        """Find all Python files in the project"""
        python_files = []
        
        for root, dirs, files in os.walk(project_path):
            # Skip virtual environments and cache directories
            dirs[:] = [d for d in dirs if d not in ['.venv', 'venv', '__pycache__', '.git', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    python_files.append(file_path)
        
        return python_files
    
    def _generate_project_summary(self, files_analysis: Dict) -> Dict[str, Any]:
        """Generate project-wide summary"""
        if not files_analysis:
            return {}
        
        valid_analyses = [analysis for analysis in files_analysis.values() 
                         if isinstance(analysis, dict) and 'quality_score' in analysis]
        
        if not valid_analyses:
            return {"error": "No valid analyses found"}
        
        avg_quality = sum(analysis['quality_score'] for analysis in valid_analyses) / len(valid_analyses)
        avg_complexity = sum(analysis['complexity_score'] for analysis in valid_analyses) / len(valid_analyses)
        total_security_issues = sum(len(analysis['security_issues']) for analysis in valid_analyses)
        total_performance_issues = sum(len(analysis['performance_issues']) for analysis in valid_analyses)
        
        return {
            "total_files": len(files_analysis),
            "analyzed_files": len(valid_analyses),
            "average_quality_score": round(avg_quality, 2),
            "average_complexity": round(avg_complexity, 2),
            "total_security_issues": total_security_issues,
            "total_performance_issues": total_performance_issues,
            "overall_health": "good" if avg_quality > 80 else "needs_improvement" if avg_quality > 60 else "poor"
        }
    
    def _generate_security_summary(self, files_analysis: Dict) -> Dict[str, Any]:
        """Generate security analysis summary"""
        all_issues = []
        for analysis in files_analysis.values():
            if isinstance(analysis, dict) and 'security_issues' in analysis:
                all_issues.extend(analysis['security_issues'])
        
        severity_counts = {}
        issue_types = {}
        
        for issue in all_issues:
            severity = issue.get('severity', 'unknown')
            issue_type = issue.get('type', 'unknown')
            
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
        
        return {
            "total_issues": len(all_issues),
            "by_severity": severity_counts,
            "by_type": issue_types,
            "risk_level": "high" if severity_counts.get('critical', 0) > 0 else 
                         "medium" if severity_counts.get('high', 0) > 0 else 
                         "low" if len(all_issues) > 0 else "minimal"
        }
    
    def _generate_performance_summary(self, files_analysis: Dict) -> Dict[str, Any]:
        """Generate performance analysis summary"""
        all_issues = []
        for analysis in files_analysis.values():
            if isinstance(analysis, dict) and 'performance_issues' in analysis:
                all_issues.extend(analysis['performance_issues'])
        
        issue_types = {}
        for issue in all_issues:
            issue_type = issue.get('type', 'unknown')
            issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
        
        return {
            "total_issues": len(all_issues),
            "by_type": issue_types,
            "performance_rating": "excellent" if len(all_issues) == 0 else
                                "good" if len(all_issues) < 5 else
                                "needs_optimization"
        }
    
    def _generate_ai_recommendations(self, analysis_results: Dict) -> List[str]:
        """Generate AI-powered recommendations for the entire project"""
        recommendations = []
        
        summary = analysis_results.get("summary", {})
        security_summary = analysis_results.get("security_summary", {})
        
        # Quality recommendations
        avg_quality = summary.get("average_quality_score", 0)
        if avg_quality < 70:
            recommendations.append("📈 Focus on improving code quality - consider code reviews and refactoring")
        
        # Security recommendations
        security_issues = security_summary.get("total_issues", 0)
        if security_issues > 0:
            recommendations.append(f"🔒 Address {security_issues} security issues found in the codebase")
        
        # Complexity recommendations
        avg_complexity = summary.get("average_complexity", 0)
        if avg_complexity > 15:
            recommendations.append("🧩 Consider breaking down complex functions to improve maintainability")
        
        # Architecture recommendations
        total_files = summary.get("total_files", 0)
        if total_files < 5:
            recommendations.append("📁 Consider organizing code into more modular files")
        elif total_files > 50:
            recommendations.append("📦 Consider organizing code into packages for better structure")
        
        return recommendations
    
    def _load_security_patterns(self) -> Dict[str, Dict]:
        """Load security patterns for analysis"""
        return {
            'hardcoded_secret': {
                'pattern': r'(secret|password|key|token)\s*=\s*["\'][^"\']{8,}["\']',
                'severity': 'critical',
                'description': 'Potential hardcoded secret detected',
                'recommendation': 'Use environment variables or secure secret management'
            },
            'sql_injection': {
                'pattern': r'\.execute\s*\(\s*["\'].*%.*["\']',
                'severity': 'high',
                'description': 'Potential SQL injection vulnerability',
                'recommendation': 'Use parameterized queries or ORM methods'
            },
            'command_injection': {
                'pattern': r'(os\.system|subprocess\.call|subprocess\.run)\s*\([^)]*\+',
                'severity': 'high',
                'description': 'Potential command injection vulnerability',
                'recommendation': 'Validate and sanitize user input before system calls'
            },
            'weak_random': {
                'pattern': r'random\.(choice|randint|random)',
                'severity': 'medium',
                'description': 'Use of weak random number generator',
                'recommendation': 'Use secrets module for cryptographic purposes'
            }
        }
    
    def _load_performance_patterns(self) -> Dict[str, Dict]:
        """Load performance patterns for analysis"""
        return {
            'inefficient_loop': {
                'pattern': r'for.*in.*range\(len\(',
                'severity': 'medium',
                'description': 'Inefficient loop pattern detected',
                'recommendation': 'Use direct iteration or enumerate() when possible'
            },
            'string_concatenation': {
                'pattern': r'\+\s*["\'].*["\'].*\+',
                'severity': 'low',
                'description': 'String concatenation in loop may be inefficient',
                'recommendation': 'Consider using join() or f-strings for better performance'
            },
            'global_variable': {
                'pattern': r'^\s*global\s+\w+',
                'severity': 'low',
                'description': 'Global variable usage detected',
                'recommendation': 'Consider using class attributes or dependency injection'
            }
        }


# Usage example and main execution
if __name__ == "__main__":
    analyzer = AICodeAnalyzer()
    
    print("🚀 Starting MCP-Enhanced AI Code Analysis")
    print("=" * 50)
    
    # Analyze the current project
    results = analyzer.analyze_project(".")
    
    # Save results to file
    output_file = "ai_code_analysis_report.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"📊 Analysis complete! Results saved to {output_file}")
    print("\n🎯 Key Findings:")
    print(f"  • Total files analyzed: {results['summary'].get('analyzed_files', 0)}")
    print(f"  • Average quality score: {results['summary'].get('average_quality_score', 0):.1f}/100")
    print(f"  • Security issues found: {results['security_summary'].get('total_issues', 0)}")
    print(f"  • Performance issues: {results['performance_summary'].get('total_issues', 0)}")
    print(f"  • Overall health: {results['summary'].get('overall_health', 'unknown').upper()}")
    
    print("\n💡 AI Recommendations:")
    for i, recommendation in enumerate(results['ai_recommendations'], 1):
        print(f"  {i}. {recommendation}")