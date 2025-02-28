from django.forms import ModelForm, Select
from attributes.models import AttrConfiguration, AttrValue
from attributes.utils import (
    get_allowed_field_choices,
    get_required_parameters,
    ALLOWED_FORM_FIELDS
)
from django.core.exceptions import ValidationError

class AttrConfigurationForm(ModelForm):
    class Meta:
        model = AttrConfiguration
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['field_type'].widget = Select(choices=get_allowed_field_choices())

    def clean(self):
        cleaned_data = super().clean()
        field_type = cleaned_data.get('field_type')
        args_json = cleaned_data.get('args') or []
        kwargs_json = cleaned_data.get('kwargs') or {}

        field_cls = ALLOWED_FORM_FIELDS.get(field_type)
        if field_cls is None:
            raise ValidationError(f"Field type '{field_type}' is not registered.")
        
        required_params = get_required_parameters(field_cls)
        missing = [param for param in required_params if param not in kwargs_json]
        if missing:
            raise ValidationError(
                f"Missing required keyword arguments for {field_type}: {missing}"
            )
        
        try:
            field_instance = field_cls(*args_json, **kwargs_json)
        except Exception as e:
            raise ValidationError(
                f"Error initializing {field_type} with provided args and kwargs: {e}"
            )
        
        return cleaned_data


class AttrConfigurationValuesForm(ModelForm):
    class Meta:
        model = AttrConfiguration
        fields = []


class AttrValueForm(ModelForm):
    class Meta:
        model = AttrValue
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance: AttrValue
        self.instance.key: AttrConfiguration # type: ignore

        if not self.instance or not getattr(self.instance, 'key', None):
            return
        
        config = self.instance.key
        field_type = config.field_type
        field_cls = ALLOWED_FORM_FIELDS.get(field_type)
        if field_cls is None:
            return

        old_field = self.fields.get('value')

        dynamic_field = field_cls(
            required=old_field.required,
            label=old_field.label,
            *config.args,
            **config.kwargs,
        )

        self.fields['value'] = dynamic_field
