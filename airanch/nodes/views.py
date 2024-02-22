from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Node
from .permissions import IsOwnerOrReadOnly
from .serializers import NodeReadSerializer, NodeWriteSerializer, NodeUpdateSerializer, AdminNodeReadSerializer

class NodeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwnerOrReadOnly, IsAuthenticated]

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
