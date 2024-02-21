from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/', include('nodes.urls')),
    path('', TemplateView.as_view(template_name="index.html"), name='index'),

]
