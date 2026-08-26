import customtkinter as ctk
import datetime

class CustomTable(ctk.CTkFrame):
    """
    A beautiful, theme-consistent scrollable table widget.
    Includes headers, alternating row colors, row selection, and warnings.
    """
    def __init__(self, parent, headers, column_weights=None, on_row_select=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.headers = headers
        self.column_weights = column_weights if column_weights else [1] * len(headers)
        self.on_row_select = on_row_select
        
        self.data_rows = []
        self.selected_row_index = None
        self.selected_row_data = None
        self.row_widgets = []  # List of lists of cell labels/buttons
        self.row_containers = [] # List of frames representing each row
        
        # Configure layout: Header frame (static) + Body frame (scrollable)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # 1. Header Frame
        self.header_frame = ctk.CTkFrame(self, height=35, fg_color="#18181b", corner_radius=6)
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        
        # Configure columns inside header frame
        for i, weight in enumerate(self.column_weights):
            try:
                weight_int = int(float(weight))
            except Exception:
                weight_int = 1
            self.header_frame.grid_columnconfigure(i, weight=weight_int)
            
        # Draw header text labels
        for i, header in enumerate(self.headers):
            label = ctk.CTkLabel(
                self.header_frame, 
                text=header, 
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#a1a1aa",
                anchor="w"
            )
            # Add padding to first and subsequent columns
            padx = (15, 5) if i == 0 else 5
            label.grid(row=0, column=i, sticky="ew", padx=padx, pady=8)
            
        # 2. Scrollable Body Frame
        self.body_frame = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        self.body_frame.grid(row=1, column=0, sticky="nsew")
        
        # Configure columns inside scrollable frame to match headers
        for i, weight in enumerate(self.column_weights):
            try:
                weight_int = int(float(weight))
            except Exception:
                weight_int = 1
            self.body_frame.grid_columnconfigure(i, weight=weight_int)

    def set_data(self, rows_list, key_mapping=None):
        """
        Populates the table with data.
        rows_list: list of dicts (or lists/tuples, but dicts are preferred for database rows)
        key_mapping: optional list of keys matching headers in order.
        """
        # Clear existing data rows
        self.clear()
        
        self.data_rows = rows_list
        if not rows_list:
            # Show "No data" row
            no_data_label = ctk.CTkLabel(
                self.body_frame,
                text="No records found",
                font=ctk.CTkFont(size=14, slant="italic"),
                text_color="#71717a"
            )
            no_data_label.grid(row=0, column=0, columnspan=len(self.headers), pady=40, sticky="nsew")
            self.row_widgets.append([no_data_label])
            return
            
        for row_idx, row_data in enumerate(rows_list):
            # Alternating row background colors
            bg_color = "#27272a" if row_idx % 2 == 0 else "#1e1e20"
            
            # Create a click-intercepting container frame for the row to allow selecting the whole row
            row_frame = ctk.CTkFrame(
                self.body_frame,
                fg_color=bg_color,
                corner_radius=4,
                cursor="hand2"
            )
            row_frame.grid(row=row_idx, column=0, columnspan=len(self.headers), sticky="ew", pady=2)
            
            for col_idx, weight in enumerate(self.column_weights):
                row_frame.grid_columnconfigure(col_idx, weight=weight)
                
            self.row_containers.append(row_frame)
            
            # Extract cell values based on key_mapping or standard index/dict
            cell_widgets = []
            for col_idx, header in enumerate(self.headers):
                cell_value = ""
                if key_mapping:
                    key = key_mapping[col_idx]
                    cell_value = row_data.get(key, "")
                elif isinstance(row_data, dict):
                    # Guess by index or standard keys
                    keys = list(row_data.keys())
                    if col_idx < len(keys):
                        cell_value = row_data[keys[col_idx]]
                else:
                    if col_idx < len(row_data):
                        cell_value = row_data[col_idx]
                        
                # Format specific values
                if isinstance(cell_value, float):
                    # Check if it has no decimals
                    if cell_value.is_integer():
                        cell_value = int(cell_value)
                    else:
                        cell_value = f"{cell_value:.2f}"
                elif isinstance(cell_value, (datetime.date, datetime.datetime)):
                    cell_value = cell_value.strftime("%Y-%m-%d")
                elif cell_value is None:
                    cell_value = "-"
                    
                # Highlight low stock items in soft orange/red if in inventory table
                text_color = "#f4f4f5"  # default off-white
                
                # Check for low inventory (Quantity column is usually index 3 or key 'quantity')
                is_low_inventory = False
                if isinstance(row_data, dict):
                    # Check if key quantity exists and is low (e.g. < 10) and it is not a tool
                    qty = row_data.get("quantity")
                    cat = row_data.get("category")
                    # Tools don't alert as much, but seeds, fertilizer, pesticides do
                    if qty is not None:
                        try:
                            qty_val = float(qty)
                            if qty_val < 10.0:
                                is_low_inventory = True
                        except ValueError:
                            pass
                
                if is_low_inventory and (col_idx == 3 or (key_mapping and key_mapping[col_idx] == "quantity")):
                    # Red highlight for low stock quantity
                    text_color = "#f87171"  # Soft red
                    font_style = ctk.CTkFont(size=12, weight="bold")
                else:
                    font_style = ctk.CTkFont(size=12)
                
                cell_label = ctk.CTkLabel(
                    row_frame,
                    text=str(cell_value),
                    font=font_style,
                    text_color=text_color,
                    anchor="w"
                )
                padx = (15, 5) if col_idx == 0 else 5
                cell_label.grid(row=0, column=col_idx, sticky="ew", padx=padx, pady=8)
                cell_widgets.append(cell_label)
                
                # Bind clicks on labels to row select function
                cell_label.bind("<Button-1>", lambda event, idx=row_idx: self._select_row(idx))
                
            self.row_widgets.append(cell_widgets)
            
            # Bind click on row frame itself
            row_frame.bind("<Button-1>", lambda event, idx=row_idx: self._select_row(idx))

    def _select_row(self, index):
        """Highlights the selected row and calls selection callback."""
        if not self.data_rows or index >= len(self.data_rows):
            return
            
        # Reset previous selection background
        if self.selected_row_index is not None and self.selected_row_index < len(self.row_containers):
            prev_bg = "#27272a" if self.selected_row_index % 2 == 0 else "#1e1e20"
            try:
                self.row_containers[self.selected_row_index].configure(fg_color=prev_bg)
            except Exception:
                pass
                
        # Highlight new selection with emerald theme accent
        self.selected_row_index = index
        self.selected_row_data = self.data_rows[index]
        
        try:
            self.row_containers[index].configure(fg_color="#047857")  # Dark emerald/mint selection color
        except Exception:
            pass
            
        if self.on_row_select:
            self.on_row_select(self.selected_row_data)

    def get_selected(self):
        """Returns the dictionary data of the selected row."""
        return self.selected_row_data

    def clear(self):
        """Clears all table rows and widgets."""
        for frame in self.row_containers:
            frame.destroy()
        
        for w_list in self.row_widgets:
            for w in w_list:
                w.destroy()
                
        self.row_containers = []
        self.row_widgets = []
        self.data_rows = []
        self.selected_row_index = None
        self.selected_row_data = None

    def refresh(self):
        """Resets selection highlights without altering data.
        Useful after form clearing to ensure no row appears selected.
        """
        # Reset previous selection background if any
        if self.selected_row_index is not None and self.selected_row_index < len(self.row_containers):
            prev_bg = "#27272a" if self.selected_row_index % 2 == 0 else "#1e1e20"
            try:
                self.row_containers[self.selected_row_index].configure(fg_color=prev_bg)
            except Exception:
                pass
        # Clear selection state
        self.selected_row_index = None
        self.selected_row_data = None
