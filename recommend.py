"""
Book recommendation engine using sentence embeddings and cosine similarity.
Creates genre profiles and matches new books against user preferences.
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict, List, Tuple, Any, Optional

class BookRecommender:
    """
    Handles book embedding generation and similarity calculations.
    """
    
    def __init__(self):
        # Load the sentence transformer model for generating embeddings
        # all-MiniLM-L6-v2: Good balance of speed and accuracy, 384-dimensional embeddings
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.embedding_dim = 384  # Dimension of the embeddings
    
    def get_book_embedding(self, book_data: Dict[str, Any]) -> np.ndarray:
    """
    Generate embedding vector for a book based on its metadata.
    
    Why embeddings? They convert text into numerical vectors that capture semantic meaning.
    Similar books will have similar vectors, allowing us to measure similarity mathematically.
    
    Args:
        book_data: Dictionary containing book information
        
    Returns:
        Normalized embedding vector (numpy array)
    """
    # Safely get all text components with proper defaults
        title = book_data.get('title', '')
        authors = book_data.get('authors', [])
        description = book_data.get('description', '')
    
    # Safely handle categories - they might be None
        categories = book_data.get('categories', [])
        if categories is None:
            categories = ['Unknown']
    
        publisher = book_data.get('publisher', '')
        page_count = str(book_data.get('page_count', ''))
    
    # Create a rich text representation of the book
        text_components = [
            title,
            ' '.join(authors) if authors else '',
            description,
            ' '.join(str(cat) for cat in categories) if categories else '',
            publisher,
            page_count
        ]
    
    # Filter out empty components and join
        book_text = ' '.join([str(comp) for comp in text_components if comp])
    
    # Generate embedding
        embedding = self.model.encode(book_text)
    
    # Normalize the embedding (convert to unit vector)
    # Why normalize? So we can use cosine similarity which measures angle between vectors
    # Cosine similarity ranges from -1 (opposite) to 1 (identical), with 0 meaning no correlation
        normalized_embedding = embedding / np.linalg.norm(embedding)
    
        return normalized_embedding
    
    def create_genre_profile(self, favorite_books: List[Dict[str, Any]]) -> Optional[np.ndarray]:
        """
        Create a genre profile vector by averaging embeddings of favorite books in that genre.
        
        The genre profile represents the "average taste" of the user for that genre.
        New books are compared against this profile to see if they match the user's preferences.
        
        Args:
            favorite_books: List of book dictionaries in the same genre
            
        Returns:
            Average embedding vector for the genre, or None if no books
        """
        if not favorite_books:
            return None
        
        embeddings = []
        for book in favorite_books:
            if 'embedding' in book:
                embeddings.append(book['embedding'])
        
        if not embeddings:
            return None
        
        # Calculate mean embedding - this represents the "center" of user's taste
        profile_vector = np.mean(embeddings, axis=0)
        
        # Normalize the profile vector
        profile_vector = profile_vector / np.linalg.norm(profile_vector)
        
        return profile_vector
    
    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embedding vectors.
        
        Cosine similarity measures the cosine of the angle between two vectors.
        - 1.0: Vectors point in the same direction (very similar)
        - 0.0: Vectors are orthogonal (no similarity)
        - -1.0: Vectors point in opposite directions (very dissimilar)
        
        Args:
            embedding1: First normalized embedding vector
            embedding2: Second normalized embedding vector
            
        Returns:
            Similarity score between 0 and 1 (we clip negative values to 0)
        """
        similarity = cosine_similarity([embedding1], [embedding2])[0][0]
        
        # Clip to 0-1 range (negative similarities are very rare with normalized embeddings)
        return max(0.0, min(1.0, similarity))
    
    def get_similarity_verdict(self, similarity_score: float) -> Tuple[str, str]:
        """
        Convert similarity score to human-readable verdict and emoji.
        
        Args:
            similarity_score: Cosine similarity score (0-1)
            
        Returns:
            Tuple of (verdict_text, emoji)
        """
        if similarity_score >= 0.7:
            return "Strong match", "✅"
        elif similarity_score >= 0.4:
            return "Partial match", "🤔"
        else:
            return "Not a match", "❌"
    
    def find_similar_books(self, 
                          target_book: Dict[str, Any], 
                          candidate_books: List[Dict[str, Any]], 
                          top_k: int = 3) -> List[Tuple[Dict[str, Any], float]]:
        """
        Find the most similar books to the target book from a list of candidates.
        
        Args:
            target_book: The book to compare against
            candidate_books: List of books to search through
            top_k: Number of similar books to return
            
        Returns:
            List of tuples (book, similarity_score) sorted by similarity
        """
        if 'embedding' not in target_book:
            return []
        
        similarities = []
        target_embedding = target_book['embedding']
        
        for book in candidate_books:
            if 'embedding' in book:
                similarity = self.calculate_similarity(target_embedding, book['embedding'])
                similarities.append((book, similarity))
        
        # Sort by similarity score (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]
    
    def prepare_favorites_with_embeddings(self, favorites: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Add embedding vectors to all favorite books.
        
        Args:
            favorites: Dictionary of genres to book lists
            
        Returns:
            Same structure but with 'embedding' added to each book
        """
        prepared_favorites = {}
        
        for genre, books in favorites.items():
            prepared_books = []
            for book in books:
                book_copy = book.copy()
                if 'embedding' not in book_copy:
                    book_copy['embedding'] = self.get_book_embedding(book_copy)
                prepared_books.append(book_copy)
            prepared_favorites[genre] = prepared_books
        

        return prepared_favorites
