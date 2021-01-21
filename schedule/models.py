from django.db import models
from salaolunique import settings
from professional.models import ProfessionalModel
from custom_user.models import CustomUser
from service.models import ServiceModel
from django.urls import reverse
from lib.templatetags.validators import validate_schedule_date
from datetime import time


class ScheduleModel(models.Model):
    schedule_service = models.ForeignKey(ServiceModel, related_name='schedule_costumer', on_delete=models.CASCADE)

    schedule_costumer = models.ForeignKey(CustomUser, related_name='schedule_costumer',on_delete=models.CASCADE)

    schedule_date = models.DateField('Qual dia você deseja agendar?', auto_now=False, auto_now_add=False, validators=[validate_schedule_date],)
    schedule_hour = models.TimeField('Qual horário você deseja agendar?', auto_now=False, auto_now_add=False, default=time(00, 00))
    schedule_professional = models.ForeignKey(ProfessionalModel, related_name='schedule_professional', on_delete=models.SET_NULL, blank=True, null=True)
    schedule_description = models.CharField('Observações:', max_length=1000, null=True, blank=True)

    schedule_service_done = models.BooleanField('Seviço realizado?', default=False)
    schedule_service_paid = models.BooleanField('Seviço pago?', default=False)
    schedule_canceled = models.BooleanField('Seviço cancelado?', default=False)
    schedule_updated_at = models.DateTimeField(null=True)
    schedule_updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='+', on_delete=models.SET_NULL, blank=True)
    schedule_author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='schedule_user', on_delete=models.SET_NULL, blank=True, null=True)
    schedule_published = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "schedule_list"
        verbose_name = "schedule"
        db_table = 'schedule_db'

    def __str__(self):
        return '%s %s' % (self.pk, self.schedule_costumer)

    def get_absolute_url(self):
        return reverse('schedule:schedule_detail', kwargs={'pk': self.pk})
