from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/',include('users.urls.user_urls' ,namespace="users") ),
    path('',include('users.urls.activity_urls' ,namespace="activity") ),
    path('accounts/', include('allauth.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL , document_root=  settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL , document_root=  settings.MEDIA_ROOT)
    urlpatterns += path('__debug__/', include('debug_toolbar.urls')),