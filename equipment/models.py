from django.db import models
from salaolunique import settings
from django.utils.html import mark_safe
from markdown import markdown
from service.models import ServiceModel
from django.utils.duration import _get_duration_components
from datetime import timedelta


class EquipmentModel(models.Model):
    CHOICES = [(i, i) for i in range(1, 51)]

    equipment_tittle = models.CharField('Tipo de equipamento*',max_length=150, unique=True)
    equipment_description = models.CharField('Descrição*', max_length=1000, null=True, blank=True)
    equipment_quantity = models.IntegerField('Quantidade deste equipamento?', choices=CHOICES, default=1)
    equipment_active = models.BooleanField('Equipamento ativo', default=True)
    equipment_author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='equipment_user', on_delete=models.SET_NULL, blank=True, null=True)
    equipment_updated_at = models.DateTimeField(null=True)
    equipment_updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='+', on_delete=models.SET_NULL, blank=True)
    equipment_published = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "equipment_list"
        verbose_name = "equipment"
        db_table = 'equipment_db'

    def __str__(self):
        return '%s %s' % (self.equipment_tittle, self.equipment_quantity)

    def get_description_as_markdown(self):
        return mark_safe(markdown(self.equipment_description, safe_mode='escape'))


class ServiceEquipmentModel(models.Model):

    equipment_service = models.ForeignKey(ServiceModel, related_name='equipment_service', on_delete=models.CASCADE)
    equipment_tittle = models.ForeignKey(EquipmentModel, related_name='equipment', on_delete=models.CASCADE)
    equipment_time = models.DurationField('Qual tempo de uso deste equipamento? Caso seja variavel estipule um tempo minimo.', default=timedelta(minutes=5))
    equipment_time_exact = models.BooleanField('Tempo de uso deste equipamento pode variar de acordo com cada cliente?', default=False)
    equipment_complement = models.BooleanField('Este equipamento é usado simutaniamente com algum outro equipamento?',default=False)
    equipment_replaced = models.ForeignKey(EquipmentModel, related_name='equipment_replaced', on_delete=models.CASCADE, null=True, blank=True)
    equipment_service_updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='+', on_delete=models.SET_NULL, blank=True)
    equipment_service_updated_at = models.DateTimeField(null=True)
    equipment_service_author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='service_equipment_author', on_delete=models.SET_NULL, blank=True, null=True)
    equipment_service_published = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "service_equipment_list"
        verbose_name = "service_equipment"
        db_table = 'service_equipment_db'

    def duration_string(self):
        days, hours, minutes, seconds, microseconds = _get_duration_components(self.equipment_time)
        string = ''

        if minutes:
            string = '{:02d} minutos'.format(minutes)

        if hours and minutes:
            string = ' e ' + string

        if hours == 1:
            string = '{:2d} hora'.format(hours) + string

        if hours > 1:
            string = '{:2d} horas'.format(hours) + string

        return string

    def service_equipment_total_time(self, service):

        service_equipment_total_time = None
        equipment_list = ServiceEquipmentModel.objects.filter(equipment_service=service)
        for equipment_duration in equipment_list:
            if equipment_duration.equipment_replaced is None:
                service_equipment_time = equipment_duration.equipment_time
                if service_equipment_total_time is None:
                    service_equipment_total_time = service_equipment_time
                else:
                    service_equipment_total_time += service_equipment_time

        return service_equipment_total_time

