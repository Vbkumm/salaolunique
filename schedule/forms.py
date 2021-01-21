from django import forms
from .models import ScheduleModel
from professional.models import ProfessionalModel


class ScheduleForm1(forms.ModelForm):
    schedule_date = forms.DateField(label='Selecione uma data dentre as disponíveis:', widget=forms.TextInput(attrs={'class': 'datepicker'}))

    class Meta:
        model = ScheduleModel
        fields = ['schedule_date', ]


class ScheduleForm2(forms.ModelForm):
    schedule_hour = forms.ChoiceField(label='Selecione um horário dentre os disponíveis:', choices=[], widget=forms.Select)

    def __init__(self, *args, **kwargs):
        schedule_hour = kwargs.pop('schedule_hour', None)
        super(ScheduleForm2, self).__init__(*args, **kwargs)
        self.fields['schedule_hour'].choices = schedule_hour

    class Meta:
        model = ScheduleModel
        fields = ['schedule_hour', ]


class ScheduleForm3(forms.ModelForm):
    schedule_description = forms.CharField(label='', widget=forms.Textarea(
        attrs={'rows': 4, 'placeholder': 'Alguma observação?'}
    ),
                                          max_length=1000,
                                          help_text='Ultrapassou o limite de 1000 caracteres.',
                                          required=False,
                                          )
    schedule_professional = forms.ChoiceField(label='Selecione um profissional:',
                                      choices=[],
                                      initial="Profissionais disponíveis",
                                      widget=forms.Select,
                                      required=True,
                                      )

    def __init__(self, *args, **kwargs):

        schedule_professional = kwargs.pop('schedule_professional', None)
        super(ScheduleForm3, self).__init__(*args, **kwargs)
        self.fields['schedule_professional'].choices = schedule_professional

    def clean_schedule_professional(self):
        schedule_professional = ProfessionalModel.objects.get(professional_name__username=self.cleaned_data['schedule_professional'])
        return schedule_professional

    class Meta:
        model = ScheduleModel
        fields = ['schedule_professional', 'schedule_description', ]
