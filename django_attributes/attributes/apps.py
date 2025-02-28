from django.apps import AppConfig





class AttributesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'attributes'

    KEY_PREFIX = "attr_"
    CACHE_TIMEOUT = 3600

    def __init__(self, app_name, app_module):
        super().__init__(app_name, app_module)

    def load_settings(self):

        from django.conf import settings
        def get_setting(name, default=None):
            val = getattr(settings, name, default)
            if callable(val):
                return val()
            return val

        self.KEY_PREFIX = get_setting("ATTRIBUTE_KEY_PREFIX", self.KEY_PREFIX)
        self.CACHE_TIMEOUT = get_setting("ATTRIBUTE_CACHE_TIMEOUT", self.CACHE_TIMEOUT)           

    def register_default(self):
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


    def ready(self):
        import attributes.signals

        self.register_default()
        self.load_settings()
