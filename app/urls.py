from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_view, name='upload'),
    path('ar/<uuid:uid>/', views.ar_scan, name='ar_scan'),
    path('card/<uuid:uid>/', views.download_card, name='card'),
    path('list/', views.list_cards, name='list'),
    path('progress/', views.progress_view, name='progress'),
]