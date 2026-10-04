import unittest

import pandas as pd

from recommender import recommend_movies


class RecommendMoviesTests(unittest.TestCase):
    def setUp(self):
        self.movies = pd.DataFrame(
            [
                {
                    "title": "Orbit One",
                    "genres": "Sci-Fi|Adventure",
                    "director": "A. Director",
                    "cast": "Actor A|Actor B",
                    "overview": "A crew explores a distant planet and encounters alien life.",
                },
                {
                    "title": "Orbit Two",
                    "genres": "Sci-Fi|Adventure",
                    "director": "A. Director",
                    "cast": "Actor C|Actor D",
                    "overview": "Explorers travel through space to find a habitable world.",
                },
                {
                    "title": "Kitchen Days",
                    "genres": "Comedy|Drama",
                    "director": "B. Director",
                    "cast": "Actor E|Actor F",
                    "overview": "A chef returns home to reopen a neighborhood restaurant.",
                },
            ]
        )

    def test_similar_movie_ranks_above_unrelated_movie(self):
        results = recommend_movies(self.movies, "Orbit One", count=2)
        self.assertEqual(results.iloc[0]["title"], "Orbit Two")

    def test_genre_filter_limits_results(self):
        results = recommend_movies(self.movies, "Orbit One", genre="Comedy")
        self.assertEqual(results["title"].tolist(), ["Kitchen Days"])

    def test_unknown_title_is_reported(self):
        with self.assertRaisesRegex(ValueError, "Unknown movie title"):
            recommend_movies(self.movies, "Not a Movie")


if __name__ == "__main__":
    unittest.main()