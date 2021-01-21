from django.db import models
from django.db.models import Q
from django.urls import reverse
from salaolunique import settings


class BrideQuerySet(models.QuerySet):
    def search(self, query=None):
        qs = self
        if query is not None:
            or_lookup = (Q(bride_name__icontains=query)
                         )

            qs = qs.filter(or_lookup).distinct() # distinct() is often necessary with Q lookups
        return qs


class BrideManager(models.Manager):

    def get_queryset(self):
        return BrideQuerySet(self.model, using=self._db)

    def search(self, query=None):
        return self.get_queryset()


class BrideModel(models.Model):
    BRIDE = '1'
    ALUMNAE = '2'
    DEBUTANTE = '3'
    INDEPENDENT = '4'
    BRIDE_CATEGORY = (
        (None, ''), (BRIDE, 'Noiva'), (ALUMNAE, 'Formanda'), (DEBUTANTE, 'Debutante'), (INDEPENDENT, 'Independente'),)
    bride_category = models.CharField('Noiva, formanda ou debutante?', choices=BRIDE_CATEGORY, max_length=1, default=BRIDE, )
    bride_user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='bride_custom_user', on_delete=models.SET_NULL, blank=True, null=True)
    bride_name = models.CharField('Nome da noiva', unique=True, max_length=80)
    bride_party_date = models.DateField('Data do evento', null=True, blank=True)
    bride_active = models.BooleanField('Noiva pronta para publicar?', default=False)
    bride_updated_at = models.DateTimeField(null=True)
    bride_updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='+',  on_delete=models.SET_NULL, blank=True)
    bride_published = models.DateTimeField(auto_now_add=True)
    bride_register_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='bride_register_user', on_delete=models.SET_NULL, blank=True, null=True)
    bride_views = models.PositiveIntegerField(default=0)

    objects = BrideManager()

    class Meta:
        verbose_name_plural = "bride_list"
        verbose_name = "bride"
        db_table = 'bride_db'

    def __str__(self):
        return '%s %s' % (self.pk, self.bride_name)

    def get_absolute_url(self):
        return reverse('bride_detail', kwargs={'pk': self.pk})

