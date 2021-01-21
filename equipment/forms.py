from django import forms
from .models import EquipmentModel, ServiceEquipmentModel


class EquipmentField(forms.ModelChoiceField):

    def __init__(self, obj_label=None, *args, **kwargs):
        super(EquipmentField, self).__init__(*args, **kwargs)
        self.obj_label = obj_label

    def label_from_instance(self, obj):
        equipment_tittle = obj.equipment_tittle

        return f'{equipment_tittle}'


class EquipmentForm1(forms.ModelForm):
    equipment_tittle = forms.CharField(label='Qual nome do equipamento?',
                                     widget=forms.TextInput(attrs={'placeholder': 'Ex. Cadeira de cabelereiro'})
                                     )
    equipment_description = forms.CharField(label='', widget=forms.Textarea(
        attrs={'rows': 4, 'placeholder': 'Descreva o equipamento e sua forma de uso com até 1000 caracteres.'}
    ),
                                          max_length=1000,
                                          help_text='The max length of the text is 1000.'
                                          )

    class Meta:
        model = EquipmentModel
        fields = ['equipment_tittle', 'equipment_description', ]


class EquipmentForm2(forms.ModelForm):

    class Meta:
        model = EquipmentModel

        fields = ['equipment_quantity', 'equipment_active', ]


class EquipmentUpdateForm(forms.ModelForm):
    equipment_tittle = forms.CharField(label='Qual nome do equipamento?',
                                       widget=forms.TextInput(attrs={'placeholder': 'Ex. Cadeira de cabelereiro'})
                                       )
    equipment_description = forms.CharField(label='', widget=forms.Textarea(
        attrs={'rows': 4, 'placeholder': 'Descreva o equipamento e sua forma de uso com até 1000 caracteres.'}
    ),
                                            max_length=1000,
                                            help_text='The max length of the text is 1000.'
                                            )

    class Meta:
        model = EquipmentModel
        fields = ['equipment_tittle', 'equipment_description', 'equipment_quantity', 'equipment_active',]


class ServiceEquipmentForm(forms.ModelForm):
    equipment_tittle = EquipmentField(label='Selecione um equipamento para realizar o serviço',
                                                  queryset=EquipmentModel.objects.all(),
                                                  empty_label="(Add um novo equipamento se nåo encontrar)",
                                                  )

    equipment_replaced = EquipmentField(label='Caso esse equipamento seja complementar a outro ou seja uma segunda opção podendo substituir outro equipamento marque aqui qual',
                               queryset=EquipmentModel.objects.all(),
                               empty_label="(equipamentos que já fazem parte do serviço)",
                               required=False,
                               )

    def __init__(self, *args, **kwargs):
        self.equipment_replaced = kwargs.pop('equipment_replaced', None)
        super(ServiceEquipmentForm, self).__init__(*args, **kwargs)
        self.fields['equipment_replaced'].queryset = self.equipment_replaced

    class Meta:
        model = ServiceEquipmentModel
        fields = ['equipment_tittle', 'equipment_time', 'equipment_time_exact', 'equipment_complement', 'equipment_replaced', ]


class ServiceEquipmentUpdateForm(forms.ModelForm):

    class Meta:
        model = ServiceEquipmentModel
        fields = ['equipment_time', 'equipment_time_exact', ]


class ServiceEquipmentFirstForm(forms.ModelForm):
    equipment_tittle = EquipmentField(label='Selecione um equipamento para realizar o serviço',
                                                  queryset=EquipmentModel.objects.all(),
                                                  empty_label="(Add um novo equipamento se nåo encontrar)",
                                                  )

    class Meta:
        model = ServiceEquipmentModel
        fields = ['equipment_tittle', 'equipment_time', 'equipment_time_exact',]
