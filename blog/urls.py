from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # Blog listing and categories
    path('', views.BlogListView.as_view(), name='list'),
    path('category/<slug:slug>/', views.BlogCategoryView.as_view(), name='category'),
    path('search/', views.BlogSearchView.as_view(), name='search'),
    
    # Individual posts
    path('<slug:slug>/', views.BlogPostDetailView.as_view(), name='post_detail'),
    
    # Newsletter subscription
    path('subscribe/', views.NewsletterSubscribeView.as_view(), name='subscribe'),
    path('unsubscribe/<str:email>/', views.NewsletterUnsubscribeView.as_view(), name='unsubscribe'),
    
    # Comments (AJAX)
    path('comment/<int:post_id>/', views.BlogCommentView.as_view(), name='comment'),
]