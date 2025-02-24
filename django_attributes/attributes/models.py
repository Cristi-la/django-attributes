from django.db import models
from django.core.validators import validate_slug
from django.core.validators import MinValueValidator

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

    def __str__(self):
        return f'{self.key}: {self.value}'