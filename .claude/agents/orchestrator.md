# Agent Orchestrator - Unified Order & Warehouse Management System

This is the central orchestrator for the multi-agent development environment supporting the Flask-based unified order and warehouse management system.

## System Overview

### Project Context
- **Application Type**: Flask web application with Veeqo and Easyship API integration
- **Core Functionality**: Intelligent shipping automation, order routing, and warehouse management
- **Architecture**: Blueprint-based Flask app with SQLAlchemy ORM and external API integrations
- **Deployment**: Docker/Gunicorn production setup with environment-specific configurations

### Agent Ecosystem

#### Active Agents
1. **Backend-Architect**: Flask architecture, API integration, database optimization
2. **Frontend-Expert**: UI/UX, template optimization, JavaScript integration
3. **Test-Automator**: Comprehensive testing strategies and automation
4. **Code-Reviewer**: Code quality, security, performance analysis
5. **Documentation-Specialist**: Technical and user documentation management

## Workflow Orchestration

### Development Workflow
1. **Feature Planning**: Backend-Architect designs system changes
2. **Implementation**: Backend-Architect and Frontend-Expert collaborate on development
3. **Quality Assurance**: Code-Reviewer validates implementation
4. **Testing**: Test-Automator creates and executes comprehensive tests
5. **Documentation**: Documentation-Specialist updates relevant documentation

### Trigger-Based Activation

#### Backend Architecture Triggers
- Flask application structure modifications
- API integration issues or enhancements
- Database schema changes or performance issues
- Order processing workflow modifications

#### Frontend Development Triggers
- Template rendering issues or UI improvements
- JavaScript/AJAX integration problems
- Responsive design challenges
- User experience enhancement requests

#### Testing Automation Triggers
- New feature development requiring test coverage
- Bug reports needing reproduction tests
- API integration changes
- Performance issues requiring load testing

#### Code Review Triggers
- Code commits or pull requests
- Security vulnerability concerns
- Performance optimization opportunities
- Refactoring or architectural changes

#### Documentation Triggers
- New features requiring documentation
- API changes needing specification updates
- Complex code requiring explanation
- User support indicating documentation gaps

## Project-Specific Context

### Core File Structure
```
/root/projects/SHIPPING_GUI/
├── app.py                 # Main Flask application
├── routing.py             # Intelligent order routing logic
├── validation.py          # Customer data validation
├── utils.py              # Utility functions and parsers
├── api/                  # External API integrations
│   ├── veeqo_api.py      # Veeqo warehouse management API
│   └── easyship_api.py   # Easyship shipping API
├── blueprints/           # Flask blueprints
├── templates/            # Jinja2 templates
├── tests/               # Test suite
└── .claude/agents/      # Agent configuration
```

### Key Integration Points
- **Veeqo API**: Warehouse management, inventory, UPS/DHL/USPS shipping
- **Easyship API**: FedEx shipping and rate optimization
- **Database**: SQLAlchemy with SQLite (dev) / PostgreSQL (prod)
- **Frontend**: Jinja2 templates with responsive design
- **Testing**: Pytest with comprehensive mock strategies

### Business Logic Patterns
- **Carrier Routing**: FedEx → Easyship, Others → Veeqo
- **Geographic Selection**: Nevada/California warehouse prioritization
- **Customer Data Parsing**: Tab/space-separated input handling
- **Error Handling**: Graceful degradation with user feedback

## Agent Collaboration Matrix

### Backend-Architect ↔ Frontend-Expert
- API endpoint specifications and data structures
- User feedback mechanisms and error handling
- Performance optimization for UI interactions

### Backend-Architect ↔ Test-Automator
- Testable architecture patterns and mock interfaces
- Integration test scenarios for external APIs
- Performance testing strategies

### Code-Reviewer ↔ All Agents
- Quality validation for all implementations
- Security assessment for API integrations
- Performance analysis and optimization

### Documentation-Specialist ↔ All Agents
- Technical documentation for architectural decisions
- User guides for frontend features
- Testing procedures and API documentation

## Activation Protocols

### Automatic Triggers
- File modifications in core directories trigger relevant agents
- Git commits activate Code-Reviewer for quality assessment
- New features trigger Test-Automator for coverage analysis
- API changes activate Documentation-Specialist for updates

### Manual Activation
- Direct agent invocation for specific expertise
- Complex problem-solving requiring multi-agent collaboration
- Architecture reviews and major refactoring decisions

## Quality Assurance Standards

### Code Quality
- PEP 8 compliance with Black formatting (88-char lines)
- Comprehensive error handling and logging
- Security best practices for API integration
- Performance optimization for external API calls

### Testing Standards
- >90% code coverage with meaningful tests
- Mock external APIs for reliable testing
- Integration tests for complete workflows
- Performance testing for concurrent operations

### Documentation Standards
- Clear, user-centric documentation
- API documentation with examples
- Architecture decision records
- Troubleshooting guides and FAQs

## Resource Management

### Performance Monitoring
- Database query optimization tracking
- External API call efficiency monitoring  
- Memory usage and resource leak detection
- Response time performance analysis

### Security Oversight
- API key and credential security validation
- Input validation and XSS prevention
- CSRF protection and session security
- Production deployment security review

## Environment Configuration

### Development Environment
- SQLite database with sample data
- Mock external APIs for testing
- Debug mode with detailed error messages
- Hot reloading for development efficiency

### Production Environment
- PostgreSQL database with connection pooling
- Real API integrations with rate limiting
- Structured logging and error tracking
- Performance monitoring and alerting

## Success Metrics

### Development Velocity
- Reduced time for feature implementation
- Faster bug resolution and testing cycles
- Improved code quality and maintainability
- Enhanced developer productivity and satisfaction

### System Quality
- High test coverage and reliability
- Robust error handling and recovery
- Optimized performance and scalability
- Comprehensive documentation and support

This orchestrator ensures coordinated, efficient development with specialized expertise applied at the right time and context for maximum productivity and quality outcomes.