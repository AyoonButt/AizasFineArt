from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView as DjangoPasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Q, Avg, Sum
from django.http import JsonResponse, HttpResponse, Http404
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import (
    CreateView, UpdateView, DetailView, ListView, 
    TemplateView, FormView, View
)
from django.core.exceptions import PermissionDenied
import json
import csv
from datetime import datetime, timedelta

from .models import UserProfile, UserWishlist, UserNotification, UserActivityLog
from .forms import (
    UserRegistrationForm, UserProfileForm, ProfilePreferencesForm,
    PrivacySettingsForm, NotificationSettingsForm, PasswordChangeForm
)
from artwork.models import Artwork
from orders.models import Order


class UserRegistrationView(CreateView):
    """User registration with profile creation"""
    form_class = UserRegistrationForm
    template_name = 'userprofiles/auth/register.html'
    success_url = reverse_lazy('userprofiles:dashboard')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.object
        
        # Create user profile
        UserProfile.objects.create(user=user)
        
        # Log the user in
        login(self.request, user)
        
        # Log registration activity
        UserActivityLog.objects.create(
            user=user,
            activity_type='profile_update',
            description='User registered',
            ip_address=self.get_client_ip(),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
        
        messages.success(self.request, 'Welcome! Your account has been created successfully.')
        return response
    
    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class CustomLoginView(LoginView):
    """Custom login view with activity logging"""
    template_name = 'userprofiles/auth/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('userprofiles:dashboard')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Update last active and log activity
        if hasattr(self.request.user, 'profile'):
            self.request.user.profile.update_last_active()
        
        UserActivityLog.objects.create(
            user=self.request.user,
            activity_type='login',
            description='User logged in',
            ip_address=self.get_client_ip(),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
        
        return response
    
    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class CustomLogoutView(LoginRequiredMixin, LogoutView):
    """Custom logout view with activity logging"""
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            UserActivityLog.objects.create(
                user=request.user,
                activity_type='logout',
                description='User logged out',
                ip_address=self.get_client_ip(),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
        return super().dispatch(request, *args, **kwargs)
    
    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class ProfileDetailView(LoginRequiredMixin, DetailView):
    """User's own profile detail view"""
    model = UserProfile
    template_name = 'userprofiles/profile_detail.html'
    context_object_name = 'profile'
    
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get user statistics
        context['total_orders'] = Order.objects.filter(user=self.request.user).count()
        context['wishlist_count'] = UserWishlist.objects.filter(user=self.request.user).count()
        context['unread_notifications'] = UserNotification.objects.filter(
            user=self.request.user, is_read=False
        ).count()
        
        # Recent activity
        context['recent_activity'] = UserActivityLog.objects.filter(
            user=self.request.user
        ).order_by('-timestamp')[:10]
        
        return context


class PublicProfileView(DetailView):
    """Public profile view for other users"""
    model = UserProfile
    template_name = 'userprofiles/public_profile.html'
    context_object_name = 'profile'
    
    def get_object(self):
        user = get_object_or_404(User, id=self.kwargs['user_id'])
        profile = get_object_or_404(UserProfile, user=user)
        
        # Check if profile is public
        if not profile.profile_public and profile.user != self.request.user:
            raise Http404("Profile not found")
        
        return profile
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Only show public information
        if self.object.profile_public:
            if self.object.show_purchase_history:
                context['public_orders'] = Order.objects.filter(
                    user=self.object.user,
                    status__in=['delivered', 'completed']
                ).count()
        
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """Edit user profile"""
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'userprofiles/profile_edit.html'
    success_url = reverse_lazy('userprofiles:profile')
    
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Log profile update
        UserActivityLog.objects.create(
            user=self.request.user,
            activity_type='profile_update',
            description='Profile updated',
            ip_address=self.get_client_ip(),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
        
        messages.success(self.request, 'Your profile has been updated successfully.')
        return response
    
    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class ProfilePreferencesView(LoginRequiredMixin, UpdateView):
    """Edit user preferences"""
    model = UserProfile
    form_class = ProfilePreferencesForm
    template_name = 'userprofiles/preferences.html'
    success_url = reverse_lazy('userprofiles:profile_preferences')
    
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Your preferences have been updated.')
        return response


class PrivacySettingsView(LoginRequiredMixin, UpdateView):
    """Edit privacy settings"""
    model = UserProfile
    form_class = PrivacySettingsForm
    template_name = 'userprofiles/privacy_settings.html'
    success_url = reverse_lazy('userprofiles:privacy_settings')
    
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Your privacy settings have been updated.')
        return response


class AccountSettingsView(LoginRequiredMixin, TemplateView):
    """Account settings overview"""
    template_name = 'userprofiles/account_settings.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['profile'] = getattr(self.request.user, 'profile', None)
        return context


class PasswordChangeView(LoginRequiredMixin, DjangoPasswordChangeView):
    """Change user password"""
    form_class = PasswordChangeForm
    template_name = 'userprofiles/password_change.html'
    success_url = reverse_lazy('userprofiles:account_settings')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Log password change
        UserActivityLog.objects.create(
            user=self.request.user,
            activity_type='password_change',
            description='Password changed',
            ip_address=self.get_client_ip(),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
        
        messages.success(self.request, 'Your password has been changed successfully.')
        return response
    
    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class AccountDeactivateView(LoginRequiredMixin, TemplateView):
    """Account deactivation"""
    template_name = 'userprofiles/account_deactivate.html'
    
    def post(self, request, *args, **kwargs):
        if request.POST.get('confirm') == 'DEACTIVATE':
            # Log deactivation
            UserActivityLog.objects.create(
                user=request.user,
                activity_type='profile_update',
                description='Account deactivated',
                ip_address=self.get_client_ip(),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            # Deactivate user
            request.user.is_active = False
            request.user.save()
            
            logout(request)
            messages.info(request, 'Your account has been deactivated.')
            return redirect('home')
        else:
            messages.error(request, 'Please type "DEACTIVATE" to confirm.')
            return self.get(request, *args, **kwargs)
    
    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class UserDashboardView(LoginRequiredMixin, TemplateView):
    """User dashboard with overview"""
    template_name = 'userprofiles/dashboard.html'
    
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Update last active
        if hasattr(user, 'profile'):
            user.profile.update_last_active()
        
        # User statistics
        context['stats'] = {
            'total_orders': Order.objects.filter(user=user).count(),
            'pending_orders': Order.objects.filter(user=user, status__in=['pending', 'confirmed']).count(),
            'wishlist_count': UserWishlist.objects.filter(user=user).count(),
            'total_spent': Order.objects.filter(
                user=user, payment_status='completed'
            ).aggregate(total=Sum('total_amount'))['total'] or 0,
        }
        
        # Recent orders
        context['recent_orders'] = Order.objects.filter(user=user).order_by('-created_at')[:5]
        
        # Recent notifications
        context['recent_notifications'] = UserNotification.objects.filter(
            user=user
        ).order_by('-created_at')[:5]
        
        # Wishlist items
        context['wishlist_items'] = UserWishlist.objects.filter(user=user).order_by('-created_at')[:6]
        
        return context


class UserStatsView(LoginRequiredMixin, View):
    """AJAX endpoint for user statistics"""
    
    def get(self, request):
        user = request.user
        
        # Calculate statistics
        stats = {
            'total_orders': Order.objects.filter(user=user).count(),
            'total_spent': float(Order.objects.filter(
                user=user, payment_status='completed'
            ).aggregate(total=Sum('total_amount'))['total'] or 0),
            'wishlist_count': UserWishlist.objects.filter(user=user).count(),
            'notifications_unread': UserNotification.objects.filter(
                user=user, is_read=False
            ).count(),
        }
        
        return JsonResponse(stats)


class WishlistView(LoginRequiredMixin, ListView):
    """User's wishlist"""
    model = UserWishlist
    template_name = 'userprofiles/wishlist.html'
    context_object_name = 'wishlist_items'
    paginate_by = 12
    
    def get_queryset(self):
        return UserWishlist.objects.filter(user=self.request.user).select_related('artwork')


class WishlistAddView(LoginRequiredMixin, View):
    """Add artwork to wishlist"""
    
    def post(self, request):
        artwork_id = request.POST.get('artwork_id')
        notes = request.POST.get('notes', '')
        
        if not artwork_id:
            messages.error(request, 'Invalid artwork.')
            return redirect('artwork:gallery')
        
        artwork = get_object_or_404(Artwork, id=artwork_id)
        
        wishlist_item, created = UserWishlist.objects.get_or_create(
            user=request.user,
            artwork=artwork,
            defaults={'notes': notes}
        )
        
        if created:
            # Log activity
            UserActivityLog.objects.create(
                user=request.user,
                activity_type='add_wishlist',
                description=f'Added {artwork.title} to wishlist',
                artwork=artwork,
                ip_address=self.get_client_ip(),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            messages.success(request, f'"{artwork.title}" has been added to your wishlist.')
        else:
            messages.info(request, f'"{artwork.title}" is already in your wishlist.')
        
        return redirect(artwork.get_absolute_url())
    
    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class WishlistRemoveView(LoginRequiredMixin, View):
    """Remove item from wishlist"""
    
    def post(self, request, wishlist_id):
        wishlist_item = get_object_or_404(UserWishlist, id=wishlist_id, user=request.user)
        artwork_title = wishlist_item.artwork.title
        
        # Log activity
        UserActivityLog.objects.create(
            user=request.user,
            activity_type='remove_wishlist',
            description=f'Removed {artwork_title} from wishlist',
            artwork=wishlist_item.artwork,
            ip_address=self.get_client_ip(),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        wishlist_item.delete()
        messages.success(request, f'"{artwork_title}" has been removed from your wishlist.')
        return redirect('userprofiles:wishlist')
    
    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class WishlistClearView(LoginRequiredMixin, View):
    """Clear entire wishlist"""
    
    def post(self, request):
        if request.POST.get('confirm') == 'clear':
            count = UserWishlist.objects.filter(user=request.user).count()
            UserWishlist.objects.filter(user=request.user).delete()
            
            # Log activity
            UserActivityLog.objects.create(
                user=request.user,
                activity_type='remove_wishlist',
                description=f'Cleared entire wishlist ({count} items)',
                ip_address=self.get_client_ip(),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            messages.success(request, f'Your wishlist has been cleared ({count} items removed).')
        else:
            messages.error(request, 'Confirmation required to clear wishlist.')
        
        return redirect('userprofiles:wishlist')
    
    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class WishlistUpdateNotesView(LoginRequiredMixin, View):
    """Update wishlist item notes"""
    
    def post(self, request):
        wishlist_id = request.POST.get('wishlist_id')
        notes = request.POST.get('notes', '')
        
        wishlist_item = get_object_or_404(UserWishlist, id=wishlist_id, user=request.user)
        wishlist_item.notes = notes
        wishlist_item.save()
        
        return JsonResponse({'success': True})


class WishlistToggleAjaxView(LoginRequiredMixin, View):
    """AJAX endpoint to toggle wishlist item"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            artwork_id = data.get('artwork_id')
            
            if not artwork_id:
                return JsonResponse({'error': 'Invalid artwork ID'}, status=400)
            
            artwork = get_object_or_404(Artwork, id=artwork_id)
            
            wishlist_item, created = UserWishlist.objects.get_or_create(
                user=request.user,
                artwork=artwork
            )
            
            if not created:
                # Remove from wishlist
                wishlist_item.delete()
                
                # Log activity
                UserActivityLog.objects.create(
                    user=request.user,
                    activity_type='remove_wishlist',
                    description=f'Removed {artwork.title} from wishlist',
                    artwork=artwork,
                    ip_address=self.get_client_ip(),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                return JsonResponse({
                    'success': True,
                    'action': 'removed',
                    'in_wishlist': False,
                    'message': f'"{artwork.title}" removed from wishlist'
                })
            else:
                # Added to wishlist
                UserActivityLog.objects.create(
                    user=request.user,
                    activity_type='add_wishlist',
                    description=f'Added {artwork.title} to wishlist',
                    artwork=artwork,
                    ip_address=self.get_client_ip(),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                return JsonResponse({
                    'success': True,
                    'action': 'added',
                    'in_wishlist': True,
                    'message': f'"{artwork.title}" added to wishlist'
                })
                
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class WishlistCountAjaxView(LoginRequiredMixin, View):
    """AJAX endpoint for wishlist count"""
    
    def get(self, request):
        count = UserWishlist.objects.filter(user=request.user).count()
        return JsonResponse({'count': count})


class NotificationListView(LoginRequiredMixin, ListView):
    """User notifications list"""
    model = UserNotification
    template_name = 'userprofiles/notifications.html'
    context_object_name = 'notifications'
    paginate_by = 20
    
    def get_queryset(self):
        return UserNotification.objects.filter(user=self.request.user).order_by('-created_at')


class NotificationDetailView(LoginRequiredMixin, DetailView):
    """Single notification detail"""
    model = UserNotification
    template_name = 'userprofiles/notification_detail.html'
    context_object_name = 'notification'
    pk_url_kwarg = 'notification_id'
    
    def get_object(self):
        notification = get_object_or_404(
            UserNotification, 
            id=self.kwargs['notification_id'], 
            user=self.request.user
        )
        
        # Mark as read
        notification.mark_as_read()
        
        return notification


class NotificationMarkReadAjaxView(LoginRequiredMixin, View):
    """AJAX endpoint to mark notification as read"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            notification_id = data.get('notification_id')
            
            notification = get_object_or_404(
                UserNotification, 
                id=notification_id, 
                user=request.user
            )
            
            notification.mark_as_read()
            
            return JsonResponse({'success': True})
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class NotificationMarkAllReadAjaxView(LoginRequiredMixin, View):
    """AJAX endpoint to mark all notifications as read"""
    
    def post(self, request):
        try:
            updated_count = UserNotification.objects.filter(
                user=request.user, 
                is_read=False
            ).update(is_read=True, read_at=timezone.now())
            
            return JsonResponse({
                'success': True,
                'updated_count': updated_count
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class NotificationSettingsView(LoginRequiredMixin, UpdateView):
    """Notification preferences"""
    model = UserProfile
    form_class = NotificationSettingsForm
    template_name = 'userprofiles/notification_settings.html'
    success_url = reverse_lazy('userprofiles:notification_settings')
    
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Your notification settings have been updated.')
        return response


class UpdateLastActiveAjaxView(LoginRequiredMixin, View):
    """AJAX endpoint to update user's last active timestamp"""
    
    def post(self, request):
        if hasattr(request.user, 'profile'):
            request.user.profile.update_last_active()
            return JsonResponse({'success': True})
        return JsonResponse({'error': 'Profile not found'}, status=404)


class UserActivityView(LoginRequiredMixin, ListView):
    """User activity log"""
    model = UserActivityLog
    template_name = 'userprofiles/activity_log.html'
    context_object_name = 'activities'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = UserActivityLog.objects.filter(user=self.request.user).select_related('artwork')
        
        # Filter by activity type if specified
        activity_type = self.request.GET.get('type')
        if activity_type:
            queryset = queryset.filter(activity_type=activity_type)
        
        # Date range filter
        date_from = self.request.GET.get('from')
        date_to = self.request.GET.get('to')
        
        if date_from:
            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(timestamp__date__gte=date_from)
            except ValueError:
                pass
        
        if date_to:
            try:
                date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(timestamp__date__lte=date_to)
            except ValueError:
                pass
        
        return queryset.order_by('-timestamp')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['activity_types'] = UserActivityLog.ACTIVITY_TYPES
        context['current_filters'] = {
            'type': self.request.GET.get('type', ''),
            'from': self.request.GET.get('from', ''),
            'to': self.request.GET.get('to', ''),
        }
        return context


class ActivityLogView(UserActivityView):
    """Alias for UserActivityView for URL consistency"""
    pass


class ActivityExportView(LoginRequiredMixin, View):
    """Export user activity log as CSV"""
    
    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="activity_log_{timezone.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Date', 'Activity', 'Description', 'Artwork', 'IP Address'])
        
        activities = UserActivityLog.objects.filter(user=request.user).select_related('artwork')
        
        for activity in activities:
            writer.writerow([
                activity.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                activity.get_activity_type_display(),
                activity.description,
                activity.artwork.title if activity.artwork else '',
                activity.ip_address or '',
            ])
        
        return response


class CollectorListView(ListView):
    """List of collectors (users with is_collector=True and public profiles)"""
    model = UserProfile
    template_name = 'userprofiles/collector_list.html'
    context_object_name = 'collectors'
    paginate_by = 20
    
    def get_queryset(self):
        return UserProfile.objects.filter(
            is_collector=True,
            profile_public=True
        ).select_related('user').order_by('-created_at')


class ArtistListView(ListView):
    """List of artists (users with is_artist=True and public profiles)"""
    model = UserProfile
    template_name = 'userprofiles/artist_list.html'
    context_object_name = 'artists'
    paginate_by = 20
    
    def get_queryset(self):
        return UserProfile.objects.filter(
            is_artist=True,
            profile_public=True
        ).select_related('user').order_by('-created_at')