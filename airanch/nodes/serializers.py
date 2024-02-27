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
    pubkey = serializers.CharField(source='pubkey.key')

    class Meta:
        model = Node
        fields = ['pubkey', 'owner', 'access_token', 'template']

    def update(self, instance, validated_data):
        pubkey_data = validated_data.pop('pubkey', None)

        # Update the PublicKey instance if 'pubkey' field is provided in the request
        if pubkey_data and 'key' in pubkey_data:
            key = pubkey_data['key']
            # Check if the instance already has a related PublicKey
            if hasattr(instance, 'pubkey'):
                # Update the existing PublicKey
                pubkey = instance.pubkey
                pubkey.key = key
                pubkey.save()
            else:
                # Create a new PublicKey and associate it with the Node instance
                PublicKey.objects.create(node=instance, key=key)

        # Update other fields of the Node instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

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
        if hasattr(obj, 'pubkey') and obj.pubkey is not None:
            # Assuming 'key' is the attribute of the PublicKey model that stores the actual public key string
            return obj.pubkey.key
        return None


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

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')