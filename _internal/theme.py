"""
AgriFarm Design System & Theme Engine.

Defines unified color palettes, typography tokens, badge mappings,
and surface styling for both Dark and Light appearance modes.
"""

from __future__ import annotations
import customtkinter as ctk


# ---------------------------------------------------------------------------
# COLOR TOKENS
# ---------------------------------------------------------------------------

PALETTE = {
    "dark": {
        # Canvases & Surfaces
        "bg_canvas": "#0B0F17",
        "bg_sidebar": "#0E1522",
        "bg_sidebar_active": "#162338",
        "bg_header": "#0E1522",
        "bg_card": "#131C2A",
        "bg_card_alt": "#172335",
        "bg_card_hover": "#1B293E",
        "bg_input": "#0D1420",
        "bg_input_focus": "#131D2E",
        "bg_table_header": "#111A28",
        "bg_row_even": "#131C2A",
        "bg_row_odd": "#0F1724",
        "bg_row_hover": "#18263B",
        "bg_row_selected": "#064E3B",
        "border_subtle": "#1B283A",
        "border_card": "#1E2D42",
        "border_input": "#25374E",
        "border_focus": "#10B981",

        # Text Hierarchy
        "text_primary": "#F8FAFC",
        "text_secondary": "#94A3B8",
        "text_muted": "#64748B",
        "text_inverse": "#0B0F17",

        # Brand & Agricultural Accents
        "brand_primary": "#10B981",       # Emerald
        "brand_primary_hover": "#059669",
        "brand_primary_subtle": "#064E3B",
        "brand_primary_text": "#34D399",

        "accent_blue": "#38BDF8",         # Sky Harvest
        "accent_blue_hover": "#0EA5E9",
        "accent_blue_subtle": "#082F49",

        "accent_amber": "#FBBF24",        # Warm Golden
        "accent_amber_hover": "#F59E0B",
        "accent_amber_subtle": "#451A03",

        "accent_rose": "#F87171",         # Alert Red
        "accent_rose_hover": "#EF4444",
        "accent_rose_subtle": "#450A0A",
    },
    "light": {
        # Canvases & Surfaces
        "bg_canvas": "#F1F5F9",
        "bg_sidebar": "#FFFFFF",
        "bg_sidebar_active": "#ECFDF5",
        "bg_header": "#FFFFFF",
        "bg_card": "#FFFFFF",
        "bg_card_alt": "#F8FAFC",
        "bg_card_hover": "#F1F5F9",
        "bg_input": "#FFFFFF",
        "bg_input_focus": "#FFFFFF",
        "bg_table_header": "#F8FAFC",
        "bg_row_even": "#FFFFFF",
        "bg_row_odd": "#F8FAFC",
        "bg_row_hover": "#F1F5F9",
        "bg_row_selected": "#D1FAE5",
        "border_subtle": "#E2E8F0",
        "border_card": "#E2E8F0",
        "border_input": "#CBD5E1",
        "border_focus": "#059669",

        # Text Hierarchy
        "text_primary": "#0F172A",
        "text_secondary": "#475569",
        "text_muted": "#94A3B8",
        "text_inverse": "#FFFFFF",

        # Brand & Agricultural Accents
        "brand_primary": "#059669",
        "brand_primary_hover": "#047857",
        "brand_primary_subtle": "#D1FAE5",
        "brand_primary_text": "#065F46",

        "accent_blue": "#0284C7",
        "accent_blue_hover": "#0369A1",
        "accent_blue_subtle": "#E0F2FE",

        "accent_amber": "#D97706",
        "accent_amber_hover": "#B45309",
        "accent_amber_subtle": "#FEF3C7",

        "accent_rose": "#DC2626",
        "accent_rose_hover": "#B91C1C",
        "accent_rose_subtle": "#FEE2E2",
    },
}


def get_current_mode() -> str:
    """Returns the active customtkinter appearance mode ('dark' or 'light')."""
    mode = ctk.get_appearance_mode().lower()
    return "light" if mode == "light" else "dark"


def color(key: str, mode: str | None = None) -> str:
    """Retrieves a theme color for the specified or current mode."""
    m = mode or get_current_mode()
    sub = PALETTE.get(m, PALETTE["dark"])
    return sub.get(key, PALETTE["dark"].get(key, "#FFFFFF"))


def dual(key: str) -> tuple[str, str]:
    """Returns a tuple of (light_color, dark_color) for CustomTkinter widgets that support dual colors."""
    light_val = PALETTE["light"].get(key, "#FFFFFF")
    dark_val = PALETTE["dark"].get(key, "#000000")
    return (light_val, dark_val)


# ---------------------------------------------------------------------------
# BADGE & STATUS METADATA
# ---------------------------------------------------------------------------

