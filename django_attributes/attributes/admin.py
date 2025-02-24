from django.contrib import admin
from attributes.models import AttrConfiguration, AttrValue
from attributes.forms import AttrConfigurationForm, AttrValueForm

@admin.register(AttrConfiguration)
class AttrConfigurationAdmin(admin.ModelAdmin):
    form = AttrConfigurationForm
    list_display = ('key', 'description', 'field_type', 'count')
    search_fields = ('key', 'description', 'field_type')
    ordering = ('key',)
    


@admin.register(AttrValue)
class AttrValueAdmin(admin.ModelAdmin):
    form = AttrValueForm
    list_display = ('key', 'value')
    search_fields = ('key__key', 'value')
    ordering = ('key',)

    readonly_fields = ('key',)