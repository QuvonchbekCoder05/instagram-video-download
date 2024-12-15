import os
import instaloader
import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from urllib.parse import urlparse
from environs import Env  # Environ kutubxonasini import qilish

env = Env()
env.read_env()  # .env faylidan muhit o'zgaruvchilarini yuklash

def home(request):
    return render(request, 'accounts/home.html')

def get_video_info(url):
    try:
        # Instagram login va parolini .env faylidan yuklash
        username = env('INSTAGRAM_USERNAME')
        password = env('INSTAGRAM_PASSWORD')
        
        
        print(f"Instagram Username: {username}, Instagram Password: {password}")

        # Instaloader yordamida hisobga kirish
        L = instaloader.Instaloader()
        L.login(username, password)

        # URL ichidan 'shortcode' ni ajratamiz
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.strip('/').split('/')
        if len(path_parts) < 2:
            return {'success': False, 'error': 'Noto‘g‘ri URL format'}
        
        

        shortcode = path_parts[1]

        # Instaloader yordamida post ma'lumotlarini olish
        post = instaloader.Post.from_shortcode(L.context, shortcode)

        # Video mavjudligini tekshirish
        if not post.is_video:
            return {'success': False, 'error': 'Bu postda video mavjud emas'}

        # Video ma'lumotlarini qaytarish
        return {
    'success': True,
    'video_url': post.video_url,
    'thumbnail': post.url,  # 'thumbnail_url' o'rniga 'url' ishlating
    'caption': post.caption,
    'likes': post.likes,
    'comments': post.comments,
    'date': post.date,
}

    except Exception as e:
        # Xatolar uchun javob
        return {'success': False, 'error': str(e)}

def preview_video(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        if not url:
            return JsonResponse({'success': False, 'error': 'URL kiritilmadi'})

        # URL orqali video ma'lumotlarini olish
        video_info = get_video_info(url)
        if video_info['success']:
            return JsonResponse(video_info)
        return JsonResponse({'success': False, 'error': video_info['error']})

def download_video(request):
    if request.method == 'POST':
        url = request.POST.get('video_url')
        if not url:
            return JsonResponse({'success': False, 'error': 'Video URL topilmadi'})

        try:
            response = requests.get(url)
            if response.status_code == 200:
                filename = f"instagram_video_{os.urandom(8).hex()}.mp4"
                filepath = os.path.join(settings.MEDIA_ROOT, filename)

                # Video faylini saqlash
                os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
                with open(filepath, 'wb') as f:
                    f.write(response.content)

                # Yuklab olish URLini qaytarish
                return JsonResponse({
                    'success': True,
                    'download_url': f"{settings.MEDIA_URL}{filename}"
                })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Noto‘g‘ri so‘rov'})
