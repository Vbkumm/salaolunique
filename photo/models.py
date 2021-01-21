from django.db import models
from salaolunique import settings
from service.models import ServiceModel
from lib.templatetags.validators import validate_file_extension
import os
import datetime
from django.core.files.base import ContentFile
from PIL import Image
from io import BytesIO


class ServicePhotoModel(models.Model):
    service_photo_file = models.FileField('Adicione uma foto.', upload_to="img/service_photo_file/", validators=[validate_file_extension], null=True, blank=True,)
    service_photo = models.ForeignKey(ServiceModel, related_name='service_photo', on_delete=models.CASCADE)
    service_photo_cover = models.BooleanField('Foto destaque?', default=False)
    photo_updated_at = models.DateTimeField(null=True)
    photo_updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='+',on_delete=models.SET_NULL, blank=True)
    photo_author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    photo_published = models.DateTimeField(auto_now_add=True)
    photo_expiration_date = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True)
    photo_views = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "service_photo_list"
        verbose_name = "service_photo"
        db_table = 'service_photo_db'

    def __str__(self):
        return self.service_photo_file.name.replace("img/service_photo_file/", "")

    def filename(self):
        return os.path.basename(self.service_photo_file.name)

    def save(self, *args, **kwargs):
        if self.service_photo_file and self.service_photo_file.name.split('.')[1] != 'jpg':
            if 'heic' in self.service_photo_file.name.split('.')[1]:
                import pyheif
                service_photo_file = self.service_photo_file
                heif_file = pyheif.read_heif(service_photo_file)
                service_photo_file = Image.frombytes(mode=heif_file.mode, size=heif_file.size, data=heif_file.data)
            else:
                service_photo_file = Image.open(self.service_photo_file)
            filename = "%s.jpg" % self.service_photo_file.name.split('.')[0]
            if service_photo_file.mode in ('RGBA', 'LA'):
                background = Image.new(service_photo_file.mode[:-1], service_photo_file.size, '#fff')
                background.paste(service_photo_file, service_photo_file.split()[-1])
                service_photo_file = background
            image_io = BytesIO()
            service_photo_file.save(image_io, format='JPEG', quality=100)

            self.service_photo_file.save(filename, ContentFile(image_io.getvalue()), save=False)

        super(ServicePhotoModel, self).save(*args, **kwargs)

    def photo_visible(self):
        if self.photo_expiration_date:
            service = self.photo_expiration_date
            if service > datetime.date.today():
                return True
            else:
                return False
        else:
            return True

    def get_valid_cover_photo(self):
        if self.service_photo_cover is True:
            if self.photo_visible() is True:
                return True

            else:
                return False
