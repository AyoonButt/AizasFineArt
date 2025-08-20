from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = 'userprofiles'

urlpatterns = [
    # Authentication URLs
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name='userprofiles/auth/password_reset.html'), 
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='userprofiles/auth/password_reset_done.html'), 
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='userprofiles/auth/password_reset_confirm.html'), 
         name='password_reset_confirm'),
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='userprofiles/auth/password_reset_complete.html'), 
         name='password_reset_complete'),
    
    # Profile Management
    path('profile/', views.ProfileDetailView.as_view(), name='profile'),
    path('profile/<int:user_id>/', views.PublicProfileView.as_view(), name='public_profile'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    path('profile/preferences/', views.ProfilePreferencesView.as_view(), name='profile_preferences'),
    path('profile/privacy/', views.PrivacySettingsView.as_view(), name='privacy_settings'),
    
    # Account Management
    path('account/', views.AccountSettingsView.as_view(), name='account_settings'),
    path('account/password/', views.PasswordChangeView.as_view(), name='password_change'),
    path('account/deactivate/', views.AccountDeactivateView.as_view(), name='account_deactivate'),
    
    # Dashboard
    path('dashboard/', views.UserDashboardView.as_view(), name='dashboard'),
    path('dashboard/stats/', views.UserStatsView.as_view(), name='user_stats'),
    path('dashboard/activity/', views.UserActivityView.as_view(), name='user_activity'),
    
    # Wishlist Management
    path('wishlist/', views.WishlistView.as_view(), name='wishlist'),
    path('wishlist/add/', views.WishlistAddView.as_view(), name='wishlist_add'),
    path('wishlist/remove/<int:wishlist_id>/', views.WishlistRemoveView.as_view(), name='wishlist_remove'),
    path('wishlist/clear/', views.WishlistClearView.as_view(), name='wishlist_clear'),
    path('wishlist/update-notes/', views.WishlistUpdateNotesView.as_view(), name='wishlist_update_notes'),
    
    # AJAX Endpoints
    path('ajax/wishlist/toggle/', views.WishlistToggleAjaxView.as_view(), name='ajax_wishlist_toggle'),
    path('ajax/wishlist/count/', views.WishlistCountAjaxView.as_view(), name='ajax_wishlist_count'),
    path('ajax/notifications/mark-read/', views.NotificationMarkReadAjaxView.as_view(), name='ajax_notification_mark_read'),
    path('ajax/notifications/mark-all-read/', views.NotificationMarkAllReadAjaxView.as_view(), name='ajax_notification_mark_all_read'),
    path('ajax/profile/update-last-active/', views.UpdateLastActiveAjaxView.as_view(), name='ajax_update_last_active'),
    
    # Notifications
    path('notifications/', views.NotificationListView.as_view(), name='notifications'),
    path('notifications/<int:notification_id>/', views.NotificationDetailView.as_view(), name='notification_detail'),
    path('notifications/settings/', views.NotificationSettingsView.as_view(), name='notification_settings'),
    
    # Activity Tracking
    path('activity/', views.ActivityLogView.as_view(), name='activity_log'),
    path('activity/export/', views.ActivityExportView.as_view(), name='activity_export'),
    
    # User Search and Discovery
    path('collectors/', views.CollectorListView.as_view(), name='collector_list'),
    path('artists/', views.ArtistListView.as_view(), name='artist_list'),
]