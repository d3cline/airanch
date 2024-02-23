from rest_framework import serializers
from .models import Node, PublicKey, Template, Port
from rest_framework.fields import ListField, IntegerField
from django.contrib.auth.models import User

class NodeWriteSerializer(serializers.ModelSerializer):
    ports = ListField(child=IntegerField(), required=False, write_only=True)

    class Meta:
        model = Node
        fields = ['name', 'owner', 'template', 'ports']

    def create(self, validated_data):
        ports_data = validated_data.pop('ports', [])
        node = Node.objects.create(**validated_data)
        for port in ports_data:
            Port.objects.create(node=node, entry_port=port)
        return node

class NodeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Node
        fields = ['pubkey', 'owner', 'template']

class NodeReadSerializer(serializers.ModelSerializer):
    ports = serializers.SerializerMethodField() 

    class Meta:
        model = Node
        exclude = ['password', 'os_user_id', 'site_route_id', 'node_domain_id', 'error_logs', 'owner']

    def get_ports(self, obj):
        ports_list = obj.ports.all()
        return [{'entry_port': port.entry_port, 'exit_port': port.exit_port} for port in ports_list]

class AdminNodeReadSerializer(serializers.ModelSerializer):
    ports = serializers.SerializerMethodField()  
    pubkey = serializers.SerializerMethodField()

    class Meta:
        model = Node
        exclude = ['password', 'os_user_id', 'site_route_id', 'node_domain_id']

    def get_pubkey(self, obj):
        return getattr(obj, 'pubkey', None) is not None

    def get_ports(self, obj):
        ports_list = obj.ports.all()
        return [{'entry_port': port.entry_port, 'exit_port': port.exit_port} for port in ports_list]


class TemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        fields = ['id', 'name']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']
