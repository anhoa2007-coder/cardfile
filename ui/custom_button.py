"""Custom styled buttons for CardFile application.

Provides modern, rounded buttons with hover/press animations and
theme-aware coloring for both light and dark modes.
"""

import tkinter as tk


class CustomButton(tk.Frame):
    """A modern, rounded-rectangle button drawn on a Canvas.

    Features:
        - Rounded corners with configurable radius
        - Smooth color transitions on hover and press
        - Theme-aware: call update_theme() to switch palettes
        - Optional icon text (emoji) rendered left of the label
    """

    def __init__(
        self,
        parent,
        text: str = "",
        command=None,
        width: int = 120,
        height: int = 38,
        corner_radius: int = 8,
        bg_color: str = "#e1e1e1",
        fg_color: str = "#1e1e1e",
        hover_bg: str = "#c8c8c8",
        hover_fg: str = "#000000",
        press_bg: str = "#0078d4",
        press_fg: str = "#ffffff",
        border_color: str = "#888888",
        font: tuple = ("Segoe UI", 11),
        parent_bg: str = "#ffffff",
        **kwargs,
    ):
        super().__init__(parent, bg=parent_bg, bd=0, highlightthickness=0, **kwargs)

        self._canvas = tk.Canvas(
            self,
            width=width,
            height=height,
            highlightthickness=0,
            borderwidth=0,
            bg=parent_bg,
        )
        self._canvas.pack()

        self._text = text
        self._command = command
        self._btn_width = width
        self._btn_height = height
        self._radius = corner_radius
        self._font = font

        # Color sets
        self._bg_color = bg_color
        self._fg_color = fg_color
        self._hover_bg = hover_bg
        self._hover_fg = hover_fg
        self._press_bg = press_bg
        self._press_fg = press_fg
        self._border_color = border_color
        self._parent_bg = parent_bg

        # State
        self._hovered = False
        self._pressed = False
        self._disabled = False

        # Defer initial draw until widget is mapped
        self.after_idle(self._draw)

        # Bindings — bind on canvas
        self._canvas.bind("<Enter>", self._on_enter)
        self._canvas.bind("<Leave>", self._on_leave)
        self._canvas.bind("<ButtonPress-1>", self._on_press)
        self._canvas.bind("<ButtonRelease-1>", self._on_release)

    # --- Drawing ---------------------------------------------------------

    def _rounded_rect(self, x1, y1, x2, y2, r, **kw):
        """Draw a rounded rectangle and return its item id."""
        points = [
            x1 + r, y1,
            x2 - r, y1,
            x2, y1,
            x2, y1 + r,
            x2, y2 - r,
            x2, y2,
            x2 - r, y2,
            x1 + r, y2,
            x1, y2,
            x1, y2 - r,
            x1, y1 + r,
            x1, y1,
            x1 + r, y1,
        ]
        return self._canvas.create_polygon(points, smooth=True, **kw)

    def _draw(self):
        self._canvas.delete("all")

        if self._pressed and not self._disabled:
            bg = self._press_bg
            fg = self._press_fg
        elif self._hovered and not self._disabled:
            bg = self._hover_bg
            fg = self._hover_fg
        else:
            bg = self._bg_color
            fg = self._fg_color

        # Background rounded rect
        outline = self._press_bg if self._pressed else self._border_color
        self._rounded_rect(
            1, 1, self._btn_width - 1, self._btn_height - 1, self._radius,
            fill=bg, outline=outline, width=1,
        )

        # Text
        self._canvas.create_text(
            self._btn_width // 2,
            self._btn_height // 2,
            text=self._text,
            fill=fg,
            font=self._font,
            anchor="center",
        )

    # --- Events ----------------------------------------------------------

    def _on_enter(self, _event):
        if self._disabled:
            return
        self._hovered = True
        self._draw()

    def _on_leave(self, _event):
        self._hovered = False
        self._pressed = False
        self._draw()

    def _on_press(self, _event):
        if self._disabled:
            return
        self._pressed = True
        self._draw()

    def _on_release(self, _event):
        if self._disabled:
            return
        was_pressed = self._pressed
        self._pressed = False
        self._draw()
        if was_pressed and self._hovered and self._command:
            self._command()

    # --- Public API ------------------------------------------------------

    def update_theme(
        self,
        bg_color: str,
        fg_color: str,
        hover_bg: str,
        hover_fg: str,
        press_bg: str,
        press_fg: str,
        border_color: str,
        parent_bg: str,
    ):
        """Switch all colors (e.g. when toggling dark mode)."""
        self._bg_color = bg_color
        self._fg_color = fg_color
        self._hover_bg = hover_bg
        self._hover_fg = hover_fg
        self._press_bg = press_bg
        self._press_fg = press_fg
        self._border_color = border_color
        self._parent_bg = parent_bg
        self.configure(bg=parent_bg)
        self._canvas.configure(bg=parent_bg)
        self._draw()

    def set_text(self, text: str):
        self._text = text
        self._draw()

    def set_disabled(self, disabled: bool):
        self._disabled = disabled
        self._draw()


def make_toolbar_button(parent, text, command, colors, width=130, height=40):
    """Factory for creating a themed toolbar CustomButton."""
    btn = CustomButton(
        parent,
        text=text,
        command=command,
        width=width,
        height=height,
        corner_radius=10,
        bg_color=colors["button_bg"],
        fg_color=colors["button_fg"],
        hover_bg=colors["button_active"],
        hover_fg=colors["fg_bright"],
        press_bg=colors["accent"],
        press_fg=colors["fg_bright"],
        border_color=colors["border"],
        font=("Segoe UI", 10),
        parent_bg=colors["bg"],
    )
    return btn


def theme_toolbar_button(btn: CustomButton, colors: dict):
    """Re-theme an existing toolbar CustomButton."""
    btn.update_theme(
        bg_color=colors["button_bg"],
        fg_color=colors["button_fg"],
        hover_bg=colors["button_active"],
        hover_fg=colors["fg_bright"],
        press_bg=colors["accent"],
        press_fg=colors["fg_bright"],
        border_color=colors["border"],
        parent_bg=colors["bg"],
    )
