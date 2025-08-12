"""
Campus Map Widget for KSSEM College
Interactive map displaying buildings, landmarks, and navigation features
"""

import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from typing import Dict, Any, Tuple, List, Optional
import logging

from config.kssem_config import CAMPUS_BUILDINGS, CAMPUS_MAP_CONFIG

class CampusMapWidget(ctk.CTkFrame):
    """Interactive campus map widget for KSSEM College"""
    
    def __init__(self, parent, system_manager):
        """Initialize the campus map widget"""
        super().__init__(parent)
        self.system_manager = system_manager
        self.logger = logging.getLogger(__name__)
        
        # Map state
        self.current_route = None
        self.selected_building = None
        self.zoom_level = 1.0
        self.pan_offset = [0, 0]
        
        # Create map components
        self._create_map_components()
        self._setup_layout()
        self._bind_events()
        
        # Initialize map
        self._create_campus_map()
        
        self.logger.info("Campus map widget initialized")
    
    def _create_map_components(self):
        """Create map display components"""
        # Map display frame
        self.map_frame = ctk.CTkFrame(self)
        
        # Control panel
        self._create_control_panel()
        
        # Information panel
        self._create_info_panel()
        
        # Search panel
        self._create_search_panel()
    
    def _create_control_panel(self):
        """Create map control panel"""
        self.control_panel = ctk.CTkFrame(self)
        
        # Title
        title_label = ctk.CTkLabel(
            self.control_panel,
            text="🗺️ KSSEM College Campus Map",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#4CAF50"
        )
        title_label.pack(pady=(10, 20))
        
        # Zoom controls
        zoom_frame = ctk.CTkFrame(self.control_panel)
        zoom_frame.pack(pady=(0, 10))
        
        zoom_label = ctk.CTkLabel(zoom_frame, text="Zoom:")
        zoom_label.pack(side="left", padx=(10, 5))
        
        self.zoom_in_btn = ctk.CTkButton(
            zoom_frame,
            text="+",
            width=30,
            command=self._zoom_in
        )
        self.zoom_in_btn.pack(side="left", padx=(0, 5))
        
        self.zoom_out_btn = ctk.CTkButton(
            zoom_frame,
            text="-",
            width=30,
            command=self._zoom_out
        )
        self.zoom_out_btn.pack(side="left", padx=(0, 10))
        
        # Reset view button
        reset_btn = ctk.CTkButton(
            self.control_panel,
            text="🔄 Reset View",
            command=self._reset_view,
            width=150
        )
        reset_btn.pack(pady=(0, 10))
        
        # Building list
        buildings_label = ctk.CTkLabel(
            self.control_panel,
            text="Buildings:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        buildings_label.pack(pady=(10, 5))
        
        # Scrollable building list
        self.buildings_listbox = tk.Listbox(
            self.control_panel,
            height=8,
            width=25,
            selectmode="single",
            font=("Arial", 10)
        )
        self.buildings_listbox.pack(pady=(0, 10))
        
        # Populate building list
        for building_id, building_info in CAMPUS_BUILDINGS.items():
            self.buildings_listbox.insert(tk.END, building_info['name'])
        
        # Bind building selection
        self.buildings_listbox.bind('<<ListboxSelect>>', self._on_building_select)
        
        # Navigation controls
        nav_label = ctk.CTkLabel(
            self.control_panel,
            text="Navigation:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        nav_label.pack(pady=(10, 5))
        
        # Start location
        start_frame = ctk.CTkFrame(self.control_panel)
        start_frame.pack(pady=(0, 5))
        
        start_label = ctk.CTkLabel(start_frame, text="From:")
        start_label.pack(side="left", padx=(10, 5))
        
        self.start_location_var = tk.StringVar()
        self.start_location_combo = ttk.Combobox(
            start_frame,
            textvariable=self.start_location_var,
            values=["Current Location"] + [b['name'] for b in CAMPUS_BUILDINGS.values()],
            width=15
        )
        self.start_location_combo.pack(side="left", padx=(0, 10))
        self.start_location_combo.set("Current Location")
        
        # End location
        end_frame = ctk.CTkFrame(self.control_panel)
        end_frame.pack(pady=(0, 10))
        
        end_label = ctk.CTkLabel(end_frame, text="To:")
        end_label.pack(side="left", padx=(10, 5))
        
        self.end_location_var = tk.StringVar()
        self.end_location_combo = ttk.Combobox(
            end_frame,
            textvariable=self.end_location_var,
            values=[b['name'] for b in CAMPUS_BUILDINGS.values()],
            width=15
        )
        self.end_location_combo.pack(side="left", padx=(0, 10))
        
        # Get directions button
        directions_btn = ctk.CTkButton(
            self.control_panel,
            text="🛣️ Get Directions",
            command=self._get_directions,
            width=150
        )
        directions_btn.pack(pady=(0, 10))
        
        # Clear route button
        clear_route_btn = ctk.CTkButton(
            self.control_panel,
            text="🗑️ Clear Route",
            command=self._clear_route,
            width=150
        )
        clear_route_btn.pack()
    
    def _create_info_panel(self):
        """Create information display panel"""
        self.info_panel = ctk.CTkFrame(self)
        
        # Title
        info_title = ctk.CTkLabel(
            self.info_panel,
            text="ℹ️ Information",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        info_title.pack(pady=(10, 15))
        
        # Information display
        self.info_text = ctk.CTkTextbox(
            self.info_panel,
            height=200,
            width=250
        )
        self.info_text.pack(padx=10, pady=(0, 10))
        
        # Default information
        self.info_text.insert("1.0", "Select a building or location to view information.")
        
        # Legend
        legend_label = ctk.CTkLabel(
            self.info_panel,
            text="Map Legend:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        legend_label.pack(pady=(10, 5))
        
        legend_text = ctk.CTkTextbox(
            self.info_panel,
            height=100,
            width=250
        )
        legend_text.pack(padx=10, pady=(0, 10))
        
        legend_content = """🏢 Buildings - Academic and administrative
🌳 Gardens - Recreational areas
🅿️ Parking - Vehicle parking zones
🚪 Entrances - Main gates and access points
🛣️ Paths - Walking routes
📍 Current Location - Your position"""
        
        legend_text.insert("1.0", legend_content)
    
    def _create_search_panel(self):
        """Create search functionality panel"""
        self.search_panel = ctk.CTkFrame(self)
        
        # Title
        search_title = ctk.CTkLabel(
            self.search_panel,
            text="🔍 Search",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        search_title.pack(pady=(10, 15))
        
        # Search input
        search_frame = ctk.CTkFrame(self.search_panel)
        search_frame.pack(pady=(0, 10))
        
        self.search_var = tk.StringVar()
        self.search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            placeholder_text="Search locations...",
            width=200
        )
        self.search_entry.pack(side="left", padx=(10, 5))
        
        search_btn = ctk.CTkButton(
            search_frame,
            text="Search",
            command=self._search_location,
            width=80
        )
        search_btn.pack(side="left", padx=(0, 10))
        
        # Search results
        results_label = ctk.CTkLabel(
            self.search_panel,
            text="Search Results:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        results_label.pack(pady=(10, 5))
        
        self.search_results_listbox = tk.Listbox(
            self.search_panel,
            height=6,
            width=25
        )
        self.search_results_listbox.pack(padx=10, pady=(0, 10))
        
        # Bind search result selection
        self.search_results_listbox.bind('<<ListboxSelect>>', self._on_search_result_select)
    
    def _setup_layout(self):
        """Setup widget layout"""
        # Configure grid weights
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Place components
        self.control_panel.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        self.map_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=10)
        self.info_panel.grid(row=0, column=2, sticky="nsew", padx=(5, 10), pady=10)
        self.search_panel.grid(row=1, column=0, columnspan=3, sticky="ew", padx=10, pady=(0, 10))
        
        # Configure column weights for map frame
        self.map_frame.grid_rowconfigure(0, weight=1)
        self.map_frame.grid_columnconfigure(0, weight=1)
    
    def _bind_events(self):
        """Bind mouse and keyboard events"""
        # Bind search entry to Enter key
        self.search_entry.bind('<Return>', lambda e: self._search_location())
        
        # Bind mouse wheel for zooming
        self.map_frame.bind('<MouseWheel>', self._on_mouse_wheel)
        
        # Bind mouse buttons for panning
        self.map_frame.bind('<Button-1>', self._on_mouse_click)
        self.map_frame.bind('<B1-Motion>', self._on_mouse_drag)
    
    def _create_campus_map(self):
        """Create and display the campus map"""
        try:
            # Create matplotlib figure
            self.fig, self.ax = plt.subplots(figsize=(10, 8))
            self.ax.set_xlim(0, CAMPUS_MAP_CONFIG['dimensions'][0])
            self.ax.set_ylim(0, CAMPUS_MAP_CONFIG['dimensions'][1])
            
            # Set map properties
            self.ax.set_title('KSSEM College Campus Map', fontsize=16, fontweight='bold')
            self.ax.set_xlabel('Meters')
            self.ax.set_ylabel('Meters')
            self.ax.grid(True, alpha=0.3)
            
            # Draw campus elements
            self._draw_buildings()
            self._draw_landmarks()
            self._draw_paths()
            self._draw_scale()
            
            # Create canvas
            self.canvas = FigureCanvasTkAgg(self.fig, self.map_frame)
            self.canvas.draw()
            self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
            
            # Add navigation toolbar
            self._add_navigation_toolbar()
            
            self.logger.info("Campus map created successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to create campus map: {e}")
            self._show_map_error()
    
    def _draw_buildings(self):
        """Draw buildings on the map"""
        building_colors = {
            'main_block': '#4CAF50',
            'library': '#2196F3',
            'cafeteria': '#FF9800',
            'auditorium': '#9C27B0',
            'sports_complex': '#00BCD4',
            'hostels': '#FF5722'
        }
        
        for building_id, building_info in CAMPUS_BUILDINGS.items():
            coords = building_info['coordinates']
            color = building_colors.get(building_id, '#757575')
            
            # Draw building rectangle
            if building_id == 'main_block':
                # Main block is larger
                rect = patches.Rectangle(
                    (coords[0] - 25, coords[1] - 20),
                    50, 40,
                    linewidth=2,
                    edgecolor='black',
                    facecolor=color,
                    alpha=0.8
                )
            else:
                # Other buildings are smaller
                rect = patches.Rectangle(
                    (coords[0] - 15, coords[1] - 10),
                    30, 20,
                    linewidth=2,
                    edgecolor='black',
                    facecolor=color,
                    alpha=0.8
                )
            
            self.ax.add_patch(rect)
            
            # Add building label
            self.ax.text(
                coords[0], coords[1] + 25,
                building_info['name'],
                ha='center',
                va='bottom',
                fontsize=8,
                fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8)
            )
            
            # Add building info on click
            self._add_building_click_handler(building_id, coords)
    
    def _draw_landmarks(self):
        """Draw landmarks on the map"""
        landmark_colors = {
            'entrance': '#4CAF50',
            'facility': '#2196F3',
            'recreation': '#8BC34A',
            'service': '#FF9800',
            'health': '#F44336',
            'technology': '#9C27B0'
        }
        
        for landmark in CAMPUS_MAP_CONFIG['landmarks']:
            coords = landmark['coordinates']
            landmark_type = landmark['type']
            color = landmark_colors.get(landmark_type, '#757575')
            
            # Draw landmark symbol
            if landmark_type == 'entrance':
                # Main gate
                circle = patches.Circle(
                    coords, 8,
                    linewidth=2,
                    edgecolor='black',
                    facecolor=color,
                    alpha=0.9
                )
                self.ax.add_patch(circle)
                
                # Gate symbol
                self.ax.text(
                    coords[0], coords[1],
                    '🚪',
                    ha='center',
                    va='center',
                    fontsize=12
                )
            
            elif landmark_type == 'facility':
                # Parking area
                rect = patches.Rectangle(
                    (coords[0] - 10, coords[1] - 5),
                    20, 10,
                    linewidth=1,
                    edgecolor='black',
                    facecolor=color,
                    alpha=0.7
                )
                self.ax.add_patch(rect)
                
                # Parking symbol
                self.ax.text(
                    coords[0], coords[1],
                    '🅿️',
                    ha='center',
                    va='center',
                    fontsize=10
                )
            
            elif landmark_type == 'recreation':
                # Garden
                circle = patches.Circle(
                    coords, 12,
                    linewidth=1,
                    edgecolor='green',
                    facecolor='lightgreen',
                    alpha=0.6
                )
                self.ax.add_patch(circle)
                
                # Garden symbol
                self.ax.text(
                    coords[0], coords[1],
                    '🌳',
                    ha='center',
                    va='center',
                    fontsize=14
                )
            
            elif landmark_type == 'service':
                # ATM
                rect = patches.Rectangle(
                    (coords[0] - 5, coords[1] - 5),
                    10, 10,
                    linewidth=1,
                    edgecolor='black',
                    facecolor=color,
                    alpha=0.8
                )
                self.ax.add_patch(rect)
                
                # ATM symbol
                self.ax.text(
                    coords[0], coords[1],
                    '🏧',
                    ha='center',
                    va='center',
                    fontsize=10
                )
            
            elif landmark_type == 'health':
                # Medical room
                rect = patches.Rectangle(
                    (coords[0] - 8, coords[1] - 6),
                    16, 12,
                    linewidth=1,
                    edgecolor='red',
                    facecolor='lightcoral',
                    alpha=0.8
                )
                self.ax.add_patch(rect)
                
                # Medical symbol
                self.ax.text(
                    coords[0], coords[1],
                    '🏥',
                    ha='center',
                    va='center',
                    fontsize=12
                )
            
            elif landmark_type == 'technology':
                # WiFi hotspots
                if isinstance(coords, list):
                    for coord in coords:
                        circle = patches.Circle(
                            coord, 3,
                            linewidth=1,
                            edgecolor='blue',
                            facecolor='lightblue',
                            alpha=0.7
                        )
                        self.ax.add_patch(circle)
                        
                        # WiFi symbol
                        self.ax.text(
                            coord[0], coord[1],
                            '📶',
                            ha='center',
                            va='center',
                            fontsize=8
                        )
            
            # Add landmark label
            if landmark_type != 'technology':
                self.ax.text(
                    coords[0], coords[1] - 15,
                    landmark['name'],
                    ha='center',
                    va='top',
                    fontsize=7,
                    bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8)
                )
    
    def _draw_paths(self):
        """Draw walking paths on the map"""
        path_color = '#666666'
        path_width = 3
        
        for path in CAMPUS_MAP_CONFIG['walking_paths']:
            if len(path) >= 2:
                # Convert path to numpy array for plotting
                path_array = np.array(path)
                self.ax.plot(
                    path_array[:, 0],
                    path_array[:, 1],
                    color=path_color,
                    linewidth=path_width,
                    alpha=0.7,
                    linestyle='-'
                )
                
                # Add path markers
                for point in path:
                    self.ax.plot(
                        point[0], point[1],
                        'o',
                        color=path_color,
                        markersize=3,
                        alpha=0.8
                    )
    
    def _draw_scale(self):
        """Draw map scale bar"""
        scale_length = 50  # 50 meters
        scale_y = 10
        
        # Scale bar
        self.ax.plot(
            [10, 10 + scale_length], [scale_y, scale_y],
            'k-',
            linewidth=3
        )
        
        # Scale labels
        self.ax.text(10, scale_y - 5, '0m', ha='center', va='top', fontsize=8)
        self.ax.text(10 + scale_length, scale_y - 5, '50m', ha='center', va='top', fontsize=8)
        
        # Scale text
        self.ax.text(
            10 + scale_length/2, scale_y + 5,
            'Scale: 1 pixel = 1 meter',
            ha='center',
            va='bottom',
            fontsize=8,
            bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8)
        )
    
    def _add_building_click_handler(self, building_id: str, coords: Tuple[int, int]):
        """Add click handler for building selection"""
        # This would be implemented with matplotlib event handling
        # For now, we'll use the building list selection
        pass
    
    def _add_navigation_toolbar(self):
        """Add navigation toolbar to the map"""
        # This would add zoom, pan, and reset tools
        # For now, we'll use the control panel buttons
        pass
    
    def _show_map_error(self):
        """Show error message when map creation fails"""
        error_label = ctk.CTkLabel(
            self.map_frame,
            text="❌ Failed to load campus map\nPlease check the console for errors.",
            font=ctk.CTkFont(size=16),
            text_color="#F44336"
        )
        error_label.grid(row=0, column=0)
    
    def _zoom_in(self):
        """Zoom in on the map"""
        self.zoom_level *= 1.2
        self._update_map_view()
    
    def _zoom_out(self):
        """Zoom out on the map"""
        self.zoom_level /= 1.2
        self._update_map_view()
    
    def _reset_view(self):
        """Reset map view to default"""
        self.zoom_level = 1.0
        self.pan_offset = [0, 0]
        self._update_map_view()
    
    def _update_map_view(self):
        """Update map view with current zoom and pan"""
        try:
            # Update axis limits based on zoom and pan
            width = CAMPUS_MAP_CONFIG['dimensions'][0] / self.zoom_level
            height = CAMPUS_MAP_CONFIG['dimensions'][1] / self.zoom_level
            
            center_x = CAMPUS_MAP_CONFIG['dimensions'][0] / 2 + self.pan_offset[0]
            center_y = CAMPUS_MAP_CONFIG['dimensions'][1] / 2 + self.pan_offset[1]
            
            self.ax.set_xlim(center_x - width/2, center_x + width/2)
            self.ax.set_ylim(center_y - height/2, center_y + height/2)
            
            # Redraw canvas
            self.canvas.draw()
            
        except Exception as e:
            self.logger.error(f"Failed to update map view: {e}")
    
    def _on_mouse_wheel(self, event):
        """Handle mouse wheel events for zooming"""
        if event.delta > 0:
            self._zoom_in()
        else:
            self._zoom_out()
    
    def _on_mouse_click(self, event):
        """Handle mouse click events"""
        # This would implement building selection on click
        pass
    
    def _on_mouse_drag(self, event):
        """Handle mouse drag events for panning"""
        # This would implement map panning
        pass
    
    def _on_building_select(self, event):
        """Handle building selection from list"""
        try:
            selection = self.buildings_listbox.curselection()
            if selection:
                index = selection[0]
                building_names = [b['name'] for b in CAMPUS_BUILDINGS.values()]
                building_name = building_names[index]
                
                # Find building info
                building_info = None
                for b_id, b_info in CAMPUS_BUILDINGS.items():
                    if b_info['name'] == building_name:
                        building_info = b_info
                        break
                
                if building_info:
                    self._show_building_info(building_info)
                    self._highlight_building(building_info['coordinates'])
                    
        except Exception as e:
            self.logger.error(f"Building selection error: {e}")
    
    def _show_building_info(self, building_info: Dict[str, Any]):
        """Display building information in info panel"""
        try:
            self.info_text.delete("1.0", tk.END)
            
            info_content = f"""🏢 {building_info['name']}

📍 Location: {building_info['coordinates']}
📝 Description: {building_info['description']}

"""
            
            # Add specific building details
            if 'floors' in building_info:
                info_content += f"🏗️ Floors: {building_info['floors']}\n"
            
            if 'departments' in building_info:
                info_content += f"🎓 Departments: {', '.join(building_info['departments'])}\n"
            
            if 'hours' in building_info:
                info_content += f"🕐 Hours: {building_info['hours']}\n"
            
            if 'capacity' in building_info:
                info_content += f"👥 Capacity: {building_info['capacity']}\n"
            
            if 'facilities' in building_info:
                info_content += f"🔧 Facilities: {', '.join(building_info['facilities'])}\n"
            
            self.info_text.insert("1.0", info_content)
            
        except Exception as e:
            self.logger.error(f"Failed to show building info: {e}")
    
    def _highlight_building(self, coords: Tuple[int, int]):
        """Highlight selected building on the map"""
        try:
            # Clear previous highlights
            for artist in self.ax.artists:
                if hasattr(artist, '_highlight'):
                    artist.remove()
            
            # Add highlight circle
            highlight = patches.Circle(
                coords, 25,
                linewidth=3,
                edgecolor='yellow',
                facecolor='none',
                alpha=0.8
            )
            highlight._highlight = True
            self.ax.add_patch(highlight)
            
            # Redraw canvas
            self.canvas.draw()
            
        except Exception as e:
            self.logger.error(f"Failed to highlight building: {e}")
    
    def _search_location(self):
        """Search for locations on campus"""
        try:
            query = self.search_var.get().strip().lower()
            if not query:
                return
            
            # Clear previous results
            self.search_results_listbox.delete(0, tk.END)
            
            results = []
            
            # Search in buildings
            for building_id, building_info in CAMPUS_BUILDINGS.items():
                if (query in building_info['name'].lower() or 
                    query in building_info['description'].lower()):
                    results.append(f"🏢 {building_info['name']}")
            
            # Search in landmarks
            for landmark in CAMPUS_MAP_CONFIG['landmarks']:
                if query in landmark['name'].lower():
                    results.append(f"📍 {landmark['name']}")
            
            # Search in departments
            for building_id, building_info in CAMPUS_BUILDINGS.items():
                if 'departments' in building_info:
                    for dept in building_info['departments']:
                        if query in dept.lower():
                            results.append(f"🎓 {dept} - {building_info['name']}")
            
            # Display results
            if results:
                for result in results[:10]:  # Limit to 10 results
                    self.search_results_listbox.insert(tk.END, result)
            else:
                self.search_results_listbox.insert(tk.END, "No results found")
            
        except Exception as e:
            self.logger.error(f"Search error: {e}")
    
    def _on_search_result_select(self, event):
        """Handle search result selection"""
        try:
            selection = self.search_results_listbox.curselection()
            if selection:
                result = self.search_results_listbox.get(selection[0])
                
                # Parse result and show information
                if result.startswith("🏢"):
                    building_name = result[2:]  # Remove emoji
                    for building_info in CAMPUS_BUILDINGS.values():
                        if building_info['name'] == building_name:
                            self._show_building_info(building_info)
                            self._highlight_building(building_info['coordinates'])
                            break
                
                elif result.startswith("📍"):
                    landmark_name = result[2:]  # Remove emoji
                    for landmark in CAMPUS_MAP_CONFIG['landmarks']:
                        if landmark['name'] == landmark_name:
                            self._show_landmark_info(landmark)
                            break
                
                elif result.startswith("🎓"):
                    # Department selected
                    dept_info = result[2:]  # Remove emoji
                    self._show_department_info(dept_info)
                    
        except Exception as e:
            self.logger.error(f"Search result selection error: {e}")
    
    def _show_landmark_info(self, landmark: Dict[str, Any]):
        """Display landmark information"""
        try:
            self.info_text.delete("1.0", tk.END)
            
            info_content = f"""📍 {landmark['name']}

📍 Location: {landmark['coordinates']}
🏷️ Type: {landmark['type'].title()}

"""
            
            self.info_text.insert("1.0", info_content)
            
        except Exception as e:
            self.logger.error(f"Failed to show landmark info: {e}")
    
    def _show_department_info(self, dept_info: str):
        """Display department information"""
        try:
            self.info_text.delete("1.0", tk.END)
            
            # Find department in buildings
            for building_id, building_info in CAMPUS_BUILDINGS.items():
                if 'departments' in building_info:
                    for dept in building_info['departments']:
                        if dept in dept_info:
                            info_content = f"""🎓 {dept}

🏢 Building: {building_info['name']}
📍 Location: {building_info['coordinates']}
📝 Description: {building_info['description']}

"""
                            self.info_text.insert("1.0", info_content)
                            return
            
            self.info_text.insert("1.0", f"Department information not found for: {dept_info}")
            
        except Exception as e:
            self.logger.error(f"Failed to show department info: {e}")
    
    def _get_directions(self):
        """Get directions between two locations"""
        try:
            start = self.start_location_var.get()
            end = self.end_location_var.get()
            
            if not end:
                messagebox.showwarning("Navigation", "Please select a destination.")
                return
            
            if start == "Current Location":
                # Use a default starting point (main gate)
                start_coords = CAMPUS_MAP_CONFIG['landmarks'][0]['coordinates']
            else:
                # Find start building coordinates
                start_coords = None
                for building_info in CAMPUS_BUILDINGS.values():
                    if building_info['name'] == start:
                        start_coords = building_info['coordinates']
                        break
                
                if not start_coords:
                    messagebox.showerror("Navigation", f"Starting location '{start}' not found.")
                    return
            
            # Find end building coordinates
            end_coords = None
            for building_info in CAMPUS_BUILDINGS.values():
                if building_info['name'] == end:
                    end_coords = building_info['coordinates']
                    break
            
            if not end_coords:
                messagebox.showerror("Navigation", f"Destination '{end}' not found.")
                return
            
            # Calculate and display route
            self._show_route(start_coords, end_coords, start, end)
            
        except Exception as e:
            self.logger.error(f"Navigation error: {e}")
            messagebox.showerror("Navigation Error", f"Failed to get directions: {e}")
    
    def _show_route(self, start_coords: Tuple[int, int], end_coords: Tuple[int, int], 
                    start_name: str, end_name: str):
        """Display route between two points"""
        try:
            # Clear previous route
            self._clear_route()
            
            # Draw route line
            route_line = self.ax.plot(
                [start_coords[0], end_coords[0]],
                [start_coords[1], end_coords[1]],
                'r--',
                linewidth=4,
                alpha=0.8,
                label='Route'
            )
            
            # Add start and end markers
            start_marker = self.ax.plot(
                start_coords[0], start_coords[1],
                'go',
                markersize=10,
                label='Start'
            )
            
            end_marker = self.ax.plot(
                end_coords[0], end_coords[1],
                'ro',
                markersize=10,
                label='End'
            )
            
            # Add route information
            distance = np.sqrt((end_coords[0] - start_coords[0])**2 + 
                             (end_coords[1] - start_coords[1])**2)
            
            route_info = f"""🛣️ Route Information

📍 From: {start_name}
🎯 To: {end_name}
📏 Distance: {distance:.1f} meters
⏱️ Estimated Time: {distance/1.4:.0f} minutes (walking)

"""
            
            self.info_text.delete("1.0", tk.END)
            self.info_text.insert("1.0", route_info)
            
            # Store current route
            self.current_route = {
                'start': start_coords,
                'end': end_coords,
                'start_name': start_name,
                'end_name': end_name,
                'distance': distance
            }
            
            # Redraw canvas
            self.canvas.draw()
            
            # Show success message
            messagebox.showinfo(
                "Route Found",
                f"Route from {start_name} to {end_name} displayed on the map.\n"
                f"Distance: {distance:.1f} meters"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to show route: {e}")
            messagebox.showerror("Route Error", f"Failed to display route: {e}")
    
    def _clear_route(self):
        """Clear current route from map"""
        try:
            # Clear route line and markers
            for line in self.ax.lines:
                if line.get_color() == 'red' or line.get_color() == 'green':
                    line.remove()
            
            # Clear route info
            if self.current_route:
                self.info_text.delete("1.0", tk.END)
                self.info_text.insert("1.0", "Select a building or location to view information.")
                self.current_route = None
            
            # Redraw canvas
            self.canvas.draw()
            
        except Exception as e:
            self.logger.error(f"Failed to clear route: {e}")
    
    def update_map(self):
        """Update the campus map display"""
        try:
            # Redraw canvas
            self.canvas.draw()
            self.logger.info("Campus map updated")
            
        except Exception as e:
            self.logger.error(f"Failed to update map: {e}")
    
    def refresh_data(self):
        """Refresh map data from system manager"""
        try:
            # This would update building information, events, etc.
            self.logger.info("Map data refreshed")
            
        except Exception as e:
            self.logger.error(f"Failed to refresh map data: {e}")