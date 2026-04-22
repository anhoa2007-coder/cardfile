"""CardFile - A personal information manager.

A Python recreation of the classic Windows 3.x CardFile application.
"""

import tkinter as tk
from ui.main_window import MainWindow


def main():
    """Application entry point."""
    # Set DPI awareness for Windows 10/11 (must be before Tk())
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    
    root = tk.Tk()
    
    # Create and run application
    app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
