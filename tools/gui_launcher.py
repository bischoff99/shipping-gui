#!/usr/bin/env python3
"""
GUI Launcher for Unified Shipping Management System
Provides both desktop and web interface options
"""

import tkinter as tk
from tkinter import messagebox
import threading
import webbrowser
import subprocess
import sys
import os
from datetime import datetime
import time


class ShippingGUILauncher:
    """Main launcher for the shipping management system"""

    def __init__(self, root):
        self.root = root
        self.root.title("🏭 Shipping Management System Launcher")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")

        # Status tracking
        self.web_server_process = None
        self.web_server_running = False

        self.create_interface()

    def create_interface(self):
        """Create the main launcher interface"""

        # Header
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=100)
        header_frame.pack(fill=tk.X, padx=5, pady=5)
        header_frame.pack_propagate(False)

        title_label = tk.Label(
            header_frame,
            text="🏭 UNIFIED SHIPPING MANAGEMENT SYSTEM",
            font=("Arial", 18, "bold"),
            bg="#2c3e50",
            fg="white",
        )
        title_label.pack(expand=True)

        subtitle_label = tk.Label(
            header_frame,
            text="Choose your interface: Desktop GUI or Web Dashboard",
            font=("Arial", 12),
            bg="#2c3e50",
            fg="#ecf0f1",
        )
        subtitle_label.pack()

        # Main content area
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Interface options
        self.create_interface_options(main_frame)

        # Status section
        self.create_status_section(main_frame)

        # System info
        self.create_system_info(main_frame)

    def create_interface_options(self, parent):
        """Create interface selection options"""
        options_frame = tk.LabelFrame(
            parent, text="🖥️ Interface Options", font=("Arial", 14, "bold")
        )
        options_frame.pack(fill=tk.X, pady=(0, 20))

        # Web Interface Option
        web_frame = tk.Frame(options_frame, bg="white", relief=tk.RAISED, bd=2)
        web_frame.pack(fill=tk.X, padx=10, pady=10)

        web_title = tk.Label(
            web_frame,
            text="🌐 Web Dashboard (Recommended)",
            font=("Arial", 16, "bold"),
            bg="white",
            fg="#2980b9",
        )
        web_title.pack(pady=10)

        web_desc = tk.Label(
            web_frame,
            text="Modern web interface with real-time dashboard,\nsmart routing, and comprehensive order management",
            font=("Arial", 11),
            bg="white",
            fg="#555",
        )
        web_desc.pack(pady=(0, 10))

        web_buttons_frame = tk.Frame(web_frame, bg="white")
        web_buttons_frame.pack(pady=10)

        tk.Button(
            web_buttons_frame,
            text="🚀 Launch Web Interface",
            command=self.launch_web_interface,
            bg="#3498db",
            fg="white",
            font=("Arial", 12, "bold"),
            width=20,
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            web_buttons_frame,
            text="🌐 Open in Browser",
            command=self.open_web_browser,
            bg="#2980b9",
            fg="white",
            font=("Arial", 12, "bold"),
            width=20,
        ).pack(side=tk.LEFT, padx=5)

        # Desktop Interface Option
        desktop_frame = tk.Frame(options_frame, bg="white", relief=tk.RAISED, bd=2)
        desktop_frame.pack(fill=tk.X, padx=10, pady=10)

        desktop_title = tk.Label(
            desktop_frame,
            text="🖥️ Desktop GUI",
            font=("Arial", 16, "bold"),
            bg="white",
            fg="#27ae60",
        )
        desktop_title.pack(pady=10)

        desktop_desc = tk.Label(
            desktop_frame,
            text="Traditional desktop interface with advanced features,\nwarehouse management, and Excel reporting",
            font=("Arial", 11),
            bg="white",
            fg="#555",
        )
        desktop_desc.pack(pady=(0, 10))

        desktop_buttons_frame = tk.Frame(desktop_frame, bg="white")
        desktop_buttons_frame.pack(pady=10)

        tk.Button(
            desktop_buttons_frame,
            text="🏭 Launch Desktop GUI",
            command=self.launch_desktop_gui,
            bg="#27ae60",
            fg="white",
            font=("Arial", 12, "bold"),
            width=20,
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            desktop_buttons_frame,
            text="⚙️ Advanced Features",
            command=self.show_advanced_features,
            bg="#16a085",
            fg="white",
            font=("Arial", 12, "bold"),
            width=20,
        ).pack(side=tk.LEFT, padx=5)

    def create_status_section(self, parent):
        """Create system status section"""
        status_frame = tk.LabelFrame(
            parent, text="📊 System Status", font=("Arial", 14, "bold")
        )
        status_frame.pack(fill=tk.X, pady=(0, 20))

        # Status indicators
        indicators_frame = tk.Frame(status_frame)
        indicators_frame.pack(fill=tk.X, padx=10, pady=10)

        # Web server status
        self.web_status_var = tk.StringVar(value="🔴 Web Server: Stopped")
        self.web_status_label = tk.Label(
            indicators_frame,
            textvariable=self.web_status_var,
            font=("Arial", 11),
            anchor="w",
        )
        self.web_status_label.pack(fill=tk.X, pady=2)

        # API status (placeholder)
        api_status_var = tk.StringVar(value="🟡 APIs: Ready for connection")
        tk.Label(
            indicators_frame,
            textvariable=api_status_var,
            font=("Arial", 11),
            anchor="w",
        ).pack(fill=tk.X, pady=2)

        # Database status
        db_status_var = tk.StringVar(value="🟢 Database: Connected")
        tk.Label(
            indicators_frame,
            textvariable=db_status_var,
            font=("Arial", 11),
            anchor="w",
        ).pack(fill=tk.X, pady=2)

    def create_system_info(self, parent):
        """Create system information section"""
        info_frame = tk.LabelFrame(
            parent, text="ℹ️ System Information", font=("Arial", 14, "bold")
        )
        info_frame.pack(fill=tk.BOTH, expand=True)

        info_text = tk.Text(
            info_frame,
            height=8,
            wrap=tk.WORD,
            font=("Consolas", 9),
            bg="#f8f9fa",
        )
        info_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        system_info = f"""
🏭 UNIFIED SHIPPING MANAGEMENT SYSTEM
{'=' * 50}

📍 Project Location: {os.getcwd()}
🐍 Python Version: {sys.version.split()[0]}
🕒 Launch Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🌐 Web Interface: http://localhost:5000/unified
📦 Order Creation: http://localhost:5000/create_order
🔗 API Endpoints: http://localhost:5000/api/*

🏭 Features Available:
• Smart order routing and warehouse selection
• Real-time API synchronization (Veeqo, Easyship, FedEx)
• Advanced customer data parsing
• Comprehensive dashboard and analytics
• Excel reporting and data export
• Desktop and web interface options

📧 For support or questions, check the project documentation.
        """

        info_text.insert("1.0", system_info.strip())
        info_text.config(state=tk.DISABLED)

    def launch_web_interface(self):
        """Launch the Flask web interface"""

        def start_server():
            try:
                self.web_status_var.set("🟡 Web Server: Starting...")
                self.root.update()

                # Start Flask app
                self.web_server_process = subprocess.Popen(
                    [sys.executable, "app.py"], cwd=os.getcwd()
                )

                # Wait a moment for server to start
                time.sleep(3)

                if self.web_server_process.poll() is None:  # Process still running
                    self.web_server_running = True
                    self.web_status_var.set(
                        "🟢 Web Server: Running on http://localhost:5000"
                    )
                    messagebox.showinfo(
                        "Success",
                        "Web server started successfully!\nOpening browser...",
                    )
                    self.open_web_browser()
                else:
                    self.web_status_var.set("🔴 Web Server: Failed to start")
                    messagebox.showerror("Error", "Failed to start web server")

            except Exception as e:
                self.web_status_var.set("🔴 Web Server: Error")
                messagebox.showerror("Error", f"Failed to start web server:\n{str(e)}")

        if self.web_server_running:
            self.open_web_browser()
        else:
            threading.Thread(target=start_server, daemon=True).start()

    def open_web_browser(self):
        """Open web interface in browser"""
        if self.web_server_running:
            webbrowser.open("http://localhost:5000/unified")
        else:
            webbrowser.open("http://localhost:5000/unified")
            messagebox.showinfo(
                "Info",
                "Opening browser. If server isn't running,\nplease start it first.",
            )

    def launch_desktop_gui(self):
        """Launch the desktop GUI"""
        try:
            gui_path = os.path.join("GUI", "unified_warehouse_system.py")
            if os.path.exists(gui_path):
                subprocess.Popen([sys.executable, gui_path])
                messagebox.showinfo("Success", "Desktop GUI launched!")
            else:
                messagebox.showerror(
                    "Error", f"Desktop GUI file not found:\n{gui_path}"
                )
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to launch desktop GUI:\n{
                    str(e)}",
            )

    def show_advanced_features(self):
        """Show advanced features dialog"""
        features_window = tk.Toplevel(self.root)
        features_window.title("Advanced Features")
        features_window.geometry("600x400")
        features_window.configure(bg="white")

        title_label = tk.Label(
            features_window,
            text="🔧 Advanced Features",
            font=("Arial", 16, "bold"),
            bg="white",
        )
        title_label.pack(pady=20)

        features_text = tk.Text(features_window, wrap=tk.WORD, font=("Arial", 11))
        features_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        advanced_features = """
🏭 ADVANCED WAREHOUSE MANAGEMENT
• Multi-warehouse inventory tracking
• Real-time stock level monitoring
• Automated reorder suggestions
• Warehouse performance analytics

🚛 INTELLIGENT ROUTING SYSTEM
• Geographic optimization
• Cost-based routing decisions
• Carrier performance tracking
• Delivery time optimization

📊 COMPREHENSIVE REPORTING
• Excel report generation
• Custom data exports
• Performance dashboards
• API usage analytics

🔄 REAL-TIME SYNCHRONIZATION
• Multi-platform API integration
• Automated data syncing
• Error handling and recovery
• Background monitoring services

🎯 SMART ORDER PROCESSING
• Customer data parsing
• Address validation
• Automated warehouse selection
• Multi-carrier support

🌐 WEB & DESKTOP INTERFACES
• Responsive web dashboard
• Traditional desktop GUI
• Mobile-friendly design
• Cross-platform compatibility
        """

        features_text.insert("1.0", advanced_features.strip())
        features_text.config(state=tk.DISABLED)

        close_button = tk.Button(
            features_window,
            text="Close",
            command=features_window.destroy,
            bg="#3498db",
            fg="white",
            font=("Arial", 12),
        )
        close_button.pack(pady=20)

    def on_closing(self):
        """Handle application closing"""
        if self.web_server_process and self.web_server_running:
            if messagebox.askquestion("Exit", "Stop web server and exit?") == "yes":
                try:
                    self.web_server_process.terminate()
                except BaseException:
                    pass
                self.root.destroy()
        else:
            self.root.destroy()


def main():
    """Launch the GUI launcher"""
    root = tk.Tk()

    # Set window icon and properties
    root.configure(bg="#f0f0f0")

    # Create the launcher
    app = ShippingGUILauncher(root)

    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_closing)

    # Start the GUI event loop
    root.mainloop()


if __name__ == "__main__":
    main()
