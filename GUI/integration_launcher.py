#!/usr/bin/env python3
"""
Integration Launcher - Unified Warehouse Management
==================================================
This script provides a unified entry point to launch different components
of the warehouse management system based on user preference.
"""

import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os
from pathlib import Path
import webbrowser


class IntegrationLauncher:
    """Main launcher for all warehouse management components"""

    def __init__(self, root):
        self.root = root
        self.root.title("🚀 Warehouse Management System - Integration Launcher")
        self.root.geometry("900x700")
        self.root.configure(bg="#2c3e50")

        self.create_interface()

    def create_interface(self):
        """Create the main launcher interface"""

        # Main title
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=120)
        title_frame.pack(fill=tk.X, pady=20)
        title_frame.pack_propagate(False)

        main_title = tk.Label(
            title_frame,
            text="🏭 WAREHOUSE MANAGEMENT SYSTEM",
            font=("Arial", 24, "bold"),
            bg="#2c3e50",
            fg="white",
        )
        main_title.pack(pady=10)

        subtitle = tk.Label(
            title_frame,
            text="Unified Integration Platform - Choose Your Interface",
            font=("Arial", 12),
            bg="#2c3e50",
            fg="#ecf0f1",
        )
        subtitle.pack()

        # Main content area
        content_frame = tk.Frame(self.root, bg="#ecf0f1")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Create two columns
        left_column = tk.Frame(content_frame, bg="#ecf0f1")
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        right_column = tk.Frame(content_frame, bg="#ecf0f1")
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)

        # Left column - Primary interfaces
        self.create_section(
            left_column,
            "🎯 PRIMARY INTERFACES",
            [
                {
                    "title": "🏭 Unified System (Recommended)",
                    "desc": "Complete unified interface with all features integrated\n• Dashboard & monitoring\n• Warehouse management\n• Order routing\n• Excel reports\n• Web interface",
                    "action": self.launch_unified_system,
                    "color": "#27ae60",
                    "file": "unified_warehouse_system.py",
                },
                {
                    "title": "🖥️ Advanced Warehouse GUI",
                    "desc": "Desktop GUI with warehouse sync and order management\n• Real-time warehouse sync\n• Order creation\n• Monitoring dashboard\n• Settings management",
                    "action": self.launch_advanced_gui,
                    "color": "#3498db",
                    "file": "advanced_warehouse_gui.py",
                },
                {
                    "title": "🌐 Web Interface",
                    "desc": "Browser-based management interface\n• Real-time dashboard\n• API endpoints\n• Mobile-friendly\n• Remote access",
                    "action": self.launch_web_interface,
                    "color": "#9b59b6",
                    "file": "advanced_web_gui.py",
                },
            ],
        )

        # Right column - Specialized tools
        self.create_section(
            right_column,
            "🔧 SPECIALIZED TOOLS",
            [
                {
                    "title": "🚛 Enhanced Routing GUI",
                    "desc": "Advanced carrier routing with copy-paste support\n• Customer data parsing\n• Multiple input formats\n• Routing validation\n• History tracking",
                    "action": self.launch_enhanced_routing,
                    "color": "#e67e22",
                    "file": "enhanced_routing_gui.py",
                },
                {
                    "title": "📊 Excel Report Generator",
                    "desc": "Comprehensive Excel reporting tool\n• Multi-sheet reports\n• Order analysis\n• Country breakdown\n• Export capabilities",
                    "action": self.launch_excel_generator,
                    "color": "#1abc9c",
                    "file": "organized_orders_gui.py",
                },
                {
                    "title": "🎯 Basic Routing Tester",
                    "desc": "Simple routing test interface\n• Product-based testing\n• Preset scenarios\n• Routing analysis\n• Quick validation",
                    "action": self.launch_basic_routing,
                    "color": "#34495e",
                    "file": "carrier_routing_gui.py",
                },
            ],
        )

        # Bottom utilities section
        utilities_frame = tk.Frame(content_frame, bg="#ecf0f1")
        utilities_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=20)

        self.create_utilities_section(utilities_frame)

        # System status
        status_frame = tk.Frame(self.root, bg="#34495e", height=40)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)

        status_text = f"✅ System ready - {
            self.count_available_components()} components available"
        tk.Label(
            status_frame,
            text=status_text,
            bg="#34495e",
            fg="white",
            font=("Arial", 10),
        ).pack(pady=10)

    def create_section(self, parent, title, items):
        """Create a section with multiple interface options"""

        # Section title
        title_label = tk.Label(
            parent,
            text=title,
            font=("Arial", 14, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50",
        )
        title_label.pack(pady=(0, 15))

        # Create cards for each item
        for item in items:
            self.create_interface_card(parent, item)

    def create_interface_card(self, parent, item):
        """Create a card for each interface option"""

        # Check if file exists
        file_exists = os.path.exists(item["file"])

        # Card frame
        card_frame = tk.Frame(parent, bg="white", relief=tk.RAISED, bd=2)
        card_frame.pack(fill=tk.X, pady=10, padx=5)

        # Header
        header_frame = tk.Frame(card_frame, bg=item["color"], height=50)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        title_label = tk.Label(
            header_frame,
            text=item["title"],
            font=("Arial", 12, "bold"),
            bg=item["color"],
            fg="white",
        )
        title_label.pack(side=tk.LEFT, padx=15, pady=15)

        # Status indicator
        status = "✅ Ready" if file_exists else "❌ Missing"
        status_label = tk.Label(
            header_frame,
            text=status,
            font=("Arial", 10),
            bg=item["color"],
            fg="white",
        )
        status_label.pack(side=tk.RIGHT, padx=15, pady=15)

        # Description
        desc_frame = tk.Frame(card_frame, bg="white")
        desc_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        desc_label = tk.Label(
            desc_frame,
            text=item["desc"],
            font=("Arial", 10),
            bg="white",
            justify=tk.LEFT,
            anchor="nw",
        )
        desc_label.pack(fill=tk.BOTH, expand=True)

        # Launch button
        button_frame = tk.Frame(card_frame, bg="white")
        button_frame.pack(fill=tk.X, padx=15, pady=(0, 15))

        button_text = "🚀 Launch" if file_exists else "❌ Unavailable"
        button_state = tk.NORMAL if file_exists else tk.DISABLED

        launch_btn = tk.Button(
            button_frame,
            text=button_text,
            command=item["action"] if file_exists else None,
            bg=item["color"],
            fg="white",
            font=("Arial", 10, "bold"),
            state=button_state,
            relief=tk.FLAT,
            cursor="hand2" if file_exists else "arrow",
        )
        launch_btn.pack(side=tk.RIGHT)

        # File info
        file_label = tk.Label(
            button_frame,
            text=f"File: {item['file']}",
            font=("Arial", 8),
            bg="white",
            fg="#7f8c8d",
        )
        file_label.pack(side=tk.LEFT)

    def create_utilities_section(self, parent):
        """Create utilities section"""

        util_frame = tk.LabelFrame(
            parent,
            text="🛠️ UTILITIES & GUIDES",
            font=("Arial", 12, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50",
        )
        util_frame.pack(fill=tk.X, pady=10)

        # Utility buttons in grid
        buttons_frame = tk.Frame(util_frame, bg="#ecf0f1")
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)

        utilities = [
            ("📋 Validation Guide", self.launch_validation_guide, "#e74c3c"),
            ("🔧 Setup Guide", self.launch_setup_guide, "#f39c12"),
            ("📊 Final Sprint Guide", self.launch_sprint_guide, "#8e44ad"),
            ("🗂️ Open Folder", self.open_project_folder, "#16a085"),
            ("📝 View Logs", self.view_system_logs, "#2980b9"),
            ("❓ Help & About", self.show_help, "#95a5a6"),
        ]

        for i, (text, action, color) in enumerate(utilities):
            row, col = divmod(i, 3)
            btn = tk.Button(
                buttons_frame,
                text=text,
                command=action,
                bg=color,
                fg="white",
                font=("Arial", 9, "bold"),
                width=18,
                height=2,
                relief=tk.FLAT,
                cursor="hand2",
            )
            btn.grid(row=row, column=col, padx=5, pady=5)

        # Configure grid weights
        for i in range(3):
            buttons_frame.grid_columnconfigure(i, weight=1)

    def count_available_components(self):
        """Count available system components"""
        files = [
            "unified_warehouse_system.py",
            "advanced_warehouse_gui.py",
            "advanced_web_gui.py",
            "enhanced_routing_gui.py",
            "organized_orders_gui.py",
            "carrier_routing_gui.py",
        ]
        return sum(1 for f in files if os.path.exists(f))

    # Launch methods
    def launch_unified_system(self):
        """Launch the unified warehouse system"""
        self.launch_python_script(
            "unified_warehouse_system.py",
            "🏭 Launching Unified Warehouse System...",
        )

    def launch_advanced_gui(self):
        """Launch advanced warehouse GUI"""
        self.launch_python_script(
            "advanced_warehouse_gui.py",
            "🖥️ Launching Advanced Warehouse GUI...",
        )

    def launch_web_interface(self):
        """Launch web interface"""
        self.launch_python_script("advanced_web_gui.py", "🌐 Starting Web Interface...")
        # Also open browser after a delay
        self.root.after(3000, lambda: webbrowser.open("http://localhost:5000"))

    def launch_enhanced_routing(self):
        """Launch enhanced routing GUI"""
        self.launch_python_script(
            "enhanced_routing_gui.py",
            "🚛 Launching Enhanced Routing System...",
        )

    def launch_excel_generator(self):
        """Launch Excel report generator"""
        self.launch_python_script(
            "organized_orders_gui.py", "📊 Launching Excel Report Generator..."
        )

    def launch_basic_routing(self):
        """Launch basic routing tester"""
        self.launch_python_script(
            "carrier_routing_gui.py", "🎯 Launching Basic Routing Tester..."
        )

    def launch_python_script(self, script_name, message):
        """Launch a Python script"""
        if not os.path.exists(script_name):
            messagebox.showerror(
                "File Not Found", f"The file '{script_name}' was not found."
            )
            return

        try:
            # Show loading message
            messagebox.showinfo("Launching", message)

            # Launch script in new process
            subprocess.Popen(
                [sys.executable, script_name],
                cwd=os.getcwd(),
                creationflags=(
                    subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
                ),
            )

        except Exception as e:
            messagebox.showerror(
                "Launch Error", f"Error launching {script_name}:\n{str(e)}"
            )

    # Utility methods
    def launch_validation_guide(self):
        """Launch validation guide"""
        guides = [
            "corrected_validation_guide.py",
            "manual_validation_guide.py",
        ]
        for guide in guides:
            if os.path.exists(guide):
                self.launch_python_script(guide, "📋 Launching Validation Guide...")
                return
        messagebox.showwarning("Guide Not Found", "Validation guide files not found.")

    def launch_setup_guide(self):
        """Launch setup guide"""
        if os.path.exists("easyship_setup_guide.py"):
            self.launch_python_script(
                "easyship_setup_guide.py", "🔧 Launching Setup Guide..."
            )
        else:
            messagebox.showwarning("Guide Not Found", "Setup guide file not found.")

    def launch_sprint_guide(self):
        """Launch final sprint guide"""
        if os.path.exists("final_sprint_guide.py"):
            self.launch_python_script(
                "final_sprint_guide.py", "📊 Launching Final Sprint Guide..."
            )
        else:
            messagebox.showwarning(
                "Guide Not Found", "Final sprint guide file not found."
            )

    def open_project_folder(self):
        """Open project folder in file explorer"""
        try:
            if sys.platform == "win32":
                os.startfile(os.getcwd())
            elif sys.platform == "darwin":
                subprocess.run(["open", os.getcwd()])
            else:
                subprocess.run(["xdg-open", os.getcwd()])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder:\n{str(e)}")

    def view_system_logs(self):
        """View system logs"""
        log_window = tk.Toplevel(self.root)
        log_window.title("📝 System Information")
        log_window.geometry("800x600")

        log_text = tk.Text(log_window, font=("Consolas", 10))
        scrollbar = tk.Scrollbar(log_window, command=log_text.yview)
        log_text.config(yscrollcommand=scrollbar.set)

        log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Generate system info
        info = f"""
🏭 WAREHOUSE MANAGEMENT SYSTEM - SYSTEM INFORMATION
===================================================

📁 Project Directory: {os.getcwd()}
🐍 Python Version: {sys.version}
🖥️ Platform: {sys.platform}

📂 AVAILABLE FILES:
==================
"""

        # List all Python files
        for file in sorted(Path(".").glob("*.py")):
            size = file.stat().st_size
            info += f"✅ {file.name} ({size:,} bytes)\n"

        info += f"""

📊 COMPONENT STATUS:
===================
Total Components: {self.count_available_components()}

🏭 Unified System: {'✅ Available' if os.path.exists('unified_warehouse_system.py') else '❌ Missing'}
🖥️ Advanced GUI: {'✅ Available' if os.path.exists('advanced_warehouse_gui.py') else '❌ Missing'}
🌐 Web Interface: {'✅ Available' if os.path.exists('advanced_web_gui.py') else '❌ Missing'}
🚛 Enhanced Routing: {'✅ Available' if os.path.exists('enhanced_routing_gui.py') else '❌ Missing'}
📊 Excel Generator: {'✅ Available' if os.path.exists('organized_orders_gui.py') else '❌ Missing'}
🎯 Basic Routing: {'✅ Available' if os.path.exists('carrier_routing_gui.py') else '❌ Missing'}

📋 GUIDES & UTILITIES:
=====================
Validation Guide: {'✅ Available' if os.path.exists('corrected_validation_guide.py') else '❌ Missing'}
Setup Guide: {'✅ Available' if os.path.exists('easyship_setup_guide.py') else '❌ Missing'}
Sprint Guide: {'✅ Available' if os.path.exists('final_sprint_guide.py') else '❌ Missing'}

🔧 INTEGRATION STATUS:
=====================
All components are designed to work together through:
• Shared warehouse mapping files
• Common API configurations
• Unified data formats
• Cross-component compatibility
        """

        log_text.insert("1.0", info)
        log_text.config(state=tk.DISABLED)

    def show_help(self):
        """Show help and about information"""
        help_window = tk.Toplevel(self.root)
        help_window.title("❓ Help & About")
        help_window.geometry("700x500")
        help_window.configure(bg="#ecf0f1")

        # Title
        title_label = tk.Label(
            help_window,
            text="🏭 WAREHOUSE MANAGEMENT SYSTEM",
            font=("Arial", 18, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50",
        )
        title_label.pack(pady=20)

        # Help content
        help_text = tk.Text(
            help_window,
            font=("Arial", 11),
            bg="white",
            relief=tk.FLAT,
            wrap=tk.WORD,
        )
        help_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        help_content = """
🚀 GETTING STARTED:
==================

1. Choose your preferred interface from the launcher
2. For first-time users, start with the "Unified System"
3. Each component can run independently or together
4. All components share the same data and configurations

🎯 RECOMMENDED WORKFLOW:
=======================

1. Start with Unified System for general management
2. Use Enhanced Routing for advanced routing tests
3. Generate Excel reports for analysis
4. Use Web Interface for remote access

🔧 TROUBLESHOOTING:
==================

• If a component won't launch, check the file exists
• Ensure all required dependencies are installed
• Check Python version compatibility (3.7+)
• View system logs for detailed information

📞 SUPPORT:
==========

For technical support or questions:
• Check the system logs for error details
• Ensure all API keys are properly configured
• Verify network connectivity for API calls

🏗️ ARCHITECTURE:
================

This unified system combines multiple approaches:
• Desktop GUI applications (Tkinter)
• Web interface (Flask)
• Carrier routing logic
• Excel report generation
• API integrations (Veeqo, Easyship)
• Real-time synchronization

Each component is designed to work independently while
sharing common data structures and configurations.
        """

        help_text.insert("1.0", help_content)
        help_text.config(state=tk.DISABLED)


def main():
    """Launch the integration system"""
    root = tk.Tk()
    IntegrationLauncher(root)
    root.mainloop()


if __name__ == "__main__":
    main()
