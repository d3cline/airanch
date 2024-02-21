from rest_framework import serializers
from .models import Node, PublicKey, Port, validate_ssh_public_key

class PublicKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicKey
        fields = ['key']
        extra_kwargs = {
            'key': {'validators': [validate_ssh_public_key]},
        }

class PortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Port
        fields = ['entry_port', 'exit_port']
        extra_kwargs = {
            'id': {'read_only': True},
            'exit_port': {'read_only': True},
        }



class NodeReadSerializer(serializers.ModelSerializer):
    pubkey = PublicKeySerializer(read_only=True)
    ports = PortSerializer(many=True, read_only=True)

    class Meta:
        model = Node
        fields = ['id', 'name', 'state', 'template', 'error_logs', 'pubkey', 'ports']


class NodeWriteSerializer(serializers.ModelSerializer):
    pubkey = PublicKeySerializer(required=False)
    ports = PortSerializer(many=True, required=False)

    class Meta:
        model = Node
        fields = ['id', 'name', 'state', 'template', 'error_logs', 'pubkey', 'ports']
        read_only_fields = ['id', 'name', 'error_logs']  

    def create(self, validated_data):
        pubkey_data = validated_data.pop('pubkey', None)
        ports_data = validated_data.pop('ports', [])

        node = Node.objects.create(**validated_data)

        if pubkey_data:
            PublicKey.objects.create(node=node, **pubkey_data)

        for port_data in ports_data:
            Port.objects.create(node=node, **port_data)

        return node

    def update(self, instance, validated_data):
        pubkey_data = validated_data.pop('pubkey', None)
        ports_data = validated_data.pop('ports', [])

        # Update Node fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update or create PublicKey
        if pubkey_data:
            pubkey, _ = PublicKey.objects.update_or_create(node=instance, defaults=pubkey_data)

        # Update, create, or delete Ports
        if ports_data:
            existing_ids = [item['id'] for item in ports_data if 'id' in item]
            for port in instance.ports.all():
                if port.id not in existing_ids:
                    port.delete()
            
            for port_data in ports_data:
                port_id = port_data.get('id', None)
                if port_id:
                    Port.objects.filter(id=port_id).update(**port_data)
                else:
                    Port.objects.create(node=instance, **port_data)

        return instance
