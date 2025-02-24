from django.apps import AppConfig


class AttributesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'attributes'

    def ready(self):
        import attributes.signals

        from django.forms import fields
        from attributes.utils import register_form_field
        from django import forms

        for field_name in fields.__all__:
            if field_name == "Field":
                continue
            dotted_path = f"django.forms.{field_name}"

            try:
                field_class = getattr(forms, field_name)
            except AttributeError:
                continue
            
            register_form_field(dotted_path, field_class)