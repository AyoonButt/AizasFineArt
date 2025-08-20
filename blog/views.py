from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, FormView
from django.db.models import Q, Count
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils import timezone
from .models import BlogPost, BlogCategory, BlogComment, BlogSubscriber
from .forms import BlogCommentForm, NewsletterSubscribeForm


class BlogListView(ListView):
    model = BlogPost
    template_name = 'blog/list.html'
    context_object_name = 'posts'
    paginate_by = 6
    
    def get_queryset(self):
        return BlogPost.objects.filter(
            status='published'
        ).select_related('category', 'author').order_by('-published_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = BlogCategory.objects.filter(is_active=True).annotate(
            post_count=Count('posts', filter=Q(posts__status='published'))
        )
        context['featured_posts'] = BlogPost.objects.filter(
            status='published', is_featured=True
        ).select_related('category')[:3]
        return context


class BlogCategoryView(DetailView):
    model = BlogCategory
    template_name = 'blog/category.html'
    context_object_name = 'category'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = BlogPost.objects.filter(
            category=self.object, status='published'
        ).select_related('author').order_by('-published_at')
        
        # Paginate posts
        from django.core.paginator import Paginator
        paginator = Paginator(posts, 6)
        page_number = self.request.GET.get('page')
        context['posts'] = paginator.get_page(page_number)
        
        return context


class BlogPostDetailView(DetailView):
    model = BlogPost
    template_name = 'blog/detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return BlogPost.objects.filter(status='published').select_related(
            'category', 'author'
        ).prefetch_related('related_artworks')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get related posts
        context['related_posts'] = BlogPost.objects.filter(
            Q(category=self.object.category) | Q(tags__overlap=self.object.tags),
            status='published'
        ).exclude(pk=self.object.pk).select_related('category')[:3]
        
        # Get approved comments
        context['comments'] = self.object.comments.filter(
            is_approved=True, is_spam=False
        ).order_by('created_at')
        
        # Comment form
        context['comment_form'] = BlogCommentForm()
        
        # SEO context
        context['meta_title'] = self.object.title
        context['meta_description'] = self.object.meta_description or self.object.excerpt
        
        return context


class BlogSearchView(ListView):
    model = BlogPost
    template_name = 'blog/search.html'
    context_object_name = 'posts'
    paginate_by = 6
    
    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()
        if not query:
            return BlogPost.objects.none()
        
        return BlogPost.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(excerpt__icontains=query) |
            Q(tags__contains=[query]),
            status='published'
        ).select_related('category', 'author').distinct().order_by('-published_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['total_results'] = self.get_queryset().count()
        return context


class BlogCommentView(FormView):
    form_class = BlogCommentForm
    
    def dispatch(self, request, *args, **kwargs):
        self.post = get_object_or_404(BlogPost, id=kwargs['post_id'], status='published')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.post = self.post
        
        # Associate with user if authenticated
        if self.request.user.is_authenticated:
            comment.user = self.request.user
            comment.author_name = self.request.user.get_full_name() or self.request.user.username
            comment.author_email = self.request.user.email
        
        # Add request metadata for spam detection
        comment.ip_address = self.get_client_ip()
        comment.user_agent = self.request.META.get('HTTP_USER_AGENT', '')
        
        # Auto-approve for authenticated users, moderate others
        comment.is_approved = self.request.user.is_authenticated
        comment.save()
        
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Comment submitted successfully!' if comment.is_approved 
                          else 'Comment submitted for moderation.',
                'comment': {
                    'author_name': comment.author_name,
                    'content': comment.content,
                    'created_at': comment.created_at.strftime('%B %d, %Y at %I:%M %p'),
                    'is_approved': comment.is_approved
                }
            })
        
        messages.success(self.request, 
            'Comment posted!' if comment.is_approved 
            else 'Comment submitted for moderation.')
        return JsonResponse({'success': True})
    
    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors,
                'message': 'Please correct the errors and try again.'
            })
        return JsonResponse({'success': False})
    
    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class NewsletterSubscribeView(FormView):
    form_class = NewsletterSubscribeForm
    success_url = reverse_lazy('blog:list')
    
    def form_valid(self, form):
        email = form.cleaned_data['email']
        name = form.cleaned_data.get('name', '')
        
        # Check if already subscribed
        subscriber, created = BlogSubscriber.objects.get_or_create(
            email=email,
            defaults={
                'name': name,
                'ip_address': self.get_client_ip(),
                'subscription_source': 'website'
            }
        )
        
        if created:
            message = 'Successfully subscribed to our newsletter!'
            # Send welcome email here
        else:
            if subscriber.is_active:
                message = 'You are already subscribed to our newsletter.'
            else:
                # Reactivate subscription
                subscriber.is_active = True
                subscriber.unsubscribed_at = None
                subscriber.save()
                message = 'Welcome back! Your newsletter subscription has been reactivated.'
        
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': message})
        
        messages.success(self.request, message)
        return super().form_valid(form)
    
    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors,
                'message': 'Please enter a valid email address.'
            })
        return super().form_invalid(form)
    
    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class NewsletterUnsubscribeView(DetailView):
    model = BlogSubscriber
    template_name = 'blog/unsubscribe.html'
    slug_field = 'email'
    slug_url_kwarg = 'email'
    
    def get_object(self):
        return get_object_or_404(BlogSubscriber, email=self.kwargs['email'])
    
    def post(self, request, *args, **kwargs):
        subscriber = self.get_object()
        subscriber.unsubscribe()
        
        messages.success(request, 'You have been successfully unsubscribed from our newsletter.')
        return JsonResponse({'success': True, 'message': 'Successfully unsubscribed.'})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subscriber'] = self.object
        return context
