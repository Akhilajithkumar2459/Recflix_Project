import pickle
import os
from django.conf import settings

BASE = settings.BASE_DIR / "recflix" / "data"

def load_data():
    return {
        'movies': {
            'data': pickle.load(open(BASE / "movies.pkl", "rb")),
            'similarity': pickle.load(open(BASE / "movie_similarity.pkl", "rb")),
            'col': 'title'
        },
        'anime': {
            'data': pickle.load(open(BASE / "anime.pkl", "rb")),
            'similarity': pickle.load(open(BASE / "anime_similarity.pkl", "rb")),
            'col': 'Title'
        },
        'webseries': {
            'data': pickle.load(open(BASE / "webseries.pkl", "rb")),
            'similarity': pickle.load(open(BASE / "webseries_similarity.pkl", "rb")),
            'col': 'Title'
        },
        'books': {
            'data': pickle.load(open(BASE / "books.pkl", "rb")),
            'similarity': pickle.load(open(BASE / "book_similarity.pkl", "rb")),
            'col': 'Title'
        },
        'games': {
            'data': pickle.load(open(BASE / "games.pkl", "rb")),
            'similarity': pickle.load(open(BASE / "game_similarity.pkl", "rb")),
            'col': 'Title'
        }
    }
