from django import forms
from .models import ServicePhotoModel


class ServicePhotoForm(forms.ModelForm):

    class Meta:
        model = ServicePhotoModel
        fields = ['service_photo_file',]


class ServicePhotoCoverForm(forms.ModelForm):
    service_photo_expiration_date = forms.DateField(label='Se promoção com validade, marque uma data fim.', required=False)

    class Meta:
        model = ServicePhotoModel
        fields = ['service_photo_cover','service_photo_expiration_date']
