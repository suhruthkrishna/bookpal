"""
BookPal - Personalized Book Recommendation Assistant
Main Streamlit application that provides the user interface.
"""

import streamlit as st
import numpy as np
from storage import load_favorites, save_favorites, add_favorite_book
from book_api import BookAPI
from recommend import BookRecommender
import time

# Page configuration
st.set_page_config(
    page_title="BookPal - Your Personal Book Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_session_state():
    """Initialize session state variables."""
    if 'favorites' not in st.session_state:
        st.session_state.favorites = load_favorites()
    if 'book_api' not in st.session_state:
        st.session_state.book_api = BookAPI()
    if 'recommender' not in st.session_state:
        st.session_state.recommender = BookRecommender()
    if 'favorites_processed' not in st.session_state:
        st.session_state.favorites_processed = False

def process_favorites_with_embeddings():
    """Add embeddings to all favorite books."""
    if not st.session_state.favorites_processed and st.session_state.favorites:
        with st.spinner("Analyzing your reading preferences..."):
            st.session_state.favorites = st.session_state.recommender.prepare_favorites_with_embeddings(
                st.session_state.favorites
            )
            st.session_state.favorites_processed = True

def main():
    """Main application function."""
    initialize_session_state()
    
    # App header
    st.title("📚 BookPal")
    st.markdown("### Your Personal Book Recommendation Assistant")
    st.markdown("---")
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.radio(
        "Choose a mode:",
        ["🏠 Home", "➕ Add Favorites", "🔍 Check a Book", "📖 My Favorites", "🐛 Debug", "🔄 Reset Data"]
    )
    
    # Home page
    if app_mode == "🏠 Home":
        show_home_page()
    
    # Add favorites page
    elif app_mode == "➕ Add Favorites":
        show_add_favorites_page()
    
    # Check a book page
    elif app_mode == "🔍 Check a Book":
        show_check_book_page()
    
    # My favorites page
    elif app_mode == "📖 My Favorites":
        show_my_favorites_page()
    
    # Debug page
    elif app_mode == "🐛 Debug":
        show_debug_page()
    
    # Reset data page
    elif app_mode == "🔄 Reset Data":
        show_reset_page()

def show_home_page():
    """Display the home page with instructions and overview."""
    st.header("Welcome to BookPal!")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### How BookPal Works
        
        1. **Build Your Profile**: Start by adding 5-6 of your favorite books across different genres
        2. **Create Taste Profiles**: BookPal analyzes your preferences using AI embeddings
        3. **Check New Books**: Enter any book's ISBN to see if it matches your taste
        4. **Get Recommendations**: Discover why a book matches (or doesn't) and get better suggestions
        
        ### What Are Embeddings?
        
        BookPal uses **sentence transformers** to convert book descriptions into numerical vectors 
        that capture the semantic meaning of the content. Similar books have similar vectors, 
        allowing us to mathematically measure how well a new book fits your established preferences.
        """)
    
    with col2:
        st.image("https://via.placeholder.com/300x400/4B7BEC/FFFFFF?text=BookPal", 
                caption="Your Personal Reading Assistant")
        
        # Quick stats
        total_books = sum(len(books) for books in st.session_state.favorites.values())
        total_genres = len(st.session_state.favorites)
        
        st.metric("Total Favorite Books", total_books)
        st.metric("Genres in Profile", total_genres)
    
    st.markdown("---")
    st.subheader("Ready to Get Started?")
    st.markdown("""
    - **New to BookPal?** → Go to **Add Favorites** to build your reading profile
    - **Already have favorites?** → Go to **Check a Book** to test new books
    - **Want to see your profile?** → Go to **My Favorites** to review your preferences
    """)

def show_add_favorites_page():
    """Page for adding favorite books."""
    st.header("Add Your Favorite Books")
    
    st.markdown("""
    Build your reading profile by adding books you love. 
    Start with 5-6 books across different genres for the best recommendations!
    """)
    
    # Initialize session state for book data
    if 'current_book_data' not in st.session_state:
        st.session_state.current_book_data = None
    
    # Genre selection
    common_genres = [
        "Fantasy", "Science Fiction", "Mystery", "Romance", "Horror",
        "Biography", "History", "Science", "Self-Help", "Thriller",
        "Young Adult", "Literary Fiction", "Historical Fiction"
    ]
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        selected_genre = st.selectbox("Select Genre", common_genres)
    
    with col2:
        isbn_input = st.text_input("Enter Book ISBN", 
                                  placeholder="e.g., 9780545010221 or 0-7475-3269-9")
    
    # Fetch book data
    if st.button("Fetch Book Details") and isbn_input:
        with st.spinner("Searching for book..."):
            book_data = st.session_state.book_api.get_book_by_isbn(isbn_input)
            
            if book_data:
                st.session_state.current_book_data = book_data
                st.success(f"Found: **{book_data['title']}** by {', '.join(book_data['authors'])}")
            else:
                st.error("Book not found. Please check the ISBN and try again.")
                st.session_state.current_book_data = None
    
    # Display book information if we have it
    if st.session_state.current_book_data:
        book_data = st.session_state.current_book_data
        
        # Display book information
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Book Details")
            st.write(f"**Title:** {book_data['title']}")
            st.write(f"**Author(s):** {', '.join(book_data['authors'])}")
            
            # Detect and display genre
            detected_genre = st.session_state.book_api.detect_genre(book_data['categories'])
            st.write(f"**Detected Genre:** {detected_genre}")
            
            st.write(f"**Publisher:** {book_data.get('publisher', 'Unknown')}")
            st.write(f"**Pages:** {book_data.get('page_count', 'Unknown')}")
            st.write(f"**ISBN:** {book_data.get('isbn', 'N/A')}")
        
        with col2:
            st.subheader("Description")
            description = book_data.get('description', 'No description available.')
            if len(description) > 500:
                st.write(description[:500] + "...")
            else:
                st.write(description)
        
        # Add to favorites - SEPARATE button that doesn't trigger rerun of the fetch
        st.markdown("---")
        st.subheader("Add to Your Favorites")
        
        if st.button("✅ Add This Book to Favorites", type="primary"):
            detected_genre = st.session_state.book_api.detect_genre(book_data['categories'])
            
            success = add_favorite_book(detected_genre, book_data)
            if success:
                st.success(f"**Success!** Added **{book_data['title']}** to your {detected_genre} favorites!")
                
                # Update session state
                st.session_state.favorites = load_favorites()
                st.session_state.favorites_processed = False
                
                # Show what's in favorites now
                st.info(f"📚 You now have {len(st.session_state.favorites.get(detected_genre, []))} books in your {detected_genre} collection")
            else:
                st.error("This book is already in your favorites!")

def show_check_book_page():
    """Page for checking if a new book matches user preferences."""
    st.header("Check if a Book Matches Your Taste")
    
    process_favorites_with_embeddings()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        isbn_to_check = st.text_input("Enter Book ISBN to Check", 
                                     placeholder="Scan or enter ISBN")
    
    if st.button("Analyze Book") and isbn_to_check:
        with st.spinner("Analyzing book and comparing with your preferences..."):
            # Fetch book data
            book_data = st.session_state.book_api.get_book_by_isbn(isbn_to_check)
            
            if not book_data:
                st.error("Book not found. Please check the ISBN and try again.")
                return
            
            # Generate embedding for the new book USING FULL DESCRIPTION
            st.info("🔍 Generating AI embedding from book description...")
            book_data['embedding'] = st.session_state.recommender.get_book_embedding(book_data)
            
            # Display what text was used for embedding
             with st.expander("📖 See what the AI analyzed:"):
                description = book_data.get('description', 'No description available.')
                st.write(f"**Description used:** {description}")
                
                categories = book_data.get('categories', [])
                # Safely handle categories (they might be dictionaries)
                category_strings = []
                for cat in categories:
                    if isinstance(cat, dict):
                        category_strings.append(str(cat.get('name', 'Unknown')))
                    else:
                        category_strings.append(str(cat))
                
                st.write(f"**Categories used:** {', '.join(category_strings) if category_strings else 'None'}")
            
            # Detect genre
            detected_genre = st.session_state.book_api.detect_genre(book_data['categories'])
            
            # Display book information
            st.subheader(f"**{book_data['title']}** by {', '.join(book_data['authors'])}")
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.image("https://via.placeholder.com/200x300/4B7BEC/FFFFFF?text=Book+Cover", 
                        caption=book_data['title'])
                st.write(f"**Genre:** {detected_genre}")
                st.write(f"**Source:** {book_data.get('source', 'Unknown')}")
                st.write(f"**ISBN:** {book_data.get('isbn', 'N/A')}")
            
            with col2:
                st.write("**Description:**")
                description = book_data.get('description', 'No description available.')
                st.write(description)
            
            st.markdown("---")
            
            # Check similarity with user's genre profile
            if detected_genre in st.session_state.favorites and st.session_state.favorites[detected_genre]:
                genre_books = st.session_state.favorites[detected_genre]
                genre_profile = st.session_state.recommender.create_genre_profile(genre_books)
                
                if genre_profile is not None:
                    similarity = st.session_state.recommender.calculate_similarity(
                        book_data['embedding'], genre_profile
                    )
                    verdict, emoji = st.session_state.recommender.get_similarity_verdict(similarity)
                    
                    # Display results
                    st.subheader("🎯 Match Analysis")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Similarity Score", f"{similarity:.2%}")
                    
                    with col2:
                        st.metric("Verdict", verdict)
                    
                    with col3:
                        st.metric("Genre", detected_genre)
                    
                    # Show verdict with emoji
                    st.markdown(f"### {emoji} {verdict}")
                    
                    # Explain what was compared
                    st.info(f"🤖 **AI Analysis**: Compared '{book_data['title']}' against your {detected_genre} taste profile using book descriptions and themes")
                    
                    # Provide recommendations based on match quality
                    if similarity < 0.7:  # Not a strong match
                        st.info("This book doesn't strongly match your usual preferences in this genre.")
                        
                        # Find similar books from user's favorites
                        similar_books = st.session_state.recommender.find_similar_books(
                            book_data, genre_books, top_k=3
                        )
                        
                        if similar_books:
                            st.subheader("📚 You Might Prefer These Instead:")
                            
                            for i, (similar_book, book_similarity) in enumerate(similar_books, 1):
                                with st.expander(f"{i}. {similar_book['title']} (Similarity: {book_similarity:.2%})"):
                                    st.write(f"**Author:** {', '.join(similar_book['authors'])}")
                                    st.write(f"**Description:** {similar_book.get('description', 'No description available.')}")
                                    st.write(f"**Why recommended:** This book from your favorites has similar writing style and themes")
                        else:
                            st.write("Try adding more books to this genre for better recommendations!")
                    else:
                        st.success("This book strongly aligns with your taste in this genre! You'll likely enjoy it.")
                
                else:
                    st.warning("Could not create genre profile. Please add more books to this genre.")
            else:
                st.warning(f"You haven't added any favorites in the {detected_genre} genre yet. "
                          f"Add some {detected_genre} books to your favorites to get personalized recommendations.")

def show_my_favorites_page():
    """Page for viewing and managing favorite books."""
    st.header("My Favorite Books")
    
    # Refresh button
    if st.button("🔄 Refresh Favorites"):
        st.session_state.favorites = load_favorites()
        st.session_state.favorites_processed = False
        st.rerun()
    
    # Force reload favorites to ensure we have the latest data
    st.session_state.favorites = load_favorites()
    process_favorites_with_embeddings()
    
    if not st.session_state.favorites:
        st.info("You haven't added any favorite books yet. Go to 'Add Favorites' to get started!")
        return
    
    total_books = sum(len(books) for books in st.session_state.favorites.values())
    total_genres = len(st.session_state.favorites)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Books in Profile", total_books)
    with col2:
        st.metric("Genres", total_genres)
    
    # Display favorites by genre
    for genre, books in st.session_state.favorites.items():
        with st.expander(f"📚 {genre} ({len(books)} books)", expanded=True):
            for i, book in enumerate(books, 1):
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(f"**{i}. {book['title']}**")
                    st.write(f"by {', '.join(book['authors'])}")
                    if book.get('publisher'):
                        st.write(f"Published by {book['publisher']}")
                    st.write(f"ISBN: {book.get('isbn', 'N/A')}")
                
                with col2:
                    if st.button(f"Remove", key=f"remove_{genre}_{i}"):
                        # Remove book from favorites
                        updated_books = [b for b in books if b != book]
                        st.session_state.favorites[genre] = updated_books
                        if not updated_books:
                            del st.session_state.favorites[genre]
                        
                        save_favorites(st.session_state.favorites)
                        st.session_state.favorites_processed = False
                        st.rerun()

def show_debug_page():
    """Debug page to see what's happening."""
    st.header("🐛 Debug Information")
    
    st.subheader("Session State")
    st.write(st.session_state)
    
    st.subheader("Favorites from File")
    favorites_from_file = load_favorites()
    st.write(favorites_from_file)
    
    st.subheader("Files in Directory")
    import os
    st.write(os.listdir('.'))
    
    st.subheader("Test Storage System")
    if st.button("Test Storage"):
        test_book = {
            'isbn': 'DEBUG123',
            'title': 'Debug Test Book',
            'authors': ['Debug Author'],
            'description': 'Debug description',
            'categories': ['Debug'],
            'source': 'Debug'
        }
        success = add_favorite_book("Debug", test_book)
        st.write(f"Storage test result: {success}")
        
        # Reload to verify
        favorites = load_favorites()
        st.write(f"Favorites after test: {favorites}")

def show_reset_page():
    """Page for resetting user data."""
    st.header("Reset Your Data")
    
    st.warning("⚠️ This action cannot be undone!")
    
    st.markdown("""
    Resetting your data will:
    - Remove all your favorite books
    - Delete your reading profile
    - Clear all your preferences
    
    You'll need to start over from scratch.
    """)
    
    if st.button("I understand - Reset All Data"):
        st.session_state.favorites = {}
        st.session_state.favorites_processed = False
        from storage import clear_favorites
        clear_favorites()
        st.success("All data has been reset!")
        time.sleep(2)
        st.rerun()

if __name__ == "__main__":
    main()

