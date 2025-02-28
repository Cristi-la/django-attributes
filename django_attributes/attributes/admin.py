from django.contrib import admin
from django.urls import path, reverse
from django.utils.html import format_html
from .models import AttrConfiguration, AttrValue
from .forms import AttrConfigurationForm, AttrConfigurationValuesForm, AttrValueForm

class AttrValueInline(admin.TabularInline):
    model = AttrValue
    extra = 0
    fields = ('order', 'value', 'updated')
    readonly_fields = ('order', 'updated')
    ordering = ('order',)
    show_change_link = True
    can_delete = False
    max_num = 0

    form = AttrValueForm
    queryset = AttrValue.objects.select_related('key').order_by('key__key', '-order')

@admin.register(AttrConfiguration)
class AttrConfigurationAdmin(admin.ModelAdmin):
    form = AttrConfigurationForm
    values_form = AttrConfigurationValuesForm

    list_display = ('key', 'description', 'field_type', 'count_link', 'return_type')
    search_fields = ('key', 'description', 'field_type')
    ordering = ('key',)

    inlines = []

    fieldsets = (
        (None, {
            'fields': ('key', 'description', 'field_type')
        }),
        ('Count', {
            'fields': ('count', 'return_type'),
            'description': "Options related to the number of values for this attribute configuration.",
        }),
        ('Arguments', {
            'classes': ('collapse',),
            'fields': ('args', 'kwargs')
        }),
    )
    values_fieldsets = ()

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/values/',
                self.admin_site.admin_view(self.values_view),
                name='attributes_attrconfiguration_values',
            ),
        ]
        return custom_urls + urls

    def count_link(self, obj):
        url = reverse('admin:attributes_attrconfiguration_values', args=[obj.pk])
        return format_html('<a href="{}">{}</a>', url, obj.count)
    count_link.short_description = "Count"


    def get_fieldsets(self, request, obj=None):
        if 'values' in request.path:
            return self.values_fieldsets
        return super().get_fieldsets(request, obj)
    
    def get_inline_instances(self, request, obj=None):
        if 'values' in request.path:
            return [AttrValueInline(self.model, self.admin_site)]
        return super().get_inline_instances(request, obj)
    
    def get_form(self, request, obj = ..., change = ..., **kwargs):
        if 'values' in request.path:
            return self.values_form
        return super().get_form(request, obj, change, **kwargs)
    
    def values_view(self, request, object_id):
        return self.change_view(request, object_id)

@admin.register(AttrValue)
class AttrValueAdmin(admin.ModelAdmin):
    form = AttrValueForm
    queryset = AttrValue.objects.select_related('key').order_by('key__key', '-order')

    list_display = ('key', 'value', 'order', 'updated')
    search_fields = ('key__key', 'value')
    ordering = ('key',)

    fieldsets = (
        (None, {
            'fields': ('key', 'value')
        }),
        ('Meta data', {
            'classes': ('collapse',),
            'fields': ('order', 'updated')
        }),
    )

    readonly_fields = ('key', 'order', 'updated')