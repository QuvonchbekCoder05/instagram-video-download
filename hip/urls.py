from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.home, name='home'),
    path('download/', views.download_video, name='download_video'),
    path('preview/', views.preview_video, name='preview_video'),
]
