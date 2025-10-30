"""
Book metadata fetcher using Google Books API with OpenLibrary fallback.
Handles ISBN lookup and book information retrieval.
"""

import requests
import re
from typing import Dict, Optional, Any

class BookAPI:
    """
    Handles book metadata retrieval from various APIs.
    """
    
    def __init__(self):
        self.google_books_base = "https://www.googleapis.com/books/v1/volumes"
        self.openlibrary_base = "https://openlibrary.org/api/volumes/brief/isbn"
    
    def clean_isbn(self, isbn: str) -> str:
        """
        Clean and validate ISBN by removing hyphens and spaces.
        
        Args:
            isbn: Raw ISBN string
            
        Returns:
            Cleaned ISBN string containing only digits and X
        """
        # Remove all non-alphanumeric characters except X (for ISBN-10)
        cleaned = re.sub(r'[^0-9X]', '', isbn.upper())
        return cleaned
    
    def fetch_from_google_books(self, isbn: str) -> Optional[Dict[str, Any]]:
        """
        Fetch book metadata from Google Books API.
        
        Args:
            isbn: Cleaned ISBN string
            
        Returns:
            Dictionary with book metadata or None if not found
        """
        try:
            params = {'q': f'isbn:{isbn}'}
            response = requests.get(self.google_books_base, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Check if we found any books
            if data.get('totalItems', 0) == 0:
                return None
            
            # Get the first result
            book_info = data['items'][0]['volumeInfo']
            
            # Get description - try multiple fields and provide better fallbacks
            description = book_info.get('description', '')
            if not description:
                description = book_info.get('subtitle', '')
            if not description:
                # Create a basic description from available info
                title = book_info.get('title', 'This book')
                authors = book_info.get('authors', [])
                categories = book_info.get('categories', [])
                
                author_text = f" by {', '.join(authors)}" if authors else ""
                category_text = f" in the {categories[0]} genre" if categories else ""
                description = f"{title}{author_text}{category_text}. A compelling read that explores its themes through engaging storytelling."
            
            # Extract relevant information
            result = {
                'title': book_info.get('title', 'Unknown Title'),
                'authors': book_info.get('authors', ['Unknown Author']),
                'description': description,
                'categories': book_info.get('categories', ['Fiction']),
                'published_date': book_info.get('publishedDate', ''),
                'publisher': book_info.get('publisher', 'Unknown Publisher'),
                'page_count': book_info.get('pageCount', 0),
                'isbn': isbn,
                'source': 'Google Books'
            }
            
            return result
            
        except (requests.RequestException, KeyError, IndexError) as e:
            print(f"Google Books API error for ISBN {isbn}: {e}")
            return None
    
    def fetch_from_openlibrary(self, isbn: str) -> Optional[Dict[str, Any]]:
        """
        Fetch book metadata from OpenLibrary API as fallback.
        
        Args:
            isbn: Cleaned ISBN string
            
        Returns:
            Dictionary with book metadata or None if not found
        """
        try:
            url = f"{self.openlibrary_base}/{isbn}.json"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if not data or 'records' not in data:
                return None
            
            # Get the first record
            record_key = list(data['records'].keys())[0]
            record = data['records'][record_key]
            
            book_data = record.get('data', {})
            
            # Get description with better fallbacks for OpenLibrary too
            description = book_data.get('description', '')
            if not description:
                # Create descriptive text from available info
                title = book_data.get('title', 'This book')
                subjects = book_data.get('subjects', [])
                
                # Extract subject names if they are dictionaries
                subject_names = []
                for subject in subjects:
                    if isinstance(subject, dict):
                        subject_names.append(subject.get('name', ''))
                    else:
                        subject_names.append(str(subject))
                
                subject_text = f" about {subject_names[0]}" if subject_names else ""
                description = f"{title}{subject_text}. An engaging work that captivates readers with its narrative and characters."
            
            # Handle subjects/categories - extract names if they are dictionaries
            subjects = book_data.get('subjects', [])
            categories = []
            for subject in subjects:
                if isinstance(subject, dict):
                    categories.append(subject.get('name', 'Unknown'))
                else:
                    categories.append(str(subject))
            
            if not categories:
                categories = ['Fiction']
            
            result = {
                'title': book_data.get('title', 'Unknown Title'),
                'authors': book_data.get('authors', [{'name': 'Unknown Author'}]),
                'description': description,
                'categories': categories,  # Use processed categories
                'published_date': book_data.get('publish_date', ''),
                'publisher': book_data.get('publishers', ['Unknown Publisher'])[0] if book_data.get('publishers') else 'Unknown Publisher',
                'page_count': book_data.get('number_of_pages', 0),
                'isbn': isbn,
                'source': 'OpenLibrary'
            }
            
            # Extract author names if they're in dictionary format
            if result['authors'] and isinstance(result['authors'][0], dict):
                result['authors'] = [author.get('name', 'Unknown Author') for author in result['authors']]
            
            return result
            
        except (requests.RequestException, KeyError, IndexError) as e:
            print(f"OpenLibrary API error for ISBN {isbn}: {e}")
            return None
    
    def get_book_by_isbn(self, isbn: str) -> Optional[Dict[str, Any]]:
        """
        Main method to get book metadata by ISBN with fallback.
        
        Args:
            isbn: Raw ISBN string (can contain spaces/hyphens)
            
        Returns:
            Dictionary with book metadata or None if book not found
        """
        cleaned_isbn = self.clean_isbn(isbn)
        
        if not cleaned_isbn:
            return None
        
        # Try Google Books first
        book_data = self.fetch_from_google_books(cleaned_isbn)
        
        # Fallback to OpenLibrary
        if not book_data:
            book_data = self.fetch_from_openlibrary(cleaned_isbn)
        
        return book_data

    def detect_genre(self, categories: list) -> str:
        """
        Detect the primary genre from book categories.
        
        Args:
            categories: List of category strings from API
            
        Returns:
            Detected genre string
        """
        # Handle None, empty list, or ['Unknown'] cases
        if not categories or categories == ['Unknown'] or categories is None:
            return "Fiction"
        
        # Ensure all categories are strings (handle dictionaries)
        category_strings = []
        for cat in categories:
            if isinstance(cat, dict):
                category_strings.append(str(cat.get('name', 'Unknown')))
            else:
                category_strings.append(str(cat))
        
        # Ensure categories is a list and convert all elements to strings
        try:
            categories_text = ' '.join(category_strings).lower()
        except (TypeError, AttributeError):
            return "Fiction"
        
        # Common genre mappings
        genre_keywords = {
            'Fantasy': ['fantasy', 'magic', 'epic', 'sword', 'dragon', 'wizard', 'middle-earth', 'thrones', 'westeros', 'mythical'],
            'Science Fiction': ['science fiction', 'sci-fi', 'space', 'future', 'dystopian', 'cyberpunk', 'alien', 'galaxy'],
            'Mystery': ['mystery', 'crime', 'detective', 'thriller', 'suspense', 'murder', 'investigation'],
            'Romance': ['romance', 'love', 'relationship', 'contemporary romance', 'historical romance'],
            'Horror': ['horror', 'ghost', 'supernatural', 'terror', 'haunted', 'zombie', 'vampire'],
            'Biography': ['biography', 'memoir', 'autobiography', 'life story'],
            'History': ['history', 'historical', 'ancient', 'medieval', 'world war'],
            'Science': ['science', 'technology', 'physics', 'biology', 'chemistry', 'mathematics'],
            'Self-Help': ['self-help', 'personal development', 'motivational', 'psychology'],
            'Young Adult': ['young adult', 'ya', 'teen', 'adolescent', 'coming of age'],
            'Classic': ['classic', 'literature', 'classic literature']
        }
        
        # Find the best matching genre
        best_match = "Fiction"  # Default
        max_matches = 0
        
        for genre, keywords in genre_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in categories_text)
            if matches > max_matches:
                max_matches = matches
                best_match = genre
        
        return best_match
