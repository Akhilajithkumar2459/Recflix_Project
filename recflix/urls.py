from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('trailer/', views.trailer_view, name='trailer'),
    path('history/', views.view_history, name='history'),
    path('clear_history/', views.clear_history, name='clear_history'),
    path('playlist/', views.playlist_view, name='playlist'),
    path('add_to_playlist/', views.add_to_playlist, name='add_to_playlist'),
    path('remove_from_playlist/', views.remove_from_playlist, name='remove_from_playlist'),

    # Category-specific URLs
    path('recommend/movies/', views.recommend, {'category': 'movies'}, name='recommend_movies'),
    path('recommend/anime/', views.recommend, {'category': 'anime'}, name='recommend_anime'),
    path('recommend/webseries/', views.recommend, {'category': 'webseries'}, name='recommend_webseries'),
    
    path('random/movies/', views.get_random, {'category': 'movies'}, name='random_movies'),
    path('random/anime/', views.get_random, {'category': 'anime'}, name='random_anime'),
    path('random/webseries/', views.get_random, {'category': 'webseries'}, name='random_webseries'),
    
    path('titles/movies/', views.get_titles, {'category': 'movies'}, name='titles_movies'),
    path('titles/anime/', views.get_titles, {'category': 'anime'}, name='titles_anime'),
    path('titles/webseries/', views.get_titles, {'category': 'webseries'}, name='titles_webseries'),

    # Recommendations endpoint (must be before generic patterns)
    path('random/recommendations/', views.get_random_recommendations, name='get_random_recommendations'),

    # Generic category URLs (should be last)
    path('recommend/<str:category>/', views.recommend, name='recommend'),
    path('titles/<str:category>/', views.get_titles, name='get_titles'),
    path('random/<str:category>/', views.get_random, name='get_random'),
    path('<str:category>/', views.category_page, name='category'),

    # New URLs
    path('games/', views.games, name='games'),

    # API URLs
    path('api/playlist/', views.playlist_view, name='playlist'),
    path('api/playlist/add/', views.add_to_playlist, name='add_to_playlist'),
    path('api/playlist/remove/', views.remove_from_playlist, name='remove_from_playlist'),
    path('api/popular/<str:category>/', views.get_popular_items, name='popular_items'),
]
