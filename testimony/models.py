from django.db import models
from django.db.models import Q
from django.urls import reverse
from salaolunique import settings
from professional.models import ProfessionalModel
from bride.models import BrideModel
from service.models import ServiceModel
from photo.models import ServicePhotoModel
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete, pre_save
from django.utils.html import mark_safe
from markdown import markdown
from django.utils import timezone


class TestimonyQuerySet(models.QuerySet):
    def search(self, query=None):
        qs = self
        if query is not None:
            or_lookup = (Q(testimony_title__icontains=query) |
                         Q(testimony_descripition__icontains=query)
                        )

            qs = qs.filter(or_lookup).distinct() # distinct() is often necessary with Q lookups
        return qs


class TestimonyManager(models.Manager):

    def get_queryset(self):
        return TestimonyQuerySet(self.model, using=self._db)

    def search(self, query=None):
        return self.get_queryset()


class TestimonyModel(models.Model):

    testimony_title = models.CharField('De um título para sua avaliação', max_length=80, null=True)
    testimony_description = models.TextField('Escreva um comentario para sua avaliação', max_length=1000, null=True)
    testimony_photo = models.ForeignKey(ServicePhotoModel, related_name='testimony_photo', null=True, on_delete=models.CASCADE)
    testimony_bride = models.ForeignKey(BrideModel, related_name='testimony_bride', null=True, blank=True, on_delete=models.CASCADE)
    testimony_professional = models.ManyToManyField(ProfessionalModel, related_name='testimony_professional', blank=True)
    testimony_service = models.ForeignKey(ServiceModel, related_name='testimony_service', null=True, blank=True, on_delete=models.CASCADE)
    testimony_rating = models.PositiveIntegerField(null=True, blank=True)
    testimony_active = models.BooleanField('Depoimento visisvel?', default=True)
    testimony_published = models.DateTimeField(auto_now_add=True)
    testimony_updated_at = models.DateTimeField(null=True)
    testimony_updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='+', on_delete=models.SET_NULL, blank=True)
    testimony_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='testimony_user', on_delete=models.SET_NULL, blank=True, null=True)

    objects = TestimonyManager()

    class Meta:
        verbose_name_plural = "testimony_list"
        verbose_name = "testimony"
        db_table = 'testimony_db'

    def __str__(self):
        return '%s %s' % (self.pk, self.testimony_title)

    def get_absolute_url(self):
        return reverse('testimony_detail', kwargs={'pk': self.pk})

    @receiver(post_save, sender=BrideModel)
    def get_testimony_bride_create(sender, instance, created,  **kwargs):
        if created:
            bride_register_user = instance.bride_register_user
            bride_name = instance.bride_name
            TestimonyModel.objects.create(testimony_bride=instance, testimony_title=bride_name, testimony_user=bride_register_user)
            instance.save()

    def get_valid_testimony_photo(self):
        if self.testimony_active is True:
            testimony_photos = ServicePhotoModel.objects.filter(testimony_photo=self)
            for photo in testimony_photos:
                if photo.photo_visible() is True:
                    return True
                else:
                    return False

    def get_last_photo(self):
        if self.testimony_active is True:
            if self.testimony_photo is not None:
                if self.get_valid_testimony_photo() is True:
                    return True

    def get_testimony_user(self):
        if not self.testimony_photo:
            if not self.testimony_bride:
                return True

    def get_description_as_markdown(self):
        return mark_safe(markdown(self.testimony_description, safe_mode='escape'))


class TestimonyDeletedModel(models.Model):
    testimony_deleted_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='testimony_deleted_user', on_delete=models.SET_NULL, blank=True, null=True)
    testimony_deleted_date = models.DateTimeField(auto_now_add=True)
    testimony_deleted_title = models.CharField(max_length=80, null=True)
    testimony_deleted_description = models.TextField(max_length=1000, null=True)
    testimony_deleted_rating = models.PositiveIntegerField(null=True)

    class Meta:
        verbose_name_plural = "testimony_deleted_list"
        verbose_name = "testimony_deleted"
        db_table = 'testimony_deleted_db'

    @receiver(pre_delete, sender=TestimonyModel)
    def get_testimony_deleted_backup(sender, instance, **kwargs):
        testimony_deleted_user = instance.testimony_updated_by
        testimony_deleted_date = timezone.now()
        testimony_deleted_title = instance.testimony_title
        testimony_deleted_description = instance.testimony_description
        testimony_deleted_rating = instance.testimony_rating
        TestimonyDeletedModel.objects.create(testimony_deleted_user=testimony_deleted_user, testimony_deleted_date=testimony_deleted_date,testimony_deleted_title=testimony_deleted_title,testimony_deleted_description=testimony_deleted_description,testimony_deleted_rating=testimony_deleted_rating)
        instance.save()

