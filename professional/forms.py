from django import forms
from .models import ProfessionalCategoryModel, ProfessionalModel, ProfessionalScheduleModel
from service.models import ServiceModel


class ServiceChoiceField(forms.ModelChoiceField):

    def __init__(self, obj_label=None, *args, **kwargs):
        super(ServiceChoiceField, self).__init__(*args, **kwargs)
        self.obj_label = obj_label

    def label_from_instance(self, obj):
        service_tittle = obj.service_tittle

        return f'{service_tittle}'


class ProfessionalCategoryChoiceField(forms.ModelMultipleChoiceField):

    def __init__(self, obj_label=None, *args, **kwargs):
        super(ProfessionalCategoryChoiceField, self).__init__(*args, **kwargs)
        self.obj_label = obj_label

    def label_from_instance(self, obj):
        category_professional = obj.category_professional
        return f'{category_professional}'


class ProfessionalForm(forms.ModelForm):
    professional_category = ProfessionalCategoryChoiceField(label='Quais habilidades esse profissional possui?',queryset=ProfessionalCategoryModel.objects.all(), widget=forms.CheckboxSelectMultiple, required=True)

    class Meta:
        model = ProfessionalModel
        fields = ['professional_category', 'professional_start_date', 'professional_active', ]


class ProfessionalCategoryForm(forms.ModelForm):

    class Meta:
        model = ProfessionalCategoryModel
        fields = ['category_professional', ]


class ProfessionalExtraSkillAddForm(forms.Form):
    professional_extra_service = forms.ModelChoiceField(queryset=ServiceModel.objects.all())


class ProfessionalNotSkillAddForm(forms.Form):
    professional_service_out = forms.ModelChoiceField(queryset=ServiceModel.objects.all())


WEEKDAYS_CHOICES = (
    ("0", "Domingo"),
    ("1", "Segunda-Feira"),
    ("2", "Terça-Feira"),
    ("3", "Quarta-Feira"),
    ("4", "Quinta-Feira"),
    ("5", "Sexta-Feira"),
    ("6", "Sabado"),
)


class ProfessionalScheduleForm(forms.ModelForm):

    professional_schedule_days = forms.ChoiceField(label='Dia da semana', choices=WEEKDAYS_CHOICES)
    professional_schedule_work_start = forms.TimeField(label='Qual primeiro horário para agendamento?',
                                    widget=forms.TimeInput(format='%H:%M'), initial='09:00')
    professional_schedule_work_end = forms.TimeField(label='Qual ultimo horário para agendamento?',
                                                       widget=forms.TimeInput(format='%H:%M'), initial='19:00')

    def __init__(self, *args, **kwargs):
        self.professional_schedule_days = kwargs.pop('professional_schedule_days', None)
        super(ProfessionalScheduleForm, self).__init__(*args, **kwargs)
        self.fields['professional_schedule_days'].choices = sorted(list({(k, v) for k, v in WEEKDAYS_CHOICES if int(k) not in self.professional_schedule_days}))

    class Meta:
        model = ProfessionalScheduleModel
        fields = ['professional_schedule_days', 'professional_schedule_work_start', 'professional_schedule_work_end', 'professional_schedule_time', ]


class ProfessionalScheduleUpdateForm(forms.ModelForm):

    professional_schedule_work_start = forms.TimeField(label='Qual primeiro horário para agendamento?',
                                    widget=forms.TimeInput(format='%H:%M'), initial='09:00')
    professional_schedule_work_end = forms.TimeField(label='Qual ultimo horário para agendamento?',
                                                       widget=forms.TimeInput(format='%H:%M'), initial='19:00')

    class Meta:
        model = ProfessionalScheduleModel
        fields = ['professional_schedule_work_start', 'professional_schedule_work_end', 'professional_schedule_time', ]
