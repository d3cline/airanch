from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Node
from .serializers import NodeReadSerializer, NodeWriteSerializer
from .permissions import IsOwnerOrReadOnly  

class NodeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwnerOrReadOnly, IsAuthenticated] 

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return NodeReadSerializer
        else:
            return NodeWriteSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            if user.is_staff or user.is_superuser:
                # If the user is an admin, return all nodes
                return Node.objects.all()
            else:
                # If the user is not an admin, filter nodes by the owner
                return Node.objects.filter(owner=user)
        else:
            # This line is technically redundant due to the IsAuthenticated permission,
            # but is useful if you decide to change permissions later.
            return Node.objects.none()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
