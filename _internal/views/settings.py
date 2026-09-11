"""
views/settings.py - Enterprise System Diagnostics & Settings Command Center.

Features:
- Live SQL Server connectivity testing with diagnostic telemetry
- Schema integrity verification across all production tables
- Dark and Light appearance theme switching with live UI re-theming
- Application runtime environment and build metadata
"""

from __future__ import annotations
import platform
import sys
import time
import customtkinter as ctk

import config
import database
import theme
from widgets import modal


class SettingsView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        # 2-column grid layout
        self.grid_columnconfigure((0, 1), weight=1, uniform="settings_cols")
        self.grid_rowconfigure(0, weight=1)

        # =====================================================================
        # LEFT COLUMN: SQL SERVER TELEMETRY & DIAGNOSTICS
        # =====================================================================
        self.left_col = ctk.CTkFrame(self, fg_color="transparent")
        self.left_col.grid(row=0, column=0, sticky="nsew", padx=(24, 12), pady=20)
        self.left_col.grid_columnconfigure(0, weight=1)

        # Database Diagnostics Card
        self.db_card = ctk.CTkFrame(
            self.left_col,
            fg_color=theme.dual("bg_card"),
            corner_radius=theme.RADIUS_CARD,
            border_width=1,
            border_color=theme.dual("border_card")
        )
        self.db_card.pack(fill="x", pady=(0, 16))
        self.db_card.grid_columnconfigure(0, weight=1)

        # Card Header
        db_header = ctk.CTkFrame(self.db_card, fg_color="transparent")
        db_header.pack(fill="x", padx=20, pady=(20, 12))

        db_title = ctk.CTkLabel(
            db_header,
            text="🗄️ SQL Server Telemetry",
            font=theme.font_title(size=16),
            text_color=theme.dual("text_primary"),
            anchor="w"
        )
        db_title.pack(anchor="w")

        db_sub = ctk.CTkLabel(
            db_header,
            text="Production enterprise database connectivity and schema diagnostics",
            font=theme.font_caption(),
            text_color=theme.dual("text_muted"),
            anchor="w"
        )
        db_sub.pack(anchor="w")

        # Telemetry Spec Grid
        telemetry_box = ctk.CTkFrame(
            self.db_card,
            fg_color=theme.dual("bg_card_alt"),
            corner_radius=theme.RADIUS_INPUT,
            border_width=1,
            border_color=theme.dual("border_subtle")
        )
        telemetry_box.pack(fill="x", padx=20, pady=(0, 16))
        telemetry_box.grid_columnconfigure(1, weight=1)

        specs = [
            ("Target Server:", f"{database.SERVER}"),
            ("Database Catalog:", f"{database.DATABASE}"),
            ("Authentication:", "Windows Integrated (Trusted)"),
            ("ODBC Driver:", f"{database.DRIVER}"),
        ]

        for r_idx, (spec_label, spec_val) in enumerate(specs):
            s_lbl = ctk.CTkLabel(
                telemetry_box,
                text=spec_label,
                font=theme.font_caption(weight="bold"),
                text_color=theme.dual("text_secondary"),
                anchor="w"
            )
            s_lbl.grid(row=r_idx, column=0, sticky="w", padx=14, pady=6)

            v_lbl = ctk.CTkLabel(
                telemetry_box,
                text=spec_val,
                font=ctk.CTkFont(family="Consolas", size=11),
                text_color=theme.dual("brand_primary_text"),
                anchor="w"
            )
            v_lbl.grid(row=r_idx, column=1, sticky="w", padx=14, pady=6)

        # Status Indicators Box
        status_box = ctk.CTkFrame(self.db_card, fg_color="transparent")
        status_box.pack(fill="x", padx=20, pady=(0, 16))
        status_box.grid_columnconfigure((0, 1), weight=1)

        # Connection status pill
        self.conn_pill = ctk.CTkFrame(
            status_box,
            fg_color=theme.dual("bg_card_alt"),
            corner_radius=theme.RADIUS_INPUT,
            border_width=1,
            border_color=theme.dual("border_subtle")
        )
        self.conn_pill.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.status_label = ctk.CTkLabel(
            self.conn_pill,
            text="● Testing connection...",
            font=theme.font_caption(weight="bold"),
            text_color=theme.dual("text_secondary")
        )
        self.status_label.pack(padx=12, pady=8)

        # Schema status pill
        self.schema_pill = ctk.CTkFrame(
            status_box,
            fg_color=theme.dual("bg_card_alt"),
            corner_radius=theme.RADIUS_INPUT,
            border_width=1,
            border_color=theme.dual("border_subtle")
        )
        self.schema_pill.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        self.schema_label = ctk.CTkLabel(
            self.schema_pill,
            text="Checking schema...",
            font=theme.font_caption(weight="bold"),
            text_color=theme.dual("text_secondary")
        )
        self.schema_label.pack(padx=12, pady=8)

        # Database Action Buttons
        btn_row = ctk.CTkFrame(self.db_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=(0, 20))
        btn_row.grid_columnconfigure((0, 1), weight=1)

        self.btn_test = ctk.CTkButton(
            btn_row,
            text="🔍 Test Latency & Ping",
            font=theme.font_body(weight="bold"),
            fg_color=theme.dual("brand_primary"),
            hover_color=theme.dual("brand_primary_hover"),
            text_color=theme.dual("text_inverse"),
            corner_radius=theme.RADIUS_BUTTON,
            height=34,
            command=self._test_connection
        )
        self.btn_test.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        self.btn_reinit = ctk.CTkButton(
            btn_row,
            text="🔄 Verify Schema Tables",
            font=theme.font_body(weight="bold"),
            fg_color=theme.dual("accent_blue"),
            hover_color=theme.dual("accent_blue_hover"),
            text_color=theme.dual("text_inverse"),
            corner_radius=theme.RADIUS_BUTTON,
            height=34,
            command=self._verify_schema
        )
        self.btn_reinit.grid(row=0, column=1, sticky="ew", padx=(6, 0))

        # =====================================================================
        # RIGHT COLUMN: APPEARANCE & SYSTEM INFO
        # =====================================================================
        self.right_col = ctk.CTkFrame(self, fg_color="transparent")
        self.right_col.grid(row=0, column=1, sticky="nsew", padx=(12, 24), pady=20)
        self.right_col.grid_columnconfigure(0, weight=1)

        # Personalization Card
        self.theme_card = ctk.CTkFrame(
            self.right_col,
            fg_color=theme.dual("bg_card"),
            corner_radius=theme.RADIUS_CARD,
            border_width=1,
            border_color=theme.dual("border_card")
        )
        self.theme_card.pack(fill="x", pady=(0, 16))

        th_header = ctk.CTkFrame(self.theme_card, fg_color="transparent")
        th_header.pack(fill="x", padx=20, pady=(20, 12))

        th_title = ctk.CTkLabel(
            th_header,
            text="🎨 Theme & Visual Presentation",
            font=theme.font_title(size=16),
            text_color=theme.dual("text_primary"),
            anchor="w"
        )
        th_title.pack(anchor="w")

        th_sub = ctk.CTkLabel(
            th_header,
            text="Synchronized light and dark visual aesthetics",
            font=theme.font_caption(),
            text_color=theme.dual("text_muted"),
            anchor="w"
        )
        th_sub.pack(anchor="w")

        theme_action_box = ctk.CTkFrame(
            self.theme_card,
            fg_color=theme.dual("bg_card_alt"),
            corner_radius=theme.RADIUS_INPUT,
            border_width=1,
            border_color=theme.dual("border_subtle")
        )
        theme_action_box.pack(fill="x", padx=20, pady=(0, 20))
        theme_action_box.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            theme_action_box,
            text="Interface Mode:",
            font=theme.font_body(weight="bold"),
            text_color=theme.dual("text_secondary")
        ).grid(row=0, column=0, sticky="w", padx=16, pady=16)

        self.theme_switch = ctk.CTkOptionMenu(
            theme_action_box,
            values=["Dark Mode", "Light Mode"],
            font=theme.font_body(weight="bold"),
            corner_radius=theme.RADIUS_INPUT,
            height=32,
            fg_color=theme.dual("brand_primary"),
            button_color=theme.dual("brand_primary_hover"),
            text_color=theme.dual("text_inverse"),
            command=self._change_theme
        )
        self.theme_switch.grid(row=0, column=1, sticky="e", padx=16, pady=16)

        # Application System Information Card
        self.sys_info_card = ctk.CTkFrame(
            self.right_col,
            fg_color=theme.dual("bg_card"),
            corner_radius=theme.RADIUS_CARD,
            border_width=1,
            border_color=theme.dual("border_card")
        )
        self.sys_info_card.pack(fill="x")

        sys_header = ctk.CTkFrame(self.sys_info_card, fg_color="transparent")
        sys_header.pack(fill="x", padx=20, pady=(20, 12))

        sys_title = ctk.CTkLabel(
            sys_header,
            text="ℹ️ Application & Environment",
            font=theme.font_title(size=16),
            text_color=theme.dual("text_primary"),
            anchor="w"
        )
        sys_title.pack(anchor="w")

        sys_sub = ctk.CTkLabel(
            sys_header,
            text="Build runtime specifications and licensing",
            font=theme.font_caption(),
            text_color=theme.dual("text_muted"),
            anchor="w"
        )
        sys_sub.pack(anchor="w")

        sys_box = ctk.CTkFrame(
            self.sys_info_card,
            fg_color=theme.dual("bg_card_alt"),
            corner_radius=theme.RADIUS_INPUT,
            border_width=1,
            border_color=theme.dual("border_subtle")
        )
        sys_box.pack(fill="x", padx=20, pady=(0, 20))
        sys_box.grid_columnconfigure(1, weight=1)

        sys_specs = [
            ("Application:", "AgriFarm Enterprise v2.4"),
            ("Python Runtime:", f"{platform.python_version()} ({platform.architecture()[0]})"),
            ("Operating System:", f"{platform.system()} {platform.release()}"),
            ("Interface Stack:", "CustomTkinter 5.x / Native GPU"),
            ("Developer & Design:", "Rafay Ahmed"),
        ]

        for r_idx, (lbl_txt, val_txt) in enumerate(sys_specs):
            ctk.CTkLabel(
                sys_box,
                text=lbl_txt,
                font=theme.font_caption(weight="bold"),
                text_color=theme.dual("text_secondary"),
                anchor="w"
            ).grid(row=r_idx, column=0, sticky="w", padx=14, pady=5)

            ctk.CTkLabel(
                sys_box,
                text=val_txt,
                font=theme.font_caption(),
                text_color=theme.dual("text_primary"),
                anchor="w"
            ).grid(row=r_idx, column=1, sticky="w", padx=14, pady=5)

    def _change_theme(self, choice: str):
        mode = "dark" if choice == "Dark Mode" else "light"
        cfg = config.load_config()
        cfg["theme_mode"] = mode
        config.save_config(cfg)
        self.controller.update_theme_style(mode)
        self.controller.refresh_all_views()

    def refresh(self):
        """Refreshes live connection and schema status."""
        self._refresh_db_status()
        mode = config.load_config().get("theme_mode", "dark")
        self.theme_switch.set("Dark Mode" if mode == "dark" else "Light Mode")

    def _refresh_db_status(self):
        success, message = database.test_connection()
        if success:
            self.status_label.configure(
                text="● SQL Server: Connected",
                text_color=theme.dual("brand_primary")
            )
            self.conn_pill.configure(border_color=theme.dual("brand_primary"))
        else:
            self.status_label.configure(
                text="● SQL Server: Offline",
                text_color=theme.dual("accent_rose")
            )
            self.conn_pill.configure(border_color=theme.dual("accent_rose"))

        schema_ok, schema_message = database.initialize_db()
        self.schema_label.configure(
            text="✓ Schema: Verified" if schema_ok else f"✗ Schema: {schema_message}",
            text_color=theme.dual("brand_primary" if schema_ok else "accent_rose")
        )
        self.schema_pill.configure(
            border_color=theme.dual("brand_primary" if schema_ok else "accent_rose")
        )

    def _test_connection(self):
        t0 = time.perf_counter()
        success, message = database.test_connection()
        latency_ms = (time.perf_counter() - t0) * 1000.0

        if success:
            modal.show_info(
                self.winfo_toplevel(),
                "SQL Server Verified",
                f"✅ Connected to SQL Server successfully.\n\n"
                f"Server: {database.SERVER}\n"
                f"Database: {database.DATABASE}\n"
                f"Latency: {latency_ms:.1f} ms\n"
                f"Authentication: Windows Integrated"
            )
        else:
            modal.show_error(
                self.winfo_toplevel(),
                "Connection Failed",
                f"Could not connect to SQL Server:\n{message}"
            )
        self._refresh_db_status()

    def _verify_schema(self):
        success, msg = database.initialize_db()
        if success:
            modal.show_info(
                self.winfo_toplevel(),
                "Schema Verified",
                "✅ Required SQL Server tables verified:\n\n"
                "• Fields (Plot acreage & status)\n"
                "• Crops (Varieties & growth stages)\n"
                "• InventoryItems (Supplies & units)\n"
                "• InventoryTransactions (Stock ledger)\n\n"
                "Data integrity is confirmed."
            )
            self.controller.refresh_all_views()
        else:
            modal.show_error(
                self.winfo_toplevel(),
                "Schema Validation Error",
                f"Database schema check failed:\n{msg}"
            )
        self._refresh_db_status()
