from django import forms
from .models import PriceModel


class PriceForm(forms.ModelForm):

    class Meta:
        model = PriceModel
        fields = ['price_value', 'price_active', ]

