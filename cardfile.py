"""CardFile manager - handles collection of cards and file I/O."""

import json
from pathlib import Path
from typing import List, Optional
from card import Card


class CardFile:
    """Manages a collection of cards with file operations."""
    
    def __init__(self):
        self.cards: List[Card] = []
        self.current_index: int = 0
        self.filepath: Optional[Path] = None
        self.modified: bool = False
    
    @property
    def current_card(self) -> Optional[Card]:
        """Get the currently selected card."""
        if not self.cards:
            return None
        return self.cards[self.current_index]
    
    @property
    def card_count(self) -> int:
        """Get total number of cards."""
        return len(self.cards)
    
    def add_card(self, title: str = "New Card", content: str = "") -> Card:
        """Add a new card and return it."""
        card = Card(title=title, content=content)
        self.cards.append(card)
        self.sort_cards()
        self.current_index = self.cards.index(card)
        self.modified = True
        return card
    
    def delete_card(self, index: Optional[int] = None) -> bool:
        """Delete card at index (or current card). Returns True if deleted."""
        if not self.cards:
            return False
        
        idx = index if index is not None else self.current_index
        if 0 <= idx < len(self.cards):
            del self.cards[idx]
            self.modified = True
            
            # Adjust current index
            if self.cards:
                self.current_index = min(self.current_index, len(self.cards) - 1)
            else:
                self.current_index = 0
            return True
        return False
    
    def duplicate_card(self, index: Optional[int] = None) -> Optional[Card]:
        """Duplicate card at index (or current card)."""
        if not self.cards:
            return None
        
        idx = index if index is not None else self.current_index
        if 0 <= idx < len(self.cards):
            original = self.cards[idx]
            new_card = Card(
                title=f"{original.title} (Copy)",
                content=original.content
            )
            self.cards.append(new_card)
            self.sort_cards()
            self.current_index = self.cards.index(new_card)
            self.modified = True
            return new_card
        return None
    
    def sort_cards(self) -> None:
        """Sort cards alphabetically by title."""
        if self.cards:
            current_card = self.current_card
            self.cards.sort(key=lambda c: c.title.lower())
            if current_card:
                self.current_index = self.cards.index(current_card)
    
    def navigate_to(self, index: int) -> bool:
        """Navigate to card at specific index."""
        if 0 <= index < len(self.cards):
            self.current_index = index
            return True
        return False
    
    def navigate_next(self) -> bool:
        """Move to next card."""
        if self.current_index < len(self.cards) - 1:
            self.current_index += 1
            return True
        return False
    
    def navigate_previous(self) -> bool:
        """Move to previous card."""
        if self.current_index > 0:
            self.current_index -= 1
            return True
        return False
    
    def search(self, query: str, search_content: bool = True) -> List[int]:
        """Search cards by title (and optionally content). Returns matching indices."""
        query = query.lower()
        results = []
        for i, card in enumerate(self.cards):
            if query in card.title.lower():
                results.append(i)
            elif search_content and query in card.content.lower():
                results.append(i)
        return results
    
    def find_next(self, query: str, from_index: int = 0) -> Optional[int]:
        """Find next card matching query starting from index."""
        results = self.search(query)
        for idx in results:
            if idx > from_index:
                return idx
        # Wrap around
        for idx in results:
            if idx <= from_index:
                return idx
        return None
    
    # File Operations
    
    def new_file(self) -> None:
        """Create a new empty cardfile."""
        self.cards = []
        self.current_index = 0
        self.filepath = None
        self.modified = False
    
    def save_to_file(self, filepath: Optional[Path] = None) -> bool:
        """Save cards to JSON file."""
        save_path = filepath or self.filepath
        if not save_path:
            return False
        
        try:
            data = {
                "version": "1.0.1",
                "cards": [card.to_dict() for card in self.cards]
            }
            save_path = Path(save_path)
            save_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
            self.filepath = save_path
            self.modified = False
            return True
        except Exception as e:
            print(f"Error saving file: {e}")
            return False
    
    def load_from_file(self, filepath: Path) -> bool:
        """Load cards from JSON file."""
        try:
            filepath = Path(filepath)
            data = json.loads(filepath.read_text(encoding="utf-8"))
            
            self.cards = [Card.from_dict(card_data) for card_data in data.get("cards", [])]
            self.current_index = 0 if self.cards else 0
            self.filepath = filepath
            self.modified = False
            self.sort_cards()
            return True
        except Exception as e:
            print(f"Error loading file: {e}")
            return False
    
    def get_title(self) -> str:
        """Get display title for window."""
        name = self.filepath.stem if self.filepath else "Untitled"
        modified_indicator = " *" if self.modified else ""
        return f"{name}{modified_indicator} - CardFile"
