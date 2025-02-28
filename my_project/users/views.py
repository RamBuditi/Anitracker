from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.http import JsonResponse
from django.contrib import messages
from .models import UserProfile, AnimeEntry
from .forms import UserProfileForm, CustomUserCreationForm
import asyncio
import aiohttp
from asgiref.sync import sync_to_async, async_to_sync
from .utils import get_favorite_anime_details, search_anime, fetch_anime_details
from django.http import JsonResponse
from functools import wraps
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from .models import AnimeReview
from .forms import AnimeReviewForm
import logging
import time
from collections import defaultdict

# Add back the signup view
def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Account created for {user.username}!')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/signup.html', {'form': form})

@login_required
def profile_view(request, user_id):
    profile = get_object_or_404(UserProfile, user_id=user_id)
    is_owner = request.user.id == user_id
    
    # Get favorite anime details
    favorite_anime = []
    if profile.favorite_anime_ids:
        # Run async function in sync context
        favorite_anime = asyncio.run(get_favorite_anime_details(profile.favorite_anime_ids))

    context = {
        'profile': profile,
        'is_owner': is_owner,
        'favorite_anime': favorite_anime,
    }
    return render(request, 'users/profile.html', context)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.userprofile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('users:profile', user_id=request.user.id)
    else:
        form = UserProfileForm(instance=request.user.userprofile)
    return render(request, 'users/edit_profile.html', {'form': form})

@login_required
def search_anime_view(request):
    query = request.GET.get('q', '')
    if query:
        results = search_anime(query)
        return JsonResponse({'results': results})
    return JsonResponse({'results': []})

@login_required
def add_favorite_anime(request):
    if request.method == 'POST':
        anime_id = request.POST.get('anime_id')
        if anime_id:
            profile = request.user.userprofile
            # Check if already at maximum limit
            if len(profile.favorite_anime_ids) >= 3:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Maximum number of favorite anime (3) reached'
                }, status=400)
            
            # Check if anime is not already in favorites
            if anime_id not in profile.favorite_anime_ids:
                profile.favorite_anime_ids.append(int(anime_id))
                profile.save()
                return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def remove_favorite_anime(request):
    if request.method == 'POST':
        anime_id = request.POST.get('anime_id')
        if anime_id:
            profile = request.user.userprofile
            if int(anime_id) in profile.favorite_anime_ids:
                profile.favorite_anime_ids.remove(int(anime_id))
                profile.save()
                return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

async def fetch_anime_details(session, anime_id):
    url = f"https://api.jikan.moe/v4/anime/{anime_id}"
    try:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                anime_data = data.get('data')
                if not anime_data:
                    return None
                    
                return {
                    'mal_id': anime_data.get('mal_id'),
                    'title': anime_data.get('title'),
                    'images': anime_data.get('images', {}),
                    'synopsis': anime_data.get('synopsis'),
                    'trailer': anime_data.get('trailer', {}),
                    'score': anime_data.get('score'),
                    'episodes': anime_data.get('episodes'),
                    'duration': anime_data.get('duration'),
                    'rating': anime_data.get('rating'),
                    'status': anime_data.get('status'),
                    'aired': anime_data.get('aired'),
                    'season': anime_data.get('season'),
                    'year': anime_data.get('year')
                }
            else:
                print(f"Error: API returned status {response.status} for anime_id {anime_id}")
                return None
                
    except aiohttp.ClientError as e:
        print(f"Client error fetching anime details: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error fetching anime details: {e}")
        return None
    


