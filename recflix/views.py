import os
import pickle
import re
import pandas as pd
import csv
import json
import requests
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import History, PlaylistItem, PopularItem
from django.conf import settings
from django.views.decorators.http import require_POST
import random

# TMDB API Configuration
TMDB_API_KEY = 'c961c7281a76d75cb6e021a59cc2ab26'  # Direct API key
TMDB_BASE_URL = 'https://api.themoviedb.org/3'
TMDB_IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500'

# RAWG API Configuration
RAWG_API_KEY = 'be4853e58ced4a049c5309f13454947e'
RAWG_BASE_URL = 'https://api.rawg.io/api'

# Load pickles
BASE_DATA = os.path.join(settings.BASE_DIR, 'recflix', 'data')

datasets = {
    'movies': {
        'data': pickle.load(open(os.path.join(BASE_DATA, 'movies.pkl'), 'rb')),
        'similarity': pickle.load(open(os.path.join(BASE_DATA, 'movie_similarity.pkl'), 'rb')),
        'col': 'title'
    },
    'anime': {
        'data': pickle.load(open(os.path.join(BASE_DATA, 'anime.pkl'), 'rb')),
        'similarity': pickle.load(open(os.path.join(BASE_DATA, 'anime_similarity.pkl'), 'rb')),
        'col': 'Title'
    },
    'books': {
        'data': pickle.load(open(os.path.join(BASE_DATA, 'books.pkl'), 'rb')),
        'similarity': pickle.load(open(os.path.join(BASE_DATA, 'books_similarity.pkl'), 'rb')),
        'col': 'Title'
    },
    'webseries': {
        'data': pickle.load(open(os.path.join(BASE_DATA, 'webseries.pkl'), 'rb')),
        'similarity': pickle.load(open(os.path.join(BASE_DATA, 'webseries_similarity.pkl'), 'rb')),
        'col': 'Title'
    },
    'games': {
        'data': pickle.load(open(os.path.join(BASE_DATA, 'games.pkl'), 'rb')),
        'similarity': pickle.load(open(os.path.join(BASE_DATA, 'games_similarity.pkl'), 'rb')),
        'col': 'Title'
    },
}

# Print dataset structure
print("\nDataset Structure:")
for category, data in datasets.items():
    print(f"\n{category.upper()}:")
    print(f"Columns: {data['data'].columns.tolist()}")
    print(f"Sample data:")
    print(data['data'].head(1))

def clean_filename(title):
    return re.sub(r'[^a-zA-Z0-9]', '', title).lower()

def find_best_poster(title, category):
    posters_path = os.path.join(settings.BASE_DIR, 'recflix', 'static', 'posters', category)
    cleaned_title = clean_filename(title)
    for file in os.listdir(posters_path):
        name, ext = os.path.splitext(file)
        if clean_filename(name) == cleaned_title:
            return f'/static/posters/{category}/{file}'
    return '/static/posters/default.jpg'

def get_directory_posters(category):
    posters_path = os.path.join(settings.BASE_DIR, 'recflix', 'static', 'posters', category)
    posters = []
    try:
        for file in os.listdir(posters_path):
            if file.endswith(('.jpg', '.jpeg', '.png')):
                posters.append({
                    'title': os.path.splitext(file)[0],
                    'poster': f'/static/posters/{category}/{file}'
                })
    except Exception as e:
        print(f"Error reading posters from {category}: {str(e)}")
    return posters

def home(request):
    recent_items = []
    if request.user.is_authenticated:
        # Get all history items and randomly select 5
        history = History.objects.filter(user=request.user).order_by('?')[:5]
        for entry in history:
            poster = find_best_poster(entry.title, entry.category)
            recent_items.append({'title': entry.title, 'category': entry.category, 'poster': poster})
    
    # Get directory posters for non-authenticated users
    directory_posters = {}
    if not request.user.is_authenticated:
        categories = ['movies', 'anime', 'webseries', 'books', 'games']
        for category in categories:
            posters = get_directory_posters(category)
            if posters:
                # Randomly select 5 posters for each category
                selected_posters = random.sample(posters, min(5, len(posters)))
                directory_posters[category] = selected_posters

    return render(request, 'index.html', {
        'recent_items': recent_items,
        'directory_posters': directory_posters
    })

def register_view(request):
    if request.method == 'POST':
        User.objects.create_user(
            username=request.POST['email'],
            email=request.POST['email'],
            password=request.POST['password'],
            first_name=request.POST['first_name'],
            last_name=request.POST['last_name']
        )
        return redirect('/login')
    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        user = authenticate(username=request.POST['email'], password=request.POST['password'])
        if user:
            login(request, user)
            return redirect('/')
        return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('/')

