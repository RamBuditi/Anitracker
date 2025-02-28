from django.urls import path
from . import views



urlpatterns = [
    path('', views.home, name='home'),
    path('anime/<int:anime_id>/', views.anime_detail, name='anime_detail'),
    path('top-anime/', views.top_anime, name='top_anime'),
    path('search_results/', views.search_results, name='search_results'),
]