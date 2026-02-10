import ctypes
from ctypes import windll, byref, c_int, c_void_p

def apply_dark_mode(root, is_dark: bool = True):
    """
    Apply dark mode to the window title bar.
    
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
        
        # Force a redraw by slightly resizing (sometimes needed)
        # However, usually DwmSetWindowAttribute works immediately on newer Windows 10/11 builds.
        # If not, we might need to trigger a non-client area paint.
        
    except Exception as e:
        print(f"Failed to apply dark mode: {e}")
