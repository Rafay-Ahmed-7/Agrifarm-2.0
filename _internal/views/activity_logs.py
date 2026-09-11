"""
views/activity_logs.py - Activity & Audit Trail Log Console for AgriFarm.

Displays system operations, CRUD events, stock ledger transactions,
and operational history with precise timestamps and searchable details.
"""

from __future__ import annotations
import logging
import customtkinter as ctk

import database
import theme
from widgets import modal
from widgets.table import CustomTable

logger = logging.getLogger("agrifarm.views.activity_logs")


class ActivityLogsView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.logs_data: list[dict] = []
        self.selected_log_id: int | None = None
        self.active_entity_filter = "All"

        # Main grid: Top stats -> Main container (table + details)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 1. Top Stat Badges / Filter Toolbar
        self._build_top_bar()

        # 2. Main Center Body (Table on left/center, detail sidebar on right)
        self._build_body()

    def _build_top_bar(self):
        self.top_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.top_bar.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 12))
        self.top_bar.grid_columnconfigure(1, weight=1)

        # Left: Quick Entity Type Filters
        left_filters = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        left_filters.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            left_filters,
            text="FILTER BY:",
            font=theme.font_micro(size=10),
            text_color=theme.dual("text_muted")
        ).pack(side="left", padx=(0, 10))

        self.filter_buttons = {}
        categories = [
            ("All", "All Activity"),
            ("Field", "🚜 Fields"),
            ("Crop", "🌱 Crops"),
            ("Inventory", "📦 Inventory"),
            ("System", "⚙️ System"),
        ]

        for code, label in categories:
            btn = ctk.CTkButton(
                left_filters,
                text=label,
                font=theme.font_caption(weight="bold"),
                corner_radius=theme.RADIUS_BADGE,
                height=30,
                width=80 if code == "All" else 100,
                fg_color=theme.dual("brand_primary_subtle") if code == "All" else "transparent",
                text_color=theme.dual("brand_primary_text") if code == "All" else theme.dual("text_secondary"),
                border_width=1,
                border_color=theme.dual("brand_primary") if code == "All" else theme.dual("border_input"),
                hover_color=theme.dual("bg_card_hover"),
                command=lambda c=code: self._set_entity_filter(c)
            )
            btn.pack(side="left", padx=3)
            self.filter_buttons[code] = btn

        # Right: Search Box + Clear Logs Button
        right_actions = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        right_actions.grid(row=0, column=1, sticky="e")

        self.search_entry = ctk.CTkEntry(
            right_actions,
            placeholder_text="🔍 Search logs...",
            height=32,
            width=200,
            corner_radius=theme.RADIUS_INPUT,
            fg_color=theme.dual("bg_input"),
            border_color=theme.dual("border_input"),
            text_color=theme.dual("text_primary")
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self._on_search_typed)

        self.btn_clear_logs = ctk.CTkButton(
            right_actions,
            text="🧹 Clear Logs",
            font=theme.font_caption(weight="bold"),
            height=32,
            width=100,
            corner_radius=theme.RADIUS_BUTTON,
            fg_color=theme.dual("bg_card"),
            hover_color=theme.dual("bg_card_hover"),
            text_color=theme.dual("text_secondary"),
            border_width=1,
            border_color=theme.dual("border_subtle"),
            command=self._confirm_clear_logs
        )
        self.btn_clear_logs.pack(side="left")

    def _build_body(self):
        self.body_frame = ctk.CTkFrame(
            self,
            fg_color=theme.dual("bg_card"),
            corner_radius=theme.RADIUS_CARD,
            border_width=1,
            border_color=theme.dual("border_card")
        )
        self.body_frame.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 20))
        self.body_frame.grid_columnconfigure(0, weight=3)
        self.body_frame.grid_columnconfigure(1, weight=1)
        self.body_frame.grid_rowconfigure(1, weight=1)

        # Header Info Banner
        info_header = ctk.CTkFrame(self.body_frame, fg_color="transparent")
        info_header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=(16, 10))
        info_header.grid_columnconfigure(0, weight=1)

        title_box = ctk.CTkFrame(info_header, fg_color="transparent")
        title_box.grid(row=0, column=0, sticky="w")

        self.lbl_title = ctk.CTkLabel(
            title_box,
            text="📋 System Activity & Transaction Audit Trail",
            font=theme.font_title(size=16),
            text_color=theme.dual("text_primary"),
            anchor="w"
        )
        self.lbl_title.pack(anchor="w")

        self.lbl_counter = ctk.CTkLabel(
            title_box,
            text="Showing 0 logged operations",
            font=theme.font_caption(),
            text_color=theme.dual("text_muted"),
            anchor="w"
        )
        self.lbl_counter.pack(anchor="w")

        # Table Component
        table_headers = ["Time", "Action", "Category", "Target Entity", "Operation Details"]
        column_weights = [2, 2, 1, 2, 4]

        self.logs_table = CustomTable(
            self.body_frame,
            headers=table_headers,
            column_weights=column_weights,
            on_row_select=self._on_row_selected
        )
        self.logs_table.grid(row=1, column=0, sticky="nsew", padx=(20, 10), pady=(0, 16))

        # Detail Inspector Card (Right Pane)
        self.inspector_card = ctk.CTkFrame(
            self.body_frame,
            fg_color=theme.dual("bg_card_alt"),
            corner_radius=theme.RADIUS_INPUT,
            border_width=1,
            border_color=theme.dual("border_subtle")
        )
        self.inspector_card.grid(row=1, column=1, sticky="nsew", padx=(0, 20), pady=(0, 16))
        self.inspector_card.grid_columnconfigure(0, weight=1)

        insp_header = ctk.CTkLabel(
            self.inspector_card,
            text="🔍 Log Inspector",
            font=theme.font_title(size=14),
            text_color=theme.dual("text_primary"),
            anchor="w"
        )
        insp_header.pack(fill="x", padx=16, pady=(16, 12))

        # Inspector Fields
        self.detail_time = self._create_inspector_row(self.inspector_card, "TIMESTAMP (UTC/LOCAL)", "Select a log entry")
        self.detail_action = self._create_inspector_row(self.inspector_card, "ACTION TYPE", "—")
        self.detail_entity = self._create_inspector_row(self.inspector_card, "TARGET ENTITY", "—")
        self.detail_desc = self._create_inspector_row(self.inspector_card, "DETAILS / PAYLOAD", "—", is_multiline=True)

        # Quick tip footer in inspector
        tip_box = ctk.CTkFrame(self.inspector_card, fg_color="transparent")
        tip_box.pack(fill="x", side="bottom", padx=16, pady=16)

        ctk.CTkLabel(
            tip_box,
            text="💡 DBMS Audit Trail",
            font=theme.font_caption(weight="bold"),
            text_color=theme.dual("brand_primary"),
            anchor="w"
        ).pack(anchor="w")

        ctk.CTkLabel(
            tip_box,
            text="All insert, update, stock and delete actions are permanently persisted to SQL Server dbo.ActivityLogs with server-side timestamps.",
            font=theme.font_caption(size=10),
            text_color=theme.dual("text_muted"),
            wraplength=200,
            justify="left",
            anchor="w"
        ).pack(anchor="w", pady=(2, 0))

    def _create_inspector_row(self, parent, label_text: str, default_val: str, is_multiline: bool = False):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=16, pady=(0, 12))

        ctk.CTkLabel(
            frame,
            text=label_text,
            font=theme.font_micro(size=9),
            text_color=theme.dual("text_muted"),
            anchor="w"
        ).pack(anchor="w", pady=(0, 2))

        val_lbl = ctk.CTkLabel(
            frame,
            text=default_val,
            font=theme.font_body(size=12, weight="normal"),
            text_color=theme.dual("text_primary"),
            anchor="w",
            wraplength=220 if is_multiline else 220,
            justify="left"
        )
        val_lbl.pack(anchor="w")
        return val_lbl

    def _set_entity_filter(self, code: str):
        self.active_entity_filter = code
        for c, btn in self.filter_buttons.items():
            if c == code:
                btn.configure(
                    fg_color=theme.dual("brand_primary_subtle"),
                    text_color=theme.dual("brand_primary_text"),
                    border_color=theme.dual("brand_primary")
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=theme.dual("text_secondary"),
                    border_color=theme.dual("border_input")
                )
        self._apply_filtering()

    def _on_search_typed(self, event=None):
        self._apply_filtering()

    def _apply_filtering(self):
        query = self.search_entry.get().strip().lower()
        filtered = []
        for log in self.logs_data:
            # Category match
            if self.active_entity_filter != "All":
                if log.get("entity_type", "").lower() != self.active_entity_filter.lower():
                    continue

            # Text query match
            if query:
                combined = f"{log.get('performed_at', '')} {log.get('action_type', '')} {log.get('entity_type', '')} {log.get('entity_name', '')} {log.get('details', '')}".lower()
                if query not in combined:
                    continue

            filtered.append(log)

        # Map to table format
        key_mapping = ["performed_at", "action_type", "entity_type", "entity_name", "details"]
        self.logs_table.set_data(filtered, key_mapping=key_mapping)
        self.lbl_counter.configure(text=f"Showing {len(filtered)} of {len(self.logs_data)} logged operations")

    def _on_row_selected(self, row_data: dict):
        self.selected_log_id = row_data.get("id")
        self.detail_time.configure(text=row_data.get("performed_at", "—"))
        self.detail_action.configure(text=f"{row_data.get('action_type', '—')} ({row_data.get('entity_type', '')})")
        self.detail_entity.configure(text=row_data.get("entity_name", "—"))
        self.detail_desc.configure(text=row_data.get("details", "—") or "No additional notes")

    def _confirm_clear_logs(self):
        def callback(confirmed):
            if confirmed:
                success, res = database.clear_activity_logs()
                if success:
                    modal.show_info(self.winfo_toplevel(), "Logs Cleared", "Activity logs have been successfully reset.")
                    self.refresh()
                else:
                    modal.show_error(self.winfo_toplevel(), "Database Error", f"Could not clear logs: {res}")

        modal.ask_confirm(
            self.winfo_toplevel(),
            "Clear Log History",
            "Are you sure you want to clear all operational activity logs?",
            callback
        )

    def refresh(self):
        """Loads live logs from SQL Server database."""
        try:
            logs = database.get_activity_logs(limit=200)
            self.logs_data = logs
            self._apply_filtering()

            # Reset inspector if selection no longer exists
            if not any(l.get("id") == self.selected_log_id for l in logs):
                self.selected_log_id = None
                self.detail_time.configure(text="Select a log entry")
                self.detail_action.configure(text="—")
                self.detail_entity.configure(text="—")
                self.detail_desc.configure(text="—")
        except Exception as e:
            logger.error(f"Failed to refresh activity logs: {e}")
            modal.show_error(self.winfo_toplevel(), "Database Error", f"Failed to fetch logs: {e}")
