from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.decorators.csrf import csrf_exempt
from . import views

app_name = 'users'

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/<int:user_id>/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('search-anime/', views.search_anime_view, name='search_anime'),
    path('add-favorite-anime/', views.add_favorite_anime, name='add_favorite_anime'),
    path('remove-favorite-anime/', views.remove_favorite_anime, name='remove_favorite_anime'),
    path('anime/update/', csrf_exempt(views.update_anime_status), name='update_anime_status'),
    path('anime/list/', views.anime_list_view, name='anime_list'),
    path('anime/<int:anime_id>/', views.anime_detail, name='anime_detail'),
     path('watch-statistics/', views.watch_statistics_view, name='watch_statistics'),
]