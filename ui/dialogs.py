"""Dialog windows for CardFile application."""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable
from utils.window_utils import apply_dark_mode, get_colors
from ui.custom_button import make_toolbar_button


class BaseDialog(tk.Toplevel):
    """Base dialog class with common functionality."""
    
    def __init__(self, parent, title: str, width: int = 350, height: int = 150):
        super().__init__(parent)
        self.title(title)
        self.transient(parent)
        self.grab_set()
        
        # Center on parent
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        
        # Result
        self.result = None
        
        # Detect parent dark mode and apply theme to dialog
        self._apply_dialog_theme(parent)
        
        # Build UI
        self.create_widgets()
        
        # Center on screen
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - width) // 2
        y = parent.winfo_y() + (parent.winfo_height() - height) // 2
        self.geometry(f"+{x}+{y}")
        
        # Bind Escape to close
        self.bind("<Escape>", lambda e: self.cancel())
    
    def _apply_dialog_theme(self, parent):
        """Apply dark/light theme to dialog based on parent window state."""
        # Try to detect dark mode from the parent MainWindow
        self._is_dark = False
        try:
            # Walk up to find the MainWindow instance
            top = parent
            if hasattr(top, "is_dark_mode"):
                self._is_dark = top.is_dark_mode.get()
            elif hasattr(top, "master") and hasattr(top.master, "is_dark_mode"):
                self._is_dark = top.master.is_dark_mode.get()
        except Exception:
            pass
        
        self._colors = get_colors(self._is_dark)
        self.configure(bg=self._colors["bg"])
        
        # Apply DWM dark title bar
        self.update_idletasks()
        apply_dark_mode(self, self._is_dark)
    
    def create_widgets(self):
        """Override in subclasses to build UI."""
        pass
    
    def ok(self):
        """Handle OK button."""
        self.destroy()
    
    def cancel(self):
        """Handle Cancel button."""
        self.result = None
        self.destroy()


class AddEditCardDialog(BaseDialog):
    """Dialog for adding or editing a card."""
    
    def __init__(self, parent, title: str = "New Card", 
                 initial_title: str = "", initial_content: str = ""):
        self.initial_title = initial_title
        self.initial_content = initial_content
        super().__init__(parent, title, width=450, height=400)
    
    def create_widgets(self):
        # Main frame with padding
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill="both", expand=True)
        
        # Title
        ttk.Label(main_frame, text="Title:").pack(anchor="w")
        self.title_entry = ttk.Entry(main_frame, width=50)
        self.title_entry.insert(0, self.initial_title)
        self.title_entry.pack(fill="x", pady=(0, 10))
        self.title_entry.focus_set()
        
        # Content
        ttk.Label(main_frame, text="Content:").pack(anchor="w")
        
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        colors = self._colors
        self.content_text = tk.Text(content_frame, wrap="word", height=10,
                                     bg=colors["bg_input"],
                                     fg=colors["fg"],
                                     insertbackground=colors["fg"],
                                     selectbackground=colors["accent"],
                                     selectforeground=colors["fg_bright"])
        scrollbar = tk.Scrollbar(content_frame, orient="vertical", 
                                   command=self.content_text.yview,
                                   bg=colors["scrollbar_bg"],
                                   troughcolor=colors["bg_alt"],
                                   activebackground=colors["scrollbar_fg"],
                                   highlightthickness=0, borderwidth=0, width=14)
        self.content_text.configure(yscrollcommand=scrollbar.set)
        
        self.content_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.content_text.insert("1.0", self.initial_content)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        ok_btn = make_toolbar_button(button_frame, "OK", self.ok,
                                      self._colors, width=80, height=28)
        ok_btn.pack(side="right", padx=(5, 0))
        cancel_btn = make_toolbar_button(button_frame, "Cancel", self.cancel,
                                          self._colors, width=80, height=28)
        cancel_btn.pack(side="right")
        
        # Bind Enter in title to OK
        self.title_entry.bind("<Return>", lambda e: self.ok())
    
    def ok(self):
        title = self.title_entry.get().strip()
        content = self.content_text.get("1.0", "end-1c")
        self.result = {"title": title or "Untitled", "content": content}
        self.destroy()


class SearchDialog(BaseDialog):
    """Dialog for searching cards."""
    
    def __init__(self, parent, on_find: Callable[[str, bool], None]):
        self.on_find = on_find
        super().__init__(parent, "Find", width=350, height=180)
    
    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill="both", expand=True)
        
        # Search field
        ttk.Label(main_frame, text="Find:").pack(anchor="w", pady=(0, 5))
        
        self.search_entry = ttk.Entry(main_frame, width=40)
        self.search_entry.pack(fill="x", pady=(0, 10))
        self.search_entry.focus_set()
        
        # Options
        self.search_content_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(main_frame, text="Search in content", 
                        variable=self.search_content_var).pack(anchor="w")
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        find_btn = make_toolbar_button(button_frame, "Find Next", self.find_next,
                                        self._colors, width=100, height=28)
        find_btn.pack(side="right", padx=(5, 0))
        close_btn = make_toolbar_button(button_frame, "Close", self.cancel,
                                        self._colors, width=80, height=28)
        close_btn.pack(side="right")
        
        # Bind Enter to find
        self.search_entry.bind("<Return>", lambda e: self.find_next())
    
    def find_next(self):
        query = self.search_entry.get()
        if query:
            self.on_find(query, self.search_content_var.get())


class GoToDialog(BaseDialog):
    """Dialog for going to a specific card by index."""
    
    def __init__(self, parent, card_count: int):
        self.card_count = card_count
        super().__init__(parent, "Go To Card", width=300, height=125)
    
    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill="both", expand=True)
        
        # Card number
        entry_frame = ttk.Frame(main_frame)
        entry_frame.pack(fill="x", pady=(0, 15))
        
        ttk.Label(entry_frame, text=f"Card number (1-{self.card_count}):").pack(side="left")
        
        self.number_entry = ttk.Entry(entry_frame, width=10)
        self.number_entry.pack(side="left", padx=(10, 0))
        self.number_entry.focus_set()
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        go_btn = make_toolbar_button(button_frame, "Go", self.ok,
                                      self._colors, width=80, height=28)
        go_btn.pack(side="right", padx=(5, 0))
        cancel_btn = make_toolbar_button(button_frame, "Cancel", self.cancel,
                                          self._colors, width=80, height=28)
        cancel_btn.pack(side="right")
        
        self.number_entry.bind("<Return>", lambda e: self.ok())
    
    def ok(self):
        try:
            num = int(self.number_entry.get())
            if 1 <= num <= self.card_count:
                self.result = num - 1  # Convert to 0-indexed
        except ValueError:
            pass
        self.destroy()


class AboutDialog(BaseDialog):
    """About dialog."""
    
    def __init__(self, parent):
        super().__init__(parent, "About CardFile", width=300, height=230)
    
    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # App name
        ttk.Label(main_frame, text="CardFile", font=("Segoe UI", 16, "bold")).pack()
        ttk.Label(main_frame, text="Version 1.0.1").pack(pady=(5, 15))
        
        # Description
        ttk.Label(main_frame, text="A personal information manager\ninspired by Windows 3.1 CardFile",
                  justify="center").pack()
        
        # OK button
        ok_btn = make_toolbar_button(main_frame, "OK", self.ok,
                                      self._colors, width=80, height=28)
        ok_btn.pack(pady=(20, 0))
