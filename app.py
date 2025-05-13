import pickle
import streamlit as st
import requests
import pandas as pd

# Fetch poster using TMDB API
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    data = requests.get(url).json()
    poster_path = data.get('poster_path', '')
    return f"https://image.tmdb.org/t/p/w500/{poster_path}" if poster_path else None

# Fetch genres from TMDB API
def fetch_genres():
    url = "https://api.themoviedb.org/3/genre/movie/list?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    data = requests.get(url).json()
    return {genre['id']: genre['name'] for genre in data['genres']}

# Fetch trending movies with filters
def fetch_trending_movies(genre_filter=None, language_filter=None):
    url = f"https://api.themoviedb.org/3/trending/movie/week?api_key=8265bd1679663a7ea12ac168da84d2e8"
    data = requests.get(url).json()['results']
    
    filtered_movies = []
    for movie in data:
        if genre_filter and not any(genre in movie.get('genre_ids', []) for genre in genre_filter):
            continue
        if language_filter and movie.get('original_language') != language_filter:
            continue
        filtered_movies.append({
            'title': movie['title'],
            'poster': fetch_poster(movie['id']),
        })
    return filtered_movies

# Recommendation function
def recommend(movie, genre_filter=None, language_filter=None):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        # Fetch movie genres and language
        movie_data = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US").json()
        if genre_filter and not any(genre in movie_data.get('genres', []) for genre in genre_filter):
            continue
        if language_filter and movie_data.get('original_language') != language_filter:
            continue
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)
    return recommended_movie_names, recommended_movie_posters

# Streamlit app
st.header('Movie Recommender System')

# Load data
movies = pickle.load(open('model/movie_list.pkl', 'rb'))
similarity = pickle.load(open('model/similarity.pkl', 'rb'))

# Dropdown for movie selection
movie_list = movies['title'].values
selected_movie = st.selectbox("Type or select a movie from the dropdown", movie_list)

# Fetch genres for filtering
genres = fetch_genres()
genre_names = list(genres.values())
selected_genres = st.multiselect("Select genres for filtering", genre_names)
selected_genre_ids = [genre_id for genre_id, genre_name in genres.items() if genre_name in selected_genres]

# Language filter
selected_language = st.selectbox("Select a language for filtering", ['All', 'en', 'hi', 'fr', 'es', 'de', 'ja'])
language_filter = None if selected_language == 'All' else selected_language

# Recommendations
if st.button('Show Recommendation'):
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie, genre_filter=selected_genre_ids, language_filter=language_filter)
    cols = st.columns(5)
    for idx, col in enumerate(cols):
        if idx < len(recommended_movie_names):
            with col:
                st.text(recommended_movie_names[idx])
                st.image(recommended_movie_posters[idx])

# Trending movies section
st.subheader("Trending Movies")
trending_movies = fetch_trending_movies(genre_filter=selected_genre_ids, language_filter=language_filter)
cols = st.columns(5)
for idx, col in enumerate(cols):
    if idx < len(trending_movies):
        with col:
            st.text(trending_movies[idx]['title'])
            st.image(trending_movies[idx]['poster'])
