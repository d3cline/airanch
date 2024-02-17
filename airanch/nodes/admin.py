from django.contrib import admin
from .models import Node, DEFAULT_ENTRY_PORTS

class NodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'application_type', 'entry_port', 'exit_port', 'state')
    search_fields = ('name', 'application_type')
    list_filter = ('application_type', 'state')

    def get_readonly_fields(self, request, obj=None):
        # If the object exists, make state field readonly unless it's in PENDING state.
        if obj and obj.state != 'PENDING':
            return ('id', 'entry_port', 'state')
        # For new objects, hide the state field as it's assumed to be PENDING.
        return ('id', 'entry_port') if obj and obj.application_type != 'custom' else ('id',)

    def get_form(self, request, obj=None, **kwargs):
        form = super(NodeAdmin, self).get_form(request, obj, **kwargs)
        # Dynamically adjust the entry_port field properties based on application_type
        if obj and obj.application_type == 'custom':
            form.base_fields['entry_port'].required = True
        # Exclude the state field for new objects (when obj is None)
        if obj is None:
            form.base_fields.pop('state', None)
        return form

    def save_model(self, request, obj, form, change):
        # Automatically set the entry_port for new objects based on DEFAULT_ENTRY_PORTS
        if not change and obj.application_type != 'custom':
            obj.entry_port = DEFAULT_ENTRY_PORTS.get(obj.application_type)
        # Set the node to PENDING state upon creation if not already set
        if not change and not hasattr(obj, 'state'):
            obj.state = 'PENDING'
        super(NodeAdmin, self).save_model(request, obj, form, change)

admin.site.register(Node, NodeAdmin)
