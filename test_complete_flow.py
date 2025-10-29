from storage import add_favorite_book, load_favorites
from book_api import BookAPI

print("=== Complete Flow Test ===")

# Test with a known ISBN
api = BookAPI()
isbn = "9780439708180"  # Harry Potter
print(f"Fetching book with ISBN: {isbn}")

book_data = api.get_book_by_isbn(isbn)

if book_data:
    print(f"✓ Successfully fetched: {book_data['title']}")
    print(f"Authors: {book_data['authors']}")
    print(f"Categories: {book_data['categories']}")
    
    # Detect genre
    genre = api.detect_genre(book_data['categories'])
    print(f"Detected genre: {genre}")
    
    # Add to favorites
    success = add_favorite_book(genre, book_data)
    print(f"Add to favorites result: {success}")
    
    # Verify it was saved
    favorites = load_favorites()
    print(f"Saved favorites: {favorites}")
    
    if genre in favorites and any(book['isbn'] == isbn for book in favorites[genre]):
        print("✓ Book successfully saved to favorites!")
    else:
        print("✗ Book was not saved to favorites")
        
else:
    print("✗ Could not fetch book data")