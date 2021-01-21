from django import forms
from .models import ServiceModel, ServiceCategoryModel
from professional.models import ProfessionalCategoryModel


class ServiceCategoryChoiceField(forms.ModelChoiceField):

    def __init__(self, obj_label=None, *args, **kwargs):
        super(ServiceCategoryChoiceField, self).__init__(*args, **kwargs)
        self.obj_label = obj_label

    def label_from_instance(self, obj):

        category_service = obj.category_service

        return f'{category_service}'


class ProfessionalCategoryChoiceField(forms.ModelChoiceField):

    def __init__(self, obj_label=None, *args, **kwargs):
        super(ProfessionalCategoryChoiceField, self).__init__(*args, **kwargs)
        self.obj_label = obj_label

    def label_from_instance(self, obj):

        category_professional = obj.category_professional

        return f'{category_professional}'


class ServiceUpdateForm(forms.ModelForm):
    service_tittle = forms.CharField(label='Qual nome do serviço?',
                                       widget=forms.TextInput(attrs={'placeholder': 'Ex. Coloração'})
                                       )
    service_category = ServiceCategoryChoiceField(label='Selecione uma catergoria de serviço',
                                            queryset=ServiceCategoryModel.objects.all(),
                                            empty_label="(Add uma nova se nåo encontrar)",
                                            required=False,
                                            initial=0,
                                            )

    service_description = forms.CharField(label='', widget=forms.Textarea(
        attrs={'rows': 4, 'placeholder': 'Aqui você pode descrever melhor o serviçø com até 1000 caracteres.'}
    ),
                                             max_length=1000,
                                             help_text='The max length of the text is 1000.'
                                             )

    class Meta:
        model = ServiceModel
        fields = ['service_tittle', 'service_category', 'service_description',
                  'service_active', ]


class ServiceForm1(forms.ModelForm):
    service_tittle = forms.CharField(label='Qual nome do serviço?',
                                     widget=forms.TextInput(attrs={'placeholder': 'Ex. Coloração'})
                                     )
    service_category = ServiceCategoryChoiceField(label='Selecione uma catergoria de serviço',
                                              queryset=ServiceCategoryModel.objects.all(),
                                              empty_label="(Add uma nova se nåo encontrar)",

                                              )

    class Meta:
        model = ServiceModel
        fields = ['service_tittle', 'service_category', ]


class ServiceForm2(forms.ModelForm):

    service_description = forms.CharField(label='', widget=forms.Textarea(
        attrs={'rows': 4, 'placeholder': 'Aqui você pode descrever melhor o serviçø com até 1000 caracteres.'}
    ),
                                          max_length=1000,
                                          help_text='The max length of the text is 1000.'
                                          )

    class Meta:
        model = ServiceModel
        fields = ['service_description', ]


class ServiceActiveForm(forms.ModelForm):

    class Meta:
        model = ServiceModel
        fields = ['service_active',]


class ServiceCategoryForm(forms.ModelForm):
    professional_category = ProfessionalCategoryChoiceField(label='Selecione uma catergoria de profissional',
                                                           queryset=ProfessionalCategoryModel.objects.all(),
                                                           empty_label="(Add uma nova se nåo encontrar)",
                                                           )

    class Meta:
        model = ServiceCategoryModel
        fields = ['category_service', 'professional_category', ]


class DashboardServiceCategoryForm(forms.ModelForm):
    professional_category = ProfessionalCategoryChoiceField(label='Selecione uma catergoria de profissional',
                                                           queryset=ProfessionalCategoryModel.objects.all(),
                                                           empty_label="(catergorias de profissionais)",
                                                           )

    class Meta:
        model = ServiceCategoryModel
        fields = ['category_service', 'professional_category', ]
