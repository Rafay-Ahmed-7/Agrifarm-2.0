import customtkinter as ctk
import logging
from logger import logger
import database
from widgets.table import CustomTable
from widgets import modal
class InventoryView(ctk.CTkFrame):
    """
    Inventory view listing stock levels and offering stock adjustment interfaces.
    """
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        # Grid layout: 2-column layout (Left: Data Table, Right: Controls & Adjustments)
        self.grid_columnconfigure(0, weight=3) # Let table be wider
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)
        
        self.selected_item_id = None
        self.inventory_list = [] # Raw database records
        
        # =====================================================================
        # LEFT COLUMN: INVENTORY LIST TABLE
        # =====================================================================
        self.table_panel = ctk.CTkFrame(self, fg_color="#18181b", corner_radius=8, border_width=1, border_color="#27272a")
        self.table_panel.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20)
        
        self.table_panel.grid_columnconfigure(0, weight=1)
        self.table_panel.grid_rowconfigure(1, weight=1)
        
        # Header
        ctk.CTkLabel(
            self.table_panel,
            text="🚜 Stock Inventory Logs",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#e4e4e7"
        ).grid(row=0, column=0, sticky="w", padx=15, pady=15)
        
        # Table
        headers = ["Item Name", "Category", "Quantity", "Unit", "Last Updated"]
        column_weights = [3, 2, 2, 1, 3]
        self.inventory_table = CustomTable(
            self.table_panel,
            headers=headers,
            column_weights=column_weights,
            on_row_select=self._on_row_selected
        )
        self.inventory_table.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        
        # =====================================================================
        # RIGHT COLUMN: ACTION & ADJUSTMENT FORMS
        # =====================================================================
        self.form_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.form_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)
        self.form_panel.grid_columnconfigure(0, weight=1)
        
        # 1. Quick Stock Adjustment Form
        self.adjust_box = ctk.CTkFrame(self.form_panel, fg_color="#18181b", corner_radius=8, border_width=1, border_color="#27272a")
        self.adjust_box.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        self.adjust_box.grid_columnconfigure((0, 1), weight=1)
        
        ctk.CTkLabel(
            self.adjust_box, 
            text="⚡ Quick Stock Adjustment", 
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#e4e4e7"
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=15, pady=12)
        
        # Target Item Dropdown
        ctk.CTkLabel(self.adjust_box, text="Select Item", font=ctk.CTkFont(size=12)).grid(row=1, column=0, columnspan=2, sticky="w", padx=15, pady=(5, 2))
        self.adj_item_combo = ctk.CTkComboBox(self.adjust_box, values=[], height=30)
        self.adj_item_combo.grid(row=2, column=0, columnspan=2, sticky="ew", padx=15, pady=(0, 10))
        
        # Adjustment Mode (Add / Subtract)
        ctk.CTkLabel(self.adjust_box, text="Adjustment Mode", font=ctk.CTkFont(size=12)).grid(row=3, column=0, sticky="w", padx=15, pady=(0, 2))
        self.adj_mode_combo = ctk.CTkComboBox(self.adjust_box, values=["➕ Add Stock", "➖ Subtract Stock"], height=30)
        self.adj_mode_combo.grid(row=4, column=0, sticky="ew", padx=15, pady=(0, 10))
        self.adj_mode_combo.set("➕ Add Stock")
        
        # Amount Entry
        ctk.CTkLabel(self.adjust_box, text="Amount / Change", font=ctk.CTkFont(size=12)).grid(row=3, column=1, sticky="w", padx=15, pady=(0, 2))
        self.adj_qty_entry = ctk.CTkEntry(self.adjust_box, placeholder_text="e.g. 5", height=30)
        self.adj_qty_entry.grid(row=4, column=1, sticky="ew", padx=15, pady=(0, 10))
        
        # Apply Button
        self.btn_apply_adj = ctk.CTkButton(
            self.adjust_box, 
            text="Apply Adjustment", 
            fg_color="#10b981", 
            hover_color="#059669",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=32,
            command=self._apply_adjustment
        )
        self.btn_apply_adj.grid(row=5, column=0, columnspan=2, sticky="ew", padx=15, pady=(5, 15))
        
        # 2. Add New Product/Item Form
        self.add_box = ctk.CTkFrame(self.form_panel, fg_color="#18181b", corner_radius=8, border_width=1, border_color="#27272a")
        self.add_box.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        self.add_box.grid_columnconfigure((0, 1), weight=1)
        
        ctk.CTkLabel(
            self.add_box, 
            text="🆕 Register New Item", 
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#e4e4e7"
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=15, pady=12)
        
        # Product Name
        ctk.CTkLabel(self.add_box, text="Item Name", font=ctk.CTkFont(size=12)).grid(row=1, column=0, columnspan=2, sticky="w", padx=15, pady=(5, 2))
        self.new_name_entry = ctk.CTkEntry(self.add_box, placeholder_text="e.g. Phosphate Fertilizer", height=30)
        self.new_name_entry.grid(row=2, column=0, columnspan=2, sticky="ew", padx=15, pady=(0, 10))
        
        # Category
        ctk.CTkLabel(self.add_box, text="Category", font=ctk.CTkFont(size=12)).grid(row=3, column=0, sticky="w", padx=15, pady=(0, 2))
        self.new_cat_combo = ctk.CTkComboBox(self.add_box, values=["Seeds", "Fertilizer", "Pesticide", "Tools"], height=30)
        self.new_cat_combo.grid(row=4, column=0, sticky="ew", padx=15, pady=(0, 10))
        self.new_cat_combo.set("Seeds")
        
        # Unit
        ctk.CTkLabel(self.add_box, text="Unit of Measure", font=ctk.CTkFont(size=12)).grid(row=3, column=1, sticky="w", padx=15, pady=(0, 2))
        self.new_unit_entry = ctk.CTkEntry(self.add_box, placeholder_text="e.g. kg, liters, units", height=30)
        self.new_unit_entry.grid(row=4, column=1, sticky="ew", padx=15, pady=(0, 10))
        
        # Initial Stock Quantity
        ctk.CTkLabel(self.add_box, text="Initial Stock Quantity", font=ctk.CTkFont(size=12)).grid(row=5, column=0, sticky="w", padx=15, pady=(0, 2))
        self.new_qty_entry = ctk.CTkEntry(self.add_box, placeholder_text="e.g. 50", height=30)
        self.new_qty_entry.grid(row=6, column=0, sticky="ew", padx=15, pady=(0, 15))
        
        # Register Button
        self.btn_register = ctk.CTkButton(
            self.add_box, 
            text="Register Item", 
            fg_color="#3b82f6", 
            hover_color="#2563eb",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=32,
            command=self._register_item
        )
        self.btn_register.grid(row=6, column=1, sticky="ew", padx=15, pady=(0, 15))
        
        # 3. Delete Selected Panel
        self.delete_box = ctk.CTkFrame(self.form_panel, fg_color="#18181b", corner_radius=8, border_width=1, border_color="#27272a")
        self.delete_box.grid(row=2, column=0, sticky="ew")
        
        self.delete_box.grid_columnconfigure(0, weight=1)
        
        self.btn_delete_item = ctk.CTkButton(
            self.delete_box,
            text="🗑️ Delete Selected Item",
            fg_color="#ef4444",
            hover_color="#dc2626",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=32,
            command=self._delete_item
        )
        self.btn_delete_item.grid(row=0, column=0, sticky="ew", padx=15, pady=15)

    def refresh(self):
        """Loads and syncs inventory levels from the database."""
        try:
            items = database.get_inventory()
            self.inventory_list = items
            
            # Map columns
            key_mapping = ["item_name", "category", "quantity", "unit", "last_updated"]
            self.inventory_table.set_data(items, key_mapping=key_mapping)
            
            # Populate target item dropdown in quick adjustment frame
            item_names = [row["item_name"] for row in items]
            self.adj_item_combo.configure(values=item_names)
            
            if item_names:
                # Keep selection or select first
                current = self.adj_item_combo.get()
                if current not in item_names:
                    self.adj_item_combo.set(item_names[0])
            else:
                self.adj_item_combo.set("")
                
        except Exception as e:
            modal.show_error(self.winfo_toplevel(), "Database Error", f"Failed to refresh inventory: {e}")

    def _on_row_selected(self, row_data):
        """Syncs the form controls with the selected item in the inventory log."""
        self.selected_item_id = row_data.get("id")
        self.adj_item_combo.set(row_data.get("item_name", ""))

    def _apply_adjustment(self):
        selected_name = self.adj_item_combo.get()
        adj_mode = self.adj_mode_combo.get()
        qty_raw = self.adj_qty_entry.get().strip()
        
        if not selected_name:
            modal.show_error(self.winfo_toplevel(), "Validation Error", "Please select an item to adjust.")
            return
            
        if not qty_raw:
            modal.show_error(self.winfo_toplevel(), "Validation Error", "Please enter an adjustment amount.")
            return
            
        try:
            qty = float(qty_raw)
            if qty <= 0:
                raise ValueError()
        except ValueError:
            modal.show_error(self.winfo_toplevel(), "Validation Error", "Amount must be a valid positive number.")
            return
            
        # Find item id
        item_id = None
        for item in self.inventory_list:
            if item["item_name"] == selected_name:
                item_id = item["id"]
                break
                
        if not item_id:
            modal.show_error(self.winfo_toplevel(), "Error", "Selected item could not be found.")
            return
            
        # Add or Subtract multiplier
        multiplier = 1.0 if "Add" in adj_mode else -1.0
        adjustment = qty * multiplier
        
        success, res = database.adjust_inventory_stock(item_id, adjustment)
        if success:
            modal.show_info(self.winfo_toplevel(), "Success", "Stock level adjusted successfully!")
            self.adj_qty_entry.delete(0, "end")
            self.refresh()
        else:
            logger.error(f"Failed to adjust inventory stock: {res}")
            modal.show_error(self.winfo_toplevel(), "Adjustment Failed", res)

    def _register_item(self):
        name = self.new_name_entry.get().strip()
        category = self.new_cat_combo.get()
        unit = self.new_unit_entry.get().strip()
        qty_raw = self.new_qty_entry.get().strip()
        
        if not name or not unit or not qty_raw:
            modal.show_error(self.winfo_toplevel(), "Validation Error", "All fields are required to register a new item.")
            return
            
        try:
            qty = float(qty_raw)
            if qty < 0:
                raise ValueError()
        except ValueError:
            modal.show_error(self.winfo_toplevel(), "Validation Error", "Initial quantity must be a non-negative number.")
            return
            
        success, res = database.add_inventory_item(name, category, qty, unit)
        if success:
            modal.show_info(self.winfo_toplevel(), "Success", f"Item '{name}' registered successfully!")
            self.new_name_entry.delete(0, "end")
            self.new_unit_entry.delete(0, "end")
            self.new_qty_entry.delete(0, "end")
            self.refresh()
        else:
            logger.error(f"Failed to register inventory item: {res}")
            modal.show_error(self.winfo_toplevel(), "Database Error", f"Could not register item: {res}")

    def _delete_item(self):
        if not self.selected_item_id:
            # Let's try matching with the adjustment combo if it's set
            combo_name = self.adj_item_combo.get()
            if combo_name:
                for item in self.inventory_list:
                    if item["item_name"] == combo_name:
                        self.selected_item_id = item["id"]
                        break
                        
        if not self.selected_item_id:
            modal.show_error(self.winfo_toplevel(), "Selection Error", "Please select an item from the table to delete.")
            return
            
        def confirm_callback(confirmed):
            if confirmed:
                success, res = database.delete_inventory_item(self.selected_item_id)
                if success:
                    modal.show_info(self.winfo_toplevel(), "Success", "Inventory item deleted successfully!")
                    self.selected_item_id = None
                    self.refresh()
                else:
                    logger.error(f"Failed to delete inventory item: {res}")
                    modal.show_error(self.winfo_toplevel(), "Database Error", f"Could not delete item: {res}")
                    
        modal.ask_confirm(
            self.winfo_toplevel(),
            "Confirm Delete",
            "Are you sure you want to permanently delete this item from inventory?",
            confirm_callback
        )
