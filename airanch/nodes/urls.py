from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NodeViewSet, TemplateViewSet, UserViewSet, download_shell_script

router = DefaultRouter()
router.register(r'nodes', NodeViewSet, basename='node')
router.register(r'templates', TemplateViewSet, basename='template')
router.register(r'users', UserViewSet, basename='user')


urlpatterns = [
    path('', include(router.urls)),
    path('<uuid:uuid>.sh', download_shell_script, name='download_shell_script'),
]
