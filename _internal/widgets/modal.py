"""
widgets/modal.py - Sleek, theme-adaptive modal dialogs.

Supports Information, Error, and Confirmation modes with keyboard bindings.
"""

from __future__ import annotations
import customtkinter as ctk
import theme


class CustomModal(ctk.CTkToplevel):
    def __init__(self, parent, title="Notification", message="", mode="info", callback=None):
        super().__init__(parent)

        self.parent = parent
        self.callback = callback
        self.result = False

        self.title(title)
        self.resizable(False, False)
        self.configure(fg_color=theme.dual("bg_card"))

        # Make modal window transient and grab focus
        self.transient(parent)
        self.grab_set()

        # Center relative to parent
        self.update_idletasks()
        try:
            parent_x = parent.winfo_rootx()
            parent_y = parent.winfo_rooty()
            parent_w = parent.winfo_width()
            parent_h = parent.winfo_height()
        except Exception:
            parent_x = 100
            parent_y = 100
            parent_w = 800
            parent_h = 600

        width = 440
        height = 210
        x = max(50, parent_x + (parent_w // 2) - (width // 2))
        y = max(50, parent_y + (parent_h // 2) - (height // 2))
        self.geometry(f"{width}x{height}+{x}+{y}")

        # Grid configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        # Content Card
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=0, column=0, sticky="nsew", padx=24, pady=(20, 10))
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)

        # Mode styling
        if mode == "error":
            icon_text = "⛔"
            accent_color = theme.dual("accent_rose")
            header_title = title if title != "Notification" else "Action Failed"
        elif mode == "confirm":
            icon_text = "⚠️"
            accent_color = theme.dual("accent_amber")
            header_title = title if title != "Notification" else "Please Confirm"
        else:
            icon_text = "✅"
            accent_color = theme.dual("brand_primary")
            header_title = title if title != "Notification" else "Operation Succeeded"

        # Icon badge
        icon_frame = ctk.CTkFrame(
            content_frame,
            width=46,
            height=46,
            corner_radius=23,
            fg_color=theme.dual("bg_card_alt"),
            border_width=1,
            border_color=accent_color
        )
        icon_frame.grid(row=0, column=0, sticky="nw", padx=(0, 16), pady=2)
        icon_frame.pack_propagate(False)

        icon_label = ctk.CTkLabel(
            icon_frame,
            text=icon_text,
            font=ctk.CTkFont(size=22),
            text_color=accent_color
        )
        icon_label.place(relx=0.5, rely=0.5, anchor="center")

        # Text container
        text_container = ctk.CTkFrame(content_frame, fg_color="transparent")
        text_container.grid(row=0, column=1, sticky="nsew")

        title_lbl = ctk.CTkLabel(
            text_container,
            text=header_title,
            font=theme.font_title(size=15),
            text_color=theme.dual("text_primary"),
            anchor="w"
        )
        title_lbl.pack(anchor="w", pady=(0, 4))

        msg_lbl = ctk.CTkLabel(
            text_container,
            text=message,
            font=theme.font_body(size=12),
            text_color=theme.dual("text_secondary"),
            anchor="w",
            justify="left",
            wraplength=320
        )
        msg_lbl.pack(anchor="w", fill="x")

        # Footer Action Buttons
        footer = ctk.CTkFrame(
            self,
            fg_color=theme.dual("bg_table_header"),
            height=56,
            corner_radius=0,
            border_width=1,
            border_color=theme.dual("border_subtle")
        )
        footer.grid(row=1, column=0, sticky="ew")
        footer.grid_columnconfigure((0, 1), weight=1)

        if mode == "confirm":
            yes_btn = ctk.CTkButton(
                footer,
                text="Confirm",
                fg_color=theme.dual("brand_primary"),
                hover_color=theme.dual("brand_primary_hover"),
                text_color=theme.dual("text_inverse"),
                font=theme.font_body(weight="bold"),
                corner_radius=theme.RADIUS_BUTTON,
                height=34,
                width=110,
                command=self._on_confirm
            )
            yes_btn.grid(row=0, column=0, padx=12, pady=11, sticky="e")

            no_btn = ctk.CTkButton(
                footer,
                text="Cancel",
                fg_color=theme.dual("bg_card"),
                hover_color=theme.dual("bg_card_hover"),
                text_color=theme.dual("text_secondary"),
                border_width=1,
                border_color=theme.dual("border_card"),
                font=theme.font_body(),
                corner_radius=theme.RADIUS_BUTTON,
                height=34,
                width=100,
                command=self._on_cancel
            )
            no_btn.grid(row=0, column=1, padx=12, pady=11, sticky="w")
        else:
            btn_color = theme.dual("brand_primary" if mode == "info" else "accent_rose")
            btn_hover = theme.dual("brand_primary_hover" if mode == "info" else "accent_rose_hover")
            ok_btn = ctk.CTkButton(
                footer,
                text="Dismiss" if mode == "error" else "Continue",
                fg_color=btn_color,
                hover_color=btn_hover,
                text_color=theme.dual("text_inverse"),
                font=theme.font_body(weight="bold"),
                corner_radius=theme.RADIUS_BUTTON,
                height=34,
                width=120,
                command=self._on_ok
            )
            ok_btn.grid(row=0, column=0, columnspan=2, pady=11)

        # Keyboard bindings
        self.bind("<Return>", lambda e: self._on_confirm() if mode == "confirm" else self._on_ok())
        self.bind("<Escape>", lambda e: self._on_cancel() if mode == "confirm" else self._on_ok())
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_confirm(self):
        self.result = True
        self._close_modal()
        if self.callback:
            self.callback(True)

    def _on_cancel(self):
        self.result = False
        self._close_modal()
        if self.callback:
            self.callback(False)

    def _on_ok(self):
        self.result = True
        self._close_modal()
        if self.callback:
            self.callback(True)

    def _on_close(self):
        self.result = False
        self._close_modal()
        if self.callback:
            self.callback(False)

    def _close_modal(self):
        try:
            self.grab_release()
            self.destroy()
        except Exception:
            pass


def show_info(parent, title, message, callback=None):
    CustomModal(parent, title=title, message=message, mode="info", callback=callback)


def show_error(parent, title, message, callback=None):
    CustomModal(parent, title=title, message=message, mode="error", callback=callback)


def ask_confirm(parent, title, message, callback):
    CustomModal(parent, title=title, message=message, mode="confirm", callback=callback)