@login_required
def anime_detail(request, anime_id):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        get_userprofile = sync_to_async(lambda: request.user.userprofile)
        get_entry = sync_to_async(AnimeEntry.objects.filter)
        get_reviews = sync_to_async(lambda anime_id, userprofile: list(AnimeReview.objects.filter(anime_id=anime_id).exclude(user_profile=userprofile)))
        get_review = sync_to_async(AnimeReview.objects.filter)

        async def fetch_details_and_data():
            userprofile = await get_userprofile()

            async with aiohttp.ClientSession() as session:
                anime = await fetch_anime_details(session, anime_id)
                if not anime:
                    return {'anime': None, 'error': 'Could not fetch anime details'}

            # Get current entry
            entries = await get_entry(user_profile=userprofile, anime_id=anime_id)
            current_entry = await sync_to_async(lambda: entries.first())()

            # Check if the user has the anime in their list
            if not current_entry:
                messages.warning(request, "You need to add this anime to your list before writing a review.")
                return {'anime': anime, 'current_entry': None, 'current_status': '', 'current_rating': None, 'current_episodes': 0, 'user_review': None, 'other_reviews': [], 'review_form': None}
            
            # Get current user's review
            user_reviews = await get_review(user_profile=userprofile, anime_id=anime_id)
            user_review = await sync_to_async(lambda: user_reviews.first())()

            # Get all reviews except current user's
            other_reviews = await get_reviews(anime_id, userprofile)

            # Create or get review form only if anime is in user's list
            if request.method == 'POST':
                review_form = AnimeReviewForm(request.POST, instance=user_review)
                if review_form.is_valid():
                    review = review_form.save(commit=False)
                    review.user_profile = userprofile
                    review.anime_id = anime_id
                    review.anime_entry = current_entry
                    await sync_to_async(review.save)()

                    # Update the user_review and other_reviews after saving
                    user_reviews = await get_review(user_profile=userprofile, anime_id=anime_id)
                    user_review = await sync_to_async(lambda: user_reviews.first())()
                    other_reviews = await get_reviews(anime_id, userprofile)

                    messages.success(request, "Review updated successfully!")
                    
                    # Update review_form with the new user_review instance
                    review_form = AnimeReviewForm(instance=user_review) # Update here
                    
            else:
                review_form = AnimeReviewForm(instance=user_review)

            return {
                'anime': anime,
                'current_entry': current_entry,
                'current_status': current_entry.status if current_entry else '',
                'current_rating': current_entry.rating if current_entry else None,
                'current_episodes': current_entry.episodes_watched if current_entry else 0,
                'user_review': user_review,
                'other_reviews': other_reviews,
                'review_form': review_form,
            }

        context = loop.run_until_complete(fetch_details_and_data())
        
        # Check if fetch_details_and_data returned a redirect
        if isinstance(context, dict):
          return render(request, 'users/anime_detail.html', context)
        else:
          return context

    except Exception as e:
        print(f"Error in anime_detail view: {e}")
        return render(request, 'users/anime_detail.html', {'anime': None, 'error': str(e)})

    finally:
        loop.close()

@login_required
@csrf_exempt
def update_anime_status(request):
    if request.method == 'POST':
        try:
            # Get data from request
            anime_id = request.POST.get('anime_id')
            status = request.POST.get('status')
            rating = request.POST.get('rating')
            episodes_watched = request.POST.get('episodes_watched', 0)

            # Validate inputs
            if not anime_id:
                return JsonResponse({'status': 'error', 'message': 'Anime ID is required'}, status=400)
            
            # Convert to proper types
            anime_id = int(anime_id)
            episodes_watched = int(episodes_watched) if episodes_watched else 0
            rating = int(rating) if rating else None

            # If status is blank, delete the entry if it exists
            if not status:
                AnimeEntry.objects.filter(
                    user_profile=request.user.userprofile,
                    anime_id=anime_id
                ).delete()
                return JsonResponse({'status': 'success', 'message': 'Entry removed'})

            # Get or create the entry
            entry, created = AnimeEntry.objects.get_or_create(
                user_profile=request.user.userprofile,
                anime_id=anime_id,
                defaults={
                    'status': status,
                    'rating': rating,
                    'episodes_watched': episodes_watched,
                }
            )

            # If entry already existed, update it
            if not created:
                entry.status = status
                entry.rating = rating
                entry.episodes_watched = episodes_watched
                entry.save()

            return JsonResponse({
                'status': 'success',
                'message': 'Status updated successfully'
            })

        except ValueError as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Invalid value provided: {str(e)}'
            }, status=400)
            
        except Exception as e:
            print(f"Error updating anime status: {str(e)}")  # For server logs
            return JsonResponse({
                'status': 'error',
                'message': 'An error occurred while updating status'
            }, status=500)

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=405)