@login_required
def category_page(request, category):
    if category == 'history':
        return view_history(request)
    if category not in datasets:
        return render(request, '404.html')
    return render(request, f'{category}.html', {'category': category})

def get_tmdb_movie_details(title):
    try:
        # First, search for the movie
        search_url = f"{TMDB_BASE_URL}/search/movie"
        params = {
            'api_key': TMDB_API_KEY,
            'query': title,
            'language': 'en-US'
        }
        response = requests.get(search_url, params=params)
        data = response.json()
        
        if data['results']:
            # Get the first result
            movie_id = data['results'][0]['id']
            
            # Get detailed movie information
            details_url = f"{TMDB_BASE_URL}/movie/{movie_id}"
            params = {
                'api_key': TMDB_API_KEY,
                'language': 'en-US',
                'append_to_response': 'credits'
            }
            response = requests.get(details_url, params=params)
            movie_data = response.json()
            
            return {
                'rating': movie_data.get('vote_average'),
                'year': movie_data.get('release_date', '')[:4],
                'director': next((crew['name'] for crew in movie_data.get('credits', {}).get('crew', []) 
                                if crew['job'] == 'Director'), None),
                'genre': ', '.join(genre['name'] for genre in movie_data.get('genres', [])),
                'description': movie_data.get('overview'),
                'poster_path': f"{TMDB_IMAGE_BASE_URL}{movie_data.get('poster_path')}" if movie_data.get('poster_path') else None
            }
    except Exception as e:
        print(f"Error fetching TMDB data: {e}")
    return None

def get_tmdb_tv_details(title):
    try:
        # First, search for the TV series
        search_url = f"{TMDB_BASE_URL}/search/tv"
        params = {
            'api_key': TMDB_API_KEY,
            'query': title,
            'language': 'en-US'
        }
        response = requests.get(search_url, params=params)
        data = response.json()
        
        if data['results']:
            # Get the first result
            tv_id = data['results'][0]['id']
            
            # Get detailed TV series information
            details_url = f"{TMDB_BASE_URL}/tv/{tv_id}"
            params = {
                'api_key': TMDB_API_KEY,
                'language': 'en-US',
                'append_to_response': 'credits'
            }
            response = requests.get(details_url, params=params)
            tv_data = response.json()
            
            return {
                'rating': tv_data.get('vote_average'),
                'year': tv_data.get('first_air_date', '')[:4],
                'creator': next((crew['name'] for crew in tv_data.get('created_by', [])), None),
                'genre': ', '.join(genre['name'] for genre in tv_data.get('genres', [])),
                'description': tv_data.get('overview'),
                'poster_path': f"{TMDB_IMAGE_BASE_URL}{tv_data.get('poster_path')}" if tv_data.get('poster_path') else None,
                'seasons': tv_data.get('number_of_seasons'),
                'episodes': tv_data.get('number_of_episodes')
            }
    except Exception as e:
        print(f"Error fetching TMDB data: {e}")
    return None

def get_tmdb_anime_details(title):
    try:
        # First, search for the anime
        search_url = f"{TMDB_BASE_URL}/search/tv"
        params = {
            'api_key': TMDB_API_KEY,
            'query': title,
            'language': 'en-US',
            'with_keywords': '210024|287501'  # Keywords for anime
        }
        response = requests.get(search_url, params=params)
        data = response.json()
        
        if data['results']:
            # Get the first result
            anime_id = data['results'][0]['id']
            
            # Get detailed anime information
            details_url = f"{TMDB_BASE_URL}/tv/{anime_id}"
            params = {
                'api_key': TMDB_API_KEY,
                'language': 'en-US',
                'append_to_response': 'credits'
            }
            response = requests.get(details_url, params=params)
            anime_data = response.json()
            
            return {
                'rating': anime_data.get('vote_average'),
                'year': anime_data.get('first_air_date', '')[:4],
                'genre': ', '.join(genre['name'] for genre in anime_data.get('genres', [])),
                'description': anime_data.get('overview'),
                'poster_path': f"{TMDB_IMAGE_BASE_URL}{anime_data.get('poster_path')}" if anime_data.get('poster_path') else None,
                'seasons': anime_data.get('number_of_seasons'),
                'episodes': anime_data.get('number_of_episodes')
            }
    except Exception as e:
        print(f"Error fetching TMDB data for anime: {e}")
    return None

