"""
views/dashboard.py - Executive Dashboard view for AgriFarm.

Displays top-level farm KPIs, active crop growth metrics,
low-inventory alerts, and a scheduled 30-day harvest timeline.
"""

from __future__ import annotations
import customtkinter as ctk

import database
import theme
from widgets.table import CustomTable


class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        # Main layout configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)  # Expand harvest table

        # 1. KPI Cards Row (4 cards grid)
        self.kpi_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.kpi_frame.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 16))
        self.kpi_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="kpi")

        # Card 1: Fields
        self.card_fields = self._create_kpi_card(
            parent=self.kpi_frame,
            col=0,
            title="CULTIVATED FIELDS",
            value="0",
            subtitle="Plots under management",
            icon="🚜",
            color_key="brand_primary"
        )

        # Card 2: Active Crops
        self.card_crops = self._create_kpi_card(
            parent=self.kpi_frame,
            col=1,
            title="ACTIVE CROPS",
            value="0",
            subtitle="Crops currently in ground",
            icon="🌱",
            color_key="accent_blue"
        )

        # Card 3: Stock Inventory Alerts
        self.card_inventory = self._create_kpi_card(
            parent=self.kpi_frame,
            col=2,
            title="INVENTORY ALERTS",
            value="0",
            subtitle="Items below safety buffer",
            icon="⚠️",
            color_key="accent_rose"
        )

        # Card 4: Upcoming 30-Day Harvests
        self.card_harvests = self._create_kpi_card(
            parent=self.kpi_frame,
            col=3,
            title="30-DAY HARVESTS",
            value="0",
            subtitle="Scheduled collection windows",
            icon="🌾",
            color_key="accent_amber"
        )

        # 2. Upcoming Harvests Panel
        self.harvests_container = ctk.CTkFrame(
            self,
            fg_color=theme.dual("bg_card"),
            corner_radius=theme.RADIUS_CARD,
            border_width=1,
            border_color=theme.dual("border_card")
        )
        self.harvests_container.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 20))
        self.harvests_container.grid_columnconfigure(0, weight=1)
        self.harvests_container.grid_rowconfigure(1, weight=1)

        # Panel Header Bar (Title + Search Filter)
        panel_header = ctk.CTkFrame(self.harvests_container, fg_color="transparent")
        panel_header.grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 12))
        panel_header.grid_columnconfigure(0, weight=1)

        header_title_box = ctk.CTkFrame(panel_header, fg_color="transparent")
        header_title_box.grid(row=0, column=0, sticky="w")

        panel_title = ctk.CTkLabel(
            header_title_box,
            text="🌾 Upcoming Harvests & Growth Schedules",
            font=theme.font_title(size=15),
            text_color=theme.dual("text_primary"),
            anchor="w"
        )
        panel_title.pack(anchor="w")

        panel_subtitle = ctk.CTkLabel(
            header_title_box,
            text="Crops due for harvest within 30 days — including overdue (click headers to sort)",
            font=theme.font_caption(),
            text_color=theme.dual("text_muted"),
            anchor="w"
        )
        panel_subtitle.pack(anchor="w")

        # Search filter input
        self.search_entry = ctk.CTkEntry(
            panel_header,
            placeholder_text="🔍 Filter harvests...",
            height=32,
            width=220,
            corner_radius=theme.RADIUS_INPUT,
            fg_color=theme.dual("bg_input"),
            border_color=theme.dual("border_input"),
            text_color=theme.dual("text_primary")
        )
        self.search_entry.grid(row=0, column=1, sticky="e")
        self.search_entry.bind("<KeyRelease>", self._on_search_typed)

        # Harvest table
        headers = ["Crop", "Variety", "Location / Field", "Expected Harvest", "Stage", "Status"]
        column_weights = [2, 2, 2, 2, 2, 1]
        self.harvest_table = CustomTable(
            self.harvests_container,
            headers=headers,
            column_weights=column_weights
        )
        self.harvest_table.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 16))

    def _create_kpi_card(self, parent, col, title, value, subtitle, icon, color_key):
        card = ctk.CTkFrame(
            parent,
            fg_color=theme.dual("bg_card"),
            corner_radius=theme.RADIUS_CARD,
            border_width=1,
            border_color=theme.dual("border_card")
        )
        card.grid(row=0, column=col, padx=(0 if col == 0 else 8, 0 if col == 3 else 8), sticky="nsew")
        card.grid_columnconfigure(0, weight=1)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=16, pady=16)
        inner.grid_columnconfigure(0, weight=1)

        # Top row: Section Overline + Icon
        top_row = ctk.CTkFrame(inner, fg_color="transparent")
        top_row.pack(fill="x")
        top_row.grid_columnconfigure(0, weight=1)

        over_lbl = ctk.CTkLabel(
            top_row,
            text=title,
            font=theme.font_micro(size=10),
            text_color=theme.dual("text_muted"),
            anchor="w"
        )
        over_lbl.grid(row=0, column=0, sticky="w")

        icon_frame = ctk.CTkFrame(
            top_row,
            width=32,
            height=32,
            corner_radius=16,
            fg_color=theme.dual("bg_card_alt"),
            border_width=1,
            border_color=theme.dual("border_subtle")
        )
        icon_frame.grid(row=0, column=1, sticky="e")
        icon_frame.pack_propagate(False)

        icon_lbl = ctk.CTkLabel(
            icon_frame,
            text=icon,
            font=ctk.CTkFont(size=15),
            text_color=theme.dual(color_key)
        )
        icon_lbl.place(relx=0.5, rely=0.5, anchor="center")

        # Value number
        val_lbl = ctk.CTkLabel(
            inner,
            text=value,
            font=theme.font_display(size=28),
            text_color=theme.dual("text_primary"),
            anchor="w"
        )
        val_lbl.pack(anchor="w", pady=(8, 2))

        # Subtitle
        sub_lbl = ctk.CTkLabel(
            inner,
            text=subtitle,
            font=theme.font_caption(size=11),
            text_color=theme.dual("text_secondary"),
            anchor="w"
        )
        sub_lbl.pack(anchor="w")

        card.val_lbl = val_lbl
        card.sub_lbl = sub_lbl
        card.color_key = color_key
        return card

    def _on_search_typed(self, event=None):
        if hasattr(self, "_search_timer") and self._search_timer:
            self.after_cancel(self._search_timer)
        self._search_timer = self.after(100, self._do_search)

    def _do_search(self):
        query = self.search_entry.get()
        self.harvest_table.filter_data(query)

    def refresh(self):
        """Loads metrics and table data, handling database errors gracefully."""
        try:
            # 1. Fetch metrics (all KPIs in a single SQL round-trip)
            stats = database.get_dashboard_metrics(low_stock_threshold=10.0)
            fields_count = stats.get("total_fields", 0)
            total_acres = stats.get("total_acres", 0.0)
            active_crops_count = stats.get("active_crops", 0)
            low_stock_count = stats.get("low_stock_alerts", 0)

            self.card_fields.val_lbl.configure(text=str(fields_count))
            self.card_fields.sub_lbl.configure(text=f"{total_acres:.1f} Total Acres Managed")
            self.card_crops.val_lbl.configure(text=str(active_crops_count))
            self.card_inventory.val_lbl.configure(text=str(low_stock_count))

            # Inventory card styling
            if low_stock_count > 0:
                self.card_inventory.configure(border_color=theme.dual("accent_rose"))
                self.card_inventory.val_lbl.configure(text_color=theme.dual("accent_rose"))
                self.card_inventory.sub_lbl.configure(
                    text=f"{low_stock_count} item{'s' if low_stock_count > 1 else ''} below safety threshold",
                    text_color=theme.dual("accent_rose")
                )
            else:
                self.card_inventory.configure(border_color=theme.dual("border_card"))
                self.card_inventory.val_lbl.configure(text_color=theme.dual("text_primary"))
                self.card_inventory.sub_lbl.configure(
                    text="All stock at optimal buffer",
                    text_color=theme.dual("text_secondary")
                )

            # 2. Upcoming Harvests Table
            upcoming = database.get_upcoming_activities(days=30)
            self.card_harvests.val_lbl.configure(text=str(len(upcoming)))
            self.card_harvests.sub_lbl.configure(
                text=f"{len(upcoming)} crop{'s' if len(upcoming) != 1 else ''} due within 30 days"
                if upcoming else "No harvests due in next 30 days"
            )

            key_mapping = ["crop_name", "variety", "field_name", "expected_harvest", "stage", "harvest_status"]
            self.harvest_table.set_data(upcoming, key_mapping=key_mapping)

            if not upcoming:
                # Polished empty state
                self.harvest_table.clear()
                empty_frame = ctk.CTkFrame(self.harvest_table.body_frame, fg_color="transparent")
                empty_frame.grid(row=0, column=0, columnspan=6, pady=48, sticky="ew")
                ctk.CTkLabel(
                    empty_frame,
                    text="🌿",
                    font=ctk.CTkFont(size=36)
                ).pack()
                ctk.CTkLabel(
                    empty_frame,
                    text="No Upcoming Harvests",
                    font=theme.font_title(size=14),
                    text_color=theme.dual("text_primary")
                ).pack(pady=(8, 4))
                ctk.CTkLabel(
                    empty_frame,
                    text="No crops are scheduled for harvest in the next 30 days.",
                    font=theme.font_caption(),
                    text_color=theme.dual("text_muted")
                ).pack()
                self.harvest_table.row_widgets.append([empty_frame])
            else:
                # Reapply active search filter if typed
                current_q = self.search_entry.get().strip()
                if current_q:
                    self.harvest_table.filter_data(current_q)

        except Exception as e:
            self.card_fields.val_lbl.configure(text="—")
            self.card_crops.val_lbl.configure(text="—")
            self.card_inventory.val_lbl.configure(text="—")
            self.card_harvests.val_lbl.configure(text="—")

            self.harvest_table.clear()
            no_db_frame = ctk.CTkFrame(self.harvest_table.body_frame, fg_color="transparent")
            no_db_frame.grid(row=0, column=0, columnspan=5, pady=40, sticky="ew")

            err_icon = ctk.CTkLabel(no_db_frame, text="⚠️", font=ctk.CTkFont(size=28))
            err_icon.pack(pady=(0, 6))

            err_label = ctk.CTkLabel(
                no_db_frame,
                text="Could not connect to SQL Server.",
                font=theme.font_body(weight="bold"),
                text_color=theme.dual("accent_rose")
            )
            err_label.pack()

            hint = ctk.CTkLabel(
                no_db_frame,
                text=f"Check the connection diagnostics in Settings tab.\nDetails: {e}",
                font=theme.font_caption(),
                text_color=theme.dual("text_muted")
            )
            hint.pack(pady=(4, 0))

            self.harvest_table.row_widgets.append([no_db_frame])
