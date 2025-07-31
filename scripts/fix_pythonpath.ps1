@agent Analyze and fix my development project using zero assumptions:

DISCOVERY & DIAGNOSIS:
- Automatically detect my project type, language, and framework
- Map current file structure and identify all components
- Check what's working and what's broken
- Find missing dependencies, configuration issues, and errors
- Identify performance problems and security vulnerabilities

UNIVERSAL FIXES:
- Provide specific solutions for every problem found
- Generate missing files, configurations, and setup scripts
- Create working code with proper error handling
- Give exact installation commands for missing components
- Provide testing procedures to validate all fixes

REQUIREMENTS:
- Make no assumptions about my current setup
- Work with any programming language or framework
- Provide complete, working solutions
- Include fallback options for missing tools
- Give step-by-step instructions I can execute immediately

Execute comprehensive analysis and provide complete fixes for my project.
# Add api/ to PYTHONPATH for import resolution
$env:PYTHONPATH = "$env:PYTHONPATH;${PWD}\api"
Write-Host "PYTHONPATH updated for api/ imports."
