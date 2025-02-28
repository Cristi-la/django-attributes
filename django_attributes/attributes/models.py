from django.db import models
from django.core.validators import validate_slug
from django.core.validators import MinValueValidator
from attributes.utils import set_attribute, set_many_attributes
import itertools

class ReturnTypes(models.TextChoices):
    LIST = 'list', 'List'
    DICT = 'dict', 'Dictionary'
    SET = 'set', 'Set'

    FIRST = 'first', 'First'
    LAST = 'last', 'Last'


class AttrConfiguration(models.Model):
    key = models.CharField(
        max_length=100,
        unique=True,
        validators=[validate_slug],
        help_text="A unique identifier for the attribute."
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="A description of this attribute configuration."
    )
    field_type = models.CharField(
        max_length=255,
        default='django.forms.CharField',
        help_text="Dotted path to the Django form field class (e.g., 'django.forms.CharField')."
    )

    count = models.PositiveIntegerField(
        default=1,
        help_text="The number of values for this attribute configuration.",
        validators=[MinValueValidator(1)],
    )

    return_type = models.CharField(
        max_length=10,
        choices=ReturnTypes.choices,
        default=ReturnTypes.FIRST,
        help_text="How to return attribute values in cache."
    )

    args = models.JSONField(
        default=list,
        blank=True,
        help_text="A JSON array of positional arguments to pass to the field constructor."
    )
    kwargs = models.JSONField(
        default=dict,
        blank=True,
        help_text="A JSON object of keyword arguments to pass to the field constructor."
    )

    def __str__(self):
        return self.key


class AttrValue(models.Model):
    key = models.ForeignKey(
        AttrConfiguration,
        on_delete=models.CASCADE,
        related_name='values',
        help_text="The attribute configuration."
    )
    value = models.TextField(
        blank=True,
        null=True,
        help_text="The value of the attribute."
    )
    order = models.PositiveIntegerField(
        default=0,
        editable=False,
        help_text="Determines the order of the values."
    )
    updated = models.DateTimeField(
        auto_now=True,
        help_text="The last time this value was updated."
    )

    def __str__(self):
        return f'{self.key}: {self.value}'
    
    @staticmethod
    def pack_values(group_list: dict, return_type: str = ReturnTypes.FIRST):
        values_list = [row[3] for row in group_list]

        if return_type == ReturnTypes.LIST:
            return group_list
        
        if return_type == ReturnTypes.LAST:
            return values_list[-1] if values_list else None
        
        if return_type == ReturnTypes.DICT:
            return {row[2]: row[3] for row in group_list}
        
        if return_type == ReturnTypes.SET:
            return set(values_list)
        
        return values_list[0] if values_list else None
        
    
    @classmethod
    def load_attribute(cls, key):
        qs = cls.objects.select_related('key').values(
            'key__return_type',
            'order',
            'value',
        ).order_by('key__key', '-order').filter(key__key=key)

        if not qs:
            return

        return_type = qs[0]['key__return_type']
        value = cls.pack_values(qs, return_type)
        set_attribute(key, value)
    
    @classmethod
    def load_attributes_cache(cls):
        qs = cls.objects.select_related('key').values(
            'key__key',
            'key__return_type',
            'order',
            'value',
        ).order_by('key__key', '-order')

        if not qs:
            return

        grouped = {}

        for attr_key, group in itertools.groupby(qs, key=lambda x: x['key__key']):
            group_list = list(group)

            return_type = group_list[0]['key__return_type']
            grouped[attr_key] = cls.pack_values(group_list, return_type)

        set_many_attributes(grouped)
    