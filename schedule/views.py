import os
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import CreateView, DetailView
from .models import ScheduleModel
from .forms import ScheduleForm1, ScheduleForm2, ScheduleForm3
from service.models import ServiceModel
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.urls import reverse_lazy
from formtools.wizard.views import SessionWizardView
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from datetime import date, datetime, time, timedelta
from professional.models import ProfessionalModel, ProfessionalScheduleModel
from django.shortcuts import HttpResponseRedirect
from django.forms.models import construct_instance
from equipment.models import ServiceEquipmentModel


def total_minutes_int(td):
    return int(td.total_seconds() / 60)


def verify_professional_schedule_breaks(schedule_time, schedule_breaks):
    for i in schedule_breaks:
        if i is not None:
            if i[0] == schedule_time:
                schedule_breaks = sorted([(val, key) for (val, key) in schedule_breaks if val != schedule_time])
    return schedule_breaks


def professional_schedule_breaks_checker(professional_schedule_time, professional_schedule_busy_hour_list, professional_schedule_breaks):
    if professional_schedule_time not in professional_schedule_busy_hour_list:
        if professional_schedule_time not in [i[0] for i in professional_schedule_breaks]:

            return professional_schedule_time


@method_decorator(login_required, name='dispatch')
class ScheduleWizardCreateView(SuccessMessageMixin, SessionWizardView):
    form_list = [ScheduleForm1, ScheduleForm2, ScheduleForm3]
    template_name = 'schedule/schedule_wizard_create.html'
    success_message = "Serviço criado com sucesso!"
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'schedule_storage'))

    def get_context_data(self, **kwargs):
        context = super(ScheduleWizardCreateView, self).get_context_data(**kwargs)
        context['service'] = ServiceModel.objects.filter(pk=self.kwargs.get('pk'))
        service = get_object_or_404(ServiceModel, pk=self.kwargs.get('pk'))
        professional_schedule_day_list = []
        weekdays = list(range(0, 7))
        professional_list = ProfessionalModel.objects.filter(professional_active=True).filter(professional_category__service_professional__service_category=service)
        for professional in professional_list:
            if professional.professional_name != self.request.user and professional.professional_schedule is not None:
                professional_schedule = ProfessionalScheduleModel.objects.filter(professional_schedule=professional)
                if len(professional_schedule) >= 1:
                    for professional_schedule_day in professional_schedule:
                        if professional_schedule_day.professional_schedule_days not in professional_schedule_day_list:
                            professional_schedule_day_list.append(professional_schedule_day.professional_schedule_days)
        professional_schedule_day_off = [item for item in weekdays if item not in professional_schedule_day_list]
        context['professional_schedule_day_off'] = professional_schedule_day_off

        base = date.today()
        schedule_date_year_list = [base + timedelta(days=x) for x in range(120)]
        professional_schedule_breaks = []
        busy_date_list = []
        for schedule_date in schedule_date_year_list:
            if schedule_date.weekday() not in professional_schedule_day_off:

                if professional_list:

                    for professional in professional_list:

                        if professional.professional_name != self.request.user and professional.professional_schedule:

                            professional_schedule_day_list = ProfessionalScheduleModel.schedule_by_professional(
                                professional.professional_schedule, professional, schedule_date.weekday() + 1)
                            if professional_schedule_day_list:
                                professional_schedule_day = professional_schedule_day_list.first()
                                professional_schedule_time = professional_schedule_day.professional_schedule_work_start
                                professional_schedule_busy_hour_list = []
                                if professional_schedule_breaks_checker(professional_schedule_time,
                                                                        professional_schedule_busy_hour_list,
                                                                        professional_schedule_breaks):
                                    professional_schedule_time = professional_schedule_breaks_checker(
                                        professional_schedule_time, professional_schedule_busy_hour_list,
                                        professional_schedule_breaks)
                                    professional_schedule_breaks.append(
                                        (professional_schedule_time, str(professional_schedule_time)[:5]))

                                while professional_schedule_day.professional_schedule_work_end > professional_schedule_time:
                                    time1 = professional_schedule_time
                                    time2 = timedelta(minutes=professional_schedule_day.professional_schedule_time)
                                    tmp_datetime = datetime.combine(date(1, 1, 1), time1)
                                    professional_schedule_time = (tmp_datetime + time2).time()

                                    if professional_schedule_breaks_checker(professional_schedule_time,
                                                                            professional_schedule_busy_hour_list,
                                                                            professional_schedule_breaks):
                                        professional_schedule_time = professional_schedule_breaks_checker(
                                            professional_schedule_time, professional_schedule_busy_hour_list,
                                            professional_schedule_breaks)
                                        professional_schedule_breaks.append(
                                            (professional_schedule_time, str(professional_schedule_time)[:5]))

                                    for schedule_professional in professional.schedule_professional.all():
                                        if schedule_professional.schedule_date == schedule_date:
                                            equipment_schedule_start = schedule_professional.schedule_hour
                                            professional_schedule_breaks = verify_professional_schedule_breaks(
                                                equipment_schedule_start, professional_schedule_breaks)
                                            equipment_time_booking = ServiceEquipmentModel.service_equipment_total_time(
                                                self,
                                                service)
                                            equipment_time_booked = ServiceEquipmentModel.service_equipment_total_time(
                                                schedule_professional.schedule_service.equipment_service,
                                                schedule_professional.schedule_service)

                                            if equipment_schedule_start <= professional_schedule_time < (
                                                    datetime.combine(date(1, 1, 1),
                                                                     equipment_schedule_start) + equipment_time_booked).time():

                                                professional_schedule_busy_hour_list.append(professional_schedule_time)
                                                professional_schedule_breaks = verify_professional_schedule_breaks(
                                                    professional_schedule_time, professional_schedule_breaks)
                                                if professional_schedule_day.professional_schedule_time < total_minutes_int(
                                                        equipment_time_booking):
                                                    professional_schedule_before_time = (datetime.combine(date(1, 1, 1),
                                                                                                          professional_schedule_time) - timedelta(
                                                        seconds=(
                                                                professional_schedule_day.professional_schedule_time * 60))).time()
                                                    professional_schedule_busy_hour_list.append(
                                                        professional_schedule_before_time)
                                                    professional_schedule_breaks = verify_professional_schedule_breaks(
                                                        professional_schedule_before_time, professional_schedule_breaks)

                                        if professional_schedule_time == schedule_professional.schedule_hour:
                                            professional_schedule_busy_hour_list.append(professional_schedule_time)

                                        if professional_schedule_breaks_checker(professional_schedule_time,
                                                                                professional_schedule_busy_hour_list,
                                                                                professional_schedule_breaks):
                                            professional_schedule_time = professional_schedule_breaks_checker(
                                                professional_schedule_time, professional_schedule_busy_hour_list,
                                                professional_schedule_breaks)
                                            professional_schedule_breaks.append(
                                                (professional_schedule_time, str(professional_schedule_time)[:5]))
                if not professional_schedule_breaks:
                    busy_date_list.append(str(schedule_date.strftime("%d-%m-%Y")))

        context['busy_date_list'] = busy_date_list

        return context

    def get_form_kwargs(self, step=None):
        kwargs = super(ScheduleWizardCreateView, self).get_form_kwargs(step)
        service = get_object_or_404(ServiceModel, pk=self.kwargs.get('pk'))
        professional_list = ProfessionalModel.objects.filter(professional_active=True).filter(professional_name__is_professional=True).filter(professional_category__service_professional__service_category=service)
        professional_schedule_breaks = []

        if step == '1':
            schedule_date = self.get_cleaned_data_for_step('0')['schedule_date']

            if professional_list:
                for equipment in service.equipment_service.all():
                    custom_user = self.request.user
                    professional_list_len = len(ProfessionalModel.objects.filter(professional_category=service.service_category.professional_category))
                    if custom_user in [i.professional_name for i in professional_list]:
                        if service.service_category.professional_category in custom_user.professional_custom_user.professional_category.all():
                            professional_list_len -= 1
                            print(f"precisaria mais equipamento caso cliente nao fosse prof")
                    if professional_list_len > equipment.equipment_tittle.equipment_quantity:
                        print(f"precisa mais equipamento{professional_list_len}")



                for professional in professional_list:
                    if professional.professional_name != self.request.user:

                        if professional.professional_schedule:

                            professional_schedule_day_list = ProfessionalScheduleModel.schedule_by_professional(professional.professional_schedule, professional, schedule_date.weekday() + 1)
                            if professional_schedule_day_list:
                                professional_schedule_day = professional_schedule_day_list.first()
                                professional_schedule_time = professional_schedule_day.professional_schedule_work_start
                                professional_schedule_busy_hour_list = []
                                if professional_schedule_breaks_checker(professional_schedule_time, professional_schedule_busy_hour_list, professional_schedule_breaks):
                                    professional_schedule_time = professional_schedule_breaks_checker(professional_schedule_time, professional_schedule_busy_hour_list, professional_schedule_breaks)
                                    professional_schedule_breaks.append((professional_schedule_time, str(professional_schedule_time)[:5]))

                                while professional_schedule_day.professional_schedule_work_end > professional_schedule_time:
                                    time1 = professional_schedule_time
                                    time2 = timedelta(minutes=professional_schedule_day.professional_schedule_time)
                                    tmp_datetime = datetime.combine(date(1, 1, 1), time1)
                                    professional_schedule_time = (tmp_datetime + time2).time()

                                    if professional_schedule_breaks_checker(professional_schedule_time, professional_schedule_busy_hour_list, professional_schedule_breaks):
                                        professional_schedule_time = professional_schedule_breaks_checker(professional_schedule_time, professional_schedule_busy_hour_list, professional_schedule_breaks)
                                        professional_schedule_breaks.append((professional_schedule_time, str(professional_schedule_time)[:5]))

                                    for schedule_professional in professional.schedule_professional.all():
                                        if schedule_professional.schedule_date == schedule_date:
                                            equipment_schedule_start = schedule_professional.schedule_hour
                                            professional_schedule_breaks = verify_professional_schedule_breaks(equipment_schedule_start, professional_schedule_breaks)
                                            equipment_time_booking = ServiceEquipmentModel.service_equipment_total_time(self, service)
                                            equipment_time_booked = ServiceEquipmentModel.service_equipment_total_time(schedule_professional.schedule_service.equipment_service, schedule_professional.schedule_service)

                                            if equipment_schedule_start <= professional_schedule_time < (datetime.combine(date(1,1,1), equipment_schedule_start) + equipment_time_booked).time():

                                                professional_schedule_busy_hour_list.append(professional_schedule_time)
                                                professional_schedule_breaks = verify_professional_schedule_breaks(professional_schedule_time, professional_schedule_breaks)
                                                if professional_schedule_day.professional_schedule_time < total_minutes_int(equipment_time_booking):
                                                    professional_schedule_before_time = (datetime.combine(date(1, 1, 1), professional_schedule_time) - timedelta(seconds=(professional_schedule_day.professional_schedule_time * 60))).time()
                                                    professional_schedule_busy_hour_list.append(professional_schedule_before_time)
                                                    professional_schedule_breaks = verify_professional_schedule_breaks(professional_schedule_before_time, professional_schedule_breaks)

                                        if professional_schedule_time == schedule_professional.schedule_hour:
                                            professional_schedule_busy_hour_list.append(professional_schedule_time)

                                        if professional_schedule_breaks_checker(professional_schedule_time, professional_schedule_busy_hour_list, professional_schedule_breaks):
                                            professional_schedule_time = professional_schedule_breaks_checker(professional_schedule_time, professional_schedule_busy_hour_list, professional_schedule_breaks)
                                            professional_schedule_breaks.append((professional_schedule_time, str(professional_schedule_time)[:5]))

            kwargs['schedule_hour'] = sorted(professional_schedule_breaks)

        professional_available_list = []

        if step == '2':
            schedule_date = self.get_cleaned_data_for_step('0')['schedule_date']
            schedule_hour = self.get_cleaned_data_for_step('1')['schedule_hour']
            for professional in professional_list:
                professional_busy_list = []
                if professional.professional_name == self.request.user:
                    professional_busy_list.append(professional)
                professional_schedule_day_list = ProfessionalScheduleModel.schedule_by_professional(professional.professional_schedule, professional, schedule_date.weekday() + 1)
                if professional_schedule_day_list:
                    professional_schedule_day = professional_schedule_day_list.first()

                    for schedule_professional in professional.schedule_professional.all():
                        if schedule_professional.schedule_date == schedule_date:
                            equipment_time_booking = ServiceEquipmentModel.service_equipment_total_time(self, service)
                            equipment_time_booked = ServiceEquipmentModel.service_equipment_total_time(schedule_professional.schedule_service.equipment_service, schedule_professional.schedule_service)
                            equipment_schedule_start = schedule_professional.schedule_hour

                            if str(schedule_hour) == str(equipment_schedule_start):
                                professional_busy_list.append(schedule_professional.schedule_professional)

                            if equipment_schedule_start <= datetime.strptime(schedule_hour, '%H:%M:%S').time() < (datetime.combine(date(1, 1, 1), equipment_schedule_start) + equipment_time_booked).time():

                                professional_busy_list.append(schedule_professional.schedule_professional)
                                if professional_schedule_day.professional_schedule_time < total_minutes_int(equipment_time_booking):
                                    professional_busy_list.append(schedule_professional.schedule_professional)

                    if professional not in professional_busy_list:
                        if professional.professional_name.first_name:
                            professional_available_list.append((professional.professional_name.username, f'{professional.professional_name.first_name} {professional.professional_name.last_name}'))
                        else:
                            professional_available_list.append((professional.professional_name.username, f'{professional.professional_name.username}'))
            kwargs['schedule_professional'] = professional_available_list

        return kwargs

    def done(self, form_list, **kwargs):
        form_data = [form.cleaned_data for form in form_list]
        schedule = ScheduleModel()
        service = get_object_or_404(ServiceModel, pk=self.kwargs.get('pk'))
        schedule.schedule_service = service
        schedule.schedule_costumer = self.request.user
        schedule.schedule_author = self.request.user
        schedule.schedule_published = timezone.now()
        for form in form_list:
            schedule = construct_instance(form, schedule, form._meta.fields, form._meta.exclude)
            schedule.schedule_date = form_data[0]['schedule_date']
            schedule.schedule_hour = form_data[1]['schedule_hour']
            schedule.schedule_professional = form_data[2]['schedule_professional']

            schedule.save()

        username = schedule.schedule_costumer

        return HttpResponseRedirect(reverse_lazy("custom_user:user_detail", kwargs={'username': username}))


@method_decorator(login_required, name='dispatch')
class ScheduleDetailView(DetailView):
    model = ScheduleModel
    template_name = 'schedule/schedule_detail.html'
    pk_url_kwarg = 'pk'
    context_object_name = 'schedule'
