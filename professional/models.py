from django.db import models
from django.db.models import Q
from django.urls import reverse
from salaolunique import settings
from django.dispatch import receiver
from django.db.models.signals import post_save


class ProfessionalCategoryModel(models.Model):
    category_professional = models.CharField('Qual nova categoria de profissional?', max_length=100, unique=True, )
    category_professional_updated_at = models.DateTimeField(null=True)
    category_professional_updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='+', on_delete=models.SET_NULL, blank=True)
    category_professional_author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    category_professional_published = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "professional_category_list"

    def __str__(self):

        return '%s %s' % (self.pk, self.category_professional)


class ProfessionalQuerySet(models.QuerySet):
    def search(self, query=None):
        qs = self
        if query is not None:
            or_lookup = (Q(professional_name__icontains=query) |
                         Q(professional_category__icontains=query)
                        )

            qs = qs.filter(or_lookup).distinct() # distinct() is often necessary with Q lookups
        return qs


class ProfessionalManager(models.Manager):

    def get_queryset(self):
        return ProfessionalQuerySet(self.model, using=self._db)

    def search(self, query=None):
        return self.get_queryset()


class ProfessionalModel(models.Model):

    professional_name = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='professional_custom_user', primary_key=True, on_delete=models.CASCADE)
    professional_category = models.ManyToManyField(ProfessionalCategoryModel, related_name='professional_category', blank=True)
    professional_active = models.BooleanField('Profissional ativo?', default=False)
    professional_published = models.DateTimeField(auto_now_add=True)
    professional_updated_at = models.DateTimeField(null=True)
    professional_updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='+',on_delete=models.SET_NULL, blank=True)
    professional_author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    professional_start_date = models.DateField('Qual data de inicio do profissional?',null=True)
    professional_views = models.PositiveIntegerField(default=0)

    objects = ProfessionalManager()

    @receiver(post_save, sender=settings.AUTH_USER_MODEL)
    def get_professional_create(sender, instance, created, **kwargs):
        if created:
            if instance.is_professional is True:
                ProfessionalModel.objects.create(professional_name=instance)
                instance.professional_custom_user.save()

    @receiver(post_save, sender=settings.AUTH_USER_MODEL)
    def save_user_professional(sender, instance, **kwargs):
        if instance.is_professional is True:
            if ProfessionalModel.objects.filter(professional_name=instance):
                pass
            else:
                ProfessionalModel.objects.create(professional_name=instance)
                instance.professional_custom_user.save()

    class Meta:
        verbose_name_plural = "professional_list"
        verbose_name = "professional"
        db_table = 'professional_db'

    def __str__(self):
        return '%s %s' % (self.pk, self.professional_name)

    def get_absolute_url(self):
        return reverse('professional_detail', kwargs={'pk': self.pk})


class ProfessionalScheduleModel(models.Model):
    CHOICES_WEEKDAY = [(i, i) for i in range(0, 7)]
    CHOICES_MIN_TIME = [(i, i) for i in range(1, 300)]

    professional_schedule = models.ForeignKey(ProfessionalModel, related_name='professional_schedule', on_delete=models.CASCADE)
    professional_schedule_days = models.IntegerField('Qual dia da semana?', choices=CHOICES_WEEKDAY, default=1)
    professional_schedule_work_start = models.TimeField('Hora da abertura da agenda?', auto_now=False, auto_now_add=False, )
    professional_schedule_work_end = models.TimeField('Ultimo horário da agenda?', auto_now=False, auto_now_add=False, )
    professional_schedule_time = models.IntegerField('Quanto tempo dura cada fração da agenda em minutos?', choices=CHOICES_MIN_TIME, default=40)
    professional_schedule_updated_at = models.DateTimeField(null=True)
    professional_schedule_updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='+', on_delete=models.SET_NULL, blank=True)
    professional_schedule_published = models.DateTimeField(auto_now_add=True)
    professional_schedule_author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        verbose_name_plural = "professional_schedule_list"
        verbose_name = "professional_schedule"
        db_table = 'professional_schedule_db'

    def __str__(self):
        return '%s %s' % (self.pk, self.professional_schedule_days)

    def schedule_by_professional(self, professional_schedule, professional_schedule_days):
        professional_schedule_day = ProfessionalScheduleModel.objects.filter(professional_schedule=professional_schedule).filter(professional_schedule_days=professional_schedule_days)
        return professional_schedule_day
