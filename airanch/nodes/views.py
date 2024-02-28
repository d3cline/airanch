from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Node, Template, Port
from .permissions import IsOwnerOrReadOnly, IsOwnerOrAdmin
from .serializers import NodeReadSerializer, NodeWriteSerializer, NodeUpdateSerializer, AdminNodeReadSerializer, TemplateSerializer, UserSerializer, RegisterSerializer

from django.contrib.auth.models import User
from rest_framework import viewsets, permissions, status
from .serializers import UserSerializer

from django.http import HttpResponse, HttpResponseServerError
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response

import requests
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import jinja2

@login_required
@csrf_exempt
def proxy_to_service(request, uuid, port, path=''):
    try:
        node = get_object_or_404(Node, pk=uuid)
        if node.owner != request.user: return HttpResponseServerError("403 Forbidden.", status=403)
        port = get_object_or_404(Port, node=node, entry_port=port)
        # Construct the service URL dynamically based on the port
        service_url = f'http://127.0.0.1:{port.exit_port}{path}'
        print(service_url)

        # Forward the request to the service
        resp = requests.request(
            method=request.method,
            url=service_url,
            headers={key: value for (key, value) in request.headers.items() if key != 'Host'},
            data=request.body,
            allow_redirects=False)

        # Return the response from the service to the client
        response = HttpResponse(
            content=resp.content,
            status=resp.status_code,
            content_type=resp.headers.get('Content-Type', 'application/octet-stream')
        )

        # Copy relevant headers from the service response
        for header in ['Content-Disposition', 'Content-Length']:
            if header in resp.headers:
                response[header] = resp.headers[header]

        return response
    except requests.exceptions.RequestException as e:
        # Log the error here if you want
        # For example: logger.error(f"Service unavailable: {e}")
        return HttpResponseServerError("Service is currently unavailable.", status=503)

@login_required
def render_template(request, uuid):
    node = get_object_or_404(Node, pk=uuid)
    if node.owner != request.user: return HttpResponseServerError("403 Forbidden.", status=403)
    template = jinja2.Template(node.template.html)
    rendered_content = template.render({'node':node})
    return HttpResponse(rendered_content)

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
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:  # For create, update, delete
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return User.objects.all()
        return User.objects.none()
