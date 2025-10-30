# 📚 BookPal — Personalized Book Recommendation Assistant

BookPal is an AI-powered reading companion that builds personalized taste profiles and recommends books that match your preferences using **semantic embeddings** and **cosine similarity**.

Built with **Streamlit**, **Sentence Transformers**, and **Google Books API**, BookPal provides an interactive way to explore and evaluate new books based on your existing favorites.

---

##  Features

* **AI-Powered Recommendations** – Uses `all-MiniLM-L6-v2` embeddings to capture semantic meaning of book descriptions.
* **Smart Genre Profiling** – Builds a per-genre "taste profile" by averaging your favorite books’ embeddings.
* **Cosine Similarity Scoring** – Quantifies how close a new book aligns with your preferences.
* **Interactive Streamlit UI** – Add favorites, analyze new books, visualize similarity, and manage your library.
* **Persistent Storage** – Saves favorites and preferences locally using JSON.
* **Debug & Reset Tools** – Inspect internal state or reset your data safely.

---

##  How It Works

### 1. Build Your Profile

You start by adding 5–6 of your favorite books across genres. BookPal fetches metadata (title, author, description, publisher, etc.) using **Google Books** and **OpenLibrary APIs**.

### 2. Generate Embeddings

Each book’s textual metadata is converted into a high‑dimensional vector representation using the `sentence-transformers` model **all-MiniLM-L6-v2**.

### 3. Create Genre Profiles

BookPal averages the embeddings of your favorite books in each genre, forming a “taste profile” vector representing your preferences.

### 4. Check New Books

When you check a new book (via ISBN), BookPal compares its embedding to your genre profiles using **cosine similarity**, generating:

*  Strong Match (≥ 0.7)
*  Partial Match (0.4 – 0.7)
*  Not a Match (< 0.4)

### 5. Get Recommendations

If a book doesn’t strongly match, BookPal suggests similar titles from your favorites that are closest in embedding space.

---

##  Architecture Overview

```
Google Books / OpenLibrary APIs
        │
        ▼
BookAPI → BookRecommender → Streamlit UI
        │             │
        ▼             ▼
   Storage Layer ← favorites.json
```

* **BookAPI** → Fetches and cleans metadata from public APIs.
* **BookRecommender** → Handles embeddings, similarity scoring, and clustering logic.
* **Streamlit App** → Provides an interactive user experience.
* **Storage Layer** → Persists user data locally.

---

##  Installation

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/bookpal.git
cd bookpal
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate   # (on macOS/Linux)
venv\Scripts\activate      # (on Windows)
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Streamlit app

```bash
streamlit run app.py
```

---

##  Testing

Run the end-to-end test to verify that BookPal can fetch book data and save favorites:

```bash
python test_complete_flow.py
```

Expected output:

```
=== Complete Flow Test ===
Fetching book with ISBN: 9780439708180
✓ Successfully fetched: Harry Potter and the Sorcerer’s Stone
Detected genre: Fantasy
✓ Book successfully saved to favorites!
```

---

##  File Structure

```
bookpal/
├── app.py                 # Main Streamlit application
├── book_api.py            # API integration for metadata retrieval
├── recommend.py           # Embedding and recommendation engine
├── storage.py             # Local persistence for favorites
├── test_complete_flow.py  # End-to-end functional test
├── requirements.txt       # Dependencies
└── favorites.json         # Local user data (auto-created)
```

---

##  Tech Stack

* **Frontend/UI**: Streamlit
* **ML Backend**: Sentence Transformers (MiniLM‑L6‑v2)
* **Data Processing**: NumPy, Scikit‑learn
* **Storage**: Local JSON persistence
* **APIs**: Google Books API, OpenLibrary API

---

##  Future Enhancements

* Integrate **Goodreads API** for richer book metadata.
* Add **user login** and **cloud persistence**.
* Support **multilingual embeddings** for international book catalogs.
* Introduce **fine-tuning** based on explicit user ratings.

---

## Author

**Suhruth Krishna Yalamanchili**
*Data Scientist | Software Engineer passionate about NLP, recommender systems, and intelligent interfaces.*

---

##  License

MIT License © 2025 Suhruth Krishna Yalamanchili
