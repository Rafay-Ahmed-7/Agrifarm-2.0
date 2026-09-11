"""
widgets/table.py - High-performance, theme-adaptive data table component.

Features:
- State-cached widget pooling / recycling for sub-millisecond filtering and sorting
- Single-event binding per pooled widget to eliminate Tk event handler churn
- Dual-theme adaptive colors (dark & light mode support)
- Column header sorting with asc/desc indicators
- Rich status & stage pill badges with lazy widget allocation
- Alternating row styling with instant hover highlights
- In-memory search filtering
- Polished empty state
"""

from __future__ import annotations
import datetime
from decimal import Decimal
import customtkinter as ctk
import theme


class CustomTable(ctk.CTkFrame):
    def __init__(self, parent, headers, column_weights=None, on_row_select=None, **kwargs):
        super().__init__(
            parent,
            fg_color="transparent",
            **kwargs
        )

        self.headers = headers
        self.column_weights = column_weights if column_weights else [1] * len(headers)
        self.on_row_select = on_row_select

        self.raw_data_rows = []
        self.data_rows = []
        self.key_mapping = None
        self.selected_row_index = None
        self.selected_row_data = None
        self.row_widgets = []
        self.row_containers = []
        self.pool_rows = []
        self._empty_frame = None

        # Sort state
        self.sort_col_idx: int | None = None
        self.sort_descending = False

        # Active search query
        self.search_query = ""

        # Layout configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 1. Header Frame
        self.header_frame = ctk.CTkFrame(
            self,
            height=38,
            corner_radius=theme.RADIUS_INPUT,
            fg_color=theme.dual("bg_table_header"),
            border_width=1,
            border_color=theme.dual("border_subtle")
        )
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 6))

        for i, weight in enumerate(self.column_weights):
            try:
                w = int(float(weight))
            except Exception:
                w = 1
            self.header_frame.grid_columnconfigure(i, weight=w)

        self.header_buttons = []
        for i, header in enumerate(self.headers):
            hdr_btn = ctk.CTkButton(
                self.header_frame,
                text=header,
                font=theme.font_caption(weight="bold"),
                text_color=theme.dual("text_secondary"),
                fg_color="transparent",
                hover_color=theme.dual("bg_card_hover"),
                anchor="w",
                height=30,
                corner_radius=4,
                command=lambda col_idx=i: self._on_header_click(col_idx)
            )
            padx = (14, 4) if i == 0 else (4, 4)
            hdr_btn.grid(row=0, column=i, sticky="ew", padx=padx, pady=4)
            self.header_buttons.append(hdr_btn)

        # 2. Scrollable Body Frame
        self.body_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )
        self.body_frame.grid(row=1, column=0, sticky="nsew")

        for i, weight in enumerate(self.column_weights):
            try:
                w = int(float(weight))
            except Exception:
                w = 1
            self.body_frame.grid_columnconfigure(i, weight=w)

    def set_data(self, rows_list, key_mapping=None):
        """Populates the table with data rows using high-speed widget recycling."""
        new_rows = list(rows_list) if rows_list else []
        if (
            hasattr(self, "_last_set_data")
            and self._last_set_data == new_rows
            and self.key_mapping == key_mapping
            and not self.search_query
            and len(self.row_containers) == len(new_rows)
        ):
            return

        self._last_set_data = [dict(r) if isinstance(r, dict) else r for r in new_rows]
        self.raw_data_rows = new_rows
        self.key_mapping = key_mapping
        self._apply_filter_and_sort()

    def filter_data(self, query: str):
        """Filters rows containing the query in any cell."""
        self.search_query = (query or "").strip().lower()
        self._apply_filter_and_sort()

    def _apply_filter_and_sort(self):
        rows = list(self.raw_data_rows)

        # Filter
        if self.search_query:
            filtered = []
            for row in rows:
                if isinstance(row, dict):
                    vals = [str(v).lower() for v in row.values() if v is not None]
                elif isinstance(row, (list, tuple)):
                    vals = [str(v).lower() for v in row if v is not None]
                else:
                    vals = [str(row).lower()]

                if any(self.search_query in val for val in vals):
                    filtered.append(row)
            rows = filtered

        # Sort
        if self.sort_col_idx is not None and self.key_mapping:
            col_key = self.key_mapping[self.sort_col_idx]

            def sort_key(item):
                val = item.get(col_key) if isinstance(item, dict) else ""
                if val is None:
                    return ""
                if isinstance(val, (int, float, Decimal)):
                    return float(val)
                if isinstance(val, (datetime.date, datetime.datetime)):
                    return val.isoformat()
                return str(val).lower()

            try:
                rows.sort(key=sort_key, reverse=self.sort_descending)
            except Exception:
                pass

        self.data_rows = rows
        self._render_rows()

    def _on_header_click(self, col_idx: int):
        if self.sort_col_idx == col_idx:
            self.sort_descending = not self.sort_descending
        else:
            self.sort_col_idx = col_idx
            self.sort_descending = False

        # Update header texts with sort arrows
        for i, btn in enumerate(self.header_buttons):
            base_title = self.headers[i]
            if i == self.sort_col_idx:
                arrow = " ↓" if self.sort_descending else " ↑"
                btn.configure(text=f"{base_title}{arrow}", text_color=theme.dual("brand_primary"))
            else:
                btn.configure(text=base_title, text_color=theme.dual("text_secondary"))

        self._apply_filter_and_sort()

    def _render_rows(self):
        # Hide empty frame if previously shown
        if self._empty_frame:
            self._empty_frame.grid_remove()

        needed = len(self.data_rows)

        if needed == 0:
            for p in self.pool_rows:
                if p["gridded"]:
                    p["frame"].grid_remove()
                    p["gridded"] = False
            self.row_containers = []
            self.row_widgets = []
            self._show_empty_state()
            return

        # Ensure pool has enough rows
        while len(self.pool_rows) < needed:
            rf = ctk.CTkFrame(
                self.body_frame,
                corner_radius=0,
                border_width=0,
                cursor="hand2",
                height=34
            )
            rf.bind("<Button-1>", lambda e, f=rf: self._on_pooled_row_click(f))
            rf.bind("<Enter>", lambda e, f=rf: self._on_pooled_row_hover(f, True))
            rf.bind("<Leave>", lambda e, f=rf: self._on_pooled_row_hover(f, False))

            for col_idx, weight in enumerate(self.column_weights):
                rf.grid_columnconfigure(col_idx, weight=int(float(weight)))

            cells = []
            for col_idx in range(len(self.headers)):
                lbl = ctk.CTkLabel(
                    rf,
                    text="",
                    font=theme.font_body(),
                    text_color=theme.dual("text_primary"),
                    anchor="w"
                )
                lbl.bind("<Button-1>", lambda e, f=rf: self._on_pooled_row_click(f))
                cells.append({
                    "lbl": lbl,
                    "badge_frame": None,
                    "badge_lbl": None,
                    "active_widget": lbl,
                    "mode": None,
                    "text": None,
                    "badge_val": None
                })

            self.pool_rows.append({
                "frame": rf,
                "cells": cells,
                "bg": None,
                "gridded": False,
                "row_idx": None
            })

        # Render rows using recycled pool
        active_containers = []
        active_row_widgets = []

        for row_idx, row_data in enumerate(self.data_rows):
            p_row = self.pool_rows[row_idx]
            rf = p_row["frame"]
            cells = p_row["cells"]

            rf._row_idx = row_idx
            p_row["row_idx"] = row_idx

            is_selected = (row_idx == self.selected_row_index)
            even = (row_idx % 2 == 0)
            if is_selected:
                row_bg = theme.dual("bg_row_selected")
            else:
                row_bg = theme.dual("bg_row_even" if even else "bg_row_odd")

            if p_row["bg"] != row_bg:
                rf.configure(fg_color=row_bg)
                p_row["bg"] = row_bg

            row_cell_widgets = []

            for col_idx, header in enumerate(self.headers):
                cell_value = self._get_cell_value(row_data, col_idx)
                formatted_value = self._format_cell_value(cell_value)
                raw_str = str(cell_value).strip() if cell_value is not None else ""
                badge_spec = theme.BADGES.get(raw_str)
                is_low_inventory = self._is_low_stock(row_data, col_idx)

                col_key = self.key_mapping[col_idx] if self.key_mapping and col_idx < len(self.key_mapping) else ""
                is_badge = bool(badge_spec and col_key in ("stage", "status", "category", "action", "action_type", "Current Stage", "Stage", "Status", "Category", "Action", "Action Type"))

                padx = (14, 4) if col_idx == 0 else (4, 4)
                cell = cells[col_idx]

                if is_badge:
                    if cell["badge_frame"] is None:
                        bf = ctk.CTkFrame(
                            rf,
                            corner_radius=theme.RADIUS_BADGE,
                            border_width=1,
                            height=24
                        )
                        bl = ctk.CTkLabel(
                            bf,
                            text="",
                            font=theme.font_caption(weight="bold"),
                            anchor="center"
                        )
                        bl.pack(padx=10, pady=2)
                        bf.bind("<Button-1>", lambda e, f=rf: self._on_pooled_row_click(f))
                        bl.bind("<Button-1>", lambda e, f=rf: self._on_pooled_row_click(f))
                        cell["badge_frame"] = bf
                        cell["badge_lbl"] = bl

                    bf = cell["badge_frame"]
                    bl = cell["badge_lbl"]
                    if cell["badge_val"] != raw_str:
                        badge_style = theme.get_badge_style(raw_str)
                        bf.configure(fg_color=badge_style["bg"], border_color=badge_style["border"])
                        bl.configure(text=f"{badge_style['icon']}  {raw_str}", text_color=badge_style["fg"])
                        cell["badge_val"] = raw_str

                    if cell["mode"] != "badge":
                        cell["lbl"].grid_remove()
                        bf.grid(row=0, column=col_idx, sticky="w", padx=padx, pady=5)
                        cell["mode"] = "badge"

                    cell["active_widget"] = bf

                elif is_low_inventory:
                    pill_key = ("low", formatted_value)
                    if cell["badge_frame"] is None:
                        bf = ctk.CTkFrame(
                            rf,
                            corner_radius=theme.RADIUS_BADGE,
                            border_width=1,
                            height=24
                        )
                        bl = ctk.CTkLabel(
                            bf,
                            text="",
                            font=theme.font_caption(weight="bold"),
                            anchor="center"
                        )
                        bl.pack(padx=8, pady=2)
                        bf.bind("<Button-1>", lambda e, f=rf: self._on_pooled_row_click(f))
                        bl.bind("<Button-1>", lambda e, f=rf: self._on_pooled_row_click(f))
                        cell["badge_frame"] = bf
                        cell["badge_lbl"] = bl

                    bf = cell["badge_frame"]
                    bl = cell["badge_lbl"]
                    if cell["badge_val"] != pill_key:
                        bf.configure(fg_color=theme.dual("accent_rose_subtle"), border_color=theme.dual("accent_rose"))
                        bl.configure(text=f"⚠️ {formatted_value}", text_color=theme.dual("accent_rose"))
                        cell["badge_val"] = pill_key

                    if cell["mode"] != "badge":
                        cell["lbl"].grid_remove()
                        bf.grid(row=0, column=col_idx, sticky="w", padx=padx, pady=5)
                        cell["mode"] = "badge"

                    cell["active_widget"] = bf

                else:
                    lbl = cell["lbl"]
                    if cell["text"] != formatted_value:
                        lbl.configure(text=formatted_value)
                        cell["text"] = formatted_value

                    if cell["mode"] != "label":
                        if cell["badge_frame"] is not None:
                            cell["badge_frame"].grid_remove()
                        lbl.grid(row=0, column=col_idx, sticky="ew", padx=padx, pady=6)
                        cell["mode"] = "label"

                    cell["active_widget"] = lbl

                row_cell_widgets.append(cell["active_widget"])

            if not p_row["gridded"]:
                rf.grid(row=row_idx, column=0, columnspan=len(self.headers), sticky="ew", pady=1)
                p_row["gridded"] = True

            active_containers.append(rf)
            active_row_widgets.append(row_cell_widgets)

        # Hide surplus rows in pool
        for p in self.pool_rows[needed:]:
            if p["gridded"]:
                p["frame"].grid_remove()
                p["gridded"] = False

        self.row_containers = active_containers
        self.row_widgets = active_row_widgets

    def _on_pooled_row_click(self, row_frame):
        idx = getattr(row_frame, "_row_idx", None)
        if idx is not None:
            self._select_row(idx)

    def _on_pooled_row_hover(self, row_frame, is_entering: bool):
        idx = getattr(row_frame, "_row_idx", None)
        if idx is not None:
            self._on_hover(row_frame, idx, is_entering)

    def _show_empty_state(self):
        if self._empty_frame is None:
            self._empty_frame = ctk.CTkFrame(self.body_frame, fg_color="transparent")
            self._empty_icon = ctk.CTkLabel(
                self._empty_frame,
                text="📋",
                font=ctk.CTkFont(size=32),
                text_color=theme.dual("text_muted")
            )
            self._empty_icon.pack(pady=(0, 6))

            self._empty_title = ctk.CTkLabel(
                self._empty_frame,
                text="",
                font=theme.font_body(weight="bold"),
                text_color=theme.dual("text_secondary")
            )
            self._empty_title.pack()

            self._empty_hint = ctk.CTkLabel(
                self._empty_frame,
                text="",
                font=theme.font_caption(),
                text_color=theme.dual("text_muted")
            )
            self._empty_hint.pack(pady=(2, 0))

        title = f"No matches for '{self.search_query}'" if self.search_query else "No records found"
        hint = "Try a different search term." if self.search_query else "Use the action forms to add records or clear filters."
        self._empty_title.configure(text=title)
        self._empty_hint.configure(text=hint)
        self._empty_frame.grid(row=0, column=0, columnspan=len(self.headers), pady=50, sticky="nsew")
        self.row_widgets.append([self._empty_frame])

    def _get_cell_value(self, row_data, col_idx):
        if self.key_mapping and col_idx < len(self.key_mapping):
            return row_data.get(self.key_mapping[col_idx], "")
        if isinstance(row_data, dict):
            keys = list(row_data.keys())
            return row_data.get(keys[col_idx], "") if col_idx < len(keys) else ""
        if isinstance(row_data, (list, tuple)):
            return row_data[col_idx] if col_idx < len(row_data) else ""
        return str(row_data)

    def _format_cell_value(self, val):
        if isinstance(val, float):
            return f"{int(val)}" if val.is_integer() else f"{val:.2f}"
        if isinstance(val, Decimal):
            f_val = float(val)
            return f"{int(f_val)}" if f_val.is_integer() else f"{f_val:.2f}"
        if isinstance(val, (datetime.date, datetime.datetime)):
            return val.strftime("%Y-%m-%d")
        if val is None or val == "":
            return "—"
        return str(val)

    def _is_low_stock(self, row_data, col_idx) -> bool:
        if not isinstance(row_data, dict):
            return False
        col_key = self.key_mapping[col_idx] if self.key_mapping and col_idx < len(self.key_mapping) else ""
        if col_key not in ("quantity", "Quantity"):
            return False
        qty = row_data.get("quantity")
        if qty is not None:
            try:
                return float(qty) < 10.0
            except (ValueError, TypeError):
                pass
        return False

    def _on_hover(self, row_frame, row_idx: int, is_entering: bool):
        if row_idx == self.selected_row_index:
            return
        if is_entering:
            row_frame.configure(fg_color=theme.dual("bg_row_hover"))
        else:
            even = (row_idx % 2 == 0)
            row_frame.configure(fg_color=theme.dual("bg_row_even" if even else "bg_row_odd"))

    def _select_row(self, index: int):
        if not self.data_rows or index >= len(self.data_rows):
            return

        # Restore previous selection
        if self.selected_row_index is not None and self.selected_row_index < len(self.row_containers):
            prev_even = (self.selected_row_index % 2 == 0)
            try:
                prev_frame = self.row_containers[self.selected_row_index]
                prev_bg = theme.dual("bg_row_even" if prev_even else "bg_row_odd")
                prev_frame.configure(fg_color=prev_bg)
                if self.selected_row_index < len(self.pool_rows):
                    self.pool_rows[self.selected_row_index]["bg"] = prev_bg
            except Exception:
                pass

        # Highlight new selection
        self.selected_row_index = index
        self.selected_row_data = self.data_rows[index]

        try:
            cur_frame = self.row_containers[index]
            sel_bg = theme.dual("bg_row_selected")
            cur_frame.configure(fg_color=sel_bg)
            if index < len(self.pool_rows):
                self.pool_rows[index]["bg"] = sel_bg
        except Exception:
            pass

        if self.on_row_select:
            self.on_row_select(self.selected_row_data)

    def get_selected(self):
        return self.selected_row_data

    def clear(self):
        """Clears all table rows while preserving widget pool for instant reuse."""
        for p in self.pool_rows:
            if p["gridded"]:
                try:
                    p["frame"].grid_remove()
                    p["gridded"] = False
                except Exception:
                    pass
        if self._empty_frame:
            self._empty_frame.grid_remove()
        self.row_containers = []
        self.row_widgets = []
        self.raw_data_rows = []
        self.data_rows = []
        self._last_set_data = None
        self.selected_row_index = None
        self.selected_row_data = None

    def refresh(self):
        """Resets selection highlights."""
        if self.selected_row_index is not None and self.selected_row_index < len(self.row_containers):
            prev_even = (self.selected_row_index % 2 == 0)
            try:
                prev_frame = self.row_containers[self.selected_row_index]
                prev_bg = theme.dual("bg_row_even" if prev_even else "bg_row_odd")
                prev_frame.configure(fg_color=prev_bg)
                if self.selected_row_index < len(self.pool_rows):
                    self.pool_rows[self.selected_row_index]["bg"] = prev_bg
            except Exception:
                pass
        self.selected_row_index = None
        self.selected_row_data = None

    def _destroy_row_widgets(self):
        """Compatibility method for external callers."""
        self.clear()
