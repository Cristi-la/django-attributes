from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete, pre_save
from attributes.models import AttrConfiguration, AttrValue
from attributes.utils import set_attribute, clear_attribute
##############################
#       Configuration        #
##############################
# attributes/signals.py

@receiver(pre_save, sender=AttrConfiguration)
def store_old_values(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            instance._old_field_type = old_instance.field_type
            instance._old_count = old_instance.count
        except sender.DoesNotExist:
            instance._old_field_type = None
            instance._old_count = None

@receiver(post_save, sender=AttrConfiguration)
def create_or_update_attr_value(sender, instance, created, **kwargs):
    if created:
        count = instance.count
        AttrValue.objects.bulk_create(
            [AttrValue(key=instance, order=i) for i in range(count)]
        )
        return

    old_field_type = getattr(instance, '_old_field_type', None)
    if old_field_type != instance.field_type:
        AttrValue.objects.filter(key=instance).update(value=None)

    old_count = getattr(instance, '_old_count', instance.count)
    new_count = instance.count

    if new_count < old_count:
        AttrValue.objects.filter(key=instance, order__gte=new_count).delete()
    elif new_count > old_count:
        new_values = [AttrValue(key=instance, order=i) for i in range(old_count, new_count)]
        AttrValue.objects.bulk_create(new_values)


@receiver(post_delete, sender=AttrConfiguration)
def delete_attr_value(sender, instance, **kwargs):
    instance.values.all().delete()

##############################
#            Values          #
##############################
@receiver(post_delete, sender=AttrValue)
def attr_value_post_delete(sender, instance, **kwargs):
    clear_attribute(instance.key.key)

@receiver(post_save, sender=AttrValue)
def attr_value_post_save(sender, instance, created, **kwargs):
    set_attribute(instance.key.key, instance.value)
    
    
