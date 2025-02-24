from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from attributes.models import AttrConfiguration, AttrValue

##############################
#       Configuration        #
##############################
@receiver(post_save, sender=AttrConfiguration)
def create_attr_value(sender, instance, created, **kwargs):
    if created:
        count = instance.count
        AttrValue.objects.bulk_create([AttrValue(key=instance) for _ in range(count)])
        return

    AttrValue.objects.filter(key=instance).update(value=None)
    

@receiver(post_delete, sender=AttrConfiguration)
def delete_attr_value(sender, instance, **kwargs):
    instance.values.all().delete()

##############################
#            Values          #
##############################
@receiver(post_delete, sender=AttrValue)
def count_down_attr_configuration(sender, instance, **kwargs):
    instance.key.count -= 1
    instance.key.save()

@receiver(post_save, sender=AttrValue)
def count_up_attr_configuration(sender, instance, created, **kwargs):
    if created:
        instance.key.count += 1
        instance.key.save()
        return