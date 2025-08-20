from django.shortcuts import render, get_object_or_404
from django.views.generic import DetailView, ListView
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Artwork, Category, Tag
from .serializers import ArtworkSerializer, CategorySerializer, TagSerializer


class ArtworkDetailView(DetailView):
    model = Artwork
    template_name = 'artwork/detail.html'
    context_object_name = 'artwork'
    
    def get_queryset(self):
        return Artwork.objects.filter(is_available=True)


class CategoryView(ListView):
    model = Artwork
    template_name = 'artwork/category.html'
    context_object_name = 'artworks'
    paginate_by = 20
    
    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Artwork.objects.filter(category=self.category, is_available=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


# API ViewSets
class ArtworkViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Artwork.objects.filter(is_available=True)
    serializer_class = ArtworkSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'medium']
    ordering_fields = ['created_at', 'price', 'title']
    ordering = ['-created_at']


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Catego
    ry.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]