def get_rawg_game_details(title):
    try:
        # First, search for the game
        search_url = f"{RAWG_BASE_URL}/games"
        params = {
            'key': RAWG_API_KEY,
            'search': title,
            'page_size': 1
        }
        response = requests.get(search_url, params=params)
        data = response.json()
        
        if data['results']:
            # Get the first result
            game = data['results'][0]
            
            # Get detailed game information
            details_url = f"{RAWG_BASE_URL}/games/{game['id']}"
            params = {
                'key': RAWG_API_KEY
            }
            response = requests.get(details_url, params=params)
            game_data = response.json()
            
            return {
                'rating': game_data.get('rating'),
                'year': game_data.get('released', '')[:4],
                'developer': next((dev['name'] for dev in game_data.get('developers', [])), None),
                'genre': ', '.join(genre['name'] for genre in game_data.get('genres', [])),
                'description': game_data.get('description'),
                'poster_path': game_data.get('background_image'),
                'platforms': ', '.join(platform['platform']['name'] for platform in game_data.get('platforms', [])),
                'metacritic': game_data.get('metacritic')
            }
    except Exception as e:
        print(f"Error fetching RAWG data: {e}")
    return None

@login_required
def recommend(request, category):
    if request.method == 'POST':
        title = request.POST.get('name')
        if category not in datasets:
            return JsonResponse({'error': 'Invalid category'}, status=400)

        df = datasets[category]['data']
        sim = datasets[category]['similarity']
        col = datasets[category]['col']

        matches = df[df[col].str.lower() == title.lower()]
        if matches.empty:
            return JsonResponse({'error': 'Title not found'}, status=404)

        idx = matches.index[0]
        distances = sorted(list(enumerate(sim[idx])), reverse=True, key=lambda x: x[1])

        recommendations = []
        for i in distances[1:6]:
            rec_title = df.iloc[i[0]][col]
            rec_poster = find_best_poster(rec_title, category)
            History.objects.create(user=request.user, title=rec_title, category=category)
            recommendations.append({'title': rec_title, 'poster': rec_poster})

        # Get API data for the selected item
        if category == 'movies':
            api_data = get_tmdb_movie_details(title)
        elif category == 'webseries':
            api_data = get_tmdb_tv_details(title)
        elif category == 'anime':
            api_data = get_tmdb_anime_details(title)
        elif category == 'games':
            api_data = get_rawg_game_details(title)
        else:
            api_data = None

        selected = {
            'title': title,
            'poster': api_data['poster_path'] if api_data and api_data['poster_path'] else find_best_poster(title, category),
            'rating': api_data['rating'] if api_data else None,
            'genre': api_data['genre'] if api_data else None,
            'description': api_data['description'] if api_data else None,
            'year': api_data['year'] if api_data else None,
            'director': api_data['director'] if category == 'movies' and api_data else None,
            'creator': api_data['creator'] if category == 'webseries' and api_data else None,
            'seasons': api_data['seasons'] if (category == 'webseries' or category == 'anime') and api_data else None,
            'episodes': api_data['episodes'] if (category == 'webseries' or category == 'anime') and api_data else None,
            'developer': api_data['developer'] if category == 'games' and api_data else None,
            'platforms': api_data['platforms'] if category == 'games' and api_data else None,
            'metacritic': api_data['metacritic'] if category == 'games' and api_data else None
        }

        return JsonResponse({'selected': selected, 'recommendations': recommendations})

@login_required
def get_titles(request, category):
    if category not in datasets:
        return JsonResponse([])
    df = datasets[category]['data']
    return JsonResponse(list(df[datasets[category]['col']].unique()), safe=False)

@login_required
def get_random(request, category):
    if category not in datasets:
        return JsonResponse({'error': 'Invalid category'}, status=400)
    df = datasets[category]['data'].sample(20)
    col = datasets[category]['col']
    data = []
    for _, row in df.iterrows():
        data.append({
            'title': row[col],
            'poster': find_best_poster(row[col], category)
        })
    return JsonResponse(data, safe=False)

@login_required
def get_random_recommendations(request):
    """Get the next 5 recommendations from user's history"""
    # Get all history items ordered by most recent first
    history = History.objects.filter(user=request.user).order_by('-id')
    
    # Get the current offset from the request, default to 0
    offset = int(request.GET.get('offset', 0))
    
    # Get the next 5 items starting from the offset
    next_items = history[offset:offset + 5]
    
    recommendations = []
    for entry in next_items:
        recommendations.append({
            'title': entry.title,
            'category': entry.category,
            'poster': find_best_poster(entry.title, entry.category)
        })
    
    # If we've reached the end of the history, start over from the beginning
    if not recommendations and history.exists():
        next_items = history[:5]
        for entry in next_items:
            recommendations.append({
                'title': entry.title,
                'category': entry.category,
                'poster': find_best_poster(entry.title, entry.category)
            })
    
    return JsonResponse({
        'recommendations': recommendations,
        'has_more': history.count() > offset + 5
    })

