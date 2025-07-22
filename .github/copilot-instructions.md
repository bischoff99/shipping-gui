<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Copilot Instructions for Unified Order & Warehouse Management System
- This is a Flask-based web application for order creation, routing, warehouse matching, and API sync between Veeqo and Easyship.
- Use modular code: separate API integration, routing, validation, and UI logic.
- Prioritize user input validation, error handling, and clear feedback in the UI.
- Use Flask Blueprints for modularity if the app grows.
- Use Jinja2 templates for all HTML rendering.
- Use requirements.txt for dependencies.
- All API keys and secrets should be loaded from environment variables or a config file, not hardcoded.
