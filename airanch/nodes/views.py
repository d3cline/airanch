from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Node, Template
from .permissions import IsOwnerOrReadOnly, IsOwnerOrAdmin
from .serializers import NodeReadSerializer, NodeWriteSerializer, NodeUpdateSerializer, AdminNodeReadSerializer, TemplateSerializer, UserSerializer, RegisterSerializer

from django.contrib.auth.models import User
from rest_framework import viewsets, permissions, status
from .serializers import UserSerializer

from django.http import HttpResponse
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['POST'])
def register_user(request):
    if request.method == 'POST':
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def download_shell_script(request, uuid):
    # Fetch the Node object by UUID
    node = get_object_or_404(Node, pk=uuid)
    
    # Render the shell script template with context
    script_content = render_to_string('tunnel.sh.jinja', {
        'node': node
        })
    
    # Create an HTTP response with the rendered script as content
    # and appropriate content type for a shell script
    response = HttpResponse(script_content, content_type='text/plain')
    # Suggest a filename for the browser to download
    response['Content-Disposition'] = f'attachment; filename="{uuid}.sh"'
    
    return response

class NodeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwnerOrAdmin, IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            if self.request.user.is_staff:
                return AdminNodeReadSerializer
            return NodeReadSerializer
        elif self.action in ['update', 'partial_update']:
            return NodeUpdateSerializer
        else:
            return NodeWriteSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Node.objects.all()
        return Node.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class TemplateViewSet(viewsets.ModelViewSet):
    queryset = Template.objects.all()
    serializer_class = TemplateSerializer
    permission_classes = [IsOwnerOrAdmin]

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return User.objects.all()
        return User.objects.none()
