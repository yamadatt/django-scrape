from django.urls import path
from . import views

app_name = 'scraper'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('targets/', views.target_list, name='target_list'),
    path('data/', views.scraped_data_list, name='data_list'),
    path('jobs/', views.job_list, name='job_list'),
    path('scrape/<int:target_id>/', views.start_scraping, name='start_scraping'),
    path('scrape-all/', views.start_all_scraping, name='start_all_scraping'),
    path('api/job/<int:job_id>/status/', views.api_job_status, name='api_job_status'),
] 