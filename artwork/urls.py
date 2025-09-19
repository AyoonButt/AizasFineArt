from django.urls import path
from . import views

app_name = 'artwork'

urlpatterns = [
    # Gallery views
    path('', views.GalleryView.as_view(), name='gallery'),
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('series/<slug:category_slug>/<slug:slug>/', views.SeriesDetailView.as_view(), name='series_detail'),
    path('<slug:category_slug>/<slug:slug>/', views.ArtworkDetailView.as_view(), name='detail'),
    path('display/<slug:category_slug>/<slug:slug>/', views.ArtworkDisplayView.as_view(), name='display'),
    
    # Search and filtering
    path('search/', views.ArtworkSearchView.as_view(), name='search'),
    path('filter/', views.ArtworkFilterView.as_view(), name='filter'),
    
    # Interactive features
    path('inquiry/<int:artwork_id>/', views.ArtworkInquiryView.as_view(), name='inquiry'),
]