BADGES = {
    # Field Statuses
    "Active": {
        "dark": {"bg": "#064E3B", "fg": "#34D399", "border": "#059669"},
        "light": {"bg": "#D1FAE5", "fg": "#065F46", "border": "#A7F3D0"},
        "icon": "●",
    },
    "Fallow": {
        "dark": {"bg": "#1E293B", "fg": "#94A3B8", "border": "#334155"},
        "light": {"bg": "#F1F5F9", "fg": "#475569", "border": "#CBD5E1"},
        "icon": "○",
    },
    "Resting": {
        "dark": {"bg": "#451A03", "fg": "#FCD34D", "border": "#78350F"},
        "light": {"bg": "#FEF3C7", "fg": "#92400E", "border": "#FDE68A"},
        "icon": "◐",
    },

    # Crop Growth Stages
    "Seedling": {
        "dark": {"bg": "#064E3B", "fg": "#86EFAC", "border": "#15803D"},
        "light": {"bg": "#DCFCE7", "fg": "#166534", "border": "#BBF7D0"},
        "icon": "🌱",
    },
    "Vegetative": {
        "dark": {"bg": "#064E3B", "fg": "#34D399", "border": "#059669"},
        "light": {"bg": "#D1FAE5", "fg": "#065F46", "border": "#A7F3D0"},
        "icon": "🌿",
    },
    "Flowering": {
        "dark": {"bg": "#3B0764", "fg": "#D8B4FE", "border": "#6B21A8"},
        "light": {"bg": "#F3E8FF", "fg": "#6B21A8", "border": "#E9D5FF"},
        "icon": "🌸",
    },
    "Harvest-Ready": {
        "dark": {"bg": "#451A03", "fg": "#FDE047", "border": "#B45309"},
        "light": {"bg": "#FEF9C3", "fg": "#854D0E", "border": "#FEF08A"},
        "icon": "🌾",
    },
    "Harvested": {
        "dark": {"bg": "#1E293B", "fg": "#94A3B8", "border": "#334155"},
        "light": {"bg": "#F1F5F9", "fg": "#475569", "border": "#CBD5E1"},
        "icon": "✓",
    },

    # Inventory Categories
    "Seeds": {
        "dark": {"bg": "#064E3B", "fg": "#86EFAC", "border": "#15803D"},
        "light": {"bg": "#DCFCE7", "fg": "#166534", "border": "#BBF7D0"},
        "icon": "🌰",
    },
    "Fertilizer": {
        "dark": {"bg": "#082F49", "fg": "#7DD3FC", "border": "#0369A1"},
        "light": {"bg": "#E0F2FE", "fg": "#0369A1", "border": "#BAE6FD"},
        "icon": "🧪",
    },
    "Pesticide": {
        "dark": {"bg": "#451A03", "fg": "#FDBA74", "border": "#C2410C"},
        "light": {"bg": "#FFEDD5", "fg": "#9A3412", "border": "#FED7AA"},
        "icon": "🛡️",
    },
    "Tools": {
        "dark": {"bg": "#1E293B", "fg": "#CBD5E1", "border": "#475569"},
        "light": {"bg": "#F1F5F9", "fg": "#334155", "border": "#CBD5E1"},
        "icon": "🔧",
    },
}


def get_badge_style(value: str, mode: str | None = None) -> dict:
    """Returns styling dictionary for a given badge or status value."""
    m = mode or get_current_mode()
    fallback = {
        "bg": color("bg_card_alt", m),
        "fg": color("text_secondary", m),
        "border": color("border_subtle", m),
        "icon": "•",
    }
    spec = BADGES.get(value)
    if not spec:
        return fallback
    mode_spec = spec.get(m, spec.get("dark", {}))
    return {
        "bg": mode_spec.get("bg", fallback["bg"]),
        "fg": mode_spec.get("fg", fallback["fg"]),
        "border": mode_spec.get("border", fallback["border"]),
        "icon": spec.get("icon", "•"),
    }


# ---------------------------------------------------------------------------
# TYPOGRAPHY
# ---------------------------------------------------------------------------

FONT_FAMILY = "Segoe UI"


def font_display(size: int = 22, weight: str = "bold") -> ctk.CTkFont:
    return ctk.CTkFont(family=FONT_FAMILY, size=size, weight=weight)


def font_title(size: int = 16, weight: str = "bold") -> ctk.CTkFont:
    return ctk.CTkFont(family=FONT_FAMILY, size=size, weight=weight)


def font_body(size: int = 12, weight: str = "normal") -> ctk.CTkFont:
    return ctk.CTkFont(family=FONT_FAMILY, size=size, weight=weight)


def font_caption(size: int = 11, weight: str = "normal") -> ctk.CTkFont:
    return ctk.CTkFont(family=FONT_FAMILY, size=size, weight=weight)


def font_micro(size: int = 10, weight: str = "bold") -> ctk.CTkFont:
    return ctk.CTkFont(family=FONT_FAMILY, size=size, weight=weight)


# ---------------------------------------------------------------------------
# GEOMETRY & RADIUS STANDARDS
# ---------------------------------------------------------------------------

RADIUS_CARD = 10
RADIUS_BUTTON = 7
RADIUS_INPUT = 6
RADIUS_BADGE = 12
