"""
Source entrypoint and enterprise desktop shell for AgriFarm.
"""

from __future__ import annotations
import datetime
import sys
from pathlib import Path
import customtkinter as ctk

import config
import database
import theme
from views.crop_tracker import CropTrackerView
from views.dashboard import DashboardView
from views.inventory import InventoryView
from views.settings import SettingsView


class AgriFarmApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Kick off background DB pre-warm immediately so caches are hot
        # before _warm_all_views() is called at the end of __init__.
        self._prewarm_future = database.pre_warm()

        # Window configuration
        self.title("AgriFarm — Enterprise Agricultural Operations")
        self.geometry("1320x840")
        self.minsize(1080, 680)

        # Apply custom logo icon
        self._apply_window_icon()

        # Apply persisted theme
        app_cfg = config.load_config()
        mode = app_cfg.get("theme_mode", "dark")
        ctk.set_appearance_mode(mode)
        ctk.set_default_color_theme("green")

        # Top-level grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Background color
        self.configure(fg_color=theme.dual("bg_canvas"))

        # State
        self.current_view_name = "Dashboard"
        self.nav_buttons: dict[str, ctk.CTkButton] = {}

        # 1. Sidebar Navigation
        self._build_sidebar()

        # 2. Main Content Container
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew")
        self.main_container.grid_rowconfigure(1, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        # 2a. Top Contextual Header Bar
        self._build_header()

        # 2b. Views Canvas
        self.content = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.content.grid(row=1, column=0, sticky="nsew")
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        self.view_factories = {
            "Dashboard": lambda: DashboardView(self.content, self),
            "Crop Tracker": lambda: CropTrackerView(self.content, self),
            "Inventory": lambda: InventoryView(self.content, self),
            "Settings": lambda: SettingsView(self.content, self),
        }
        self.views = {}

        # Initialize and display Dashboard immediately for sub-second launch
        self._get_or_create_view("Dashboard")
        self.show_view("Dashboard")

        # Defer background warming of secondary views so window is instantly visible and interactive!
        self.after(50, self._warm_inactive_views)

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self,
            width=240,
            corner_radius=0,
            fg_color=theme.dual("bg_sidebar"),
            border_width=1,
            border_color=theme.dual("border_subtle")
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(7, weight=1)

        # Brand Header Lockup
        brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_frame.grid(row=0, column=0, padx=20, pady=(24, 20), sticky="ew")

        logo_badge = ctk.CTkFrame(
            brand_frame,
            width=38,
            height=38,
            corner_radius=10,
            fg_color=theme.dual("brand_primary_subtle"),
            border_width=1,
            border_color=theme.dual("brand_primary")
        )
        logo_badge.pack(side="left", padx=(0, 12))
        logo_badge.pack_propagate(False)

        logo_lbl = ctk.CTkLabel(
            logo_badge,
            text="🌱",
            font=ctk.CTkFont(size=20),
            text_color=theme.dual("brand_primary")
        )
        logo_lbl.place(relx=0.5, rely=0.5, anchor="center")

        brand_text_box = ctk.CTkFrame(brand_frame, fg_color="transparent")
        brand_text_box.pack(side="left", fill="both", expand=True)

        brand_title = ctk.CTkLabel(
            brand_text_box,
            text="AgriFarm",
            font=theme.font_title(size=18),
            text_color=theme.dual("text_primary"),
            anchor="w"
        )
        brand_title.pack(anchor="w")

        brand_sub = ctk.CTkLabel(
            brand_text_box,
            text="Enterprise Ops",
            font=theme.font_caption(size=10, weight="bold"),
            text_color=theme.dual("brand_primary"),
            anchor="w"
        )
        brand_sub.pack(anchor="w")

        # Section Overline
        nav_label = ctk.CTkLabel(
            self.sidebar,
            text="CORE NAVIGATION",
            font=theme.font_micro(size=9),
            text_color=theme.dual("text_muted"),
            anchor="w"
        )
        nav_label.grid(row=1, column=0, padx=22, pady=(10, 6), sticky="w")

        # Nav Items
        nav_items = [
            (2, "Dashboard", "📊"),
            (3, "Crop Tracker", "🌱"),
            (4, "Inventory", "📦"),
            (5, "Settings", "⚙️"),
        ]

        for row, name, icon in nav_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"  {icon}   {name}",
                anchor="w",
                height=42,
                corner_radius=theme.RADIUS_BUTTON,
                font=theme.font_body(size=13, weight="normal"),
                fg_color="transparent",
                hover_color=theme.dual("bg_card_hover"),
                text_color=theme.dual("text_secondary"),
                command=lambda selected=name: self.show_view(selected)
            )
            btn.grid(row=row, column=0, padx=14, pady=3, sticky="ew")
            self.nav_buttons[name] = btn

        # Bottom System Info Card
        sys_card = ctk.CTkFrame(
            self.sidebar,
            corner_radius=theme.RADIUS_INPUT,
            fg_color=theme.dual("bg_card_alt"),
            border_width=1,
            border_color=theme.dual("border_subtle")
        )
        sys_card.grid(row=8, column=0, padx=14, pady=20, sticky="sew")

        live_row = ctk.CTkFrame(sys_card, fg_color="transparent")
        live_row.pack(fill="x", padx=12, pady=(10, 4))

        status_dot = ctk.CTkLabel(
            live_row,
            text="●",
            font=ctk.CTkFont(size=11),
            text_color=theme.dual("brand_primary")
        )
        status_dot.pack(side="left", padx=(0, 6))

        status_text = ctk.CTkLabel(
            live_row,
            text="SQL Server • Live",
            font=theme.font_caption(weight="bold"),
            text_color=theme.dual("text_primary")
        )
        status_text.pack(side="left")

        target_lbl = ctk.CTkLabel(
            sys_card,
            text="IT-Tauheed / AgriFarm",
            font=ctk.CTkFont(size=10, family="Consolas"),
            text_color=theme.dual("text_secondary"),
            anchor="w"
        )
        target_lbl.pack(fill="x", padx=12, pady=(0, 4))

        auth_lbl = ctk.CTkLabel(
            sys_card,
            text="🔒 Windows Authentication",
            font=theme.font_micro(size=9),
            text_color=theme.dual("text_muted"),
            anchor="w"
        )
        auth_lbl.pack(fill="x", padx=12, pady=(0, 10))

    def _build_header(self):
        self.header_bar = ctk.CTkFrame(
            self.main_container,
            height=64,
            corner_radius=0,
            fg_color=theme.dual("bg_header"),
            border_width=1,
            border_color=theme.dual("border_subtle")
        )
        self.header_bar.grid(row=0, column=0, sticky="ew")
        self.header_bar.grid_propagate(False)
        self.header_bar.grid_columnconfigure(1, weight=1)

        # Title & Context
        title_box = ctk.CTkFrame(self.header_bar, fg_color="transparent")
        title_box.grid(row=0, column=0, padx=24, pady=12, sticky="w")

        self.hdr_title = ctk.CTkLabel(
            title_box,
            text="Farm Dashboard",
            font=theme.font_title(size=18),
            text_color=theme.dual("text_primary"),
            anchor="w"
        )
        self.hdr_title.pack(anchor="w")

        self.hdr_subtitle = ctk.CTkLabel(
            title_box,
            text="Operational metrics, active harvests, and field health",
            font=theme.font_caption(),
            text_color=theme.dual("text_secondary"),
            anchor="w"
        )
        self.hdr_subtitle.pack(anchor="w")

        # Right Action Panel
        right_box = ctk.CTkFrame(self.header_bar, fg_color="transparent")
        right_box.grid(row=0, column=1, padx=24, pady=14, sticky="e")

        # Date Badge
        today_str = datetime.date.today().strftime("%a, %b %d, %Y")
        date_badge = ctk.CTkFrame(
            right_box,
            corner_radius=theme.RADIUS_BADGE,
            fg_color=theme.dual("bg_card_alt"),
            border_width=1,
            border_color=theme.dual("border_subtle"),
            height=32
        )
        date_badge.pack(side="left", padx=(0, 10))

        date_lbl = ctk.CTkLabel(
            date_badge,
            text=f"📅  {today_str}",
            font=theme.font_caption(weight="bold"),
            text_color=theme.dual("text_secondary")
        )
        date_lbl.pack(padx=12, pady=4)

        # Global Refresh Button
        self.btn_sync = ctk.CTkButton(
            right_box,
            text="🔄 Sync Data",
            font=theme.font_caption(weight="bold"),
            fg_color=theme.dual("brand_primary_subtle"),
            hover_color=theme.dual("bg_card_hover"),
            text_color=theme.dual("brand_primary_text"),
            border_width=1,
            border_color=theme.dual("brand_primary"),
            corner_radius=theme.RADIUS_BUTTON,
            height=32,
            width=100,
            command=self.refresh_all_views
        )
        self.btn_sync.pack(side="left")

    def _get_or_create_view(self, name: str):
        if name not in self.views:
            view = self.view_factories[name]()
            view.grid(row=0, column=0, sticky="nsew")
            view._is_dirty = False
            self.views[name] = view
            refresh = getattr(view, "refresh", None)
            if refresh:
                try:
                    refresh()
                except Exception:
                    pass
        return self.views[name]

    def _warm_inactive_views(self):
        """Warm remaining views in background idle so tab navigation is instant."""
        try:
            if hasattr(self, '_prewarm_future') and self._prewarm_future:
                self._prewarm_future.result(timeout=1)
        except Exception:
            pass

        for name in ["Crop Tracker", "Inventory", "Settings"]:
            if name not in self.views:
                try:
                    view = self.view_factories[name]()
                    view.grid(row=0, column=0, sticky="nsew")
                    view._is_dirty = False
                    self.views[name] = view
                    # Keep active view raised
                    if self.current_view_name in self.views:
                        self.views[self.current_view_name].tkraise()
                    refresh = getattr(view, "refresh", None)
                    if refresh:
                        refresh()
                except Exception:
                    pass

    def _warm_all_views(self):
        """Pre-populates all views."""
        for name in self.view_factories:
            view = self._get_or_create_view(name)
            refresh = getattr(view, "refresh", None)
            if refresh:
                try:
                    refresh()
                except Exception:
                    pass
            view._is_dirty = False

    def show_view(self, name: str):
        self.current_view_name = name
        view = self._get_or_create_view(name)
        
        # Raise view immediately - feels instant because content is pre-warmed!
        view.tkraise()

        # Update header contextual text
        context_map = {
            "Dashboard": ("Farm Dashboard", "Operational metrics, active harvests, and field health"),
            "Crop Tracker": ("Crop & Field Tracker", "Manage farm plots, planting schedules, and crop life-cycles"),
            "Inventory": ("Stock & Resource Inventory", "Monitor supplies, adjust stock levels, and track consumption"),
            "Settings": ("System & Database Diagnostics", "SQL Server connection telemetry and application customization"),
        }
        title, subtitle = context_map.get(name, (name, ""))
        self.hdr_title.configure(text=title)
        self.hdr_subtitle.configure(text=subtitle)

        # Update active nav button state
        for btn_name, btn in self.nav_buttons.items():
            if btn_name == name:
                btn.configure(
                    fg_color=theme.dual("bg_sidebar_active"),
                    text_color=theme.dual("brand_primary"),
                    font=theme.font_body(size=13, weight="bold")
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=theme.dual("text_secondary"),
                    font=theme.font_body(size=13, weight="normal")
                )

        # Always refresh on navigation so data is current when user lands on the view.
        refresh = getattr(view, "refresh", None)
        if refresh:
            try:
                refresh()
            except Exception:
                pass
        view._is_dirty = False

    def refresh_all_views(self, force: bool = True, affected_views: set | None = None):
        """Refreshes the active view immediately; marks only affected inactive views dirty.

        Pass ``affected_views={'Dashboard','Crop Tracker'}`` to avoid marking
        unrelated views (e.g. Inventory) dirty when a crop mutation happens.
        Defaults to marking all views dirty when affected_views is None.
        """
        database.invalidate_cache()
        for name, view in self.views.items():
            should_refresh = (affected_views is None) or (name in affected_views)
            if not should_refresh:
                continue
            if name == self.current_view_name:
                refresh = getattr(view, "refresh", None)
                if refresh:
                    try:
                        refresh()
                    except Exception:
                        pass
                view._is_dirty = False
            else:
                view._is_dirty = True

    def _apply_window_icon(self):
        candidates = []
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            candidates.append(Path(sys._MEIPASS) / "Logo" / "1F33E_color.ico")
            candidates.append(Path(sys._MEIPASS) / "_internal" / "Logo" / "1F33E_color.ico")
        this_dir = Path(__file__).resolve().parent
        candidates.append(this_dir / "Logo" / "1F33E_color.ico")
        candidates.append(this_dir.parent / "_internal" / "Logo" / "1F33E_color.ico")
        if getattr(sys, "frozen", False):
            exe_dir = Path(sys.executable).resolve().parent
            candidates.append(exe_dir / "_internal" / "Logo" / "1F33E_color.ico")
            candidates.append(exe_dir / "Logo" / "1F33E_color.ico")

        for p in candidates:
            if p.exists():
                try:
                    self.iconbitmap(str(p))
                    break
                except Exception:
                    pass

    def update_theme_style(self, mode: str):
        ctk.set_appearance_mode(mode)
        cfg = config.load_config()
        cfg["theme_mode"] = mode.lower()
        config.save_config(cfg)
        self._warm_all_views()
        self.show_view(self.current_view_name)


def main():
    AgriFarmApp().mainloop()


if __name__ == "__main__":
    main()
