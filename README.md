# Movie Recommender

A small Streamlit app that recommends movies using content similarity across genres, directors, cast, and plot summaries. The catalog is local, so no API key or dataset download is needed. Poster images load from TMDB's image CDN when an internet connection is available.

## Run locally

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL printed by Streamlit, usually `http://localhost:8501`.

## Run tests

```powershell
python -m unittest discover -s tests -v
```

## How recommendations work

Each movie is represented by TF-IDF features built from its metadata. Genres and directors receive extra weight, then cosine similarity ranks the remaining titles. This is a content-based baseline; it does not use user ratings or collaborative filtering.