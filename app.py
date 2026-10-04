from __future__ import annotations

import html
from pathlib import Path

import pandas as pd
import streamlit as st

from recommender import recommend_movies


DATA_PATH = Path(__file__).parent / "movies.csv"


@st.cache_data
def load_movies() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH, keep_default_na=False)


def render_movie_card(movie: pd.Series, similarity: float | None = None) -> None:
    title = html.escape(str(movie["title"]))
    genres = " / ".join(html.escape(part) for part in movie["genres"].split("|"))
    poster = html.escape(str(movie["poster_url"]), quote=True)
    year = html.escape(str(movie["year"]))
    score = f'<span class="match">{similarity:.0%} match</span>' if similarity is not None else ""

    st.markdown(
        f"""
        <article class="movie-card">
          <div class="poster" style="background-image: linear-gradient(180deg, transparent 60%, rgba(9, 25, 22, .55)), url('{poster}')">
            <span class="year">{year}</span>
          </div>
          <div class="movie-copy">
            <div class="movie-title-line"><h3>{title}</h3>{score}</div>
            <p class="genres">{genres}</p>
          </div>
        </article>
        """,
        unsafe_allow_html=True,
    )


st.set_page_config(page_title="Reelwise | Movie Discovery", page_icon="🎬", layout="wide")
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
    :root { --ink:#14231f; --muted:#65736d; --paper:#f4f5ef; --line:#dce2d9; --forest:#173c32; --lime:#d4f36b; }
    .stApp { background:var(--paper); color:var(--ink); }
    [data-testid="stHeader"] { background:transparent; }
    .block-container { max-width:1320px; padding-top:2rem; padding-bottom:4rem; }
    html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
    h1, h2, h3 { font-family:'Space Grotesk',sans-serif !important; color:var(--ink); }
    h1 { font-size:42px !important; line-height:1.08 !important; margin:0 !important; }
    h2 { font-size:25px !important; }
    h3 { font-size:16px !important; }
    .brand-row { display:flex; align-items:center; gap:12px; margin-bottom:6px; }
    .brand-mark { width:38px; height:38px; display:grid; place-items:center; border-radius:8px; background:var(--lime); color:var(--forest); font-size:20px; }
    .brand-note { color:var(--muted); font-size:13px; padding-top:8px; }
    .intro { border-bottom:1px solid var(--line); padding:12px 0 26px; margin-bottom:24px; }
    .intro p { color:var(--muted); margin:10px 0 0; font-size:15px; }
    .section-head { display:flex; justify-content:space-between; align-items:baseline; border-bottom:1px solid var(--line); margin:24px 0 18px; padding-bottom:10px; }
    .section-head h2 { margin:0; }
    .section-kicker { color:var(--muted); font-size:12px; text-transform:uppercase; }
    .movie-card { overflow:hidden; border:1px solid var(--line); border-radius:7px; background:#fffefa; margin-bottom:18px; transition:transform .18s ease, box-shadow .18s ease; }
    .movie-card:hover { transform:translateY(-3px); box-shadow:0 10px 24px rgba(20,35,31,.12); }
    .poster { aspect-ratio:2 / 2.8; position:relative; background-color:#29463c; background-size:cover; background-position:center; }
    .year { position:absolute; top:10px; right:10px; padding:4px 8px; border-radius:4px; color:var(--ink); background:var(--lime); font-size:11px; font-weight:700; }
    .movie-copy { padding:12px 13px 14px; min-height:78px; }
    .movie-title-line { display:flex; justify-content:space-between; align-items:flex-start; gap:7px; }
    .movie-title-line h3 { margin:0; }
    .genres { color:var(--muted); font-size:11px; line-height:1.5; margin:7px 0 0; }
    .match { flex:0 0 auto; padding:3px 6px; border-radius:4px; background:#e8f4c7; color:#35521e; font-size:10px; font-weight:700; }
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div { background:#fffefa; border-color:var(--line); }
    @media (max-width:700px) { .block-container { padding:1.25rem 1rem 3rem; } h1 { font-size:34px !important; } .brand-note { display:none; } }
    </style>
    """,
    unsafe_allow_html=True,
)

movies = load_movies()
genre_options = sorted({genre for values in movies["genres"] for genre in values.split("|")})

st.markdown(
    '<div class="brand-row"><div class="brand-mark">R</div><h1>Reelwise</h1><div class="brand-note">A better next watch.</div></div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="intro"><p>Movie recommendations shaped by the stories, genres, and filmmakers you love.</p></div>',
    unsafe_allow_html=True,
)

recommend_tab, browse_tab = st.tabs(["For you", "Browse catalog"])

with recommend_tab:
    control_columns = st.columns([2.2, 1.3, 1])
    with control_columns[0]:
        selected_title = st.selectbox("A movie you like", movies["title"].tolist())
    with control_columns[1]:
        selected_genre = st.selectbox("Narrow by genre", ["All genres", *genre_options])
    with control_columns[2]:
        result_count = st.slider("Recommendations", min_value=3, max_value=10, value=6)

    chosen_movie = movies[movies["title"] == selected_title].iloc[0]
    genres_label = " / ".join(html.escape(part) for part in chosen_movie["genres"].split("|"))
    st.markdown(
        f'<div class="section-head"><h2>Because you picked {html.escape(selected_title)}</h2><span class="section-kicker">{html.escape(str(chosen_movie["year"]))} &nbsp;·&nbsp; {genres_label}</span></div>',
        unsafe_allow_html=True,
    )

    recommendations = recommend_movies(
        movies,
        selected_title,
        count=result_count,
        genre=None if selected_genre == "All genres" else selected_genre,
    )
    if recommendations.empty:
        st.info("No other titles in that genre yet. Try another genre or choose All genres.")
    else:
        recommendation_columns = st.columns(4)
        for index, (_, movie) in enumerate(recommendations.iterrows()):
            with recommendation_columns[index % len(recommendation_columns)]:
                render_movie_card(movie, float(movie["similarity"]))

with browse_tab:
    filter_columns = st.columns([2, 1])
    with filter_columns[0]:
        query = st.text_input("Search movies", placeholder="Title, director, actor, or story")
    with filter_columns[1]:
        catalog_genre = st.selectbox("Catalog genre", ["All genres", *genre_options], key="catalog_genre")

    catalog = movies.copy()
    if catalog_genre != "All genres":
        catalog = catalog[catalog["genres"].str.contains(rf"(?:^|\|){catalog_genre}(?:\||$)", case=False, regex=True)]
    if query.strip():
        searchable = catalog[["title", "director", "cast", "overview", "genres"]].agg(" ".join, axis=1)
        catalog = catalog[searchable.str.contains(query.strip(), case=False, regex=False)]

    st.markdown(
        f'<div class="section-head"><h2>All movies</h2><span class="section-kicker">{len(catalog)} titles</span></div>',
        unsafe_allow_html=True,
    )
    if catalog.empty:
        st.info("No titles found. Try a broader search.")
    else:
        catalog_columns = st.columns(4)
        for index, (_, movie) in enumerate(catalog.iterrows()):
            with catalog_columns[index % len(catalog_columns)]:
                render_movie_card(movie)

st.markdown(
    '<div style="border-top:1px solid #dce2d9;padding-top:16px;color:#65736d;font-size:12px">Recommendations use content similarity across genres, directors, cast, and story.</div>',
    unsafe_allow_html=True,
)