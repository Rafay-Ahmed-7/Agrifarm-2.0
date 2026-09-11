"""
views/inventory.py - Enterprise Stock & Resource Inventory Hub.

Features:
- Live stock table with category badges, low-stock warning chips, and column sorting
- Instant search and category filter tabs (All, Seeds, Fertilizer, Pesticide, Tools)
- Quick stock adjustment with live on-hand balance preview
- Supply registration and safe deletion workflows
"""

from __future__ import annotations
import decimal
from decimal import Decimal
import logging
import customtkinter as ctk

import database
import theme
from logger import logger
from widgets import modal
from widgets.table import CustomTable


class InventoryView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        # 2-column grid layout (Left: Table 3 parts, Right: Forms 2 parts)
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        self.selected_item_id: int | None = None
        self.inventory_list: list[dict] = []
        self.active_category_filter = "All"

        # =====================================================================
        # LEFT COLUMN: INVENTORY DATA TABLE & FILTER BAR
        # =====================================================================
        self.table_panel = ctk.CTkFrame(
            self,
            fg_color=theme.dual("bg_card"),
            corner_radius=theme.RADIUS_CARD,
            border_width=1,
            border_color=theme.dual("border_card")
        )
        self.table_panel.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=16)
        self.table_panel.grid_columnconfigure(0, weight=1)
        self.table_panel.grid_rowconfigure(2, weight=1)

        # Header Row
        tbl_hdr = ctk.CTkFrame(self.table_panel, fg_color="transparent")
        tbl_hdr.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))
        tbl_hdr.grid_columnconfigure(0, weight=1)

        title_box = ctk.CTkFrame(tbl_hdr, fg_color="transparent")
        title_box.grid(row=0, column=0, sticky="w")

        panel_title = ctk.CTkLabel(
            title_box,
            text="📦 Stock & Resource Ledger",
            font=theme.font_title(size=15),
            text_color=theme.dual("text_primary"),
            anchor="w"
        )
        panel_title.pack(anchor="w")

        self.sub_metrics_lbl = ctk.CTkLabel(
            title_box,
            text="0 items tracked",
            font=theme.font_caption(),
            text_color=theme.dual("text_muted"),
            anchor="w"
        )
        self.sub_metrics_lbl.pack(anchor="w")

        # Search Bar
        self.search_entry = ctk.CTkEntry(
            tbl_hdr,
            placeholder_text="🔍 Search stock...",
            height=32,
            width=180,
            corner_radius=theme.RADIUS_INPUT,
            fg_color=theme.dual("bg_input"),
            border_color=theme.dual("border_input"),
            text_color=theme.dual("text_primary")
        )
        self.search_entry.bind("<KeyRelease>", self._on_search_typed)

        # Category Filter Chips Row
        cat_bar = ctk.CTkFrame(self.table_panel, fg_color="transparent")
        cat_bar.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 10))

        self.cat_buttons = {}
        categories = ["All", "Seeds", "Fertilizer", "Pesticide", "Tools"]
        for cat in categories:
            btn = ctk.CTkButton(
                cat_bar,
                text=cat,
                height=26,
                corner_radius=theme.RADIUS_BADGE,
                font=theme.font_caption(weight="bold"),
                fg_color=theme.dual("bg_card_alt") if cat != "All" else theme.dual("brand_primary_subtle"),
                text_color=theme.dual("text_secondary") if cat != "All" else theme.dual("brand_primary_text"),
                border_width=1,
                border_color=theme.dual("border_subtle") if cat != "All" else theme.dual("brand_primary"),
                hover_color=theme.dual("bg_card_hover"),
                command=lambda c=cat: self._set_category_filter(c)
            )
            btn.pack(side="left", padx=(0, 6))
            self.cat_buttons[cat] = btn

        # Inventory Table
        headers = ["Item Name", "Category", "Quantity", "Unit", "Last Updated"]
        column_weights = [3, 2, 2, 1, 3]
        self.inventory_table = CustomTable(
            self.table_panel,
            headers=headers,
            column_weights=column_weights,
            on_row_select=self._on_row_selected
        )
        self.inventory_table.grid(row=2, column=0, sticky="nsew", padx=16, pady=(0, 16))

        # =====================================================================
        # RIGHT COLUMN: ACTION & ADJUSTMENT WORKBENCH
        # =====================================================================
        self.form_panel = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )
        self.form_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=16)
        self.form_panel.grid_columnconfigure(0, weight=1)

        # 1. Quick Stock Adjustment Card
        self.adjust_box = ctk.CTkFrame(
            self.form_panel,
            fg_color=theme.dual("bg_card"),
            corner_radius=theme.RADIUS_CARD,
            border_width=1,
            border_color=theme.dual("border_card")
        )
        self.adjust_box.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        self.adjust_box.grid_columnconfigure((0, 1), weight=1)

        adj_hdr = ctk.CTkLabel(
            self.adjust_box,
            text="⚡ Quick Stock Adjustment",
            font=theme.font_title(size=14),
            text_color=theme.dual("text_primary"),
            anchor="w"
        )
        adj_hdr.grid(row=0, column=0, columnspan=2, sticky="w", padx=16, pady=(14, 4))

        adj_sub = ctk.CTkLabel(
            self.adjust_box,
            text="Add or deduct inventory from on-hand balances",
            font=theme.font_caption(),
            text_color=theme.dual("text_muted"),
            anchor="w"
        )
        adj_sub.grid(row=1, column=0, columnspan=2, sticky="w", padx=16, pady=(0, 10))

        # Target Item Dropdown
        ctk.CTkLabel(self.adjust_box, text="Target Supply *", font=theme.font_caption(weight="bold"), text_color=theme.dual("text_secondary")).grid(row=2, column=0, columnspan=2, sticky="w", padx=16, pady=(2, 2))
        self.adj_item_combo = ctk.CTkComboBox(
            self.adjust_box,
            values=[],
            height=32,
            corner_radius=theme.RADIUS_INPUT,
            fg_color=theme.dual("bg_input"),
            border_color=theme.dual("border_input"),
            text_color=theme.dual("text_primary"),
            command=self._on_combo_item_selected
        )
        self.adj_item_combo.grid(row=3, column=0, columnspan=2, sticky="ew", padx=16, pady=(0, 4))

        # Balance preview indicator
        self.adj_balance_preview = ctk.CTkLabel(
            self.adjust_box,
            text="Current on-hand: —",
            font=theme.font_caption(weight="bold"),
            text_color=theme.dual("brand_primary"),
            anchor="w"
        )
        self.adj_balance_preview.grid(row=4, column=0, columnspan=2, sticky="w", padx=16, pady=(0, 10))

        # Adjustment Mode
        ctk.CTkLabel(self.adjust_box, text="Operation", font=theme.font_caption(weight="bold"), text_color=theme.dual("text_secondary")).grid(row=5, column=0, sticky="w", padx=16, pady=(0, 2))
        self.adj_mode_combo = ctk.CTkComboBox(
            self.adjust_box,
            values=["➕ Add Stock", "➖ Subtract Stock"],
            height=32,
            corner_radius=theme.RADIUS_INPUT,
            fg_color=theme.dual("bg_input"),
            border_color=theme.dual("border_input"),
            text_color=theme.dual("text_primary")
        )
        self.adj_mode_combo.grid(row=6, column=0, sticky="ew", padx=16, pady=(0, 10))
        self.adj_mode_combo.set("➕ Add Stock")

        # Amount Entry
        ctk.CTkLabel(self.adjust_box, text="Quantity Change *", font=theme.font_caption(weight="bold"), text_color=theme.dual("text_secondary")).grid(row=5, column=1, sticky="w", padx=16, pady=(0, 2))
        self.adj_qty_entry = ctk.CTkEntry(
            self.adjust_box,
            placeholder_text="e.g. 10",
            height=32,
            corner_radius=theme.RADIUS_INPUT,
            fg_color=theme.dual("bg_input"),
            border_color=theme.dual("border_input"),
            text_color=theme.dual("text_primary")
        )
        self.adj_qty_entry.grid(row=6, column=1, sticky="ew", padx=16, pady=(0, 10))

        # Quick Preset Buttons
        preset_frame = ctk.CTkFrame(self.adjust_box, fg_color="transparent")
        preset_frame.grid(row=7, column=0, columnspan=2, sticky="ew", padx=16, pady=(0, 12))
        for preset_val in ("5", "10", "25", "50"):
            p_btn = ctk.CTkButton(
                preset_frame,
                text=f"+{preset_val}",
                width=50,
                height=26,
                corner_radius=theme.RADIUS_BUTTON,
                font=theme.font_caption(weight="bold"),
                fg_color=theme.dual("bg_card_alt"),
                hover_color=theme.dual("bg_card_hover"),
                text_color=theme.dual("text_secondary"),
                border_width=1,
                border_color=theme.dual("border_subtle"),
                command=lambda v=preset_val: self._apply_preset_qty(v)
            )
            p_btn.pack(side="left", padx=(0, 6))

        # Apply Button
        self.btn_apply_adj = ctk.CTkButton(
            self.adjust_box,
            text="Confirm Stock Adjustment",
            fg_color=theme.dual("brand_primary"),
            hover_color=theme.dual("brand_primary_hover"),
            text_color=theme.dual("text_inverse"),
            font=theme.font_body(weight="bold"),
            corner_radius=theme.RADIUS_BUTTON,
            height=34,
            command=self._apply_adjustment
        )
        self.btn_apply_adj.grid(row=8, column=0, columnspan=2, sticky="ew", padx=16, pady=(0, 16))

        # 2. Add New Product Card
        self.add_box = ctk.CTkFrame(
            self.form_panel,
            fg_color=theme.dual("bg_card"),
            corner_radius=theme.RADIUS_CARD,
            border_width=1,
            border_color=theme.dual("border_card")
        )
        self.add_box.grid(row=1, column=0, sticky="ew", pady=(0, 14))
        self.add_box.grid_columnconfigure((0, 1), weight=1)

        reg_hdr = ctk.CTkLabel(
            self.add_box,
            text="🆕 Register New Stock Item",
            font=theme.font_title(size=14),
            text_color=theme.dual("text_primary"),
            anchor="w"
        )
        reg_hdr.grid(row=0, column=0, columnspan=2, sticky="w", padx=16, pady=(14, 4))

        reg_sub = ctk.CTkLabel(
            self.add_box,
            text="Add supplies, chemicals, seeds, or farm implements",
            font=theme.font_caption(),
            text_color=theme.dual("text_muted"),
            anchor="w"
        )
        reg_sub.grid(row=1, column=0, columnspan=2, sticky="w", padx=16, pady=(0, 10))

        # Item Name
        ctk.CTkLabel(self.add_box, text="Item Name *", font=theme.font_caption(weight="bold"), text_color=theme.dual("text_secondary")).grid(row=2, column=0, columnspan=2, sticky="w", padx=16, pady=(0, 2))
        self.new_name_entry = ctk.CTkEntry(self.add_box, placeholder_text="e.g. Phosphate Fertilizer", height=32, corner_radius=theme.RADIUS_INPUT, fg_color=theme.dual("bg_input"), border_color=theme.dual("border_input"), text_color=theme.dual("text_primary"))
        self.new_name_entry.grid(row=3, column=0, columnspan=2, sticky="ew", padx=16, pady=(0, 10))

        # Category
        ctk.CTkLabel(self.add_box, text="Category", font=theme.font_caption(weight="bold"), text_color=theme.dual("text_secondary")).grid(row=4, column=0, sticky="w", padx=16, pady=(0, 2))
        self.new_cat_combo = ctk.CTkComboBox(self.add_box, values=["Seeds", "Fertilizer", "Pesticide", "Tools"], height=32, corner_radius=theme.RADIUS_INPUT, fg_color=theme.dual("bg_input"), border_color=theme.dual("border_input"), text_color=theme.dual("text_primary"))
        self.new_cat_combo.grid(row=5, column=0, sticky="ew", padx=16, pady=(0, 10))
        self.new_cat_combo.set("Seeds")

        # Unit of Measure
        ctk.CTkLabel(self.add_box, text="Unit of Measure *", font=theme.font_caption(weight="bold"), text_color=theme.dual("text_secondary")).grid(row=4, column=1, sticky="w", padx=16, pady=(0, 2))
        self.new_unit_entry = ctk.CTkEntry(self.add_box, placeholder_text="e.g. kg, liters, units", height=32, corner_radius=theme.RADIUS_INPUT, fg_color=theme.dual("bg_input"), border_color=theme.dual("border_input"), text_color=theme.dual("text_primary"))
        self.new_unit_entry.grid(row=5, column=1, sticky="ew", padx=16, pady=(0, 10))

        # Initial Quantity
        ctk.CTkLabel(self.add_box, text="Initial Stock Quantity *", font=theme.font_caption(weight="bold"), text_color=theme.dual("text_secondary")).grid(row=6, column=0, columnspan=2, sticky="w", padx=16, pady=(0, 2))
        self.new_qty_entry = ctk.CTkEntry(self.add_box, placeholder_text="e.g. 50", height=32, corner_radius=theme.RADIUS_INPUT, fg_color=theme.dual("bg_input"), border_color=theme.dual("border_input"), text_color=theme.dual("text_primary"))
        self.new_qty_entry.grid(row=7, column=0, columnspan=2, sticky="ew", padx=16, pady=(0, 12))

        # Register Button
        self.btn_register = ctk.CTkButton(
            self.add_box,
            text="Register Item in Inventory",
            fg_color=theme.dual("accent_blue"),
            hover_color=theme.dual("accent_blue_hover"),
            text_color=theme.dual("text_inverse"),
            font=theme.font_body(weight="bold"),
            corner_radius=theme.RADIUS_BUTTON,
            height=34,
            command=self._register_item
        )
        self.btn_register.grid(row=8, column=0, columnspan=2, sticky="ew", padx=16, pady=(0, 16))

        # 3. Delete Selected Item Card
        self.delete_box = ctk.CTkFrame(
            self.form_panel,
            fg_color=theme.dual("bg_card"),
            corner_radius=theme.RADIUS_CARD,
            border_width=1,
            border_color=theme.dual("border_card")
        )
        self.delete_box.grid(row=2, column=0, sticky="ew", pady=(0, 16))
        self.delete_box.grid_columnconfigure(0, weight=1)

        del_hdr = ctk.CTkLabel(
            self.delete_box,
            text="🗑️ Remove Stock Item",
            font=theme.font_title(size=14),
            text_color=theme.dual("text_primary"),
            anchor="w"
        )
        del_hdr.pack(anchor="w", padx=16, pady=(14, 2))

        self.del_target_lbl = ctk.CTkLabel(
            self.delete_box,
            text="No item selected (click a row to choose)",
            font=theme.font_caption(),
            text_color=theme.dual("text_muted"),
            anchor="w"
        )
        self.del_target_lbl.pack(anchor="w", padx=16, pady=(0, 10))

        self.btn_delete_item = ctk.CTkButton(
            self.delete_box,
            text="Delete Selected Stock Item",
            fg_color=theme.dual("accent_rose"),
            hover_color=theme.dual("accent_rose_hover"),
            text_color=theme.dual("text_inverse"),
            font=theme.font_body(weight="bold"),
            corner_radius=theme.RADIUS_BUTTON,
            height=34,
            command=self._delete_item
        )
        self.btn_delete_item.pack(fill="x", padx=16, pady=(0, 16))

    def _apply_preset_qty(self, val: str):
        self.adj_qty_entry.delete(0, "end")
        self.adj_qty_entry.insert(0, val)

    def _set_category_filter(self, cat: str):
        self.active_category_filter = cat
        for c, btn in self.cat_buttons.items():
            if c == cat:
                btn.configure(
                    fg_color=theme.dual("brand_primary_subtle"),
                    text_color=theme.dual("brand_primary_text"),
                    border_color=theme.dual("brand_primary")
                )
            else:
                btn.configure(
                    fg_color=theme.dual("bg_card_alt"),
                    text_color=theme.dual("text_secondary"),
                    border_color=theme.dual("border_subtle")
                )
        # If data hasn't been loaded yet (background warm failed silently),
        # refresh first so inventory_list is populated before filtering.
        if not self.inventory_list:
            self.refresh()
        else:
            self._apply_category_and_search()

    def _on_search_typed(self, event=None):
        if hasattr(self, "_search_timer") and self._search_timer:
            self.after_cancel(self._search_timer)
        self._search_timer = self.after(100, self._apply_category_and_search)

    def _apply_category_and_search(self):
        query = self.search_entry.get().strip().lower()
        items = list(self.inventory_list)

        # Apply category filter
        if self.active_category_filter != "All":
            items = [item for item in items if str(item.get("category", "")).lower() == self.active_category_filter.lower()]

        # Apply search query
        if query:
            items = [
                item for item in items
                if query in str(item.get("item_name", "")).lower()
                or query in str(item.get("category", "")).lower()
                or query in str(item.get("unit", "")).lower()
            ]

        key_mapping = ["item_name", "category", "quantity", "unit", "last_updated"]
        self.inventory_table.set_data(items, key_mapping=key_mapping)

    def refresh(self):
        """Loads and syncs inventory levels from SQL Server."""
        try:
            items = database.get_inventory()
            self.inventory_list = items

            # Update metrics count
            low_stock_items = [i for i in items if float(i.get("quantity", 0)) < 10.0]
            count_str = f"{len(items)} SKU{'s' if len(items) != 1 else ''} tracked"
            if low_stock_items:
                count_str += f"  •  ⚠️ {len(low_stock_items)} low on stock"
            self.sub_metrics_lbl.configure(text=count_str)

            # Apply table filtering
            self._apply_category_and_search()

            # Populate target item dropdown in quick adjustment frame
            item_names = [row["item_name"] for row in items]
            self.adj_item_combo.configure(values=item_names)

            if item_names:
                current = self.adj_item_combo.get()
                if current not in item_names:
                    self.adj_item_combo.set(item_names[0])
                self._update_balance_preview(self.adj_item_combo.get())
            else:
                self.adj_item_combo.set("")
                self.adj_balance_preview.configure(text="Current on-hand: —")

        except Exception as e:
            logger.error(f"Failed to refresh inventory: {e}")
            modal.show_error(self.winfo_toplevel(), "Database Error", f"Failed to refresh inventory: {e}")

    def _on_combo_item_selected(self, choice: str):
        self._update_balance_preview(choice)

    def _update_balance_preview(self, item_name: str):
        found = next((i for i in self.inventory_list if i.get("item_name") == item_name), None)
        if found:
            qty = found.get("quantity", 0)
            unit = found.get("unit", "")
            f_qty = float(qty) if isinstance(qty, (Decimal, int, float)) else 0.0
            color = theme.dual("accent_rose") if f_qty < 10.0 else theme.dual("brand_primary")
            self.adj_balance_preview.configure(
                text=f"Current on-hand: {f_qty:.2f} {unit}" + ("  (⚠️ Low Buffer)" if f_qty < 10.0 else ""),
                text_color=color
            )
            self.del_target_lbl.configure(
                text=f"Selected: {item_name} ({f_qty:.2f} {unit})",
                text_color=theme.dual("text_secondary")
            )
        else:
            self.adj_balance_preview.configure(text="Current on-hand: —")

    def _on_row_selected(self, row_data):
        self.selected_item_id = row_data.get("id")
        item_name = row_data.get("item_name", "")
        self.adj_item_combo.set(item_name)
        self._update_balance_preview(item_name)

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

        item_id = None
        for item in self.inventory_list:
            if item["item_name"] == selected_name:
                item_id = item["id"]
                break

        if not item_id:
            modal.show_error(self.winfo_toplevel(), "Error", "Selected item could not be found.")
            return

        multiplier = 1.0 if "Add" in adj_mode else -1.0
        adjustment = qty * multiplier

        success, res = database.adjust_inventory_stock(item_id, adjustment)
        if success:
            modal.show_info(self.winfo_toplevel(), "Success", "Stock level adjusted successfully!")
            self.adj_qty_entry.delete(0, "end")
            self.refresh()
            if hasattr(self.controller, "refresh_all_views"):
                self.controller.refresh_all_views()
        else:
            logger.error(f"Failed to adjust inventory stock: {res}")
            modal.show_error(self.winfo_toplevel(), "Adjustment Failed", str(res))

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
            if hasattr(self.controller, "refresh_all_views"):
                self.controller.refresh_all_views()
        else:
            logger.error(f"Failed to register inventory item: {res}")
            modal.show_error(self.winfo_toplevel(), "Database Error", f"Could not register item: {res}")

    def _delete_item(self):
        if not self.selected_item_id:
            combo_name = self.adj_item_combo.get()
            if combo_name:
                for item in self.inventory_list:
                    if item["item_name"] == combo_name:
                        self.selected_item_id = item["id"]
                        break

        if not self.selected_item_id:
            modal.show_error(self.winfo_toplevel(), "Selection Error", "Please select an item from the table or dropdown to delete.")
            return

        def confirm_callback(confirmed):
            if confirmed:
                success, res = database.delete_inventory_item(self.selected_item_id)
                if success:
                    modal.show_info(self.winfo_toplevel(), "Success", "Inventory item removed successfully.")
                    self.selected_item_id = None
                    self.del_target_lbl.configure(text="No item selected")
                    self.refresh()
                    if hasattr(self.controller, "refresh_all_views"):
                        self.controller.refresh_all_views()
                else:
                    logger.error(f"Failed to delete inventory item: {res}")
                    modal.show_error(self.winfo_toplevel(), "Database Error", f"Could not delete item: {res}")

        modal.ask_confirm(
            self.winfo_toplevel(),
            "Confirm Supply Removal",
            "Are you sure you want to permanently delete this inventory item?",
            confirm_callback
        )
