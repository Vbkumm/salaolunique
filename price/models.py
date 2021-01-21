from django.db import models
from django.urls import reverse
from salaolunique import settings
from service.models import ServiceModel
from django.dispatch import receiver
from django.db.models.signals import post_save
from model_utils import FieldTracker
from combo.models import ComboModel


class PriceModel(models.Model):
    price_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    old_price_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_service = models.ForeignKey(ServiceModel, related_name='price_service', on_delete=models.CASCADE, null=True, blank=True)
    price_combo = models.ForeignKey(ComboModel, related_name='price_combo', on_delete=models.CASCADE, null=True, blank=True)
    price_active = models.BooleanField('Preço visisvel?', default=False)
    price_updated_at = models.DateTimeField(null=True)
    price_updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='+', on_delete=models.SET_NULL, blank=True)
    price_published = models.DateTimeField(auto_now_add=True)
    price_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='price_user', on_delete=models.SET_NULL, blank=True, null=True)
    price_value_tracker = FieldTracker(fields=['price_value'])

    def save(self, *args, **kwargs):
        if not self.price_value:
            self.price_value = self.price_value
            self.old_price_value = self.price_value_tracker.previous('price_value')

        super(PriceModel, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.price_service) + ": R$ " + str(self.price_value)

    class Meta:
        verbose_name_plural = "price_list"
        verbose_name = "price"
        db_table = 'price_db'

    def get_absolute_url(self):
        return reverse('price_detail', kwargs={'pk': self.pk})

    @receiver(post_save, sender=ServiceModel)
    def get_price_service_create(sender, instance, created,  **kwargs):
        if created:
            service_author = instance.service_author

            PriceModel.objects.create(price_service=instance, price_user=service_author)
            instance.service_author.save()

    @receiver(post_save, sender=ComboModel)
    def get_price_combo_create(sender, instance, created,  **kwargs):
        if created:
            combo_author = instance.combo_author

            PriceModel.objects.create(price_combo=instance, price_user=combo_author)
            instance.combo_author.save()
