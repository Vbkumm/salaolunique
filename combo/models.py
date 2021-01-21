from django.db import models
from salaolunique import settings
from service.models import ServiceModel
from django.utils.html import mark_safe
from markdown import markdown
from django.urls import reverse
import datetime


# Create your models here.


class ComboModel(models.Model):
    combo_tittle = models.CharField('Título do pacote*', max_length=150, unique=True)
    combo_description = models.CharField('Descrição do pacote*', max_length=1000, null=True, blank=True)
    combo_active = models.BooleanField('Pacote inativo', default=True)
    combo_updated_at = models.DateTimeField(null=True)
    combo_updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='+', on_delete=models.SET_NULL, blank=True)
    combo_author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='combo_user', on_delete=models.SET_NULL, blank=True, null=True)
    combo_published = models.DateTimeField(auto_now_add=True)
    combo_expiration_date = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True)
    combo_views = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "combo_list"
        verbose_name = "combo"
        db_table = 'combo_db'

    def __str__(self):
        return '%s %s' % (self.pk, self.combo_tittle)

    def get_absolute_url(self):
        return reverse('combo:combo_detail', kwargs={'pk': self.pk})

    def get_description_as_markdown(self):
        return mark_safe(markdown(self.combo_description, safe_mode='escape'))

    def combo_visible(self):
        if self.combo_active is False:
            if self.combo_expiration_date:
                combo = self.combo_expiration_date
                if combo > datetime.date.today():
                    return True
                else:
                    return False
            else:
                return True
        else:
            return False


class ComboServiceModel(models.Model):
    CHOICES = [(i, i) for i in range(1, 11)]

    combo_service_quantity = models.ForeignKey(ComboModel, related_name='combo_service_quantity', on_delete=models.CASCADE)
    combo_service = models.ForeignKey(ServiceModel, related_name='combo_service', on_delete=models.CASCADE)
    service_quantity = models.IntegerField('Quantidade de serviços?', choices=CHOICES, default=1)
    combo_service_updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='+', on_delete=models.SET_NULL, blank=True)
    combo_service_author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='combo_service_user', on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        verbose_name_plural = "combo_service_list"
        verbose_name = "combo_service"
        db_table = 'combo_service_db'
