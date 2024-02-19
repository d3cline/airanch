from django.contrib import admin
from .models import Node, Port

class PortInline(admin.TabularInline):
    model = Port
    extra = 1  # Specifies the number of blank forms the formset initially displays.

class NodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'state')
    search_fields = ['name']
    list_filter = ['state']
    inlines = [PortInline]  # Add the inline here

    def get_readonly_fields(self, request, obj=None):
        # If the object exists, make state field readonly unless it's in PENDING state.
        if obj and obj.state != 'PENDING':
            return ('id', 'state')
        # For new objects, make the id field readonly.
        return ('id',)

    def get_form(self, request, obj=None, **kwargs):
        form = super(NodeAdmin, self).get_form(request, obj, **kwargs)
        # For new objects, exclude the state field (when obj is None)
        if obj is None:
            form.base_fields.pop('state', None)
        return form

    def save_model(self, request, obj, form, change):
        # Set the node to PENDING state upon creation if not already set
        if not change and not hasattr(obj, 'state'):
            obj.state = 'PENDING'
        super(NodeAdmin, self).save_model(request, obj, form, change)

admin.site.register(Node, NodeAdmin)
