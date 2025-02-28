from django import forms
import inspect
from django.core.cache import cache
from django.apps import apps
from django.forms import CharField
import warnings

ALLOWED_FORM_FIELDS = {}

def register_form_field(dotted_path, field_class, fail_silently=True):
    if not issubclass(field_class, forms.Field):
        if fail_silently:
            return
        raise ValueError("The field_class must be a subclass of django.forms.Field")
    
    existing = ALLOWED_FORM_FIELDS.get(dotted_path)
    if existing is not None:
        if existing != field_class:
            if fail_silently:
                return
            raise ValueError(f"A different field class is already registered for '{dotted_path}'")
        return  

    ALLOWED_FORM_FIELDS[dotted_path] = field_class

def get_field_class(dotted_path):
    try:
        return ALLOWED_FORM_FIELDS[dotted_path]
    except KeyError:
        warnings.warn(f"Field class not found for '{dotted_path}'. Using CharField as fallback.")
        return CharField

def get_allowed_field_choices():
    choices = [(dotted, field_cls.__name__) for dotted, field_cls in ALLOWED_FORM_FIELDS.items()]
    return sorted(choices, key=lambda x: x[1])

def get_required_parameters(field_cls):
    sig = inspect.signature(field_cls.__init__)
    required_params = []
    for name, param in sig.parameters.items():
        if name == 'self' or param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            continue

        if param.default is inspect.Parameter.empty:
            required_params.append(name)
    return required_params

def get_app_config():
    return apps.get_app_config('attributes')

def set_attribute(key, value):
    config = get_app_config()
    cache_key = f"{config.KEY_PREFIX}{key}"
    cache.set(cache_key, value, config.CACHE_TIMEOUT)

def set_many_attributes(data: dict):
    config = get_app_config()
    cache_data = {f"{config.KEY_PREFIX}{key}": value for key, value in data.items()}
    cache.set_many(cache_data, config.CACHE_TIMEOUT)

def get_attribute(key, default=None):
    config = get_app_config()
    cache_key = f"{config.KEY_PREFIX}{key}"
    return cache.get(cache_key, default)

def clear_attribute(key):
    config = get_app_config()
    cache_key = f"{config.KEY_PREFIX}{key}"
    cache.delete(cache_key)