import customtkinter as ctk

class CustomModal(ctk.CTkToplevel):
    """
    A beautiful modal dialog box designed with CustomTkinter.
    Supports Info, Error, and Confirmation modes.
    Blocks the parent window while active.
    """
    def __init__(self, parent, title="Notification", message="", mode="info", callback=None):
        super().__init__(parent)
        
        self.parent = parent
        self.callback = callback
        self.result = False
        
        self.title(title)
        self.resizable(False, False)
        self.configure(fg_color="#18181b") # Deep charcoal background
        
        # Make modal window transient and grab focus
        self.transient(parent)
        self.grab_set()
        
        # Center the window relative to the parent window
        self.update_idletasks()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        width = 400
        height = 200
        x = parent_x + (parent_width // 2) - (width // 2)
        y = parent_y + (parent_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        # Layout configurations
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1) # Message text
        self.grid_rowconfigure(1, weight=0) # Button panel
        
        # Main content container
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)
        
        # Set icon/accent color based on mode
        if mode == "error":
            icon_text = "❌"
            accent_color = "#ef4444"  # Red
        elif mode == "confirm":
            icon_text = "❓"
            accent_color = "#3b82f6"  # Blue
        else:
            icon_text = "ℹ️"
            accent_color = "#10b981"  # Mint/Emerald
            
        icon_label = ctk.CTkLabel(
            content_frame, 
            text=icon_text, 
            font=ctk.CTkFont(size=36),
            text_color=accent_color
        )
        icon_label.grid(row=0, column=0, padx=(0, 15), sticky="nw")
        
        # Message Label
        msg_label = ctk.CTkLabel(
            content_frame,
            text=message,
            font=ctk.CTkFont(size=13),
            text_color="#e4e4e7",
            anchor="w",
            justify="left",
            wraplength=300
        )
        msg_label.grid(row=0, column=1, sticky="nsew")
        
        # Button Panel
        btn_frame = ctk.CTkFrame(self, fg_color="#09090b", height=60, corner_radius=0)
        btn_frame.grid(row=1, column=0, sticky="ew")
        
        btn_frame.grid_columnconfigure((0, 1), weight=1)
        
        if mode == "confirm":
            # Yes Button
            yes_btn = ctk.CTkButton(
                btn_frame,
                text="Yes",
                fg_color="#059669",
                hover_color="#047857",
                text_color="white",
                font=ctk.CTkFont(size=13, weight="bold"),
                width=100,
                command=self._on_confirm
            )
            yes_btn.grid(row=0, column=0, padx=10, pady=15, sticky="e")
            
            # No Button
            no_btn = ctk.CTkButton(
                btn_frame,
                text="No",
                fg_color="#3f3f46",
                hover_color="#52525b",
                text_color="#e4e4e7",
                font=ctk.CTkFont(size=13),
                width=100,
                command=self._on_cancel
            )
            no_btn.grid(row=0, column=1, padx=10, pady=15, sticky="w")
        else:
            # Ok Button (Info or Error)
            ok_btn = ctk.CTkButton(
                btn_frame,
                text="OK",
                fg_color="#10b981" if mode == "info" else "#ef4444",
                hover_color="#059669" if mode == "info" else "#dc2626",
                text_color="white",
                font=ctk.CTkFont(size=13, weight="bold"),
                width=120,
                command=self._on_ok
            )
            ok_btn.grid(row=0, column=0, columnspan=2, pady=15)
            
        # Bind Close event
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
        self.grab_release()
        self.destroy()

# Static helpers for quick calling (mimicking standard messagebox functions)
def show_info(parent, title, message, callback=None):
    CustomModal(parent, title=title, message=message, mode="info", callback=callback)

def show_error(parent, title, message, callback=None):
    CustomModal(parent, title=title, message=message, mode="error", callback=callback)

def ask_confirm(parent, title, message, callback):
    """Note: ask_confirm requires a callback since Tkinter is event-driven."""
    CustomModal(parent, title=title, message=message, mode="confirm", callback=callback)
