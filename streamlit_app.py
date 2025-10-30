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
                st.write(f"**Categories used:** {', '.join(categories) if categories else 'None'}")
            
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
