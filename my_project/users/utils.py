import requests
from typing import List, Dict
import asyncio
import aiohttp
from typing import Dict, Any, Optional


async def fetch_anime_details(session: aiohttp.ClientSession, anime_id: int) -> Optional[Dict[str, Any]]:
    url = f"https://api.jikan.moe/v4/anime/{anime_id}"
    try:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data['data']
            else:
                print(f"Error: API returned status {response.status} for anime_id {anime_id}")
                return None
    except aiohttp.ClientError as e:
        print(f"Client error fetching anime details for {anime_id}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
async def get_favorite_anime_details(anime_ids: List[int]) -> List[Dict]:
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_anime_details(session, anime_id) for anime_id in anime_ids]
        results = await asyncio.gather(*tasks)
        return [r for r in results if r is not None]

def search_anime(query: str) -> List[Dict]:
    url = f"https://api.jikan.moe/v4/anime?q={query}&limit=5"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['data']
    return []




def parse_duration_to_minutes(self, duration_str):
    """
    Parses a duration string from the Jikan API (e.g., "24 min per ep")
    and returns the duration in minutes as an integer.
    """
    if not duration_str:
        return 0
    duration_minutes = 0
    try:
        if 'hr' in duration_str:
            parts = duration_str.split('hr')
            hours = int(parts[0].strip())
            duration_minutes += hours * 60
            if 'min' in parts[1]:
                minutes = int(parts[1].split('min')[0].strip())
                duration_minutes += minutes
        elif 'min' in duration_str:
            minutes = int(duration_str.split('min')[0].strip())
            duration_minutes += minutes
        else:
            print(f"Warning: Could not parse duration string: {duration_str}")
            return 0
    except (ValueError, IndexError) as e:
        print(f"Error parsing duration string: {duration_str}, Error: {e}")
        return 0

    return duration_minutes