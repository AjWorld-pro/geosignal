from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import NotificationPreference, UserSettings, Notification


@receiver(post_save, sender=User)
def create_user_core_objects(sender, instance, created, **kwargs):
    if created:
        NotificationPreference.objects.get_or_create(user=instance)
        UserSettings.objects.get_or_create(user=instance)
        Notification.objects.create(
            user=instance,
            title='Welcome to Geosginal',
            message='Your account has been created. Start by searching for network coverage in your area.',
            notification_type='success',
        )
