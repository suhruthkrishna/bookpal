"""
Data persistence layer for BookPal.
Handles saving and loading user favorites and preferences.
"""

import json
import os
from typing import Dict, List, Any

# Default file path for storing favorites
FAVORITES_FILE = "favorites.json"

def load_favorites() -> Dict[str, List[Dict[str, Any]]]:
    """
    Load user's favorite books from JSON file.
    
    Returns:
        Dictionary where keys are genres and values are lists of book dictionaries.
        Example: {"Fantasy": [{"isbn": "123", "title": "Book Title", ...}]}
    """
    if not os.path.exists(FAVORITES_FILE):
        # Return empty structure if file doesn't exist
        return {}
    
    try:
        with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading favorites: {e}")
        return {}

def save_favorites(favorites: Dict[str, List[Dict[str, Any]]]) -> bool:
    """
    Save user's favorite books to JSON file.
    
    Args:
        favorites: Dictionary of genres to book lists
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(FAVORITES_FILE, 'w', encoding='utf-8') as f:
            json.dump(favorites, f, indent=2, ensure_ascii=False)
        return True
    except IOError as e:
        print(f"Error saving favorites: {e}")
        return False

def add_favorite_book(genre: str, book_data: Dict[str, Any]) -> bool:
    """
    Add a book to favorites for a specific genre.
    
    Args:
        genre: The genre category (e.g., "Fantasy", "Mystery")
        book_data: Dictionary containing book information
        
    Returns:
        True if successful, False otherwise
    """
    favorites = load_favorites()
    
    # Initialize genre list if it doesn't exist
    if genre not in favorites:
        favorites[genre] = []
    
    # Check if book already exists (by ISBN)
    isbn = book_data.get('isbn')
    if isbn and any(book.get('isbn') == isbn for book in favorites[genre]):
        print(f"Book with ISBN {isbn} already in favorites for {genre}")
        return False
    
    # Add the book
    favorites[genre].append(book_data)
    
    return save_favorites(favorites)

def get_all_favorites() -> Dict[str, List[Dict[str, Any]]]:
    """Get all favorite books organized by genre."""
    return load_favorites()

def clear_favorites() -> bool:
    """Clear all favorites (useful for testing/reset)."""
    try:
        if os.path.exists(FAVORITES_FILE):
            os.remove(FAVORITES_FILE)
        return True
    except IOError as e:
        print(f"Error clearing favorites: {e}")
        return False