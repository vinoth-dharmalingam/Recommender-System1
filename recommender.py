"""Content-based movie recommendations from a local movie catalog."""

from __future__ import annotations

import re

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


REQUIRED_COLUMNS = {"title", "genres", "director", "cast", "overview"}


def _features(row: pd.Series) -> str:
    genres = str(row["genres"]).replace("|", " ")
    director = str(row["director"])
    cast = str(row["cast"])
    overview = str(row["overview"])
    return " ".join(
        [genres] * 3
        + [director] * 2
        + [cast]
        + [overview]
    )


def recommend_movies(
    movies: pd.DataFrame,
    title: str,
    count: int = 6,
    genre: str | None = None,
) -> pd.DataFrame:
    """Return the closest titles, optionally restricted to one genre."""
    missing = REQUIRED_COLUMNS.difference(movies.columns)
    if missing:
        raise ValueError(f"Movie data is missing required columns: {', '.join(sorted(missing))}")
    if count < 1:
        raise ValueError("count must be at least 1")

    matches = movies.index[movies["title"].str.casefold() == title.casefold()].tolist()
    if not matches:
        raise ValueError(f"Unknown movie title: {title}")

    feature_text = movies.apply(_features, axis=1)
    matrix = TfidfVectorizer(stop_words="english").fit_transform(feature_text)
    scores = cosine_similarity(matrix[matches[0]], matrix).ravel()

    ranked = movies.copy()
    ranked["similarity"] = scores
    ranked = ranked.drop(index=matches[0])
    if genre:
        escaped_genre = re.escape(genre)
        ranked = ranked[ranked["genres"].str.contains(rf"(?:^|\|){escaped_genre}(?:\||$)", case=False, regex=True)]

    return ranked.sort_values(
        ["similarity", "title"], ascending=[False, True], kind="stable"
    ).head(count)