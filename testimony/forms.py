from django import forms
from .models import TestimonyModel, ProfessionalModel, ServiceModel, BrideModel


class ProfessionalChoiceField(forms.ModelMultipleChoiceField):

    def __init__(self, obj_label=None, *args, **kwargs):
        super(ProfessionalChoiceField, self).__init__(*args, **kwargs)
        self.obj_label = obj_label

    def label_from_instance(self, obj):
        if obj.professional_name.first_name:
            last_name = obj.professional_name.last_name
            first_name = obj.professional_name.first_name
            return f'{first_name} {last_name}'
        else:
            username = obj.professional_name.username
            return f'{username}'


class TestimonyServiceForm1(forms.ModelForm):
    testimony_description = forms.CharField(label='', widget=forms.Textarea(
        attrs={'rows': 4, 'placeholder': 'Deixe seu comentário aqui.'}
    ),
                                            max_length=1000,
                                            help_text='Comentários podem conter até 1000 caracteres.', required=False,
                                            )

    class Meta:
        model = TestimonyModel
        fields = ['testimony_title', 'testimony_description', ]


class TestimonyServiceForm2(forms.ModelForm):

    testimony_professional = ProfessionalChoiceField(label='Se desejar marque o profissional que realizou o serviço',queryset=ProfessionalModel.objects.filter(professional_active=True), widget=forms.CheckboxSelectMultiple, required=False)

    class Meta:
        model = TestimonyModel
        fields = ['testimony_professional', ]


class TestimonyServiceForm3(forms.ModelForm):
    testimony_rating = forms.ChoiceField(label='Qual sua avaliação para o serviço?', widget=forms.Select(), choices=([('1', 'Péssimo'), ('2', 'Ruim'), ('3', 'Mais ou menos'), ('4', 'Bom'), ('5', 'Ótimo'), ]), initial='5', required=True)

    class Meta:
        model = TestimonyModel
        fields = ['testimony_rating', ]


class TestimonyUpdateForm(forms.ModelForm):
    testimony_description = forms.CharField(label='Comentario', widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Deixe seu comentário aqui.'}), max_length=1000, help_text='Comentários podem conter até 1000 caracteres.', required=False,)
    testimony_professional = ProfessionalChoiceField(label='Se desejar marque o profissional que realizou o serviço',queryset=ProfessionalModel.objects.filter(professional_active=True), widget=forms.CheckboxSelectMultiple, required=False)
    testimony_rating = forms.ChoiceField(label='Qual sua avaliação para o serviço?', widget=forms.Select(), choices=([('1', 'Péssimo'), ('2', 'Ruim'), ('3', 'Mais ou menos'), ('4', 'Bom'), ('5', 'Ótimo'), ]), initial='5', required=True, )

    class Meta:
        model = TestimonyModel
        fields = ['testimony_title', 'testimony_description', 'testimony_professional', 'testimony_rating', ]


class TestimonyPhotoForm1(forms.ModelForm):
    testimony_description = forms.CharField(label='', widget=forms.Textarea(
        attrs={'rows': 4, 'placeholder': 'Descreva a foto em até 1000 caracteres.'}
    ),
                                          max_length=1000,
                                          help_text='The max length of the text is 1000.',
                                          required=False,
                                          )

    class Meta:
        model = TestimonyModel
        fields = ['testimony_description',]


class TestimonyPhotoForm2(forms.ModelForm):
    testimony_professional = ProfessionalChoiceField(label='Se desejar marque o profissional que realizou o serviço',
                                                     queryset=ProfessionalModel.objects.filter(
                                                         professional_active=True), widget=forms.CheckboxSelectMultiple,
                                                     required=False)


    testimony_bride = forms.ModelChoiceField(label='Esta foto esta relacionada com alguma noiva marque se estiver.',
                                             queryset=BrideModel.objects.all(),
                                             empty_label="(Selecione uma noiva)",
                                             widget=forms.Select, required=False,
                                             )

    class Meta:
        model = TestimonyModel
        fields = ['testimony_professional', 'testimony_bride', 'testimony_active',]


class TestimonyPhotoUpdateForm(forms.ModelForm):
    testimony_description = forms.CharField(label='', widget=forms.Textarea(
        attrs={'rows': 4, 'placeholder': 'Descreva a foto em até 1000 caracteres.'}
    ),
                                            max_length=1000,
                                            help_text='Deve conter no maximo 1000 caracteres.',
                                            required=False,
                                            )

    testimony_professional = ProfessionalChoiceField(label='Se desejar marque o profissional que realizou o serviço',
                                                     queryset=ProfessionalModel.objects.filter(
                                                         professional_active=True), widget=forms.CheckboxSelectMultiple,
                                                     required=False)


    testimony_bride = forms.ModelChoiceField(label='Esta foto esta relacionada com alguma produção marque se estiver.',
                                             queryset=BrideModel.objects.all().order_by('bride_name'),
                                             empty_label="(Selecione uma produção)",
                                             widget=forms.Select, required=False,
                                             )

    class Meta:
        model = TestimonyModel
        fields = ['testimony_description', 'testimony_professional', 'testimony_bride', 'testimony_active',]


class TestimonyPhotoCommentForm(forms.ModelForm):

    class Meta:
        model = TestimonyModel
        fields = ['testimony_description', ]


class TestimonyBrideUpdateForm(forms.ModelForm):
    testimony_description = forms.CharField(label='', widget=forms.Textarea(
        attrs={'rows': 4, 'placeholder': 'Descreva a produção em até 1000 caracteres.'}
    ),
                                            max_length=1000,
                                            help_text='The max length of the text is 1000.', required=False,
                                            )

    testimony_professional = ProfessionalChoiceField(label='Se desejar marque o profissional que realizou o serviço',
                                                     queryset=ProfessionalModel.objects.filter(
                                                         professional_active=True), widget=forms.CheckboxSelectMultiple,
                                                     required=False)

    class Meta:
        model = TestimonyModel
        fields = ['testimony_description', 'testimony_professional', ]
