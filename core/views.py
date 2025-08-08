from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse, HttpResponse
from .models import Contact
from .mongodb import connect_to_mongodb, disconnect_from_mongodb
import logging
import os
from django.conf import settings
from django.views import View
from django.views.generic import TemplateView
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import time

logger = logging.getLogger(__name__)

# Create your views here.

def home(request):
    return render(request, 'core/home.html')

def about(request):
    return render(request, 'core/about.html')

def contact(request):
    if request.method == 'POST':
        try:
            # Connect to MongoDB
            db = connect_to_mongodb()
            
            name = request.POST.get('name')
            email = request.POST.get('email')
            subject = request.POST.get('subject')
            message = request.POST.get('message')

            # Create new contact entry
            contact_data = {
                'name': name,
                'email': email,
                'subject': subject,
                'message': message,
                'created_at': datetime.utcnow()
            }
            
            # Insert into contacts collection
            db.contacts.insert_one(contact_data)

            # Disconnect from MongoDB
            disconnect_from_mongodb(db.client)

            return JsonResponse({
                'success': True,
                'message': 'Message sent successfully!'
            })
        except Exception as e:
            logger.error(f"Error in contact form submission: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
        finally:
            # Ensure we disconnect from MongoDB even if there's an error
            try:
                if 'db' in locals():
                    disconnect_from_mongodb(db.client)
            except:
                pass
    
    return render(request, 'core/contact.html')

def projects(request):
    return render(request, 'core/projects.html')

def blog(request):
    return render(request, 'core/blog.html')

def resume(request):
    return render(request, 'core/resume.html')

class VideoStreamView(View):
    def get(self, request, video_name):
        try:
            video_path = os.path.join(settings.STATIC_ROOT, 'videos', video_name)
            
            if not os.path.exists(video_path):
                logger.error(f"Video file not found: {video_path}")
                return HttpResponse(status=404)
            
            file_size = os.path.getsize(video_path)
            
            # Set a smaller chunk size for better streaming
            chunk_size = min(1024 * 1024, file_size)  # 1MB or file size, whichever is smaller
            
            range_header = request.META.get('HTTP_RANGE', '').strip()
            range_match = re.match(r'bytes=(\d+)-(\d*)', range_header)
            
            if range_match:
                first_byte, last_byte = range_match.groups()
                first_byte = int(first_byte)
                last_byte = int(last_byte) if last_byte else file_size - 1
                
                if last_byte >= file_size:
                    last_byte = file_size - 1
                
                length = last_byte - first_byte + 1
                
                response = StreamingHttpResponse(
                    self.file_iterator(video_path, first_byte, last_byte, chunk_size),
                    status=206,
                    content_type='video/mp4'
                )
                
                response['Content-Length'] = length
                response['Content-Range'] = f'bytes {first_byte}-{last_byte}/{file_size}'
                response['Accept-Ranges'] = 'bytes'
                response['Cache-Control'] = 'public, max-age=31536000'  # Cache for 1 year
                return response
            
            response = StreamingHttpResponse(
                self.file_iterator(video_path, chunk_size=chunk_size),
                content_type='video/mp4'
            )
            response['Content-Length'] = file_size
            response['Accept-Ranges'] = 'bytes'
            response['Cache-Control'] = 'public, max-age=31536000'  # Cache for 1 year
            return response
            
        except ConnectionAbortedError:
            logger.warning(f"Connection aborted while streaming video {video_name}")
            return HttpResponse(status=499)  # Client Closed Request
        except Exception as e:
            logger.error(f"Error streaming video {video_name}: {str(e)}")
            return HttpResponse(status=500)
    
    def file_iterator(self, file_path, start_byte=None, end_byte=None, chunk_size=None):
        if chunk_size is None:
            chunk_size = settings.VIDEO_CHUNK_SIZE
        
        try:
            with open(file_path, 'rb') as f:
                if start_byte is not None:
                    f.seek(start_byte)
                
                remaining = end_byte - start_byte + 1 if end_byte is not None else None
                
                while True:
                    if remaining is not None and remaining <= 0:
                        break
                    
                    try:
                        # Read smaller chunks for better streaming
                        read_size = min(chunk_size, remaining) if remaining is not None else chunk_size
                        chunk = f.read(read_size)
                        
                        if not chunk:
                            break
                        
                        if remaining is not None:
                            remaining -= len(chunk)
                        
                        yield chunk
                        
                        # Add a small delay to prevent overwhelming the connection
                        time.sleep(0.01)
                        
                    except ConnectionAbortedError:
                        logger.warning("Connection aborted during chunk reading")
                        break
                    except Exception as e:
                        logger.error(f"Error reading chunk: {str(e)}")
                        break
                        
        except Exception as e:
            logger.error(f"Error in file_iterator: {str(e)}")
            raise

class ProjectsView(TemplateView):
    template_name = 'core/projects.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any additional context data here
        return context

class BlogPostView(View):
    def get(self, request):
        try:
            page = int(request.GET.get('page', 1))
            per_page = int(request.GET.get('per_page', 6))
            
            # Your Medium blog URLs
            blog_urls = [
                'https://medium.com/@saadabid21g/how-to-use-proxies-in-scrapy-for-web-scraping-315a89db2988',
                'https://medium.com/@saadabid21g/integrating-playwright-into-scrapy-for-dynamic-scraping-1fb929cc5b36',
                'https://medium.com/@saadabid21g/how-to-use-proxies-in-google-colab-step-by-step-tutorial-0fd3653c53f8',
                'https://medium.com/@saadabid21g/master-web-scraping-with-scrapingbee-proxy-api-1d962190f111',
                'https://medium.com/@saadabid21g/a-beginners-guide-to-proxy-ips-for-scraping-4857c95034c7',
                'https://medium.com/@saadabid21g/difference-between-web-scrapping-api-and-proxy-api-6be0fa4f5292',
                'https://medium.com/@saadabid21g/mastering-bardeen-a-guide-to-no-code-web-scraping-c1787add99fc',
                'https://medium.com/@saadabid21g/git-bash-basics-your-first-steps-debdfbe17966',
                'https://medium.com/@saadabid21g/no-code-data-scraping-tools-bardeen-and-relevance-ai-683a980fc91d'
            ]
            
            posts = []
            for url in blog_urls[(page-1)*per_page:page*per_page]:
                try:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    }
                    response = requests.get(url, headers=headers)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract title
                    title = soup.find('h1')
                    if not title:
                        title = soup.find('meta', property='og:title')
                        title = title['content'] if title else 'Untitled'
                    else:
                        title = title.text.strip()
                    
                    # Extract date
                    date = soup.find('time')
                    if not date:
                        date = soup.find('meta', property='article:published_time')
                        date = date['content'] if date else ''
                    else:
                        date = date.text.strip()
                    
                    # Extract image
                    image = soup.find('meta', property='og:image')
                    image = image['content'] if image else '/static/default-blog.jpg'
                    
                    # Extract excerpt
                    excerpt = soup.find('meta', property='og:description')
                    excerpt = excerpt['content'] if excerpt else ''
                    
                    # Extract category/tags
                    category = 'Web Scraping'  # Default category
                    tags = soup.find_all('a', class_='pw-tag')
                    if tags:
                        category = tags[0].text.strip()
                    
                    # Extract content
                    content_div = soup.find('article')
                    content = ''
                    if content_div:
                        paragraphs = content_div.find_all('p')
                        content = ' '.join([p.text.strip() for p in paragraphs[:3]])  # First 3 paragraphs
                    
                    post = {
                        'title': title,
                        'date': date,
                        'category': category,
                        'excerpt': excerpt,
                        'content': content,
                        'image': image,
                        'url': url
                    }
                    posts.append(post)
                except Exception as e:
                    logger.error(f"Error fetching blog post from {url}: {str(e)}")
                    continue
            
            return JsonResponse({
                'posts': posts,
                'has_more': len(blog_urls) > page * per_page
            })
            
        except Exception as e:
            logger.error(f"Error in blog post view: {str(e)}")
            return JsonResponse({
                'error': 'Error fetching blog posts'
            }, status=500)
