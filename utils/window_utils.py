import ctypes
from ctypes import windll, byref, c_int, c_void_p


def is_system_dark_mode() -> bool:
    """Detect whether Windows is using dark mode for apps.

    Reads the registry key:
        HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize
        -> AppsUseLightTheme  (DWORD: 0 = dark, 1 = light)

    Returns True if the system is in dark mode, False otherwise.
    Falls back to False on non-Windows or older systems without the key.
    """
    try:
        import winreg
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize",
        ) as key:
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return value == 0  # 0 means dark mode
    except Exception:
        return False


# --- Color Palette ---
DARK_COLORS = {
    "bg":           "#1e1e1e",
    "bg_alt":       "#252526",
    "bg_elevated":  "#2d2d30",
    "bg_input":     "#3c3c3c",
    "fg":           "#d4d4d4",
    "fg_dim":       "#808080",
    "fg_bright":    "#ffffff",
    "accent":       "#569cd6",
    "accent_hover": "#6cb0f0",
    "border":       "#3c3c3c",
    "selected_bg":  "#094771",
    "selected_fg":  "#ffffff",
    "button_bg":    "#3c3c3c",
    "button_fg":    "#cccccc",
    "button_active":"#505050",
    "menu_bg":      "#252526",
    "menu_fg":      "#cccccc",
    "scrollbar_bg": "#3c3c3c",
    "scrollbar_fg": "#686868",
}

LIGHT_COLORS = {
    "bg":           "#ffffff",
    "bg_alt":       "#f3f3f3",
    "bg_elevated":  "#f9f9f9",
    "bg_input":     "#ffffff",
    "fg":           "#1e1e1e",
    "fg_dim":       "#6e6e6e",
    "fg_bright":    "#000000",
    "accent":       "#0078d4",
    "accent_hover": "#106ebe",
    "border":       "#d4d4d4",
    "selected_bg":  "#cce8ff",
    "selected_fg":  "#000000",
    "button_bg":    "#e1e1e1",
    "button_fg":    "#1e1e1e",
    "button_active":"#c8c8c8",
    "menu_bg":      "#f3f3f3",
    "menu_fg":      "#1e1e1e",
    "scrollbar_bg": "#e1e1e1",
    "scrollbar_fg": "#a0a0a0",
}


def get_colors(is_dark: bool) -> dict:
    """Return the color palette for the given theme."""
    return DARK_COLORS if is_dark else LIGHT_COLORS


def apply_dark_title_bar(root, is_dark: bool = True):
    """
    Apply dark mode to the window title bar using the Windows DWM API.

    Args:
        root: The tkinter root window or toplevel window.
        is_dark: True to enable dark mode, False for light mode.
    """
    try:
        # DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20

        # Get window handle
        hwnd = windll.user32.GetParent(root.winfo_id())

        # Set the attribute
        value = c_int(1 if is_dark else 0)
        windll.dwmapi.DwmSetWindowAttribute(
            hwnd, 
            DWMWA_USE_IMMERSIVE_DARK_MODE, 
            byref(value), 
            ctypes.sizeof(value)
        )

    except Exception as e:
        print(f"Failed to apply dark title bar: {e}")


def apply_dark_mode(root, is_dark: bool = True):
    """
    Apply dark mode to the window title bar.
    Kept for backward compatibility — delegates to apply_dark_title_bar.
    
    Args:
        root: The tkinter root window or toplevel window.
        is_dark: True to enable dark mode, False for light mode.
    """
    apply_dark_title_bar(root, is_dark)


def style_menu(menu, colors: dict):
    """Apply theme colors to a tk.Menu and all its sub-menus recursively."""
    menu.configure(
        bg=colors["menu_bg"],
        fg=colors["menu_fg"],
        activebackground=colors["accent"],
        activeforeground=colors["fg_bright"],
        relief="flat",
        borderwidth=0,
    )
    # Recurse into sub-menus
    last = menu.index("end")
    if last is not None:
        for i in range(last + 1):
            try:
                submenu = menu.nametowidget(menu.entrycget(i, "menu"))
                style_menu(submenu, colors)
            except Exception:
                pass
