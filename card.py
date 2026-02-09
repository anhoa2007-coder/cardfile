"""Card data model for CardFile application."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import json


@dataclass
class Card:
    """Represents a single card in the CardFile."""
    
    title: str = "Untitled"
    content: str = ""
    created: datetime = field(default_factory=datetime.now)
    modified: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Ensure title is not empty."""
        if not self.title.strip():
            self.title = "Untitled"
    
    def update_content(self, new_content: str) -> None:
        """Update content and modification timestamp."""
        self.content = new_content
        self.modified = datetime.now()
    
    def update_title(self, new_title: str) -> None:
        """Update title and modification timestamp."""
        self.title = new_title.strip() or "Untitled"
        self.modified = datetime.now()
    
    def to_dict(self) -> dict:
        """Convert card to dictionary for serialization."""
        return {
            "title": self.title,
            "content": self.content,
            "created": self.created.isoformat(),
            "modified": self.modified.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Card":
        """Create a Card from a dictionary."""
        return cls(
            title=data.get("title", "Untitled"),
            content=data.get("content", ""),
            created=datetime.fromisoformat(data["created"]) if "created" in data else datetime.now(),
            modified=datetime.fromisoformat(data["modified"]) if "modified" in data else datetime.now()
        )
    
    def get_index_title(self, max_length: int = 20) -> str:
        """Get truncated title for index display."""
        if len(self.title) <= max_length:
            return self.title
        return self.title[:max_length - 3] + "..."