@login_required
def anime_list_view(request):
    entries = AnimeEntry.objects.filter(user_profile=request.user.userprofile)
    anime_ids = [entry.anime_id for entry in entries]
    anime_details = asyncio.run(get_favorite_anime_details(anime_ids))
    
    # Combine anime details with user entries
    anime_list = []
    for details in anime_details:
        entry = next((e for e in entries if e.anime_id == details['mal_id']), None)
        if entry:
            anime_list.append({
                'details': details,
                'status': entry.status,
                'rating': entry.rating,
                'episodes_watched': entry.episodes_watched
            })
    
    return render(request, 'users/anime_list.html', {'anime_list': anime_list})



async def fetch_anime_with_retry(session, anime_id, max_retries=3):
    for attempt in range(max_retries):
        try:
            url = f"https://api.jikan.moe/v4/anime/{anime_id}"
            async with session.get(url) as response:
                if response.status == 429:  # Rate limited
                    wait_time = int(response.headers.get('Retry-After', 2))
                    await asyncio.sleep(wait_time)
                    continue
                    
                if response.status == 200:
                    data = await response.json()
                    return data.get('data')
                    
                print(f"Error fetching anime {anime_id}: Status {response.status}")
                
        except Exception as e:
            print(f"Error fetching anime {anime_id}: {str(e)}")
            
        # Wait before retry
        await asyncio.sleep(2)
    
    return None

async def fetch_all_anime_details(anime_ids):
    async with aiohttp.ClientSession() as session:
        # Process in chunks of 2 to respect rate limits
        chunk_size = 2
        all_results = []
        
        for i in range(0, len(anime_ids), chunk_size):
            chunk = anime_ids[i:i + chunk_size]
            tasks = [fetch_anime_with_retry(session, anime_id) for anime_id in chunk]
            chunk_results = await asyncio.gather(*tasks)
            all_results.extend([r for r in chunk_results if r is not None])
            
            # Wait between chunks
            if i + chunk_size < len(anime_ids):
                await asyncio.sleep(1)
                
        return all_results

@login_required
def watch_statistics_view(request):
    user_profile = request.user.userprofile
    
    # Get all entries
    entries = AnimeEntry.objects.filter(user_profile=user_profile)
    
    # Get unique anime IDs
    anime_ids = list(set([entry.anime_id for entry in entries]))
    
    # Fetch all anime details with retry logic
    all_anime_details = asyncio.run(fetch_all_anime_details(anime_ids))
    
    # Create dictionary of anime details
    anime_details_dict = {anime['mal_id']: anime for anime in all_anime_details if anime is not None}
    
    # Track missing anime
    missing_anime_ids = [aid for aid in anime_ids if aid not in anime_details_dict]
    
    # Initialize categorized_anime with defaultdict
    categorized_anime = defaultdict(list)
    
    # Map status codes to display names
    status_display = {
        'watching': 'Currently Watching',
        'completed': 'Completed',
        'plan_to_watch': 'Plan to Watch',
        'dropped': 'Dropped'
    }
    
    # Organize entries into categories
    for entry in entries:
        display_status = status_display.get(entry.status, entry.status)
        
        # If we have the anime details, use them
        if entry.anime_id in anime_details_dict:
            categorized_anime[display_status].append({
                'details': anime_details_dict[entry.anime_id],
                'entry': entry
            })
        # If we don't have details, create a minimal entry
        else:
            categorized_anime[display_status].append({
                'details': {
                    'mal_id': entry.anime_id,
                    'title': f'Anime ID: {entry.anime_id}',
                    'images': {'jpg': {'image_url': None}},
                    'episodes': None
                },
                'entry': entry
            })
    
    # Sort each category by title
    for status in categorized_anime:
        categorized_anime[status].sort(key=lambda x: x['details']['title'])
    
    # Add debugging information
    debug_info = {
        'total_entries': len(entries),
        'unique_anime_ids': len(anime_ids),
        'successful_fetches': len(anime_details_dict),
        'missing_anime_ids': missing_anime_ids,
        'entries_by_status': {status: len(entries.filter(status=status)) for status in dict(AnimeEntry.STATUS_CHOICES).keys()}
    }
    
    context = {
        'categorized_anime': dict(categorized_anime),
        'stats': user_profile.get_watch_stats(),
        'debug_info': debug_info
    }
    
    return render(request, 'users/watch_statistics.html', context)