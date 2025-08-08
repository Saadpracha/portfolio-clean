from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('projects/', views.ProjectsView.as_view(), name='projects'),
    path('blog/', views.blog, name='blog'),
    path('resume/', views.resume, name='resume'),
    path('video/<str:video_name>/', views.VideoStreamView.as_view(), name='video_stream'),
    path('api/blog-posts/', views.BlogPostView.as_view(), name='blog_posts'),
] 