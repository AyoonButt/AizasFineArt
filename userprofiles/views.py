"""
Minimal Userprofiles Views - Basic functionality for URL compatibility
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from django.contrib import messages


class CustomLoginView(LoginView):
    """Custom login view"""
    template_name = 'userprofiles/auth/login.html'
    redirect_authenticated_user = True


class CustomLogoutView(LogoutView):
    """Custom logout view"""
    template_name = 'userprofiles/auth/logout.html'


# Placeholder views - these can be expanded later
@login_required
def placeholder_view(request):
    """Placeholder view for missing functionality"""
    messages.info(request, "This feature is coming soon!")
    return redirect('userprofiles:profile_dashboard')


# Create placeholder class-based views for the URLs
class PlaceholderView(TemplateView):
    template_name = 'userprofiles/placeholder.html'
    
    def get(self, request, *args, **kwargs):
        messages.info(request, "This feature is coming soon!")
        return redirect('userprofiles:profile_dashboard')


# Map all the old view names to placeholders
ProfileDetailView = PlaceholderView
PublicProfileView = PlaceholderView
ProfileEditView = PlaceholderView
ProfilePreferencesView = PlaceholderView
PrivacySettingsView = PlaceholderView
AccountSettingsView = PlaceholderView
PasswordChangeView = PlaceholderView
AccountDeactivateView = PlaceholderView
UserDashboardView = PlaceholderView
UserStatsView = PlaceholderView
UserActivityView = PlaceholderView
WishlistView = PlaceholderView
WishlistAddView = PlaceholderView
WishlistRemoveView = PlaceholderView
WishlistClearView = PlaceholderView
WishlistUpdateNotesView = PlaceholderView
WishlistToggleAjaxView = PlaceholderView
WishlistCountAjaxView = PlaceholderView
NotificationMarkReadAjaxView = PlaceholderView
NotificationMarkAllReadAjaxView = PlaceholderView
UpdateLastActiveAjaxView = PlaceholderView
NotificationListView = PlaceholderView
NotificationDetailView = PlaceholderView
NotificationSettingsView = PlaceholderView
ActivityLogView = PlaceholderView
ActivityExportView = PlaceholderView
CollectorListView = PlaceholderView
ArtistListView = PlaceholderView