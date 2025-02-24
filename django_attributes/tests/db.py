import os
import sys
import django

project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_path not in sys.path:
    sys.path.append(project_path)


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()


from attributes.forms import ALLOWED_FORM_FIELDS
from attributes.models import AttrConfiguration
from attributes.utils import get_required_parameters

def create_attr_configs():
    AttrConfiguration.objects.all().delete()

    for dotted_path, field_cls in ALLOWED_FORM_FIELDS.items():
        field_type_str = field_cls.__name__
        key = f"TEST_{field_type_str.upper()}"
        _, created = AttrConfiguration.objects.get_or_create(
            key=key,
            defaults={'field_type': dotted_path}
        )
        
        if created:
            required_params = get_required_parameters(field_cls)
            print(f"Created: {key} for field type {field_type_str}: {required_params}")
        else:
            print(f"Already exists: {key}")

if __name__ == "__main__":
    create_attr_configs()
