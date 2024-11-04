from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('base.urls.user_urls')),
    path('api/v1/', include('base.urls.api_urls')),
    path('', RedirectView.as_view(url='https://mrphilip.pythonanywhere.com/portfolio/reup', permanent=False)),  # Redirect root URL to external website
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
