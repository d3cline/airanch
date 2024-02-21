from django.contrib import admin
from django.utils.html import format_html
from .models import PublicKey, Node, Port

@admin.register(PublicKey)
class PublicKeyAdmin(admin.ModelAdmin):
    list_display = ('key_shortened', 'associated_node')
    search_fields = ('key',)

    def key_shortened(self, obj):
        return format_html("<code>{}</code>", obj.key[:50] + "...") if obj.key else "N/A"
    key_shortened.short_description = "Public Key (Shortened)"

    def associated_node(self, obj):
        return obj.publickey.name if hasattr(obj, 'publickey') else 'No associated node'
    associated_node.short_description = "Associated Node"

class PortInline(admin.TabularInline):
    model = Port
    extra = 1
    min_num = 1

@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'state', 'os_user_id', 'site_route_id', 'node_domain_id', 'pubkey_link')
    search_fields = ('name', 'state', 'os_user_id', 'site_route_id', 'node_domain_id')
    list_filter = ('state',)
    inlines = [PortInline]

    def pubkey_link(self, obj):
        return format_html("<a href='/admin/yourapp/publickey/{}/change/'>View PublicKey</a>", obj.pubkey.id) if obj.pubkey else "No Public Key"
    pubkey_link.short_description = "Public Key"

@admin.register(Port)
class PortAdmin(admin.ModelAdmin):
    list_display = ('node', 'entry_port', 'exit_port', 'port_app_id')
    list_filter = ('node',)
    search_fields = ('entry_port', 'exit_port', 'node__name')

# Note: Replace 'yourapp' in the pubkey_link method with the actual app name of your Django project.
