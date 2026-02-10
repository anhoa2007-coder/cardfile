"""Main window for CardFile application."""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from cardfile import CardFile
from ui.dialogs import AddEditCardDialog, SearchDialog, GoToDialog, AboutDialog
from utils.window_utils import apply_dark_mode


class MainWindow:
    """Main CardFile application window."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.cardfile = CardFile()
        
        # Configure root window
        self.root.title("Untitled - CardFile")
        self.root.geometry("650x500")
        self.root.minsize(500, 400)
        
        # Use Windows 11 theme
        self.style = ttk.Style()
        if "vista" in self.style.theme_names():
            self.style.theme_use("vista")
        elif "winnative" in self.style.theme_names():
            self.style.theme_use("winnative")
        
        # Custom styles
        self.style.configure("Index.TButton", padding=(8, 4))
        self.style.configure("Selected.TButton", padding=(8, 4))
        
        # Search state
        self.last_search_query = ""
        self.search_dialog = None
        
        # Initialize dark mode variable (needed for menu)
        self.is_dark_mode = tk.BooleanVar(value=True)
        
        # Build UI
        self.create_menu()
        self.create_toolbar()
        self.create_index_bar()
        self.create_card_view()
        self.create_status_bar()
        
        # Apply theme (needs UI elements to be ready)
        self.apply_theme()
        
        # Bind keyboard shortcuts
        self.bind_shortcuts()
        
        # Start with one card
        self.cardfile.add_card("Welcome", "Welcome to CardFile!\n\nClick Edit > Add Card or press Ctrl+N to create a new card.")
        
        self.refresh_ui()
    
    def create_menu(self):
        """Create menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+Shift+N")
        file_menu.add_command(label="Open...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_close)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Add Card", command=self.add_card, accelerator="Ctrl+N")
        edit_menu.add_command(label="Edit Card", command=self.edit_card, accelerator="F2")
        edit_menu.add_command(label="Duplicate Card", command=self.duplicate_card, accelerator="Ctrl+D")
        edit_menu.add_separator()
        edit_menu.add_separator()
        edit_menu.add_command(label="Go To...", command=self.goto_card, accelerator="Ctrl+G")
        edit_menu.add_command(label="Find...", command=self.find_card, accelerator="Ctrl+F")
        edit_menu.add_command(label="Find Next", command=self.find_next, accelerator="F3")
        edit_menu.add_separator()
        edit_menu.add_command(label="Previous Card", command=self.previous_card, accelerator="Ctrl+PgUp")
        edit_menu.add_command(label="Next Card", command=self.next_card, accelerator="Ctrl+PgDn")
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_checkbutton(label="Dark Mode", variable=self.is_dark_mode, command=self.apply_theme)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About CardFile", command=self.show_about)
    
    def create_toolbar(self):
        """Create toolbar with common actions."""
        toolbar = ttk.Frame(self.root, padding="5")
        toolbar.pack(fill="x")
        
        # Navigation buttons
        ttk.Button(toolbar, text="◀ Prev", command=self.previous_card, width=8).pack(side="left", padx=(0, 2))
        ttk.Button(toolbar, text="Next ▶", command=self.next_card, width=8).pack(side="left", padx=(0, 10))
        
        # Card actions
        ttk.Button(toolbar, text="+ Add", command=self.add_card, width=8).pack(side="left", padx=(0, 2))
        ttk.Button(toolbar, text="✎ Edit", command=self.edit_card, width=8).pack(side="left", padx=(0, 2))
        ttk.Button(toolbar, text="🗑 Delete", command=self.delete_card, width=8).pack(side="left", padx=(0, 10))
        
        # Search
        ttk.Button(toolbar, text="🔍 Find", command=self.find_card, width=8).pack(side="left")
    
    def create_index_bar(self):
        """Create horizontal index bar showing card tabs."""
        index_frame = ttk.Frame(self.root)
        index_frame.pack(fill="x", padx=5)
        
        # Scrollable frame for tabs
        self.index_canvas = tk.Canvas(index_frame, height=40, highlightthickness=0)
        self.index_scrollbar = ttk.Scrollbar(index_frame, orient="horizontal", 
                                              command=self.index_canvas.xview)
        self.index_inner = ttk.Frame(self.index_canvas)
        
        self.index_canvas.configure(xscrollcommand=self.index_scrollbar.set)
        
        self.index_scrollbar.pack(side="bottom", fill="x")
        self.index_canvas.pack(side="top", fill="x")
        
        self.index_window = self.index_canvas.create_window((0, 0), window=self.index_inner, anchor="nw")
        
        self.index_inner.bind("<Configure>", self._on_index_configure)
        self.index_canvas.bind("<Configure>", self._on_canvas_configure)
    
    def _on_index_configure(self, event):
        self.index_canvas.configure(scrollregion=self.index_canvas.bbox("all"))
    
    def _on_canvas_configure(self, event):
        # Ensure inner frame is at least as wide as canvas
        pass
    
    def create_card_view(self):
        """Create main card view area."""
        # Card frame with border
        card_frame = ttk.LabelFrame(self.root, text="Card", padding="10")
        card_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Title (read-only display)
        title_frame = ttk.Frame(card_frame)
        title_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(title_frame, text="Title:", font=("Segoe UI", 9, "bold")).pack(side="left")
        self.title_label = ttk.Label(title_frame, text="", font=("Segoe UI", 11))
        self.title_label.pack(side="left", padx=(10, 0))
        
        # Content (read-only display)
        content_frame = ttk.Frame(card_frame)
        content_frame.pack(fill="both", expand=True)
        
        self.content_text = tk.Text(content_frame, wrap="word", font=("Segoe UI", 10),
                                     state="disabled", bg="#f9f9f9", relief="flat",
                                     padx=10, pady=10)
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", 
                                   command=self.content_text.yview)
        self.content_text.configure(yscrollcommand=scrollbar.set)
        
        self.content_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Double-click to edit
        self.content_text.bind("<Double-Button-1>", lambda e: self.edit_card())
    
    def create_status_bar(self):
        """Create status bar."""
        self.status_bar = ttk.Label(self.root, text="Ready", relief="sunken", anchor="w", padding=(5, 2))
        self.status_bar.pack(fill="x", side="bottom")
    
    def bind_shortcuts(self):
        """Bind keyboard shortcuts."""
        self.root.bind("<Control-Shift-n>", lambda e: self.new_file())
        self.root.bind("<Control-Shift-N>", lambda e: self.new_file())
        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-s>", lambda e: self.save_file())
        self.root.bind("<Control-n>", lambda e: self.add_card())
        self.root.bind("<Control-d>", lambda e: self.duplicate_card())
        self.root.bind("<Delete>", lambda e: self.delete_card())
        self.root.bind("<F2>", lambda e: self.edit_card())
        self.root.bind("<Control-g>", lambda e: self.goto_card())
        self.root.bind("<Control-f>", lambda e: self.find_card())
        self.root.bind("<F3>", lambda e: self.find_next())
        self.root.bind("<Control-Prior>", lambda e: self.previous_card())  # Ctrl+PgUp
        self.root.bind("<Control-Next>", lambda e: self.next_card())       # Ctrl+PgDn
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    # --- UI Refresh ---
    
    def refresh_ui(self):
        """Refresh all UI elements to match current state."""
        self.root.title(self.cardfile.get_title())
        self.refresh_index()
        self.refresh_card_view()
        self.refresh_status()
    
    def refresh_index(self):
        """Refresh the index tab bar."""
        # Clear existing tabs
        for widget in self.index_inner.winfo_children():
            widget.destroy()
        
        # Create tabs for each card
        for i, card in enumerate(self.cardfile.cards):
            text = card.get_index_title(15)
            
            if i == self.cardfile.current_index:
                # Current card gets a distinct look
                btn = tk.Button(self.index_inner, text=text,
                               command=lambda idx=i: self.navigate_to(idx),
                               relief="sunken", bg="#e0e0e0", padx=8, pady=4)
            else:
                btn = tk.Button(self.index_inner, text=text,
                               command=lambda idx=i: self.navigate_to(idx),
                               relief="raised", padx=8, pady=4)
            
            btn.pack(side="left", padx=2, pady=4)
    
    def refresh_card_view(self):
        """Refresh the card content display."""
        card = self.cardfile.current_card
        
        if card:
            self.title_label.config(text=card.title)
            
            self.content_text.config(state="normal")
            self.content_text.delete("1.0", "end")
            self.content_text.insert("1.0", card.content)
            self.content_text.config(state="disabled")
        else:
            self.title_label.config(text="(No cards)")
            self.content_text.config(state="normal")
            self.content_text.delete("1.0", "end")
            self.content_text.insert("1.0", "Press Ctrl+N to add a new card")
            self.content_text.config(state="disabled")
    
    def refresh_status(self):
        """Refresh status bar."""
        count = self.cardfile.card_count
        current = self.cardfile.current_index + 1 if count > 0 else 0
        self.status_bar.config(text=f"Card {current} of {count}")
    
    # --- Card Operations ---
    
    def add_card(self):
        """Add a new card."""
        dialog = AddEditCardDialog(self.root, "New Card")
        self.root.wait_window(dialog)
        
        if dialog.result:
            self.cardfile.add_card(dialog.result["title"], dialog.result["content"])
            self.refresh_ui()
    
    def edit_card(self):
        """Edit the current card."""
        card = self.cardfile.current_card
        if not card:
            return
        
        dialog = AddEditCardDialog(self.root, "Edit Card", 
                                   initial_title=card.title, 
                                   initial_content=card.content)
        self.root.wait_window(dialog)
        
        if dialog.result:
            card.update_title(dialog.result["title"])
            card.update_content(dialog.result["content"])
            self.cardfile.modified = True
            self.cardfile.sort_cards()
            self.refresh_ui()
    
    def delete_card(self):
        """Delete the current card."""
        if not self.cardfile.cards:
            return
        
        card = self.cardfile.current_card
        if messagebox.askyesno("Delete Card", f"Delete card '{card.title}'?"):
            self.cardfile.delete_card()
            self.refresh_ui()
    
    def duplicate_card(self):
        """Duplicate the current card."""
        if self.cardfile.duplicate_card():
            self.refresh_ui()
    
    # --- Navigation ---
    
    def navigate_to(self, index: int):
        """Navigate to specific card index."""
        if self.cardfile.navigate_to(index):
            self.refresh_ui()
    
    def previous_card(self):
        """Go to previous card."""
        if self.cardfile.navigate_previous():
            self.refresh_ui()
    
    def next_card(self):
        """Go to next card."""
        if self.cardfile.navigate_next():
            self.refresh_ui()
    
    def goto_card(self):
        """Show Go To dialog."""
        if not self.cardfile.cards:
            return
        
        dialog = GoToDialog(self.root, self.cardfile.card_count)
        self.root.wait_window(dialog)
        
        if dialog.result is not None:
            self.navigate_to(dialog.result)
    
    # --- Search ---
    
    def find_card(self):
        """Show search dialog."""
        def on_find(query: str, search_content: bool):
            self.last_search_query = query
            idx = self.cardfile.find_next(query, self.cardfile.current_index)
            if idx is not None:
                self.navigate_to(idx)
            else:
                messagebox.showinfo("Find", f"No cards found matching '{query}'")
        
        dialog = SearchDialog(self.root, on_find)
        self.root.wait_window(dialog)
    
    def find_next(self):
        """Find next match for last search."""
        if self.last_search_query:
            idx = self.cardfile.find_next(self.last_search_query, self.cardfile.current_index)
            if idx is not None:
                self.navigate_to(idx)
    
    # --- File Operations ---
    
    def check_save(self) -> bool:
        """Check if file needs saving. Returns True if OK to proceed."""
        if self.cardfile.modified:
            result = messagebox.askyesnocancel(
                "Save Changes",
                "Do you want to save changes to the current file?"
            )
            if result is None:  # Cancel
                return False
            if result:  # Yes
                return self.save_file()
        return True
    
    def new_file(self):
        """Create a new empty cardfile."""
        if not self.check_save():
            return
        
        self.cardfile.new_file()
        self.cardfile.add_card("Welcome", "Your new CardFile is ready!\n\nAdd cards using Ctrl+N.")
        self.refresh_ui()
    
    def open_file(self):
        """Open an existing cardfile."""
        if not self.check_save():
            return
        
        filepath = filedialog.askopenfilename(
            title="Open CardFile",
            filetypes=[("CardFile", "*.crd"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filepath:
            if self.cardfile.load_from_file(Path(filepath)):
                self.refresh_ui()
            else:
                messagebox.showerror("Error", "Failed to open file")
    
    def save_file(self) -> bool:
        """Save the current cardfile."""
        if self.cardfile.filepath:
            if self.cardfile.save_to_file():
                self.refresh_ui()
                return True
            else:
                messagebox.showerror("Error", "Failed to save file")
                return False
        else:
            return self.save_file_as()
    
    def save_file_as(self) -> bool:
        """Save the cardfile to a new location."""
        filepath = filedialog.asksaveasfilename(
            title="Save CardFile As",
            defaultextension=".crd",
            filetypes=[("CardFile", "*.crd"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filepath:
            if self.cardfile.save_to_file(Path(filepath)):
                self.refresh_ui()
                return True
            else:
                messagebox.showerror("Error", "Failed to save file")
                return False
        return False
    
    def on_close(self):
        """Handle window close."""
        if self.check_save():
            self.root.destroy()
    
    # --- Help ---
    
    def show_about(self):
        """Show About dialog."""
        AboutDialog(self.root)

    def apply_theme(self):
        """Apply the current theme settings."""
        is_dark = self.is_dark_mode.get()
        apply_dark_mode(self.root, is_dark)
        
        # UI Colors
        bg_color = "#2d2d2d" if is_dark else "#f9f9f9"
        fg_color = "#ffffff" if is_dark else "#000000"
        
        # Content Text
        self.content_text.config(bg=bg_color, fg=fg_color, insertbackground=fg_color)
        
        # Title Label (Inherits from frame usually, but let's be explicit if needed)
        # For ttk widgets, we should use styles, but direct configuration works for some properties
        # Ideally we'd configure a dark theme for ttk, but that's more involved.
        # Let's stick to the requested changes for now which seem focused on the main content area look.

