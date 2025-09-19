from django.http import HttpResponse
from django.urls import path

def test_view(request):
    return HttpResponse("Minimal Django server is working!")

urlpatterns = [
    path('', test_view, name='test'),
]