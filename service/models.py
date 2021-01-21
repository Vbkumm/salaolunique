from django.db import models
from salaolunique import settings
from django.db.models import Q
from django.urls import reverse
from datetime import timedelta
from professional.models import ProfessionalCategoryModel, ProfessionalModel
from django.utils.html import mark_safe
from markdown import markdown
from django.utils.duration import _get_duration_components
from django.dispatch import receiver
from django.db.models.signals import post_save
# Create your models here.


class ServiceCategoryModel(models.Model):
    category_service = models.CharField('Qual nova categoria de serviços?', max_length=100, unique=True)
    professional_category = models.ForeignKey(ProfessionalCategoryModel, related_name='service_professional', on_delete=models.SET_NULL, blank=True, null=True)
    category_service_author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    category_service_published = models.DateTimeField(auto_now_add=True)
    category_service_updated_at = models.DateTimeField(null=True)
    category_service_updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='+',on_delete=models.SET_NULL, blank=True)

    class Meta:
        verbose_name_plural = "service_category_list"

    def __str__(self):
        return '%s %s' % (self.pk, self.category_service)


class ServiceQuerySet(models.QuerySet):
    def search(self, query=None):
        qs = self
        if query is not None:
            or_lookup = (Q(service_tittle__icontains=query) |
                         Q(service_description__icontains=query)
                        )

            qs = qs.filter(or_lookup).distinct() # distinct() is often necessary with Q lookups
        return qs


class ServiceManager(models.Manager):

    def get_queryset(self):
        return ServiceQuerySet(self.model, using=self._db)

    def search(self, query=None):
        return self.get_queryset()


class ServiceModel(models.Model):

    service_tittle = models.CharField('Título*',max_length=150, unique=True)
    service_description = models.CharField('Descrição*', max_length=1000, null=True, blank=True)
    service_active = models.BooleanField('Serviçø inativo', default=True)
    service_author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='service_user', on_delete=models.SET_NULL, blank=True, null=True)
    service_category = models.ForeignKey(ServiceCategoryModel, related_name='service_category', on_delete=models.SET_NULL, blank=True, null=True)
    service_updated_at = models.DateTimeField(null=True)
    service_updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='+',on_delete=models.SET_NULL, blank=True)
    service_published = models.DateTimeField(auto_now_add=True)
    service_views = models.PositiveIntegerField(default=0)

    objects = ServiceManager()

    class Meta:
        verbose_name_plural = "service_list"
        verbose_name = "service"
        db_table = 'service_db'

    def __str__(self):
        return '%s %s' % (self.pk, self.service_tittle)

    def get_absolute_url(self):
        return reverse('service:service_detail', kwargs={'pk': self.pk})

    def get_description_as_markdown(self):
        return mark_safe(markdown(self.service_description, safe_mode='escape'))


class ProfessionalServicesSkillModel(models.Model):
    professional_service_in = models.ManyToManyField(ServiceModel, related_name='professional_service_in')
    professional_service_out = models.ManyToManyField(ServiceModel, related_name='professional_service_out')
    professional_extra_service = models.ManyToManyField(ServiceModel, related_name='professional_extra_service')
    service_professional_skill = models.OneToOneField(ProfessionalModel, related_name='service_professional_skill', on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "professional_skill_list"
        verbose_name = "professional_skill"
        db_table = 'professional_skill_db'

    @receiver(post_save, sender=ProfessionalModel)
    def get_professional_skill_create(sender, instance, created, **kwargs):
        if created:
            ProfessionalServicesSkillModel.objects.create(service_professional_skill=instance)

        else:
            professional_category_list = list(instance.professional_category.all()[:])
            professional_service_skill = instance.service_professional_skill
            professional_service_skill.professional_service_in.clear()
            for professional_category in professional_category_list:
                service_list = list(ServiceModel.objects.filter(service_category__professional_category=professional_category))
                for service in service_list:
                    if service not in professional_service_skill.professional_service_in.all():
                        professional_service_skill.professional_service_in.add(service)
                        if service in professional_service_skill.professional_extra_service.all():
                            professional_service_skill.professional_extra_service.remove(service)
            professional_service_skill.save()

    @receiver(post_save, sender=ServiceModel)
    def update_professional_category(sender, instance, created, **kwargs):
        if created:
            professional_list = list(ProfessionalModel.objects.filter(professional_category=instance.service_category.professional_category)[:])
            for professional in professional_list:
                professional.save()



