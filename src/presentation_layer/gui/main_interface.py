"""
Main GUI Interface for KSSEM Virtual AI Assistant Kiosk
Provides touchscreen interface with campus map, voice interaction, and accessibility features
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import customtkinter as ctk
from PIL import Image, ImageTk
import requests
import json
from datetime import datetime
import threading
import asyncio
from typing import Dict, List, Optional, Any
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# Set appearance mode and color theme
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class KSSEMMainInterface:
    """
    Main GUI interface for KSSEM Virtual AI Assistant
    Provides intuitive touchscreen interface with accessibility features
    """
    
    def __init__(self):
        """Initialize the main interface"""
        self.root = ctk.CTk()
        self.root.title("KSSEM Virtual AI Assistant")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        
        # API configuration
        self.api_base_url = "http://localhost:8000"
        self.session_id = self._generate_session_id()
        
        # UI state
        self.current_mode = "normal"  # normal, high_contrast, large_text
        self.voice_enabled = False
        self.current_conversation = []
        
        # Campus map data
        self.campus_map_data = None
        self.map_figure = None
        self.map_canvas = None
        
        # Initialize UI components
        self.setup_main_layout()
        self.load_campus_data()
        self.create_campus_map()
        
        # Start the GUI
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def setup_main_layout(self):
        """Setup the main layout with all components"""
        
        # Main container
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header
        self.create_header()
        
        # Main content area (split into left and right)
        self.content_frame = ctk.CTkFrame(self.main_frame)
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left panel (Chat and controls)
        self.left_panel = ctk.CTkFrame(self.content_frame)
        self.left_panel.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Right panel (Map and information)
        self.right_panel = ctk.CTkFrame(self.content_frame)
        self.right_panel.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        # Setup panels
        self.create_chat_interface()
        self.create_control_panel()
        self.create_map_panel()
        self.create_info_panel()
        
        # Footer
        self.create_footer()
    
    def create_header(self):
        """Create the header with logo and title"""
        header_frame = ctk.CTkFrame(self.main_frame, height=80)
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        header_frame.pack_propagate(False)
        
        # KSSEM Logo and title
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        
        # Title
        title_label = ctk.CTkLabel(
            title_frame,
            text="🎓 KSSEM Virtual AI Assistant",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#1f538d"
        )
        title_label.pack(side="left", pady=10)
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="KS School of Engineering and Management • Bangalore",
            font=ctk.CTkFont(size=14),
            text_color="#666666"
        )
        subtitle_label.pack(side="left", padx=(20, 0), pady=10)
        
        # Accessibility controls
        self.create_accessibility_controls(header_frame)
    
    def create_accessibility_controls(self, parent):
        """Create accessibility control buttons"""
        access_frame = ctk.CTkFrame(parent, fg_color="transparent")
        access_frame.pack(side="right", padx=20, pady=10)
        
        # High contrast button
        self.contrast_btn = ctk.CTkButton(
            access_frame,
            text="🔆 High Contrast",
            width=120,
            height=30,
            command=self.toggle_high_contrast
        )
        self.contrast_btn.pack(side="top", pady=2)
        
        # Large text button
        self.large_text_btn = ctk.CTkButton(
            access_frame,
            text="🔍 Large Text",
            width=120,
            height=30,
            command=self.toggle_large_text
        )
        self.large_text_btn.pack(side="top", pady=2)
    
    def create_chat_interface(self):
        """Create the chat interface"""
        chat_frame = ctk.CTkFrame(self.left_panel)
        chat_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Chat title
        chat_title = ctk.CTkLabel(
            chat_frame,
            text="💬 Ask me anything about KSSEM!",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        chat_title.pack(pady=(10, 5))
        
        # Chat display area
        self.chat_display = ctk.CTkTextbox(
            chat_frame,
            height=300,
            font=ctk.CTkFont(size=14),
            wrap="word"
        )
        self.chat_display.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Initial welcome message
        self.add_message("Assistant", "Hello! Welcome to KSSEM. I'm here to help you with:\n• Campus navigation and directions\n• Information about departments and facilities\n• Admission and course details\n• Faculty and contact information\n• Placement statistics\n• Emergency contacts\n\nHow can I assist you today?")
        
        # Input area
        input_frame = ctk.CTkFrame(chat_frame, fg_color="transparent")
        input_frame.pack(fill="x", padx=10, pady=10)
        
        # Text input
        self.text_input = ctk.CTkEntry(
            input_frame,
            placeholder_text="Type your question here...",
            font=ctk.CTkFont(size=14),
            height=40
        )
        self.text_input.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.text_input.bind("<Return>", lambda e: self.send_message())
        
        # Send button
        self.send_btn = ctk.CTkButton(
            input_frame,
            text="Send",
            width=80,
            height=40,
            command=self.send_message
        )
        self.send_btn.pack(side="right")
    
    def create_control_panel(self):
        """Create control panel with quick actions"""
        control_frame = ctk.CTkFrame(self.left_panel)
        control_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Title
        control_title = ctk.CTkLabel(
            control_frame,
            text="Quick Actions",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        control_title.pack(pady=10)
        
        # Button grid
        button_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=10, pady=5)
        
        # Quick action buttons
        buttons = [
            ("📍 Find Library", lambda: self.quick_query("Where is the library?")),
            ("🏢 Departments", lambda: self.quick_query("Tell me about departments")),
            ("🎓 Admissions", lambda: self.quick_query("How can I apply for admission?")),
            ("💼 Placements", lambda: self.quick_query("What are the placement statistics?")),
            ("🍽️ Cafeteria", lambda: self.quick_query("Where is the cafeteria?")),
            ("🚨 Emergency", lambda: self.quick_query("Emergency contacts"))
        ]
        
        for i, (text, command) in enumerate(buttons):
            row, col = i // 2, i % 2
            btn = ctk.CTkButton(
                button_frame,
                text=text,
                width=140,
                height=35,
                command=command
            )
            btn.grid(row=row, column=col, padx=5, pady=3, sticky="ew")
        
        # Configure grid weights
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
    
    def create_map_panel(self):
        """Create the campus map panel"""
        map_frame = ctk.CTkFrame(self.right_panel)
        map_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Map title
        map_title = ctk.CTkLabel(
            map_frame,
            text="🗺️ KSSEM Campus Map",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        map_title.pack(pady=10)
        
        # Map container
        self.map_container = ctk.CTkFrame(map_frame)
        self.map_container.pack(fill="both", expand=True, padx=10, pady=5)
    
    def create_info_panel(self):
        """Create information display panel"""
        info_frame = ctk.CTkFrame(self.right_panel)
        info_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Info title
        info_title = ctk.CTkLabel(
            info_frame,
            text="📋 Campus Information",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        info_title.pack(pady=10)
        
        # Info display
        self.info_display = ctk.CTkTextbox(
            info_frame,
            height=150,
            font=ctk.CTkFont(size=12)
        )
        self.info_display.pack(fill="both", padx=10, pady=5)
        
        # Default info
        self.update_info_display({
            "Total Departments": "5 (CSE, ECE, ME, Civil, MBA)",
            "Total Students": "~1,380",
            "Campus Area": "25 acres",
            "Established": "2005",
            "Location": "Bangalore, Karnataka"
        })
    
    def create_footer(self):
        """Create footer with status and timestamps"""
        footer_frame = ctk.CTkFrame(self.main_frame, height=40)
        footer_frame.pack(fill="x", padx=10, pady=(5, 10))
        footer_frame.pack_propagate(False)
        
        # Status
        self.status_label = ctk.CTkLabel(
            footer_frame,
            text="🟢 System Online • Ready to help",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="left", padx=20, pady=10)
        
        # Timestamp
        self.time_label = ctk.CTkLabel(
            footer_frame,
            text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            font=ctk.CTkFont(size=12)
        )
        self.time_label.pack(side="right", padx=20, pady=10)
        
        # Update time every second
        self.update_time()
    
    def load_campus_data(self):
        """Load campus data from API"""
        try:
            response = requests.get(f"{self.api_base_url}/campus/map", timeout=5)
            if response.status_code == 200:
                self.campus_map_data = response.json()
                self.update_status("🟢 Campus data loaded")
            else:
                self.update_status("🟡 Using offline data")
        except Exception as e:
            self.update_status("🟡 API unavailable - offline mode")
            print(f"Failed to load campus data: {e}")
    
    def create_campus_map(self):
        """Create and display the campus map"""
        if not self.campus_map_data:
            # Create placeholder map
            self.create_placeholder_map()
            return
        
        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(6, 4))
        fig.patch.set_facecolor('white')
        
        # Plot buildings
        buildings = self.campus_map_data.get('buildings', [])
        
        for building in buildings:
            coords = building['coordinates']
            if 'corners' in coords:
                corners = coords['corners']
                # Create building rectangle
                x_coords = [corner[0] for corner in corners] + [corners[0][0]]
                y_coords = [corner[1] for corner in corners] + [corners[0][1]]
                
                # Color code by building type
                color = self.get_building_color(building.get('type', 'academic'))
                ax.plot(x_coords, y_coords, color=color, linewidth=2)
                ax.fill(x_coords, y_coords, color=color, alpha=0.3)
                
                # Add building label
                center = coords.get('center', [0, 0])
                ax.text(center[0], center[1], building['name'].split(' - ')[0], 
                       fontsize=8, ha='center', va='center', weight='bold')
        
        # Plot pathways
        pathways = self.campus_map_data.get('pathways', [])
        for pathway in pathways:
            coords = pathway['coordinates']
            x_coords = [coord[0] for coord in coords]
            y_coords = [coord[1] for coord in coords]
            ax.plot(x_coords, y_coords, 'gray', linewidth=pathway.get('width', 3), alpha=0.7)
        
        # Plot kiosk locations
        kiosks = self.campus_map_data.get('kiosk_locations', [])
        for kiosk in kiosks:
            coords = kiosk['coordinates']
            ax.plot(coords[0], coords[1], 'ro', markersize=10, label='Kiosk' if kiosk == kiosks[0] else "")
        
        # Formatting
        ax.set_xlim(-50, 450)
        ax.set_ylim(-50, 450)
        ax.set_aspect('equal')
        ax.set_title('KSSEM Campus Layout', fontsize=14, weight='bold')
        ax.grid(True, alpha=0.3)
        
        # Add legend
        if kiosks:
            ax.legend(loc='upper right')
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, self.map_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        self.map_figure = fig
        self.map_canvas = canvas
    
    def create_placeholder_map(self):
        """Create a placeholder map when data is not available"""
        placeholder_label = ctk.CTkLabel(
            self.map_container,
            text="🗺️\n\nCampus Map\nLoading...\n\nPlease check your\nconnection to the server",
            font=ctk.CTkFont(size=16),
            justify="center"
        )
        placeholder_label.pack(expand=True)
    
    def get_building_color(self, building_type: str) -> str:
        """Get color for building based on type"""
        colors = {
            'academic': '#3498db',
            'facility': '#2ecc71',
            'administrative': '#e74c3c'
        }
        return colors.get(building_type, '#95a5a6')
    
    def add_message(self, sender: str, message: str):
        """Add a message to the chat display"""
        timestamp = datetime.now().strftime("%H:%M")
        
        # Format message
        if sender == "Assistant":
            formatted_message = f"🤖 Assistant [{timestamp}]:\n{message}\n\n"
            self.chat_display.insert("end", formatted_message)
        else:
            formatted_message = f"👤 You [{timestamp}]:\n{message}\n\n"
            self.chat_display.insert("end", formatted_message)
        
        # Scroll to bottom
        self.chat_display.see("end")
        
        # Update conversation history
        self.current_conversation.append({
            "sender": sender,
            "message": message,
            "timestamp": timestamp
        })
    
    def send_message(self):
        """Send user message to the API"""
        message = self.text_input.get().strip()
        if not message:
            return
        
        # Clear input
        self.text_input.delete(0, "end")
        
        # Add user message to chat
        self.add_message("You", message)
        
        # Update status
        self.update_status("🔄 Processing your request...")
        
        # Send to API in background thread
        threading.Thread(target=self._process_message, args=(message,), daemon=True).start()
    
    def _process_message(self, message: str):
        """Process message through API (runs in background thread)"""
        try:
            # Prepare request
            request_data = {
                "query": message,
                "session_id": self.session_id,
                "use_voice": False
            }
            
            # Send to API
            response = requests.post(
                f"{self.api_base_url}/query",
                json=request_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Update UI in main thread
                self.root.after(0, self._handle_api_response, result)
            else:
                self.root.after(0, self._handle_api_error, f"API Error: {response.status_code}")
                
        except Exception as e:
            self.root.after(0, self._handle_api_error, str(e))
    
    def _handle_api_response(self, result: Dict):
        """Handle successful API response"""
        # Add assistant response
        response_text = result.get('response', 'I apologize, but I encountered an issue processing your request.')
        self.add_message("Assistant", response_text)
        
        # Update info panel if additional information is available
        if result.get('additional_info'):
            self.display_additional_info(result['additional_info'])
        
        # Handle navigation data
        if result.get('navigation_data'):
            self.display_navigation_info(result['navigation_data'])
        
        # Update status
        confidence = result.get('confidence', 0)
        self.update_status(f"🟢 Response ready (confidence: {confidence:.1%})")
    
    def _handle_api_error(self, error_message: str):
        """Handle API errors"""
        self.add_message("Assistant", f"I'm sorry, I'm having trouble connecting to my services. Error: {error_message}\n\nPlease try again or contact the help desk.")
        self.update_status("🔴 Connection error")
    
    def quick_query(self, query: str):
        """Send a quick query"""
        self.text_input.delete(0, "end")
        self.text_input.insert(0, query)
        self.send_message()
    
    def display_additional_info(self, info: Dict):
        """Display additional information in the info panel"""
        if info.get('type') == 'department_info' and 'department' in info:
            dept = info['department']
            self.update_info_display({
                "Department": dept['name'],
                "Head": dept['head']['name'],
                "Location": f"Block {dept['location']['block']}",
                "Faculty": f"{dept['faculty_count']} members",
                "Students": f"{dept['student_capacity']} capacity",
                "Contact": dept['contact']['email']
            })
        elif info.get('type') == 'facility_info':
            self.info_display.delete("1.0", "end")
            self.info_display.insert("1.0", f"📍 {info.get('question', 'Facility Information')}\n\n{info.get('answer', 'No details available.')}")
    
    def display_navigation_info(self, nav_data: Dict):
        """Display navigation information"""
        if nav_data.get('has_full_route'):
            nav_text = f"🚶‍♂️ Navigation Info:\n"
            nav_text += f"Distance: {nav_data.get('distance', 0):.0f} meters\n"
            nav_text += f"Time: {nav_data.get('estimated_time', 0):.0f} seconds\n\n"
            nav_text += "First steps:\n"
            for i, instruction in enumerate(nav_data.get('instructions', [])[:3], 1):
                nav_text += f"{i}. {instruction}\n"
            
            self.info_display.delete("1.0", "end")
            self.info_display.insert("1.0", nav_text)
    
    def update_info_display(self, info_dict: Dict[str, str]):
        """Update the information display panel"""
        self.info_display.delete("1.0", "end")
        
        info_text = ""
        for key, value in info_dict.items():
            info_text += f"• {key}: {value}\n"
        
        self.info_display.insert("1.0", info_text)
    
    def update_status(self, status: str):
        """Update the status label"""
        self.status_label.configure(text=status)
    
    def update_time(self):
        """Update the time display"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.configure(text=current_time)
        self.root.after(1000, self.update_time)
    
    def toggle_high_contrast(self):
        """Toggle high contrast mode"""
        if self.current_mode == "high_contrast":
            ctk.set_appearance_mode("light")
            self.current_mode = "normal"
            self.contrast_btn.configure(text="🔆 High Contrast")
        else:
            ctk.set_appearance_mode("dark")
            self.current_mode = "high_contrast"
            self.contrast_btn.configure(text="☀️ Normal View")
    
    def toggle_large_text(self):
        """Toggle large text mode"""
        # This would require rebuilding the interface with larger fonts
        # For now, just show a message
        messagebox.showinfo("Large Text", "Large text mode would be implemented with dynamic font scaling.")
    
    def on_closing(self):
        """Handle application closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()

# Main entry point
if __name__ == "__main__":
    try:
        # Create and run the application
        app = KSSEMMainInterface()
        app.run()
    except Exception as e:
        print(f"Failed to start KSSEM Virtual AI Assistant: {e}")
        # Fallback to basic tkinter if customtkinter fails
        import tkinter as tk
        root = tk.Tk()
        root.title("KSSEM Virtual AI Assistant - Error")
        root.geometry("400x200")
        
        error_label = tk.Label(root, text=f"Failed to start application:\n{e}", wraplength=350)
        error_label.pack(expand=True)
        
        root.mainloop()