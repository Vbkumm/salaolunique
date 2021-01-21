from __future__ import unicode_literals
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.files.base import ContentFile
from PIL import Image
from io import BytesIO
from photo.models import ServicePhotoModel
from lib.templatetags.validators import validate_file_extension


class CustomUser(AbstractUser):
    picture = models.FileField('Foto perfil', upload_to='img/profile_picture/', blank=True, null=True, validators=[validate_file_extension])
    about = models.TextField('Curta descrição', max_length=1000, null=True, blank=True)
    is_professional = models.BooleanField('Faz parte da equipe L`unique?', default=False)
    photo_bookmark = models.ManyToManyField(ServicePhotoModel, related_name='photo_bookmark')

    def get_professional(self):
        professional_custom_user_list = self.objects.filter(is_professional=True)
        return professional_custom_user_list

    def save(self, *args, **kwargs):
        if self.picture and self.picture.name.split('.')[1] != 'jpg':
            if 'heic' in self.picture.name.split('.')[1]:
                import pyheif
                picture = self.picture
                heif_file = pyheif.read_heif(picture)
                picture = Image.frombytes(mode=heif_file.mode, size=heif_file.size, data=heif_file.data)
            else:
                picture = Image.open(self.picture)

            filename = "%s.jpg" % self.picture.name.split('.')[0]
            if picture.mode in ('RGBA', 'LA'):
                background = Image.new(picture.mode[:-1], picture.size, '#fff')
                background.paste(picture, picture.split()[-1])
                picture = background
            image_io = BytesIO()
            picture.save(image_io, format='JPEG', quality=100)

            self.picture.save(filename, ContentFile(image_io.getvalue()), save=False)
            img = Image.open(self.picture)
            (width, height) = img.size
            if width > 900:
                if 800 / width < 800 / height:
                    factor = 800 / height
                else:
                    factor = 800 / width

                size = (int(width * factor), int(height * factor))
                img = img.resize(size, Image.ANTIALIAS)
                img.save(self.picture.path, optimize=True)

        super(CustomUser, self).save(*args, **kwargs)
