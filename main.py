"""CardFile - A personal information manager.

A Python recreation of the classic Windows 3.x CardFile application.
"""

import tkinter as tk
from ui.main_window import MainWindow


def main():
    """Application entry point."""
    root = tk.Tk()
    
    # Set DPI awareness for Windows 10/11
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    
    # Create and run application
    app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
