import datetime
import customtkinter as ctk
import database
from widgets.table import CustomTable

class DashboardView(ctk.CTkFrame):
    """
    Dashboard view showing top-level KPIs and upcoming activities.
    """
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        # Main layout configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)  # Make table area expand
        
        # 1. Header Title
        self.header_label = ctk.CTkLabel(
            self,
            text="📊 Farm Dashboard",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#f4f4f5",
            anchor="w"
        )
        self.header_label.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 15))
        
        # 2. KPI Cards Panel
        self.kpi_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.kpi_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        self.kpi_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Card 1: Fields
        self.fields_card = self._create_kpi_card(
            self.kpi_frame, 
            title="Total Cultivated Fields", 
            value="0", 
            icon="🚜", 
            color="#10b981", 
            col=0
        )
        
        # Card 2: Crops
        self.crops_card = self._create_kpi_card(
            self.kpi_frame, 
            title="Active Crops", 
            value="0", 
            icon="🌱", 
            color="#3b82f6", 
            col=1
        )
        
        # Card 3: Inventory warnings
        self.inventory_card = self._create_kpi_card(
            self.kpi_frame, 
            title="Low Inventory Alerts", 
            value="0", 
            icon="⚠️", 
            color="#ef4444", 
            col=2
        )
        
        # 3. Upcoming Harvests Panel
        self.harvests_container = ctk.CTkFrame(self, fg_color="#18181b", corner_radius=8, border_width=1, border_color="#27272a")
        self.harvests_container.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        self.harvests_container.grid_columnconfigure(0, weight=1)
        self.harvests_container.grid_rowconfigure(1, weight=1)
        
        # Panel Title
        self.panel_title = ctk.CTkLabel(
            self.harvests_container,
            text="🌾 Upcoming Harvests & Deadlines (Next 30 Days)",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#e4e4e7",
            anchor="w"
        )
        self.panel_title.grid(row=0, column=0, sticky="ew", padx=15, pady=15)
        
        # Harvest table
        headers = ["Crop", "Variety", "Location / Field", "Expected Harvest", "Current Stage"]
        column_weights = [1, 1, 1, 1, 1]
        self.harvest_table = CustomTable(
            self.harvests_container, 
            headers=headers, 
            column_weights=column_weights
        )
        self.harvest_table.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))

    def _create_kpi_card(self, parent, title, value, icon, color, col):
        """Helper to create a beautiful, unified KPI card."""
        card = ctk.CTkFrame(
            parent, 
            fg_color="#18181b", 
            corner_radius=8, 
            border_width=1, 
            border_color="#27272a"
        )
        card.grid(row=0, column=col, padx=(0 if col == 0 else 10, 0 if col == 2 else 10), sticky="ew")
        
        card.grid_columnconfigure(0, weight=1)
        card.grid_columnconfigure(1, weight=0)
        
        # Texts layout
        text_frame = ctk.CTkFrame(card, fg_color="transparent")
        text_frame.grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        title_lbl = ctk.CTkLabel(
            text_frame, 
            text=title, 
            font=ctk.CTkFont(size=12, weight="normal"), 
            text_color="#a1a1aa"
        )
        title_lbl.pack(anchor="w")
        
        value_lbl = ctk.CTkLabel(
            text_frame, 
            text=value, 
            font=ctk.CTkFont(size=28, weight="bold"), 
            text_color=color
        )
        value_lbl.pack(anchor="w", pady=(5, 0))
        
        # Icon layout
        icon_lbl = ctk.CTkLabel(
            card, 
            text=icon, 
            font=ctk.CTkFont(size=36),
            text_color=color
        )
        icon_lbl.grid(row=0, column=1, padx=20, pady=15, sticky="e")
        
        # Store label reference to update value later
        card.value_lbl = value_lbl
        return card

    def refresh(self):
        """Loads metrics and table data, handling database connectivity errors gracefully."""
        try:
            # 1. Load Stats
            stats = database.get_dashboard_metrics(low_stock_threshold=10.0)
            self.fields_card.value_lbl.configure(text=str(stats.get("total_fields", 0)))
            self.crops_card.value_lbl.configure(text=str(stats.get("active_crops", 0)))
            
            low_stock_count = stats.get("low_stock_alerts", 0)
            self.inventory_card.value_lbl.configure(text=str(low_stock_count))
            # Highlight border to red if alerts exist
            if low_stock_count > 0:
                self.inventory_card.configure(border_color="#ef4444")
            else:
                self.inventory_card.configure(border_color="#27272a")
            
            # 2. Load Table
            upcoming = database.get_upcoming_activities(days=30)
            
            # Map database keys to columns
            # Keys: ['id', 'crop_name', 'variety', 'field_name', 'expected_harvest', 'stage']
            key_mapping = ["crop_name", "variety", "field_name", "expected_harvest", "stage"]
            self.harvest_table.set_data(upcoming, key_mapping=key_mapping)
            
        except Exception as e:
            # Set to 0 and show error in table if DB is offline
            self.fields_card.value_lbl.configure(text="-")
            self.crops_card.value_lbl.configure(text="-")
            self.inventory_card.value_lbl.configure(text="-")
            self.inventory_card.configure(border_color="#27272a")
            
            self.harvest_table.clear()
            no_db_label = ctk.CTkLabel(
                self.harvest_table.body_frame,
                text=f"Could not connect to database.\nPlease check credentials in Settings tab.",
                font=ctk.CTkFont(size=14, slant="italic"),
                text_color="#ef4444"
            )
            no_db_label.grid(row=0, column=0, columnspan=5, pady=40, sticky="ew")
            self.harvest_table.row_widgets.append([no_db_label])
