"""
views/crop_tracker.py - Executive Crop and Field Management Workbench.

Provides synchronized, dual-panel CRUD interfaces for:
1. Field acreage, soil profiles, and plot operational status.
2. Cultivated crops, growth stage progression, and planting/harvest schedules.
"""

from __future__ import annotations
import datetime
import logging
import customtkinter as ctk

import database
import theme
from logger import logger
from widgets import modal
from widgets.table import CustomTable


class CropTrackerView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        # 2-column grid layout
        self.grid_columnconfigure((0, 1), weight=1, uniform="panels")
        self.grid_rowconfigure(0, weight=1)

        self.selected_field_id: int | None = None
        self.selected_crop_id: int | None = None
        self.fields_list: list[dict] = []

        # =====================================================================
        # LEFT COLUMN: FIELDS WORKBENCH
        # =====================================================================
        self.fields_panel = ctk.CTkFrame(
            self,
            fg_color=theme.dual("bg_card"),
            corner_radius=theme.RADIUS_CARD,
            border_width=1,
            border_color=theme.dual("border_card")
        )
        self.fields_panel.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=16)
        self.fields_panel.grid_columnconfigure(0, weight=1)
        self.fields_panel.grid_rowconfigure(2, weight=1)  # Expand table

        # Fields Header
        f_header = ctk.CTkFrame(self.fields_panel, fg_color="transparent")
        f_header.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))
        f_header.grid_columnconfigure(0, weight=1)

        f_title_box = ctk.CTkFrame(f_header, fg_color="transparent")
        f_title_box.grid(row=0, column=0, sticky="w")

        self.f_panel_title = ctk.CTkLabel(
            f_title_box,
            text="🚜 Fields & Plots",
            font=theme.font_title(size=15),
            text_color=theme.dual("text_primary"),
            anchor="w"
        )
        self.f_panel_title.pack(anchor="w")

        self.f_count_lbl = ctk.CTkLabel(
            f_title_box,
            text="0 plots registered",
            font=theme.font_caption(),
            text_color=theme.dual("text_muted"),
            anchor="w"
        )
        self.f_count_lbl.pack(anchor="w")

        # Field Search
        self.f_search_entry = ctk.CTkEntry(
            f_header,
            placeholder_text="🔍 Filter fields...",
            height=30,
            width=160,
            corner_radius=theme.RADIUS_INPUT,
            fg_color=theme.dual("bg_input"),
            border_color=theme.dual("border_input"),
            text_color=theme.dual("text_primary")
        )
        self.f_search_entry.bind("<KeyRelease>", self._on_field_search)

        # Fields Table
        fields_headers = ["Name", "Area (Ac)", "Soil Type", "Status"]
        fields_mapping = ["name", "area_acres", "soil_type", "status"]
        self.fields_table = CustomTable(
            self.fields_panel,
            headers=fields_headers,
            column_weights=[2, 1, 2, 2],
            on_row_select=self._on_field_row_selected
        )
        self.fields_table.grid(row=2, column=0, sticky="nsew", padx=16, pady=(0, 10))

        # Fields Form Card
        self.fields_form = ctk.CTkFrame(
            self.fields_panel,
            fg_color=theme.dual("bg_card_alt"),
            corner_radius=theme.RADIUS_CARD,
            border_width=1,
            border_color=theme.dual("border_subtle")
        )
        self.fields_form.grid(row=3, column=0, sticky="ew", padx=16, pady=(0, 16))
        self.fields_form.grid_columnconfigure((0, 1), weight=1)

        # Form Mode Banner
        self.f_banner = ctk.CTkLabel(
            self.fields_form,
            text="✦ MODE: New Field Entry",
            font=theme.font_micro(size=9),
            text_color=theme.dual("brand_primary"),
            anchor="w"
        )
        self.f_banner.grid(row=0, column=0, columnspan=2, sticky="w", padx=14, pady=(10, 4))

        # Fields Form Inputs
        lbl_fname = ctk.CTkLabel(self.fields_form, text="Field Name *", font=theme.font_caption(weight="bold"), text_color=theme.dual("text_secondary"))
        lbl_fname.grid(row=1, column=0, sticky="w", padx=14, pady=(4, 2))
        self.f_name_entry = ctk.CTkEntry(self.fields_form, placeholder_text="e.g. North Meadow", height=32, corner_radius=theme.RADIUS_INPUT, fg_color=theme.dual("bg_input"), border_color=theme.dual("border_input"), text_color=theme.dual("text_primary"))
        self.f_name_entry.grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 8))

        lbl_farea = ctk.CTkLabel(self.fields_form, text="Area (Acres) *", font=theme.font_caption(weight="bold"), text_color=theme.dual("text_secondary"))
        lbl_farea.grid(row=1, column=1, sticky="w", padx=14, pady=(4, 2))
        self.f_area_entry = ctk.CTkEntry(self.fields_form, placeholder_text="e.g. 10.5", height=32, corner_radius=theme.RADIUS_INPUT, fg_color=theme.dual("bg_input"), border_color=theme.dual("border_input"), text_color=theme.dual("text_primary"))
        self.f_area_entry.grid(row=2, column=1, sticky="ew", padx=14, pady=(0, 8))

        lbl_fsoil = ctk.CTkLabel(self.fields_form, text="Soil Type", font=theme.font_caption(weight="bold"), text_color=theme.dual("text_secondary"))
        lbl_fsoil.grid(row=3, column=0, sticky="w", padx=14, pady=(2, 2))
        self.f_soil_entry = ctk.CTkEntry(self.fields_form, placeholder_text="e.g. Clay Loam", height=32, corner_radius=theme.RADIUS_INPUT, fg_color=theme.dual("bg_input"), border_color=theme.dual("border_input"), text_color=theme.dual("text_primary"))
        self.f_soil_entry.grid(row=4, column=0, sticky="ew", padx=14, pady=(0, 10))

        lbl_fstatus = ctk.CTkLabel(self.fields_form, text="Status", font=theme.font_caption(weight="bold"), text_color=theme.dual("text_secondary"))
        lbl_fstatus.grid(row=3, column=1, sticky="w", padx=14, pady=(2, 2))
        self.f_status_combo = ctk.CTkComboBox(self.fields_form, values=["Active", "Fallow", "Resting"], height=32, corner_radius=theme.RADIUS_INPUT, fg_color=theme.dual("bg_input"), border_color=theme.dual("border_input"), text_color=theme.dual("text_primary"))
        self.f_status_combo.grid(row=4, column=1, sticky="ew", padx=14, pady=(0, 10))
        self.f_status_combo.set("Active")

        # Action Buttons Row
        self.fields_btn_frame = ctk.CTkFrame(self.fields_form, fg_color="transparent")
        self.fields_btn_frame.grid(row=5, column=0, columnspan=2, sticky="ew", padx=14, pady=(4, 12))
        self.fields_btn_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.btn_field_add = ctk.CTkButton(
            self.fields_btn_frame,
            text="➕ Add Field",
            fg_color=theme.dual("brand_primary"),
            hover_color=theme.dual("brand_primary_hover"),
            text_color=theme.dual("text_inverse"),
            font=theme.font_body(weight="bold"),
            corner_radius=theme.RADIUS_BUTTON,
            height=32,
            command=self._add_field
        )
        self.btn_field_add.grid(row=0, column=0, padx=3, sticky="ew")

        self.btn_field_update = ctk.CTkButton(
            self.fields_btn_frame,
            text="💾 Save",
            fg_color=theme.dual("accent_blue"),
            hover_color=theme.dual("accent_blue_hover"),
            text_color=theme.dual("text_inverse"),
            font=theme.font_body(weight="bold"),
            corner_radius=theme.RADIUS_BUTTON,
            height=32,
            command=self._update_field
        )
        self.btn_field_update.grid(row=0, column=1, padx=3, sticky="ew")

        self.btn_field_delete = ctk.CTkButton(
            self.fields_btn_frame,
            text="🗑️ Delete",
            fg_color=theme.dual("accent_rose"),
            hover_color=theme.dual("accent_rose_hover"),
            text_color=theme.dual("text_inverse"),
            font=theme.font_body(weight="bold"),
            corner_radius=theme.RADIUS_BUTTON,
            height=32,
            command=self._delete_field
        )
        self.btn_field_delete.grid(row=0, column=2, padx=3, sticky="ew")

        self.btn_field_clear = ctk.CTkButton(
            self.fields_btn_frame,
            text="✖ Deselect",
            fg_color="transparent",
            hover_color=theme.dual("bg_card_hover"),
            text_color=theme.dual("text_secondary"),
            border_width=1,
            border_color=theme.dual("border_subtle"),
            font=theme.font_caption(),
            corner_radius=theme.RADIUS_BUTTON,
            height=32,
            command=self._clear_field_form
        )
        self.btn_field_clear.grid(row=0, column=3, padx=3, sticky="ew")

        # =====================================================================
        # RIGHT COLUMN: CROPS WORKBENCH
        # =====================================================================
        self.crops_panel = ctk.CTkFrame(
            self,
            fg_color=theme.dual("bg_card"),
            corner_radius=theme.RADIUS_CARD,
            border_width=1,
            border_color=theme.dual("border_card")
        )
        self.crops_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=16)
        self.crops_panel.grid_columnconfigure(0, weight=1)
        self.crops_panel.grid_rowconfigure(2, weight=1)

        # Crops Header
        c_header = ctk.CTkFrame(self.crops_panel, fg_color="transparent")
        c_header.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))
        c_header.grid_columnconfigure(0, weight=1)

        c_title_box = ctk.CTkFrame(c_header, fg_color="transparent")
        c_title_box.grid(row=0, column=0, sticky="w")

        self.c_panel_title = ctk.CTkLabel(
            c_title_box,
            text="🌱 Cultivated Crops",
            font=theme.font_title(size=15),
            text_color=theme.dual("text_primary"),
            anchor="w"
        )
        self.c_panel_title.pack(anchor="w")

        self.c_count_lbl = ctk.CTkLabel(
            c_title_box,
            text="0 crops tracked",
            font=theme.font_caption(),
            text_color=theme.dual("text_muted"),
            anchor="w"
        )
        self.c_count_lbl.pack(anchor="w")

        # Crop Search
        self.c_search_entry = ctk.CTkEntry(
            c_header,
            placeholder_text="🔍 Filter crops...",
            height=30,
            width=160,
            corner_radius=theme.RADIUS_INPUT,
            fg_color=theme.dual("bg_input"),
            border_color=theme.dual("border_input"),
            text_color=theme.dual("text_primary")
        )
        self.c_search_entry.grid(row=0, column=1, sticky="e")
        self.c_search_entry.bind("<KeyRelease>", self._on_crop_search)

        # Crops Table
        crops_headers = ["Crop", "Variety", "Field", "Planting Date", "Stage"]
        crops_mapping = ["name", "variety", "field_name", "planting_date", "stage"]
        self.crops_table = CustomTable(
            self.crops_panel,
            headers=crops_headers,
            column_weights=[2, 2, 2, 2, 2],
            on_row_select=self._on_crop_row_selected
        )
        self.crops_table.grid(row=2, column=0, sticky="nsew", padx=16, pady=(0, 10))

        # Crops Form Card
        self.crops_form = ctk.CTkFrame(
            self.crops_panel,
            fg_color=theme.dual("bg_card_alt"),
            corner_radius=theme.RADIUS_CARD,
            border_width=1,
            border_color=theme.dual("border_subtle")
        )
        self.crops_form.grid(row=3, column=0, sticky="ew", padx=16, pady=(0, 16))
        self.crops_form.grid_columnconfigure((0, 1), weight=1)

        # Crop Form Banner
        self.c_banner = ctk.CTkLabel(
            self.crops_form,
            text="✦ MODE: New Crop Entry",
            font=theme.font_micro(size=9),
            text_color=theme.dual("brand_primary"),
            anchor="w"
        )
        self.c_banner.grid(row=0, column=0, columnspan=2, sticky="w", padx=14, pady=(10, 4))

        # Crop Form Inputs
        lbl_cname = ctk.CTkLabel(self.crops_form, text="Crop Name *", font=theme.font_caption(weight="bold"), text_color=theme.dual("text_secondary"))
        lbl_cname.grid(row=1, column=0, sticky="w", padx=14, pady=(4, 2))
        self.c_name_entry = ctk.CTkEntry(self.crops_form, placeholder_text="e.g. Corn", height=32, corner_radius=theme.RADIUS_INPUT, fg_color=theme.dual("bg_input"), border_color=theme.dual("border_input"), text_color=theme.dual("text_primary"))
        self.c_name_entry.grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 8))

        lbl_cvar = ctk.CTkLabel(self.crops_form, text="Variety", font=theme.font_caption(weight="bold"), text_color=theme.dual("text_secondary"))
        lbl_cvar.grid(row=1, column=1, sticky="w", padx=14, pady=(4, 2))
        self.c_variety_entry = ctk.CTkEntry(self.crops_form, placeholder_text="e.g. Sweet Yellow", height=32, corner_radius=theme.RADIUS_INPUT, fg_color=theme.dual("bg_input"), border_color=theme.dual("border_input"), text_color=theme.dual("text_primary"))
        self.c_variety_entry.grid(row=2, column=1, sticky="ew", padx=14, pady=(0, 8))

        lbl_cfield = ctk.CTkLabel(self.crops_form, text="Field Location *", font=theme.font_caption(weight="bold"), text_color=theme.dual("text_secondary"))
        lbl_cfield.grid(row=3, column=0, sticky="w", padx=14, pady=(2, 2))
        self.c_field_combo = ctk.CTkComboBox(self.crops_form, values=[], height=32, corner_radius=theme.RADIUS_INPUT, fg_color=theme.dual("bg_input"), border_color=theme.dual("border_input"), text_color=theme.dual("text_primary"))
        self.c_field_combo.grid(row=4, column=0, sticky="ew", padx=14, pady=(0, 8))

        lbl_cstage = ctk.CTkLabel(self.crops_form, text="Growth Stage", font=theme.font_caption(weight="bold"), text_color=theme.dual("text_secondary"))
        lbl_cstage.grid(row=3, column=1, sticky="w", padx=14, pady=(2, 2))
        self.c_stage_combo = ctk.CTkComboBox(self.crops_form, values=["Seedling", "Vegetative", "Flowering", "Harvest-Ready", "Harvested"], height=32, corner_radius=theme.RADIUS_INPUT, fg_color=theme.dual("bg_input"), border_color=theme.dual("border_input"), text_color=theme.dual("text_primary"))
        self.c_stage_combo.grid(row=4, column=1, sticky="ew", padx=14, pady=(0, 8))
        self.c_stage_combo.set("Seedling")

        lbl_cplant = ctk.CTkLabel(self.crops_form, text="Planting Date (YYYY-MM-DD) *", font=theme.font_caption(weight="bold"), text_color=theme.dual("text_secondary"))
        lbl_cplant.grid(row=5, column=0, sticky="w", padx=14, pady=(2, 2))
        self.c_planting_entry = ctk.CTkEntry(self.crops_form, placeholder_text="YYYY-MM-DD", height=32, corner_radius=theme.RADIUS_INPUT, fg_color=theme.dual("bg_input"), border_color=theme.dual("border_input"), text_color=theme.dual("text_primary"))
        self.c_planting_entry.grid(row=6, column=0, sticky="ew", padx=14, pady=(0, 10))

        lbl_charv = ctk.CTkLabel(self.crops_form, text="Expected Harvest (YYYY-MM-DD)", font=theme.font_caption(weight="bold"), text_color=theme.dual("text_secondary"))
        lbl_charv.grid(row=5, column=1, sticky="w", padx=14, pady=(2, 2))
        self.c_harvest_entry = ctk.CTkEntry(self.crops_form, placeholder_text="YYYY-MM-DD", height=32, corner_radius=theme.RADIUS_INPUT, fg_color=theme.dual("bg_input"), border_color=theme.dual("border_input"), text_color=theme.dual("text_primary"))
        self.c_harvest_entry.grid(row=6, column=1, sticky="ew", padx=14, pady=(0, 10))

        # Default dates
        self.c_planting_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        self.c_harvest_entry.insert(0, (datetime.date.today() + datetime.timedelta(days=90)).strftime("%Y-%m-%d"))

        # Crops Action Buttons
        self.crops_btn_frame = ctk.CTkFrame(self.crops_form, fg_color="transparent")
        self.crops_btn_frame.grid(row=7, column=0, columnspan=2, sticky="ew", padx=14, pady=(4, 12))
        self.crops_btn_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.btn_crop_add = ctk.CTkButton(
            self.crops_btn_frame,
            text="➕ Plant Crop",
            fg_color=theme.dual("brand_primary"),
            hover_color=theme.dual("brand_primary_hover"),
            text_color=theme.dual("text_inverse"),
            font=theme.font_body(weight="bold"),
            corner_radius=theme.RADIUS_BUTTON,
            height=32,
            command=self._add_crop
        )
        self.btn_crop_add.grid(row=0, column=0, padx=3, sticky="ew")

        self.btn_crop_update = ctk.CTkButton(
            self.crops_btn_frame,
            text="💾 Save",
            fg_color=theme.dual("accent_blue"),
            hover_color=theme.dual("accent_blue_hover"),
            text_color=theme.dual("text_inverse"),
            font=theme.font_body(weight="bold"),
            corner_radius=theme.RADIUS_BUTTON,
            height=32,
            command=self._update_crop
        )
        self.btn_crop_update.grid(row=0, column=1, padx=3, sticky="ew")

        self.btn_crop_delete = ctk.CTkButton(
            self.crops_btn_frame,
            text="🗑️ Delete",
            fg_color=theme.dual("accent_rose"),
            hover_color=theme.dual("accent_rose_hover"),
            text_color=theme.dual("text_inverse"),
            font=theme.font_body(weight="bold"),
            corner_radius=theme.RADIUS_BUTTON,
            height=32,
            command=self._delete_crop
        )
        self.btn_crop_delete.grid(row=0, column=2, padx=3, sticky="ew")

        self.btn_crop_clear = ctk.CTkButton(
            self.crops_btn_frame,
            text="✖ Deselect",
            fg_color="transparent",
            hover_color=theme.dual("bg_card_hover"),
            text_color=theme.dual("text_secondary"),
            border_width=1,
            border_color=theme.dual("border_subtle"),
            font=theme.font_caption(),
            corner_radius=theme.RADIUS_BUTTON,
            height=32,
            command=self._clear_crop_form
        )
    def _on_field_search(self, event=None):
        if hasattr(self, "_f_search_timer") and self._f_search_timer:
            self.after_cancel(self._f_search_timer)
        self._f_search_timer = self.after(100, self._do_field_search)

    def _do_field_search(self):
        self.fields_table.filter_data(self.f_search_entry.get())

    def _on_crop_search(self, event=None):
        if hasattr(self, "_c_search_timer") and self._c_search_timer:
            self.after_cancel(self._c_search_timer)
        self._c_search_timer = self.after(100, self._do_crop_search)

    def _do_crop_search(self):
        self.crops_table.filter_data(self.c_search_entry.get())

    def refresh(self):
        """Reloads all field and crop records from SQL Server."""
        try:
            # 1. Fetch Fields
            fields = database.get_fields()
            self.fields_list = fields
            self.f_count_lbl.configure(text=f"{len(fields)} plot{'s' if len(fields) != 1 else ''} registered")

            fields_mapping = ["name", "area_acres", "soil_type", "status"]
            self.fields_table.set_data(fields, key_mapping=fields_mapping)

            # Re-apply active field filter if typed
            if self.f_search_entry.get().strip():
                self.fields_table.filter_data(self.f_search_entry.get())

            # Populate field combobox in crops form
            field_names = [f["name"] for f in fields]
            self.c_field_combo.configure(values=field_names)
            if field_names:
                current_selection = self.c_field_combo.get()
                if current_selection not in field_names:
                    self.c_field_combo.set(field_names[0])
            else:
                self.c_field_combo.set("")

            # 2. Fetch Crops
            crops = database.get_crops_with_fields()
            self.c_count_lbl.configure(text=f"{len(crops)} crop{'s' if len(crops) != 1 else ''} tracked")

            crops_mapping = ["name", "variety", "field_name", "planting_date", "stage"]
            self.crops_table.set_data(crops, key_mapping=crops_mapping)

            # Re-apply active crop filter if typed
            if self.c_search_entry.get().strip():
                self.crops_table.filter_data(self.c_search_entry.get())

        except Exception as e:
            logger.error(f"Failed to refresh crop tracker: {e}")
            modal.show_error(self.winfo_toplevel(), "Database Error", f"Failed to refresh data: {e}")

    # =====================================================================
    # FIELDS CRUD LOGIC
    # =====================================================================
    def _on_field_row_selected(self, row_data):
        self.selected_field_id = row_data.get("id")
        self.f_name_entry.delete(0, "end")
        self.f_name_entry.insert(0, row_data.get("name", ""))

        self.f_area_entry.delete(0, "end")
        self.f_area_entry.insert(0, str(row_data.get("area_acres", "")))

        self.f_soil_entry.delete(0, "end")
        self.f_soil_entry.insert(0, row_data.get("soil_type", "") or "")

        self.f_status_combo.set(row_data.get("status", "Active"))

        # Update banner
        self.f_banner.configure(
            text=f"✦ EDITING: {row_data.get('name', 'Selected Field')} (ID: {self.selected_field_id})",
            text_color=theme.dual("accent_blue")
        )

    def _clear_field_form(self):
        self.selected_field_id = None
        self.f_name_entry.delete(0, "end")
        self.f_area_entry.delete(0, "end")
        self.f_soil_entry.delete(0, "end")
        self.f_status_combo.set("Active")
        self.f_banner.configure(
            text="✦ MODE: New Field Entry",
            text_color=theme.dual("brand_primary")
        )
        self.fields_table.refresh()

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
            if hasattr(self.controller, "refresh_all_views"):
                self.controller.refresh_all_views(affected_views={"Dashboard", "Crop Tracker"})
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
            modal.show_info(self.winfo_toplevel(), "Success", "Field details updated successfully!")
            self._clear_field_form()
            self.refresh()
            if hasattr(self.controller, "refresh_all_views"):
                self.controller.refresh_all_views(affected_views={"Dashboard", "Crop Tracker"})
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
                    modal.show_info(self.winfo_toplevel(), "Success", "Field and its associated crops deleted.")
                    self._clear_field_form()
                    self.refresh()
                    if hasattr(self.controller, "refresh_all_views"):
                        self.controller.refresh_all_views(affected_views={"Dashboard", "Crop Tracker"})
                else:
                    modal.show_error(self.winfo_toplevel(), "Database Error", f"Could not delete field: {res}")

        modal.ask_confirm(
            self.winfo_toplevel(),
            "Confirm Field Removal",
            "Are you sure you want to delete this field?\nThis will permanently delete all crops planted in this plot.",
            confirm_callback
        )

    # =====================================================================
    # CROPS CRUD LOGIC
    # =====================================================================
    def _on_crop_row_selected(self, row_data):
        self.selected_crop_id = row_data.get("id")
        self.c_name_entry.delete(0, "end")
        self.c_name_entry.insert(0, row_data.get("name", ""))

        self.c_variety_entry.delete(0, "end")
        self.c_variety_entry.insert(0, row_data.get("variety", "") or "")

        self.c_field_combo.set(row_data.get("field_name", ""))
        self.c_stage_combo.set(row_data.get("stage", "Seedling"))

        self.c_planting_entry.delete(0, "end")
        planting = row_data.get("planting_date", "")
        if isinstance(planting, (datetime.date, datetime.datetime)):
            planting = planting.strftime("%Y-%m-%d")
        self.c_planting_entry.insert(0, str(planting) if planting else "")

        self.c_harvest_entry.delete(0, "end")
        harvest = row_data.get("expected_harvest", "")
        if isinstance(harvest, (datetime.date, datetime.datetime)):
            harvest = harvest.strftime("%Y-%m-%d")
        self.c_harvest_entry.insert(0, str(harvest) if harvest else "")

        # Update banner
        self.c_banner.configure(
            text=f"✦ EDITING: {row_data.get('name', 'Crop')} ({row_data.get('variety', '')})",
            text_color=theme.dual("accent_blue")
        )

    def _clear_crop_form(self):
        self.selected_crop_id = None
        self.c_name_entry.delete(0, "end")
        self.c_variety_entry.delete(0, "end")
        self.c_planting_entry.delete(0, "end")
        self.c_planting_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        self.c_harvest_entry.delete(0, "end")
        self.c_harvest_entry.insert(0, (datetime.date.today() + datetime.timedelta(days=90)).strftime("%Y-%m-%d"))
        self.c_banner.configure(
            text="✦ MODE: New Crop Entry",
            text_color=theme.dual("brand_primary")
        )
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
            modal.show_error(self.winfo_toplevel(), "Validation Error", "Please select a valid field plot. Add fields first if needed.")
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

        if expected_harvest and expected_harvest < planting_date:
            modal.show_error(self.winfo_toplevel(), "Validation Error", "Expected harvest date cannot be before planting date.")
            return

        success, res = database.add_crop(field_id, name, variety, planting_date, expected_harvest, stage)
        if success:
            modal.show_info(self.winfo_toplevel(), "Success", f"Crop '{name}' planted successfully!")
            self._clear_crop_form()
            self.refresh()
            if hasattr(self.controller, "refresh_all_views"):
                self.controller.refresh_all_views(affected_views={"Dashboard", "Crop Tracker"})
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

        if expected_harvest and expected_harvest < planting_date:
            modal.show_error(self.winfo_toplevel(), "Validation Error", "Expected harvest date cannot be before planting date.")
            return

        success, res = database.update_crop(self.selected_crop_id, field_id, name, variety, planting_date, expected_harvest, stage)
        if success:
            modal.show_info(self.winfo_toplevel(), "Success", "Crop details updated successfully!")
            self._clear_crop_form()
            self.refresh()
            if hasattr(self.controller, "refresh_all_views"):
                self.controller.refresh_all_views(affected_views={"Dashboard", "Crop Tracker"})
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
                    modal.show_info(self.winfo_toplevel(), "Success", "Crop record removed successfully.")
                    self._clear_crop_form()
                    self.refresh()
                    if hasattr(self.controller, "refresh_all_views"):
                        self.controller.refresh_all_views(affected_views={"Dashboard", "Crop Tracker"})
                else:
                    modal.show_error(self.winfo_toplevel(), "Database Error", f"Could not delete crop: {res}")

        modal.ask_confirm(
            self.winfo_toplevel(),
            "Confirm Crop Removal",
            "Are you sure you want to remove this crop record?",
            confirm_callback
        )
