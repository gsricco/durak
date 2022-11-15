"""configs URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

admin.site.site_header = "Администрирование Durak Roll"
admin.site.site_title = "Администрирование Durak Roll"
admin.site.index_title = ""

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ws_chat/', include('ws_chat.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),  # редактор текста в админке
    path('', include('content_manager.urls')),  # управление контентом на сайте
    path('', include('django.contrib.auth.urls')),  # выход из личного кабинета
    path('', include('social_django.urls', namespace='social')),  # авторизация через соц сети
    # path('api/v1/', include('support_chat.urls', namespace='support_chat')),  # чат поддержки    - улетел в api_router

    path('', include('api_router.swagger.urls')),
    path('', include('api_router.routers.V1.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
