from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/', include('nodes.urls')),
    path('', TemplateView.as_view(template_name="index.html"), name='index'),

]  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)