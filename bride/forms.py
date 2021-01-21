from django import forms
from .models import BrideModel
from custom_user.models import CustomUser


class BrideUserChoiceField(forms.ModelChoiceField):

    def __init__(self, obj_label=None, *args, **kwargs):
        super(BrideUserChoiceField, self).__init__(*args, **kwargs)
        self.obj_label = obj_label

    def label_from_instance(self, obj):
        if obj.first_name:
            last_name = obj.last_name
            first_name = obj.first_name
            return f'{first_name} {last_name}'
        else:
            username = obj.username
            return f'{username}'


class BrideForm1(forms.ModelForm):
    bride_name = forms.CharField(label='Nome?',
                                     widget=forms.TextInput(attrs={'placeholder': 'Ex. Gabriela Luna Da Rosa Kumm'})
                                     )
    bride_user = BrideUserChoiceField(label='Marque uma cliente, caso ela já tenha cadastro.',
                                             queryset=CustomUser.objects.filter(bride_custom_user=None),
                                             empty_label="(Selecione uma cliente, caso ela já tenha cadastro)",
                                             widget=forms.Select, required=False,
                                             )

    class Meta:
        model = BrideModel
        fields = ['bride_name', 'bride_category', 'bride_user',]


class BrideForm2(forms.ModelForm):

    class Meta:
        model = BrideModel
        fields = ['bride_party_date', 'bride_active',]


class BrideUpdateForm(forms.ModelForm):
    bride_name = forms.CharField(label='Nome?',
                                 widget=forms.TextInput(attrs={'placeholder': 'Ex. Gabriela Luna Da Rosa Kumm'})
                                 )
    bride_user = BrideUserChoiceField(label='Marque uma cliente, caso ela já tenha cadastro.',
                                        queryset=CustomUser.objects.filter(bride_custom_user=None),
                                        empty_label="(Selecione uma cliente, caso ela já tenha cadastro)",
                                        widget=forms.Select, required=False,
                                        )

    class Meta:
        model = BrideModel
        fields = ['bride_name', 'bride_category', 'bride_user', 'bride_party_date', 'bride_active',]

