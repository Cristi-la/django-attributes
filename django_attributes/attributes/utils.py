from django import forms
import inspect

ALLOWED_FORM_FIELDS = {}

def register_form_field(dotted_path, field_class):
    """
    Registers a Django form field class under a specific dotted path.
    Raises a ValueError if:
      - field_class is not a subclass of forms.Field.
      - A different field class is already registered for the same dotted_path.
    If the same field_class is already registered, it does nothing.
    """
    if not issubclass(field_class, forms.Field):
        raise ValueError("The field_class must be a subclass of django.forms.Field")
    
    existing = ALLOWED_FORM_FIELDS.get(dotted_path)
    if existing is not None:
        if existing != field_class:
            raise ValueError(f"A different field class is already registered for '{dotted_path}'")
        return  

    ALLOWED_FORM_FIELDS[dotted_path] = field_class


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