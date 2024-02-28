from django.contrib import admin
from .models import Node, Port, PublicKey, Template

class PublicKeyInline(admin.StackedInline):
    model = PublicKey
    can_delete = False
    verbose_name_plural = 'Public Keys'
    fk_name = 'node'
    extra = 0 

class PortInline(admin.TabularInline):
    model = Port
    extra = 1 
    min_num = 1 

class TemplateInline(admin.StackedInline):
    model = Template
    extra = 0  
    min_num = 1  
    max_num = 1  

@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'state', 'os_user_id')
    search_fields = ('name', 'state', 'os_user_id')
    readonly_fields = ['state', 'os_user_id', 'error_logs', 'password']
    list_filter = ('state',)
    inlines = [PublicKeyInline, PortInline] 


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'html')
    search_fields = ('name',)

@admin.register(PublicKey)
class PublicKeyAdmin(admin.ModelAdmin):
    list_display = ('key', 'node')
    search_fields = ('node',)