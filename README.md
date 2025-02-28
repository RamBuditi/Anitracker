# Anitracker

Anitracker is a web application that allows anime enthusiasts to search, track, and rate their favorite anime shows. Built with Django and powered by the Jikan API, Anitracker provides a comprehensive platform for managing your anime watching experience.

![Screenshot 2025-02-28 095556](https://github.com/user-attachments/assets/7bd7b67a-f830-4bca-9013-315840d171bd)

## Features

### Anime Tracking
- **Search Functionality**: Easily find anime titles using the powerful search feature
  
 ![Screenshot 2025-02-28 100144](https://github.com/user-attachments/assets/c760c88d-4f8b-41bf-86ce-0d50be8c8e34)
  
- **Episode Tracking**: Keep track of which episodes you've watched for each anime
- **Rating System**: Rate anime on a scale to remember your favorites
- **Review Writing**: Share your thoughts by writing detailed reviews


### Seasonal Anime
- Browse anime by season to discover new shows
- Stay up-to-date with the latest releases


### User Profiles
- **Watch Statistics**: View comprehensive statistics about your watching habits
  - Total days of anime watched
  - Number of completed anime
  - Average rating given
- **Anime List**: Access a complete list of all anime you've watched with your ratings and progress

### User Authentication
- Create personal accounts
- Secure login/logout functionality
- Personalized experience across devices

## Technologies Used

- **Backend**: Django (Python web framework)
- **Frontend**: HTML, CSS, JavaScript
- **UI Framework**: Bootstrap
- **API**: Jikan API (unofficial MyAnimeList API)
- **Database**: SQLite (development)

## Screenshots

### Home Page
![Home Page](https://api.placeholder.com/600/300)

### Anime Details
![Anime Details](https://api.placeholder.com/600/300)

### Profile Statistics
![Profile Statistics](https://api.placeholder.com/600/300)

## Getting Started

### Prerequisites
- Python 3.8+
- pip (Python package installer)
- Virtual environment (recommended)

### Installation
1. Clone the repository:
   ```
   git clone https://github.com/yourusername/anitracker.git
   cd anitracker
   ```

2. Set up a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```
   python manage.py migrate
   ```

5. Run the development server:
   ```
   python manage.py runserver
   ```

6. Access the application at `http://localhost:8000`

## Usage

1. **Create an Account**: Sign up to start tracking your anime
2. **Search for Anime**: Use the search bar to find anime titles
3. **Track Episodes**: Mark episodes as watched as you progress through a series
4. **Rate and Review**: Share your thoughts and ratings after watching
5. **View Statistics**: Check your profile to see your watching statistics and history



## Acknowledgments

- [Jikan API](https://jikan.moe/) for providing anime data
- [Bootstrap](https://getbootstrap.com/) for the responsive UI components
- All anime creators and studios for their amazing work
