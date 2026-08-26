"""
views/settings.py  –  Settings view for AgriFarm (SQLite edition).

The PostgreSQL connection-credential form has been replaced with an
informational panel confirming that the app uses a self-contained local
SQLite database.  The Theme & Personalisation section is unchanged.
"""

import customtkinter as ctk
import config
import database
from widgets import modal
from pathlib import Path


class SettingsView(ctk.CTkFrame):
    """
    Settings view containing database information and appearance theme selection.

    Since AgriFarm now uses a local SQLite file (farm_db.sqlite) there are
    no host / port / user / password credentials to configure.  The database
    panel therefore shows the file path and offers a 'Re-initialise' action
    for diagnostics.
    """

    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        # Grid Layout (single column, multiple cards)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1), weight=0)
        self.grid_rowconfigure(2, weight=1)  # bottom spacer

        # ── Header ──────────────────────────────────────────────────────────
        ctk.CTkLabel(
            self,
            text="⚙️ Application Settings",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#f4f4f5",
            anchor="w"
        ).grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 15))

        # Two-column card row
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.content_frame.grid_columnconfigure((0, 1), weight=1, uniform="equal")

        # ── 1. DATABASE INFO BOX ─────────────────────────────────────────────
        self.db_box = ctk.CTkFrame(
            self.content_frame,
            fg_color="#18181b",
            corner_radius=8,
            border_width=1,
            border_color="#27272a"
        )
        self.db_box.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.db_box.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.db_box,
            text="🗄️ Local SQLite Database",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#e4e4e7"
        ).grid(row=0, column=0, sticky="w", padx=15, pady=15)

        # Subtitle description
        ctk.CTkLabel(
            self.db_box,
            text=(
                "AgriFarm stores all data in a self-contained SQLite file.\n"
                "No server, no credentials, and no internet connection required."
            ),
            font=ctk.CTkFont(size=12),
            text_color="#a1a1aa",
            justify="left",
            wraplength=320
        ).grid(row=1, column=0, sticky="w", padx=15, pady=(0, 12))

        # Database file path display
        db_path = Path(__file__).parent.parent / "farm_db.sqlite"
        ctk.CTkLabel(
            self.db_box,
            text="Database File Path",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#a1a1aa"
        ).grid(row=2, column=0, sticky="w", padx=15, pady=(5, 3))

        self.db_path_label = ctk.CTkLabel(
            self.db_box,
            text=str(db_path),
            font=ctk.CTkFont(size=11, family="Courier"),
            text_color="#34d399",
            anchor="w",
            wraplength=340
        )
        self.db_path_label.grid(row=3, column=0, sticky="ew", padx=15, pady=(0, 15))

        # Status indicator
        ctk.CTkLabel(
            self.db_box,
            text="Connection Status",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#a1a1aa"
        ).grid(row=4, column=0, sticky="w", padx=15, pady=(0, 3))

        self.status_label = ctk.CTkLabel(
            self.db_box,
            text="● Checking…",
            font=ctk.CTkFont(size=12),
            text_color="#a1a1aa",
            anchor="w"
        )
        self.status_label.grid(row=5, column=0, sticky="ew", padx=15, pady=(0, 15))

        # File size indicator
        self.size_label = ctk.CTkLabel(
            self.db_box,
            text="File size: –",
            font=ctk.CTkFont(size=11),
            text_color="#71717a",
            anchor="w"
        )
        self.size_label.grid(row=6, column=0, sticky="ew", padx=15, pady=(0, 10))

        # Action buttons
        self.btn_frame = ctk.CTkFrame(self.db_box, fg_color="transparent")
        self.btn_frame.grid(row=7, column=0, sticky="ew", padx=15, pady=(5, 15))
        self.btn_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            self.btn_frame,
            text="🔍 Test Connection",
            fg_color="#3f3f46",
            hover_color="#52525b",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=32,
            command=self._test_connection
        ).grid(row=0, column=0, padx=(0, 5), sticky="ew")

        ctk.CTkButton(
            self.btn_frame,
            text="🔄 Re-initialise DB",
            fg_color="#10b981",
            hover_color="#059669",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=32,
            command=self._reinitialise_db
        ).grid(row=0, column=1, padx=(5, 0), sticky="ew")

        # ── 2. APPEARANCE CONFIGURATION BOX ─────────────────────────────────
        self.app_box = ctk.CTkFrame(
            self.content_frame,
            fg_color="#18181b",
            corner_radius=8,
            border_width=1,
            border_color="#27272a"
        )
        self.app_box.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        self.app_box.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.app_box,
            text="🎨 Theme & Personalisation",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#e4e4e7"
        ).grid(row=0, column=0, sticky="w", padx=15, pady=15)

        ctk.CTkLabel(
            self.app_box,
            text="Select Interface Appearance Mode",
            font=ctk.CTkFont(size=12),
            text_color="#a1a1aa"
        ).grid(row=1, column=0, sticky="w", padx=15, pady=(5, 5))

        self.theme_switch = ctk.CTkComboBox(
            self.app_box,
            values=["Dark Mode", "Light Mode"],
            height=32,
            command=self._on_theme_changed
        )
        self.theme_switch.grid(row=2, column=0, sticky="w", padx=15, pady=(0, 15))

        # Load theme preference into UI
        self._load_theme_setting()

        # Run connection check after widget is ready
        self.after(200, self._refresh_db_status)

    # ── Private helpers ──────────────────────────────────────────────────────

    def _load_theme_setting(self):
        """Reads theme_mode from config and sets the ComboBox accordingly."""
        cfg = config.load_config()
        mode = cfg.get("theme_mode", "dark")
        self.theme_switch.set("Dark Mode" if mode == "dark" else "Light Mode")

    def _refresh_db_status(self):
        """Updates the live status and file-size labels."""
        success, message = database.test_connection()
        if success:
            self.status_label.configure(
                text="● Connected – database is accessible",
                text_color="#10b981"
            )
        else:
            self.status_label.configure(
                text=f"● Error – {message}",
                text_color="#ef4444"
            )

        # Show file size if it exists
        db_path = Path(__file__).parent.parent / "farm_db.sqlite"
        if db_path.exists():
            size_kb = db_path.stat().st_size / 1024
            self.size_label.configure(text=f"File size: {size_kb:.1f} KB")
        else:
            self.size_label.configure(text="File size: (not yet created)")

    def _test_connection(self):
        success, message = database.test_connection()
        if success:
            modal.show_info(
                self.winfo_toplevel(),
                "Connection Successful",
                "✅ SQLite database is accessible and working correctly.\n\n"
                f"File: {Path(__file__).parent.parent / 'farm_db.sqlite'}"
            )
        else:
            modal.show_error(
                self.winfo_toplevel(),
                "Connection Failed",
                f"Could not access SQLite database:\n{message}"
            )
        self._refresh_db_status()

    def _reinitialise_db(self):
        """Re-runs table creation (safe – uses IF NOT EXISTS) and seeds if empty."""
        success, msg = database.initialize_db()
        if success:
            modal.show_info(
                self.winfo_toplevel(),
                "Database Ready",
                "Database schema verified and sample data seeded (if empty).\n\n"
                "All views have been refreshed."
            )
            self.controller.refresh_all_views()
        else:
            modal.show_error(
                self.winfo_toplevel(),
                "Initialisation Failed",
                f"Could not initialise the database:\n{msg}"
            )
        self._refresh_db_status()

    def _on_theme_changed(self, selection):
        mode = "dark" if selection == "Dark Mode" else "light"
        cfg = config.load_config()
        cfg["theme_mode"] = mode
        config.save_config(cfg)
        ctk.set_appearance_mode(mode)
        self.controller.update_theme_style(mode)

    def refresh(self):
        """Called by the main controller when this view is shown."""
        self._refresh_db_status()
