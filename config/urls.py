from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from users.views import HomeView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='root-home'),
    path('users/', include('users.urls')),
    path('incidents/', include('incidents.urls')),
    path('reports/', include('reports.urls')),
    path('notifications/', include('notifications.urls')),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)