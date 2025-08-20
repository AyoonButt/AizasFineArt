from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone


class BlogCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Blog Categories"
        ordering = ['display_order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('blog:category', kwargs={'slug': self.slug})


class BlogPost(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(BlogCategory, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    
    # Content
    excerpt = models.TextField(max_length=300, help_text="Brief description for listings and SEO")
    content = models.TextField()
    
    # Featured image - Supabase URL
    featured_image_url = models.URLField(blank=True, help_text="Supabase storage URL for featured image")
    featured_image_alt = models.CharField(max_length=125, blank=True)
    featured_image_caption = models.CharField(max_length=200, blank=True)
    
    # Gallery images for process/tutorial posts
    gallery_images = models.JSONField(default=list, blank=True, help_text="Array of additional image URLs")
    
    # SEO and metadata
    meta_description = models.CharField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=200, blank=True)
    
    # Publishing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    allow_comments = models.BooleanField(default=True)
    
    # Related content
    related_artworks = models.ManyToManyField('artwork.Artwork', blank=True, related_name='blog_posts')
    tags = models.JSONField(default=list, blank=True, help_text="Array of tag strings")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-published_at', '-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Ensure slug uniqueness
        if BlogPost.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
            self.slug = f"{self.slug}-{self.pk or 'new'}"
        
        # Set published_at when status changes to published
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})

    @property
    def reading_time(self):
        """Estimate reading time in minutes"""
        word_count = len(self.content.split())
        return max(1, round(word_count / 200))  # Average 200 words per minute

    @property
    def is_published(self):
        return self.status == 'published' and self.published_at

    def get_next_post(self):
        """Get next published post"""
        return BlogPost.objects.filter(
            status='published',
            published_at__gt=self.published_at
        ).order_by('published_at').first()

    def get_previous_post(self):
        """Get previous published post"""
        return BlogPost.objects.filter(
            status='published',
            published_at__lt=self.published_at
        ).order_by('-published_at').first()


class BlogComment(models.Model):
    """Comments on blog posts"""
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    author_name = models.CharField(max_length=100)
    author_email = models.EmailField()
    author_website = models.URLField(blank=True)
    
    content = models.TextField()
    
    # Moderation
    is_approved = models.BooleanField(default=False)
    is_spam = models.BooleanField(default=False)
    
    # Optional user association
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Request metadata for spam detection
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author_name} on {self.post.title}"

    def approve(self):
        """Approve the comment"""
        self.is_approved = True
        self.approved_at = timezone.now()
        self.save(update_fields=['is_approved', 'approved_at'])


class BlogSubscriber(models.Model):
    """Email subscribers for blog updates"""
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True)
    
    # Subscription preferences
    is_active = models.BooleanField(default=True)
    subscribe_new_posts = models.BooleanField(default=True)
    subscribe_featured_posts = models.BooleanField(default=True)
    
    # Categories they're interested in
    categories = models.ManyToManyField(BlogCategory, blank=True)
    
    # Metadata
    subscription_source = models.CharField(max_length=100, blank=True, help_text="How they subscribed")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.email} - {'Active' if self.is_active else 'Inactive'}"

    def unsubscribe(self):
        """Unsubscribe the user"""
        self.is_active = False
        self.unsubscribed_at = timezone.now()
        self.save(update_fields=['is_active', 'unsubscribed_at'])


class NewsletterCampaign(models.Model):
    """Newsletter campaigns for blog content"""
    CAMPAIGN_STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('sending', 'Sending'),
        ('sent', 'Sent'),
        ('cancelled', 'Cancelled'),
    ]

    title = models.CharField(max_length=200)
    subject_line = models.CharField(max_length=200)
    
    # Content
    featured_posts = models.ManyToManyField(BlogPost, related_name='newsletter_campaigns')
    custom_content = models.TextField(blank=True, help_text="Additional custom content")
    
    # Targeting
    send_to_all = models.BooleanField(default=True)
    target_categories = models.ManyToManyField(BlogCategory, blank=True)
    
    # Scheduling
    status = models.CharField(max_length=20, choices=CAMPAIGN_STATUS_CHOICES, default='draft')
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    # Statistics
    total_recipients = models.PositiveIntegerField(default=0)
    total_sent = models.PositiveIntegerField(default=0)
    total_opened = models.PositiveIntegerField(default=0)
    total_clicked = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"

    @property
    def open_rate(self):
        """Calculate email open rate"""
        if self.total_sent > 0:
            return round((self.total_opened / self.total_sent) * 100, 2)
        return 0

    @property
    def click_rate(self):
        """Calculate email click rate"""
        if self.total_sent > 0:
            return round((self.total_clicked / self.total_sent) * 100, 2)
        return 0
