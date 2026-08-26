import customtkinter as ctk
import database
import datetime
from widgets.table import CustomTable
from widgets import modal
import logging
from logger import logger

class CropTrackerView(ctk.CTkFrame):
    """
    Crop Tracker View showing fields and crops with independent CRUD controls.
    """
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        # Grid layout: 2 columns (Left: Fields, Right: Crops)
        self.grid_columnconfigure((0, 1), weight=1, uniform="equal")
        self.grid_rowconfigure(0, weight=1)
        
        # Local state for selected items
        self.selected_field_id = None
        self.selected_crop_id = None
        self.fields_list = [] # Store raw field objects for dropdown mapping
        
        # =====================================================================
        # LEFT COLUMN: FIELDS PANEL
        # =====================================================================
        self.fields_panel = ctk.CTkFrame(self, fg_color="#18181b", corner_radius=8, border_width=1, border_color="#27272a")
        self.fields_panel.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20)
        
        self.fields_panel.grid_columnconfigure(0, weight=1)
        self.fields_panel.grid_rowconfigure(2, weight=1) # Expand table
        
        # Fields Header
        ctk.CTkLabel(
            self.fields_panel,
            text="🚜 Fields Inventory",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#e4e4e7"
        ).grid(row=0, column=0, sticky="w", padx=15, pady=15)
        
        # Fields Table
        fields_headers = ["Name", "Area (Ac)", "Soil Type", "Status"]
        fields_mapping = ["name", "area_acres", "soil_type", "status"]
        self.fields_table = CustomTable(
            self.fields_panel,
            headers=fields_headers,
            column_weights=[2, 1, 2, 2],
            on_row_select=self._on_field_row_selected
        )
        self.fields_table.grid(row=2, column=0, sticky="nsew", padx=15, pady=(0, 15))
        
        # Fields Form
        self.fields_form = ctk.CTkFrame(self.fields_panel, fg_color="#09090b", corner_radius=6)
        self.fields_form.grid(row=3, column=0, sticky="ew", padx=15, pady=15)
        self.fields_form.grid_columnconfigure((0, 1), weight=1)
        
        # Fields Form Fields
        ctk.CTkLabel(self.fields_form, text="Field Name", font=ctk.CTkFont(size=12)).grid(row=0, column=0, sticky="w", padx=10, pady=(10, 2))
        self.f_name_entry = ctk.CTkEntry(self.fields_form, placeholder_text="e.g. North Meadow", height=30)
        self.f_name_entry.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(self.fields_form, text="Area (Acres)", font=ctk.CTkFont(size=12)).grid(row=0, column=1, sticky="w", padx=10, pady=(10, 2))
        self.f_area_entry = ctk.CTkEntry(self.fields_form, placeholder_text="e.g. 10.5", height=30)
        self.f_area_entry.grid(row=1, column=1, sticky="ew", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(self.fields_form, text="Soil Type", font=ctk.CTkFont(size=12)).grid(row=2, column=0, sticky="w", padx=10, pady=(0, 2))
        self.f_soil_entry = ctk.CTkEntry(self.fields_form, placeholder_text="e.g. Clay Loam", height=30)
        self.f_soil_entry.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(self.fields_form, text="Status", font=ctk.CTkFont(size=12)).grid(row=2, column=1, sticky="w", padx=10, pady=(0, 2))
        self.f_status_combo = ctk.CTkComboBox(self.fields_form, values=["Active", "Fallow", "Resting"], height=30)
        self.f_status_combo.grid(row=3, column=1, sticky="ew", padx=10, pady=(0, 10))
        self.f_status_combo.set("Active")
        
        # Fields Action Buttons
        self.fields_btn_frame = ctk.CTkFrame(self.fields_form, fg_color="transparent")
        self.fields_btn_frame.grid(row=4, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        self.fields_btn_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.btn_field_add = ctk.CTkButton(self.fields_btn_frame, text="➕ Add", fg_color="#10b981", hover_color="#059669", height=30, command=self._add_field)
        self.btn_field_add.grid(row=0, column=0, padx=2)
        
        self.btn_field_update = ctk.CTkButton(self.fields_btn_frame, text="💾 Save", fg_color="#3b82f6", hover_color="#2563eb", height=30, command=self._update_field)
        self.btn_field_update.grid(row=0, column=1, padx=2)
        
        self.btn_field_delete = ctk.CTkButton(self.fields_btn_frame, text="🗑️ Delete", fg_color="#ef4444", hover_color="#dc2626", height=30, command=self._delete_field)
        self.btn_field_delete.grid(row=0, column=2, padx=2)
        
        # =====================================================================
        # RIGHT COLUMN: CROPS PANEL
        # =====================================================================
        self.crops_panel = ctk.CTkFrame(self, fg_color="#18181b", corner_radius=8, border_width=1, border_color="#27272a")
        self.crops_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)
        
        self.crops_panel.grid_columnconfigure(0, weight=1)
        self.crops_panel.grid_rowconfigure(2, weight=1) # Expand table
        
        # Crops Header
        ctk.CTkLabel(
            self.crops_panel,
            text="🌱 Cultivated Crops",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#e4e4e7"
        ).grid(row=0, column=0, sticky="w", padx=15, pady=15)
        
        # Crops Table
        crops_headers = ["Crop", "Variety", "Field", "Planting Date", "Stage"]
        crops_mapping = ["name", "variety", "field_name", "planting_date", "stage"]
        self.crops_table = CustomTable(
            self.crops_panel,
            headers=crops_headers,
            column_weights=[1, 1, 2, 2, 2],
            on_row_select=self._on_crop_row_selected
        )
        self.crops_table.grid(row=2, column=0, sticky="nsew", padx=15, pady=(0, 15))
        
        # Crops Form
        self.crops_form = ctk.CTkFrame(self.crops_panel, fg_color="#09090b", corner_radius=6)
        self.crops_form.grid(row=3, column=0, sticky="ew", padx=15, pady=15)
        self.crops_form.grid_columnconfigure((0, 1), weight=1)
        
        # Crops Form Fields
        ctk.CTkLabel(self.crops_form, text="Crop Name", font=ctk.CTkFont(size=12)).grid(row=0, column=0, sticky="w", padx=10, pady=(10, 2))
        self.c_name_entry = ctk.CTkEntry(self.crops_form, placeholder_text="e.g. Corn", height=30)
        self.c_name_entry.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(self.crops_form, text="Variety", font=ctk.CTkFont(size=12)).grid(row=0, column=1, sticky="w", padx=10, pady=(10, 2))
        self.c_variety_entry = ctk.CTkEntry(self.crops_form, placeholder_text="e.g. Sweet Yellow", height=30)
        self.c_variety_entry.grid(row=1, column=1, sticky="ew", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(self.crops_form, text="Field Location", font=ctk.CTkFont(size=12)).grid(row=2, column=0, sticky="w", padx=10, pady=(0, 2))
        self.c_field_combo = ctk.CTkComboBox(self.crops_form, values=[], height=30)
        self.c_field_combo.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(self.crops_form, text="Growth Stage", font=ctk.CTkFont(size=12)).grid(row=2, column=1, sticky="w", padx=10, pady=(0, 2))
        self.c_stage_combo = ctk.CTkComboBox(self.crops_form, values=["Seedling", "Vegetative", "Flowering", "Harvest-Ready", "Harvested"], height=30)
        self.c_stage_combo.grid(row=3, column=1, sticky="ew", padx=10, pady=(0, 10))
        self.c_stage_combo.set("Seedling")
        
        ctk.CTkLabel(self.crops_form, text="Planting Date (YYYY-MM-DD)", font=ctk.CTkFont(size=12)).grid(row=4, column=0, sticky="w", padx=10, pady=(0, 2))
        self.c_planting_entry = ctk.CTkEntry(self.crops_form, placeholder_text="YYYY-MM-DD", height=30)
        self.c_planting_entry.grid(row=5, column=0, sticky="ew", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(self.crops_form, text="Expected Harvest (YYYY-MM-DD)", font=ctk.CTkFont(size=12)).grid(row=4, column=1, sticky="w", padx=10, pady=(0, 2))
        self.c_harvest_entry = ctk.CTkEntry(self.crops_form, placeholder_text="YYYY-MM-DD", height=30)
        self.c_harvest_entry.grid(row=5, column=1, sticky="ew", padx=10, pady=(0, 10))
        
        # Populate planting date with today
        self.c_planting_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        # Populate harvest date with today + 90 days as a placeholder
        self.c_harvest_entry.insert(0, (datetime.date.today() + datetime.timedelta(days=90)).strftime("%Y-%m-%d"))
        
        # Crops Action Buttons
        self.crops_btn_frame = ctk.CTkFrame(self.crops_form, fg_color="transparent")
        self.crops_btn_frame.grid(row=6, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        self.crops_btn_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.btn_crop_add = ctk.CTkButton(self.crops_btn_frame, text="➕ Add", fg_color="#10b981", hover_color="#059669", height=30, command=self._add_crop)
        self.btn_crop_add.grid(row=0, column=0, padx=2)
        
        self.btn_crop_update = ctk.CTkButton(self.crops_btn_frame, text="💾 Save", fg_color="#3b82f6", hover_color="#2563eb", height=30, command=self._update_crop)
        self.btn_crop_update.grid(row=0, column=1, padx=2)
        
        self.btn_crop_delete = ctk.CTkButton(self.crops_btn_frame, text="🗑️ Delete", fg_color="#ef4444", hover_color="#dc2626", height=30, command=self._delete_crop)
        self.btn_crop_delete.grid(row=0, column=2, padx=2)

    def refresh(self):
        """Reloads all field and crop data from the database."""
        try:
            # 1. Fetch Fields
            fields = database.get_fields()
            self.fields_list = fields
            
            # Map field names for crop dropdown and tables
            fields_mapping = ["name", "area_acres", "soil_type", "status"]
            self.fields_table.set_data(fields, key_mapping=fields_mapping)
            
            # Populate Field dropdown values in Crop form
            field_names = [f["name"] for f in fields]
            self.c_field_combo.configure(values=field_names)
            if field_names:
                # Keep current or select first
                current_selection = self.c_field_combo.get()
                if current_selection not in field_names:
                    self.c_field_combo.set(field_names[0])
            else:
                self.c_field_combo.set("")
                
            # 2. Fetch Crops
            crops = database.get_crops_with_fields()
            crops_mapping = ["name", "variety", "field_name", "planting_date", "stage"]
            self.crops_table.set_data(crops, key_mapping=crops_mapping)
            
        except Exception as e:
            modal.show_error(self.winfo_toplevel(), "Database Error", f"Failed to refresh data: {e}")

    # =====================================================================
    # FIELDS CRUD LOGIC
    # =====================================================================
    def _on_field_row_selected(self, row_data):
        """Populates the Fields form when a row is selected in the fields table."""
        self.selected_field_id = row_data.get("id")
        
        self.f_name_entry.delete(0, "end")
        self.f_name_entry.insert(0, row_data.get("name", ""))
        
        self.f_area_entry.delete(0, "end")
        self.f_area_entry.insert(0, str(row_data.get("area_acres", "")))
        
        self.f_soil_entry.delete(0, "end")
        self.f_soil_entry.insert(0, row_data.get("soil_type", ""))
        
        self.f_status_combo.set(row_data.get("status", "Active"))

    def _clear_field_form(self):
        self.selected_field_id = None
        self.f_name_entry.delete(0, "end")
        self.f_area_entry.delete(0, "end")
        self.f_soil_entry.delete(0, "end")
        self.f_status_combo.set("Active")
        # De-select in table
        self.fields_table.selected_row_index = None
        self.fields_table.selected_row_data = None
        self.fields_table.refresh() # Resets UI highlights

    def _add_field(self):
        name = self.f_name_entry.get().strip()
        area_raw = self.f_area_entry.get().strip()
        soil = self.f_soil_entry.get().strip()
        status = self.f_status_combo.get()
        
        if not name or not area_raw:
            modal.show_error(self.winfo_toplevel(), "Validation Error", "Name and Area fields are required.")
            return
            
        try:
            area = float(area_raw)
            if area <= 0:
                raise ValueError()
        except ValueError:
            modal.show_error(self.winfo_toplevel(), "Validation Error", "Area must be a valid positive number.")
            return
            
        success, res = database.add_field(name, area, soil, status)
        if success:
            modal.show_info(self.winfo_toplevel(), "Success", f"Field '{name}' added successfully!")
            self._clear_field_form()
            self.refresh()
        else:
            modal.show_error(self.winfo_toplevel(), "Database Error", f"Could not add field: {res}")

    def _update_field(self):
        if not self.selected_field_id:
            modal.show_error(self.winfo_toplevel(), "Selection Error", "Please select a field from the table to edit.")
            return
            
        name = self.f_name_entry.get().strip()
        area_raw = self.f_area_entry.get().strip()
        soil = self.f_soil_entry.get().strip()
        status = self.f_status_combo.get()
        
        if not name or not area_raw:
            modal.show_error(self.winfo_toplevel(), "Validation Error", "Name and Area fields are required.")
            return
            
        try:
            area = float(area_raw)
            if area <= 0:
                raise ValueError()
        except ValueError:
            modal.show_error(self.winfo_toplevel(), "Validation Error", "Area must be a valid positive number.")
            return
            
        success, res = database.update_field(self.selected_field_id, name, area, soil, status)
        if success:
            modal.show_info(self.winfo_toplevel(), "Success", f"Field updated successfully!")
            self._clear_field_form()
            self.refresh()
        else:
            modal.show_error(self.winfo_toplevel(), "Database Error", f"Could not update field: {res}")

    def _delete_field(self):
        if not self.selected_field_id:
            modal.show_error(self.winfo_toplevel(), "Selection Error", "Please select a field from the table to delete.")
            return
            
        def confirm_callback(confirmed):
            if confirmed:
                success, res = database.delete_field(self.selected_field_id)
                if success:
                    modal.show_info(self.winfo_toplevel(), "Success", "Field deleted successfully!")
                    self._clear_field_form()
                    self.refresh()
                else:
                    modal.show_error(self.winfo_toplevel(), "Database Error", f"Could not delete field: {res}")
                    
        modal.ask_confirm(
            self.winfo_toplevel(), 
            "Confirm Delete", 
            "Are you sure you want to delete this field?\nThis will permanently delete all crops planted in this field.", 
            confirm_callback
        )

    # =====================================================================
    # CROPS CRUD LOGIC
    # =====================================================================
    def _on_crop_row_selected(self, row_data):
        """Populates the Crops form when a row is selected in the crops table."""
        self.selected_crop_id = row_data.get("id")
        
        self.c_name_entry.delete(0, "end")
        self.c_name_entry.insert(0, row_data.get("name", ""))
        
        self.c_variety_entry.delete(0, "end")
        self.c_variety_entry.insert(0, row_data.get("variety", ""))
        
        self.c_field_combo.set(row_data.get("field_name", ""))
        self.c_stage_combo.set(row_data.get("stage", "Seedling"))
        
        self.c_planting_entry.delete(0, "end")
        planting = row_data.get("planting_date", "")
        if isinstance(planting, (datetime.date, datetime.datetime)):
            planting = planting.strftime("%Y-%m-%d")
        self.c_planting_entry.insert(0, str(planting))
        
        self.c_harvest_entry.delete(0, "end")
        harvest = row_data.get("expected_harvest", "")
        if isinstance(harvest, (datetime.date, datetime.datetime)):
            harvest = harvest.strftime("%Y-%m-%d")
        self.c_harvest_entry.insert(0, str(harvest))

    def _clear_crop_form(self):
        self.selected_crop_id = None
        self.c_name_entry.delete(0, "end")
        self.c_variety_entry.delete(0, "end")
        self.c_planting_entry.delete(0, "end")
        self.c_planting_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        self.c_harvest_entry.delete(0, "end")
        self.c_harvest_entry.insert(0, (datetime.date.today() + datetime.timedelta(days=90)).strftime("%Y-%m-%d"))
        # Reset selection details
        self.crops_table.selected_row_index = None
        self.crops_table.selected_row_data = None
        self.crops_table.refresh()

    def _get_selected_field_id_from_combo(self):
        selected_name = self.c_field_combo.get()
        for f in self.fields_list:
            if f["name"] == selected_name:
                return f["id"]
        return None

    def _add_crop(self):
        name = self.c_name_entry.get().strip()
        variety = self.c_variety_entry.get().strip()
        stage = self.c_stage_combo.get()
        planting_raw = self.c_planting_entry.get().strip()
        harvest_raw = self.c_harvest_entry.get().strip()
        
        field_id = self._get_selected_field_id_from_combo()
        if not field_id:
            modal.show_error(self.winfo_toplevel(), "Validation Error", "Please select a valid field location. Add fields first if needed.")
            return
            
        if not name:
            modal.show_error(self.winfo_toplevel(), "Validation Error", "Crop name is required.")
            return
            
        # Validate Dates
        try:
            planting_date = datetime.datetime.strptime(planting_raw, "%Y-%m-%d").date()
        except ValueError:
            modal.show_error(self.winfo_toplevel(), "Validation Error", "Planting date must match format YYYY-MM-DD.")
            return
            
        expected_harvest = None
        if harvest_raw:
            try:
                expected_harvest = datetime.datetime.strptime(harvest_raw, "%Y-%m-%d").date()
            except ValueError:
                modal.show_error(self.winfo_toplevel(), "Validation Error", "Expected harvest date must match format YYYY-MM-DD or be left empty.")
                return
                
        # Validate harvest date
        if expected_harvest and expected_harvest < planting_date:
            modal.show_error(self.winfo_toplevel(), "Validation Error", "Expected harvest date cannot be before planting date.")
            return
        success, res = database.add_crop(field_id, name, variety, planting_date, expected_harvest, stage)
        if success:
            modal.show_info(self.winfo_toplevel(), "Success", f"Crop '{name}' successfully planted!")
            self._clear_crop_form()
            self.refresh()
        else:
            logger.error(f"Failed to add crop: {res}")
            modal.show_error(self.winfo_toplevel(), "Database Error", f"Could not plant crop: {res}")

    def _update_crop(self):
        if not self.selected_crop_id:
            modal.show_error(self.winfo_toplevel(), "Selection Error", "Please select a crop from the table to edit.")
            return
            
        name = self.c_name_entry.get().strip()
        variety = self.c_variety_entry.get().strip()
        stage = self.c_stage_combo.get()
        planting_raw = self.c_planting_entry.get().strip()
        harvest_raw = self.c_harvest_entry.get().strip()
        
        field_id = self._get_selected_field_id_from_combo()
        if not field_id:
            modal.show_error(self.winfo_toplevel(), "Validation Error", "Please select a valid field location.")
            return
            
        if not name:
            modal.show_error(self.winfo_toplevel(), "Validation Error", "Crop name is required.")
            return
            
        # Validate Dates
        try:
            planting_date = datetime.datetime.strptime(planting_raw, "%Y-%m-%d").date()
        except ValueError:
            modal.show_error(self.winfo_toplevel(), "Validation Error", "Planting date must match format YYYY-MM-DD.")
            return
            
        expected_harvest = None
        if harvest_raw:
            try:
                expected_harvest = datetime.datetime.strptime(harvest_raw, "%Y-%m-%d").date()
            except ValueError:
                modal.show_error(self.winfo_toplevel(), "Validation Error", "Expected harvest date must match format YYYY-MM-DD or be left empty.")
                return
                
        # Validate harvest date
        if expected_harvest and expected_harvest < planting_date:
            modal.show_error(self.winfo_toplevel(), "Validation Error", "Expected harvest date cannot be before planting date.")
            return
        success, res = database.update_crop(self.selected_crop_id, field_id, name, variety, planting_date, expected_harvest, stage)
        if success:
            modal.show_info(self.winfo_toplevel(), "Success", "Crop details updated successfully!")
            self._clear_crop_form()
            self.refresh()
        else:
            logger.error(f"Failed to update crop: {res}")
            modal.show_error(self.winfo_toplevel(), "Database Error", f"Could not update crop: {res}")

    def _delete_crop(self):
        if not self.selected_crop_id:
            modal.show_error(self.winfo_toplevel(), "Selection Error", "Please select a crop from the table to delete.")
            return
            
        def confirm_callback(confirmed):
            if confirmed:
                success, res = database.delete_crop(self.selected_crop_id)
                if success:
                    modal.show_info(self.winfo_toplevel(), "Success", "Crop record removed successfully!")
                    self._clear_crop_form()
                    self.refresh()
                else:
                    modal.show_error(self.winfo_toplevel(), "Database Error", f"Could not delete crop: {res}")
                    
        modal.ask_confirm(
            self.winfo_toplevel(), 
            "Confirm Delete", 
            "Are you sure you want to remove this crop record?", 
            confirm_callback
        )
