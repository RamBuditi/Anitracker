from django.shortcuts import render, redirect
from django.core.paginator import Paginator
import requests
import aiohttp
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.http import JsonResponse
from django.contrib import messages
from users.models import UserProfile, AnimeEntry
import asyncio
import aiohttp
from asgiref.sync import sync_to_async, async_to_sync
from django.http import JsonResponse
from functools import wraps
from django.views.decorators.csrf import csrf_exempt
from users.views import fetch_anime_details


def home(request):
    search_query = request.GET.get('q', '')  # Default to empty string if 'q' is not present
    current_season = request.GET.get('season')
    current_year = request.GET.get('year')
    season_page = request.GET.get('season_page')

    anime_list = []
    season_info = {}
    prev_season = None
    next_season = None

    if season_page:
        season, year = season_page.split('/')
        url = f'https://api.jikan.moe/v4/seasons/{year}/{season}'
        current_season = season
        current_year = year
    else:
        url = 'https://api.jikan.moe/v4/seasons/now'

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        anime_list = data.get('data', [])
        if not season_page:
            season_info = {
                'season': data.get('data', [{}])[0].get('season', 'Unknown').capitalize(),
                'year': data.get('data', [{}])[0].get('year', None)
            }
            current_season = season_info.get('season')
            current_year = season_info.get('year')

    if anime_list:
        paginator = Paginator(anime_list, 8)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
    else:
        page_obj = None

    seasons = ['winter', 'spring', 'summer', 'fall']
    if current_season:
        current_season_index = seasons.index(current_season.lower())

        try:
            current_year_int = int(current_year) if current_year else None
        except (ValueError, TypeError):
            current_year_int = None

        if current_year_int is not None:
            prev_year = current_year_int - 1 if current_season_index == 0 else current_year_int
            next_year = current_year_int + 1 if current_season_index == 3 else current_year_int

            prev_season_index = (current_season_index - 1) % 4
            next_season_index = (current_season_index + 1) % 4

            prev_season = (seasons[prev_season_index], prev_year)
            next_season = (seasons[next_season_index], next_year)

    return render(request, 'viewer/home.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'season_info': {'season': current_season, 'year': current_year} if current_season and current_year else season_info,
        'prev_season': prev_season,
        'next_season': next_season,
    })



def anime_detail(request, anime_id):
    if request.user.is_authenticated:
        # Redirect to the user-specific anime detail view
        return redirect('users:anime_detail', anime_id=anime_id)
    
    # Create a new event loop for this request
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        async def fetch_details():
            async with aiohttp.ClientSession() as session:
                anime = await fetch_anime_details(session, anime_id)
                return {'anime': anime, 'current_entry': None}

        # Run the async function in the new event loop
        context = loop.run_until_complete(fetch_details())
        return render(request, 'viewer/anime_detail.html', context)

    except Exception as e:
        print(f"Error in anime_detail view: {e}")
        return render(request, 'viewer/anime_detail.html', {'anime': None, 'error': str(e)})

    finally:
        loop.close()


async def fetch_jikan_data(url):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            print(f"Error fetching data from Jikan: {e}")
            return None

async def top_anime(request):
    top_rated_url = 'https://api.jikan.moe/v4/top/anime?filter=bypopularity'
    most_popular_url = 'https://api.jikan.moe/v4/top/anime?filter=favorite'
    top_upcoming_url = 'https://api.jikan.moe/v4/seasons/upcoming'

    top_rated_data = await fetch_jikan_data(top_rated_url)
    most_popular_data = await fetch_jikan_data(most_popular_url)
    top_upcoming_data = await fetch_jikan_data(top_upcoming_url)

    top_rated_anime = top_rated_data['data'] if top_rated_data else []
    most_popular_anime = most_popular_data['data'] if most_popular_data else []
    top_upcoming_anime = top_upcoming_data['data'] if top_upcoming_data else []

    # Sort the lists
    top_rated_anime = sorted(top_rated_anime, key=lambda x: x['score'], reverse=True)
    most_popular_anime = sorted(most_popular_anime, key=lambda x: x['members'], reverse=True)
    top_upcoming_anime = sorted(top_upcoming_anime, key=lambda x: x['members'], reverse=True)

    context = {
        'top_rated_anime': top_rated_anime,
        'most_popular_anime': most_popular_anime,
        'top_upcoming_anime': top_upcoming_anime,
    }

    # Use sync_to_async to call the synchronous render function
    return await sync_to_async(render)(request, 'viewer/top_anime.html', context)


def search_results(request):
    search_query = request.GET.get('q')
    selected_age_ratings = request.GET.getlist('age_rating')
    selected_genres = request.GET.getlist('genre')

    url = f'https://api.jikan.moe/v4/anime?q={search_query}'
    if selected_age_ratings:
        for rating in selected_age_ratings:
            url += f'&rating={rating}'
    if selected_genres:
        for genre in selected_genres:
            url += f'&genres={genre}'

    response = requests.get(url)
    anime_list = []
    if response.status_code == 200:
        anime_list = response.json().get('data', [])

    # Fetch all genres from Jikan API
    genres_response = requests.get('https://api.jikan.moe/v4/genres/anime')
    if genres_response.status_code == 200:
        genres = genres_response.json().get('data', [])
    else:
        genres = []

    # Fetch all age ratings (static list as they don't change often)
    age_ratings = ['g', 'pg', 'pg13', 'r17', 'r', 'rx']

    paginator = Paginator(anime_list, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'search_query': search_query,
        'page_obj': page_obj,
        'selected_age_ratings': selected_age_ratings,
        'selected_genres': selected_genres,
        'age_ratings': age_ratings,
        'genres': genres,
    }
    return render(request, 'viewer/search_results.html', context)