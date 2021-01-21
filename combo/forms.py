from django import forms
from .models import ComboModel, ComboServiceModel
from service.models import ServiceModel


class ServiceChoiceField(forms.ModelChoiceField):

    def __init__(self, obj_label=None, *args, **kwargs):
        super(ServiceChoiceField, self).__init__(*args, **kwargs)
        self.obj_label = obj_label

    def label_from_instance(self, obj):
        service_tittle = obj.service_tittle

        return f'{service_tittle}'


class ComboForm1(forms.ModelForm):
    combo_tittle = forms.CharField(label='Qual nome do pacote?',
                                     widget=forms.TextInput(attrs={'placeholder': 'Ex. Pacote com 4 Serviços de Escova'})
                                     )
    combo_description = forms.CharField(label='', widget=forms.Textarea(
        attrs={'rows': 4, 'placeholder': 'Aqui você pode descrever melhor o combo com regras com até 1000 caracteres.'}
    ),
                                          max_length=1000,
                                          help_text='The max length of the text is 1000.'
                                          )

    class Meta:
        model = ComboModel
        fields = ['combo_tittle', 'combo_description', ]


class ComboForm2(forms.ModelForm):
    combo_expiration_date = forms.DateField(label='Se o pacote tiver validade, marque uma data fim.',
                                                    required=False)

    class Meta:
        model = ComboModel

        fields = ['combo_active', 'combo_expiration_date', ]


class ComboServiceForm(forms.ModelForm):
    combo_service = ServiceChoiceField(label='Selecione um serviço',
                                              queryset=ServiceModel.objects.filter(service_active=False),
                                              empty_label="(Selecione um serviço)",)

    class Meta:
        model = ComboServiceModel

        fields = ['combo_service', 'service_quantity', ]


class ComboUpdateForm(forms.ModelForm):
    combo_tittle = forms.CharField(label='Qual nome do pacote?',
                                     widget=forms.TextInput(attrs={'placeholder': 'Ex. Pacote com 4 Serviços de Escova'})
                                     )
    combo_description = forms.CharField(label='Detalhe regras do pacote', widget=forms.Textarea(
        attrs={'rows': 4, 'placeholder': 'Aqui você pode descrever melhor o pacote com regras com até 1000 caracteres.'}
    ),
                                          max_length=1000,
                                          help_text='The max length of the text is 1000.'
                                          )
    combo_expiration_date = forms.DateField(label='Se o pacote tiver validade, marque uma data fim.',
                                            required=False)

    class Meta:
        model = ComboModel
        fields = ['combo_tittle', 'combo_description', 'combo_active', 'combo_expiration_date', ]
