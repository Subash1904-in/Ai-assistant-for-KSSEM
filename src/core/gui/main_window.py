"""
Main GUI Window for KSSEM College Virtual AI Assistant
Touchscreen interface with voice, text, and touch interactions
"""

import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import threading
import time
from typing import Dict, Any, Optional
from pathlib import Path

from .components.campus_map import CampusMapWidget
from .components.query_interface import QueryInterface
from .components.navigation_panel import NavigationPanel
from .components.resource_panel import ResourcePanel
from .components.status_bar import StatusBar
from .components.accessibility_panel import AccessibilityPanel
from config.kssem_config import COLLEGE_INFO, ACCESSIBILITY_FEATURES

class MainWindow:
    """Main application window for the Virtual AI Assistant"""
    
    def __init__(self, system_manager):
        """Initialize the main window"""
        self.system_manager = system_manager
        self.logger = logging.getLogger(__name__)
        
        # Initialize customtkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create main window
        self.root = ctk.CTk()
        self._setup_window()
        self._create_widgets()
        self._setup_layout()
        self._bind_events()
        
        # Start system
        self._start_system()
        
        self.logger.info("Main window initialized successfully")
    
    def _setup_window(self):
        """Setup main window properties"""
        # Fullscreen for kiosk mode
        self.root.attributes('-fullscreen', True)
        self.root.title(f"KSSEM College Virtual AI Assistant - {COLLEGE_INFO['name']}")
        
        # Set window icon (if available)
        icon_path = Path(__file__).parent.parent.parent / "assets" / "kssem_icon.png"
        if icon_path.exists():
            self.root.iconphoto(True, tk.PhotoImage(file=str(icon_path)))
        
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
        # Set minimum size
        self.root.minsize(1200, 800)
    
    def _create_widgets(self):
        """Create all GUI widgets"""
        # Create main container
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        
        # Left sidebar for navigation and controls
        self._create_left_sidebar()
        
        # Main content area
        self._create_main_content()
        
        # Status bar at bottom
        self._create_status_bar()
        
        # Accessibility panel (can be toggled)
        self._create_accessibility_panel()
    
    def _create_left_sidebar(self):
        """Create left sidebar with navigation controls"""
        self.left_sidebar = ctk.CTkFrame(self.main_frame, width=300)
        self.left_sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 0))
        self.left_sidebar.grid_rowconfigure(1, weight=1)
        self.left_sidebar.grid_columnconfigure(0, weight=1)
        
        # Header with college logo and name
        self._create_sidebar_header()
        
        # Navigation tabs
        self._create_navigation_tabs()
        
        # Quick actions
        self._create_quick_actions()
    
    def _create_sidebar_header(self):
        """Create sidebar header with college branding"""
        header_frame = ctk.CTkFrame(self.left_sidebar)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        # College logo (placeholder)
        logo_label = ctk.CTkLabel(
            header_frame, 
            text="🎓", 
            font=ctk.CTkFont(size=48),
            text_color="#4CAF50"
        )
        logo_label.pack(pady=(10, 5))
        
        # College name
        college_name = ctk.CTkLabel(
            header_frame,
            text=COLLEGE_INFO['name'],
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#FFFFFF"
        )
        college_name.pack(pady=(0, 5))
        
        # College location
        location_label = ctk.CTkLabel(
            header_frame,
            text=COLLEGE_INFO['location'],
            font=ctk.CTkFont(size=12),
            text_color="#B0B0B0"
        )
        location_label.pack(pady=(0, 10))
    
    def _create_navigation_tabs(self):
        """Create navigation tabs for different features"""
        # Tab container
        self.tab_container = ctk.CTkTabview(self.left_sidebar)
        self.tab_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        # Home tab
        home_tab = self.tab_container.add("🏠 Home")
        self._create_home_tab(home_tab)
        
        # Navigation tab
        nav_tab = self.tab_container.add("🧭 Navigation")
        self._create_navigation_tab(nav_tab)
        
        # Resources tab
        resources_tab = self.tab_container.add("📚 Resources")
        self._create_resources_tab(resources_tab)
        
        # Help tab
        help_tab = self.tab_container.add("❓ Help")
        self._create_help_tab(help_tab)
    
    def _create_home_tab(self, parent):
        """Create home tab content"""
        # Welcome message
        welcome_label = ctk.CTkLabel(
            parent,
            text="Welcome to KSSEM College!",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        welcome_label.pack(pady=(20, 10))
        
        # Quick query input
        query_label = ctk.CTkLabel(parent, text="Ask me anything:")
        query_label.pack(pady=(10, 5))
        
        self.quick_query_entry = ctk.CTkEntry(
            parent,
            placeholder_text="e.g., Where is the library?",
            width=250
        )
        self.quick_query_entry.pack(pady=(0, 10))
        
        # Quick query button
        quick_query_btn = ctk.CTkButton(
            parent,
            text="Ask",
            command=self._handle_quick_query,
            width=100
        )
        quick_query_btn.pack()
        
        # Voice query button
        voice_btn = ctk.CTkButton(
            parent,
            text="🎤 Voice Query",
            command=self._start_voice_query,
            width=200,
            fg_color="#FF6B6B"
        )
        voice_btn.pack(pady=(20, 0))
        
        # Recent queries
        recent_label = ctk.CTkLabel(
            parent,
            text="Recent Queries:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        recent_label.pack(pady=(20, 10))
        
        self.recent_queries_list = ctk.CTkTextbox(parent, height=100, width=250)
        self.recent_queries_list.pack()
        self.recent_queries_list.insert("1.0", "No recent queries")
    
    def _create_navigation_tab(self, parent):
        """Create navigation tab content"""
        # Campus map button
        map_btn = ctk.CTkButton(
            parent,
            text="🗺️ Campus Map",
            command=self._show_campus_map,
            width=200
        )
        map_btn.pack(pady=(20, 10))
        
        # Find location button
        location_btn = ctk.CTkButton(
            parent,
            text="📍 Find Location",
            command=self._find_location,
            width=200
        )
        location_btn.pack(pady=(0, 10))
        
        # Get directions button
        directions_btn = ctk.CTkButton(
            parent,
            text="🛣️ Get Directions",
            command=self._get_directions,
            width=200
        )
        directions_btn.pack(pady=(0, 10))
        
        # Building list
        buildings_label = ctk.CTkLabel(
            parent,
            text="Buildings:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        buildings_label.pack(pady=(20, 10))
        
        from config.kssem_config import CAMPUS_BUILDINGS
        for building_id, building_info in CAMPUS_BUILDINGS.items():
            building_btn = ctk.CTkButton(
                parent,
                text=f"🏢 {building_info['name']}",
                command=lambda b=building_id: self._select_building(b),
                width=200,
                height=30
            )
            building_btn.pack(pady=(0, 5))
    
    def _create_resources_tab(self, parent):
        """Create resources tab content"""
        # Library resources
        library_btn = ctk.CTkButton(
            parent,
            text="📖 Library",
            command=lambda: self._show_resource("library"),
            width=200
        )
        library_btn.pack(pady=(20, 10))
        
        # Course information
        courses_btn = ctk.CTkButton(
            parent,
            text="📚 Courses",
            command=lambda: self._show_resource("courses"),
            width=200
        )
        courses_btn.pack(pady=(0, 10))
        
        # Faculty directory
        faculty_btn = ctk.CTkButton(
            parent,
            text="👨‍🏫 Faculty",
            command=lambda: self._show_resource("faculty"),
            width=200
        )
        faculty_btn.pack(pady=(0, 10))
        
        # Events calendar
        events_btn = ctk.CTkButton(
            parent,
            text="📅 Events",
            command=lambda: self._show_resource("events"),
            width=200
        )
        events_btn.pack(pady=(0, 10))
        
        # Student services
        services_btn = ctk.CTkButton(
            parent,
            text="🛠️ Services",
            command=lambda: self._show_resource("services"),
            width=200
        )
        services_btn.pack(pady=(0, 10))
    
    def _create_help_tab(self, parent):
        """Create help tab content"""
        # Help topics
        help_topics = [
            "How to use the assistant",
            "Navigation help",
            "Voice commands",
            "Accessibility features",
            "Emergency contacts"
        ]
        
        for topic in help_topics:
            topic_btn = ctk.CTkButton(
                parent,
                text=f"❓ {topic}",
                command=lambda t=topic: self._show_help_topic(t),
                width=200,
                height=30
            )
            topic_btn.pack(pady=(0, 5))
        
        # Emergency contacts
        emergency_label = ctk.CTkLabel(
            parent,
            text="Emergency:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        emergency_label.pack(pady=(20, 10))
        
        from config.kssem_config import EMERGENCY_CONTACTS
        for service, contact in EMERGENCY_CONTACTS.items():
            contact_label = ctk.CTkLabel(
                parent,
                text=f"{service.title()}: {contact}",
                font=ctk.CTkFont(size=12)
            )
            contact_label.pack(pady=(0, 2))
    
    def _create_quick_actions(self):
        """Create quick action buttons"""
        actions_frame = ctk.CTkFrame(self.left_sidebar)
        actions_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        
        # Settings button
        settings_btn = ctk.CTkButton(
            actions_frame,
            text="⚙️ Settings",
            command=self._show_settings,
            width=120
        )
        settings_btn.pack(side="left", padx=(0, 5))
        
        # Exit button
        exit_btn = ctk.CTkButton(
            actions_frame,
            text="🚪 Exit",
            command=self._exit_application,
            width=120,
            fg_color="#FF6B6B"
        )
        exit_btn.pack(side="right", padx=(5, 0))
    
    def _create_main_content(self):
        """Create main content area"""
        self.main_content = ctk.CTkFrame(self.main_frame)
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=(0, 0), pady=(0, 0))
        self.main_content.grid_rowconfigure(0, weight=1)
        self.main_content.grid_columnconfigure(0, weight=1)
        
        # Initialize with home view
        self._show_home_view()
    
    def _create_status_bar(self):
        """Create status bar at bottom"""
        self.status_bar = StatusBar(self.root, self.system_manager)
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")
    
    def _create_accessibility_panel(self):
        """Create accessibility panel"""
        self.accessibility_panel = AccessibilityPanel(self.root)
        # Initially hidden, can be toggled
    
    def _setup_layout(self):
        """Setup widget layout and grid configuration"""
        # Configure grid weights for main content
        self.main_content.grid_rowconfigure(0, weight=1)
        self.main_content.grid_columnconfigure(0, weight=1)
    
    def _bind_events(self):
        """Bind keyboard and mouse events"""
        # Bind escape key to exit fullscreen
        self.root.bind('<Escape>', self._toggle_fullscreen)
        
        # Bind F11 to toggle fullscreen
        self.root.bind('<F11>', self._toggle_fullscreen)
        
        # Bind Ctrl+Q to quit
        self.root.bind('<Control-q>', self._exit_application)
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self._exit_application)
    
    def _start_system(self):
        """Start the system manager"""
        try:
            # Start system in background thread
            threading.Thread(target=self.system_manager.start, daemon=True).start()
            
            # Wait a moment for system to start
            time.sleep(1)
            
            # Update status
            self.status_bar.update_status("System starting...")
            
        except Exception as e:
            self.logger.error(f"Failed to start system: {e}")
            messagebox.showerror("System Error", f"Failed to start system: {e}")
    
    def _show_home_view(self):
        """Show the home view in main content"""
        # Clear main content
        for widget in self.main_content.winfo_children():
            widget.destroy()
        
        # Create home view
        home_frame = ctk.CTkFrame(self.main_content)
        home_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        home_frame.grid_rowconfigure(1, weight=1)
        home_frame.grid_columnconfigure(0, weight=1)
        
        # Welcome header
        welcome_header = ctk.CTkLabel(
            home_frame,
            text="Welcome to KSSEM College Virtual AI Assistant",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#4CAF50"
        )
        welcome_header.grid(row=0, column=0, pady=(20, 10))
        
        # Subtitle
        subtitle = ctk.CTkLabel(
            home_frame,
            text="Your intelligent guide to campus navigation, resources, and information",
            font=ctk.CTkFont(size=16),
            text_color="#B0B0B0"
        )
        subtitle.grid(row=1, column=0, pady=(0, 20))
        
        # Quick actions grid
        actions_frame = ctk.CTkFrame(home_frame)
        actions_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        
        # Create quick action buttons
        quick_actions = [
            ("🗺️ Campus Map", self._show_campus_map, "#4CAF50"),
            ("📚 Library", lambda: self._show_resource("library"), "#2196F3"),
            ("👨‍🏫 Faculty", lambda: self._show_resource("faculty"), "#FF9800"),
            ("📅 Events", lambda: self._show_resource("events"), "#9C27B0"),
            ("🧭 Navigation", self._show_navigation, "#00BCD4"),
            ("❓ Help", self._show_help, "#FF5722")
        ]
        
        for i, (text, command, color) in enumerate(quick_actions):
            row = i // 3
            col = i % 3
            
            btn = ctk.CTkButton(
                actions_frame,
                text=text,
                command=command,
                width=200,
                height=80,
                fg_color=color,
                font=ctk.CTkFont(size=16, weight="bold")
            )
            btn.grid(row=row, column=col, padx=10, pady=10)
        
        # Recent activity
        recent_frame = ctk.CTkFrame(home_frame)
        recent_frame.grid(row=3, column=0, sticky="ew", pady=(20, 0))
        
        recent_label = ctk.CTkLabel(
            recent_frame,
            text="Recent Activity",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        recent_label.pack(pady=(20, 10))
        
        # Placeholder for recent activity
        recent_text = ctk.CTkTextbox(recent_frame, height=150)
        recent_text.pack(padx=20, pady=(0, 20))
        recent_text.insert("1.0", "No recent activity to display.")
    
    def _show_campus_map(self):
        """Show campus map in main content"""
        # Clear main content
        for widget in self.main_content.winfo_children():
            widget.destroy()
        
        # Create campus map widget
        self.campus_map = CampusMapWidget(self.main_content, self.system_manager)
        self.campus_map.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    
    def _show_navigation(self):
        """Show navigation panel in main content"""
        # Clear main content
        for widget in self.main_content.winfo_children():
            widget.destroy()
        
        # Create navigation panel
        self.navigation_panel = NavigationPanel(self.main_content, self.system_manager)
        self.navigation_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    
    def _show_resource(self, resource_type: str):
        """Show resource panel in main content"""
        # Clear main content
        for widget in self.main_content.winfo_children():
            widget.destroy()
        
        # Create resource panel
        self.resource_panel = ResourcePanel(self.main_content, self.system_manager, resource_type)
        self.resource_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    
    def _show_help(self):
        """Show help information in main content"""
        # Clear main content
        for widget in self.main_content.winfo_children():
            widget.destroy()
        
        # Create help view
        help_frame = ctk.CTkFrame(self.main_content)
        help_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        help_label = ctk.CTkLabel(
            help_frame,
            text="Help & Support",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        help_label.pack(pady=(20, 20))
        
        # Help content
        help_text = ctk.CTkTextbox(help_frame, height=400)
        help_text.pack(padx=20, pady=(0, 20))
        
        help_content = """
        KSSEM College Virtual AI Assistant - Help Guide
        
        🎯 How to Use:
        1. Ask questions using text or voice
        2. Navigate campus using the map
        3. Access resources and information
        4. Get directions between locations
        
        🗣️ Voice Commands:
        - "Where is the library?"
        - "How do I get to Room 101?"
        - "What are the library hours?"
        - "Show me faculty information"
        
        🧭 Navigation:
        - Use the campus map to find locations
        - Get step-by-step directions
        - View building information
        
        📚 Resources:
        - Library catalog and hours
        - Course information
        - Faculty directory
        - Event calendar
        
        ♿ Accessibility:
        - High contrast mode
        - Large text option
        - Voice navigation
        - Screen reader support
        
        🆘 Emergency:
        - Campus Security: +91-80-2848-1235
        - Medical Room: +91-80-2848-1236
        - Fire Safety: +91-80-2848-1237
        
        For additional help, contact the IT department.
        """
        
        help_text.insert("1.0", help_content)
    
    def _handle_quick_query(self):
        """Handle quick query from sidebar"""
        query = self.quick_query_entry.get().strip()
        if query:
            self._process_query(query)
            self.quick_query_entry.delete(0, tk.END)
    
    def _start_voice_query(self):
        """Start voice query recording"""
        # This would integrate with the speech engine
        messagebox.showinfo("Voice Query", "Voice query feature coming soon!")
    
    def _process_query(self, query: str):
        """Process a user query"""
        try:
            # Process query through system manager
            result = self.system_manager.process_query(query)
            
            if result["success"]:
                # Show response in main content
                self._show_query_response(query, result["response"])
                
                # Add to recent queries
                self._add_recent_query(query)
            else:
                messagebox.showerror("Query Error", f"Failed to process query: {result['error']}")
                
        except Exception as e:
            self.logger.error(f"Query processing error: {e}")
            messagebox.showerror("Error", f"An error occurred: {e}")
    
    def _show_query_response(self, query: str, response: str):
        """Show query response in main content"""
        # Clear main content
        for widget in self.main_content.winfo_children():
            widget.destroy()
        
        # Create response view
        response_frame = ctk.CTkFrame(self.main_content)
        response_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # Query display
        query_label = ctk.CTkLabel(
            response_frame,
            text=f"Query: {query}",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        query_label.pack(pady=(20, 10))
        
        # Response display
        response_text = ctk.CTkTextbox(response_frame, height=300)
        response_text.pack(padx=20, pady=(0, 20))
        response_text.insert("1.0", response)
        
        # Back button
        back_btn = ctk.CTkButton(
            response_frame,
            text="← Back to Home",
            command=self._show_home_view,
            width=150
        )
        back_btn.pack(pady=(0, 20))
    
    def _add_recent_query(self, query: str):
        """Add query to recent queries list"""
        current_text = self.recent_queries_list.get("1.0", tk.END).strip()
        
        if current_text == "No recent queries":
            self.recent_queries_list.delete("1.0", tk.END)
        
        # Add new query at the top
        timestamp = time.strftime("%H:%M")
        new_query = f"[{timestamp}] {query}\n"
        
        if current_text != "No recent queries":
            new_query += current_text + "\n"
        
        self.recent_queries_list.delete("1.0", tk.END)
        self.recent_queries_list.insert("1.0", new_query)
    
    def _select_building(self, building_id: str):
        """Handle building selection from navigation tab"""
        from config.kssem_config import CAMPUS_BUILDINGS
        
        building_info = CAMPUS_BUILDINGS[building_id]
        messagebox.showinfo(
            building_info['name'],
            f"Location: {building_info['description']}\n"
            f"Coordinates: {building_info['coordinates']}"
        )
    
    def _find_location(self):
        """Show location finder interface"""
        self._show_navigation()
    
    def _get_directions(self):
        """Show directions interface"""
        self._show_navigation()
    
    def _show_settings(self):
        """Show settings dialog"""
        messagebox.showinfo("Settings", "Settings panel coming soon!")
    
    def _show_help_topic(self, topic: str):
        """Show help for specific topic"""
        messagebox.showinfo(f"Help - {topic}", f"Help content for {topic} coming soon!")
    
    def _toggle_fullscreen(self, event=None):
        """Toggle fullscreen mode"""
        if self.root.attributes('-fullscreen'):
            self.root.attributes('-fullscreen', False)
        else:
            self.root.attributes('-fullscreen', True)
    
    def _exit_application(self, event=None):
        """Exit the application"""
        if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
            try:
                self.system_manager.shutdown()
                self.root.quit()
            except Exception as e:
                self.logger.error(f"Error during shutdown: {e}")
                self.root.quit()
    
    def run(self):
        """Start the main event loop"""
        try:
            self.root.mainloop()
        except Exception as e:
            self.logger.error(f"Main loop error: {e}")
            raise