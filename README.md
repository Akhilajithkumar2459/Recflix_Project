# Recflix_Project

Recflix is a Django-based web application that provides personalized recommendations for movies, anime, web series, books, and games. It leverages precomputed similarity data and external APIs to offer tailored suggestions, manage user playlists, and track viewing history.

## Features

- **Personalized Recommendations:** Get recommendations for movies, anime, web series, books, and games based on your selections and similarity models.
- **User Authentication:** Register, log in, and manage your account securely.
- **Playlist Management:** Add, view, and remove items from your personal playlist.
- **History Tracking:** View and clear your recommendation and viewing history.
- **Popular Items:** See what's trending among users.
- **Rich Metadata:** Fetches additional details (ratings, genres, posters, etc.) from TMDB and RAWG APIs.
- **Random Suggestions:** Explore random picks from each category.
- **Modern UI:** Responsive web interface with category-specific pages and poster images.

## Project Structure

- `recflix/` - Main Django app containing models, views, templates, static files, and data.
- `recflix_project/` - Django project configuration.
- `recflix/data/` - Precomputed `.pkl` files for similarity-based recommendations.
- `recflix/static/posters/` - Poster images for each category.
- `recflix/templates/` - HTML templates for the web interface.

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/recflix_project.git
   cd recflix_project
   ```

2. **Install dependencies:**
   ```bash
   pip install django pandas requests
   ```

3. **Prepare data files:**
   - Ensure all `.pkl` files are present in `recflix/data/`.
   - Place poster images in the appropriate subfolders under `recflix/static/posters/`.

4. **Apply migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

6. **Access the app:**
   - Open your browser and go to `http://127.0.0.1:8000/`

## API Keys

- The app uses TMDB and RAWG APIs for fetching metadata. You may need to set your own API keys in `recflix/views.py` for production use.

## Usage

- Register for an account or log in.
- Select a category (movies, anime, web series, books, games).
- Search for a title to get recommendations.
- Add items to your playlist or view your history.
- Explore popular and random recommendations.

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](LICENSE) (or your preferred license) 