@login_required
def view_history(request):
    history = History.objects.filter(user=request.user).order_by('-id')
    items = [{'title': h.title, 'category': h.category, 'poster': find_best_poster(h.title, h.category)} for h in history]
    return render(request, 'history.html', {'history': items})

@login_required
def clear_history(request):
    History.objects.filter(user=request.user).delete()
    return redirect('/history')

def trailer_view(request):
    trailers = {}
    csv_path = os.path.join(settings.BASE_DIR, 'recflix', 'static', 'trailers.csv')
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    title, link = row[0].strip(), row[1].strip()
                    if title and link:
                        trailers[title] = link
        print(f"Loaded {len(trailers)} trailers")
    except Exception as e:
        print(f"Error loading trailers: {e}")
    
    # Convert trailers dictionary to JSON string and escape single quotes
    trailers_json = json.dumps(trailers).replace("'", "\\'")
    print(f"First few trailers: {list(trailers.items())[:5]}")
    return render(request, 'trailer.html', {'trailers': trailers_json})

@require_POST
def add_to_playlist(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'User not authenticated'})
    
    title = request.POST.get('title')
    category = request.POST.get('category')
    
    if not title or not category:
        return JsonResponse({'success': False, 'error': 'Missing title or category'})
    
    print(f"Adding to playlist - Title: {title}, Category: {category}")
    
    # Get poster URL using the find_best_poster function
    poster = find_best_poster(title, category)
    
    # Create playlist item
    try:
        PlaylistItem.objects.create(
            user=request.user,
            title=title,
            category=category,
            poster=poster
        )

        # Update popular items
        popular_item, created = PopularItem.objects.get_or_create(
            title=title,
            category=category,
            defaults={'poster': poster}
        )
        if not created:
            popular_item.count += 1
            popular_item.save()
            print(f"Updated popular item count for {title}: {popular_item.count}")
        else:
            print(f"Created new popular item for {title}")

        return JsonResponse({'success': True})
    except Exception as e:
        print(f"Error in add_to_playlist: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})

def get_popular_items(request, category):
    """Get the most popular items for a specific category"""
    try:
        print(f"Fetching popular items for category: {category}")
        # Validate category
        valid_categories = ['movies', 'anime', 'webseries', 'books', 'games']
        if category not in valid_categories:
            print(f"Invalid category: {category}")
            return JsonResponse({'error': 'Invalid category'}, status=400)

        # First check if the PopularItem model exists and has any records
        try:
            all_items = PopularItem.objects.all()
            print(f"Total items in database: {all_items.count()}")
        except Exception as e:
            print(f"Error accessing PopularItem model: {str(e)}")
            return JsonResponse({'error': 'Database error'}, status=500)

        # Get items for the specific category
        try:
            popular_items = PopularItem.objects.filter(category=category, count__gte=2).order_by('-count', '-last_updated')[:10]
            print(f"Found {popular_items.count()} popular items for {category}")
            
            # Debug: Print all items in this category regardless of count
            category_items = PopularItem.objects.filter(category=category)
            print(f"Total items in category {category}: {category_items.count()}")
            for item in category_items:
                print(f"Item: {item.title}, Count: {item.count}")
            
            items = []
            for item in popular_items:
                items.append({
                    'title': item.title,
                    'poster': item.poster,
                    'count': item.count
                })
            print(f"Returning {len(items)} items")
            return JsonResponse({'items': items})
        except Exception as e:
            print(f"Error querying popular items: {str(e)}")
            return JsonResponse({'error': 'Error querying popular items'}, status=500)
    except Exception as e:
        print(f"Unexpected error in get_popular_items: {str(e)}")
        return JsonResponse({'error': 'Unexpected error'}, status=500)

@require_POST
def remove_from_playlist(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'User not authenticated'})
    
    title = request.POST.get('title')
    category = request.POST.get('category')
    
    if not title or not category:
        return JsonResponse({'success': False, 'error': 'Missing title or category'})
    
    try:
        PlaylistItem.objects.filter(
            user=request.user,
            title=title,
            category=category
        ).delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def playlist_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Get user's playlist items grouped by category
    movies = PlaylistItem.objects.filter(user=request.user, category='movies')
    anime = PlaylistItem.objects.filter(user=request.user, category='anime')
    webseries = PlaylistItem.objects.filter(user=request.user, category='webseries')
    games = PlaylistItem.objects.filter(user=request.user, category='games')
    books = PlaylistItem.objects.filter(user=request.user, category='books')
    
    context = {
        'movies': movies,
        'anime': anime,
        'webseries': webseries,
        'games': games,
        'books': books
    }
    
    return render(request, 'playlist.html', context)

def games(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'games.html')
