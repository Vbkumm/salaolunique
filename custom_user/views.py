from django.views.generic import UpdateView, ListView, DetailView
from django.urls import reverse_lazy, reverse
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from custom_user.models import CustomUser
from custom_user.forms import UpdateListUserForm
from django.shortcuts import get_object_or_404
from .forms import UpdateUserForm
from django.contrib.auth.decorators import login_required
from schedule.models import ScheduleModel
from datetime import datetime
from equipment.models import ServiceEquipmentModel
from django.utils.duration import _get_duration_components


class TermsView(TemplateView):
    template_name = "custom_user/terms.html"


class CookiesView(TemplateView):
    template_name = "custom_user/cookies.html"


@method_decorator(login_required, name='dispatch')
class UserDetailView(DetailView):
    model = CustomUser
    template_name = 'custom_user/user_detail.html'
    context_object_name = 'user_profile'

    def get_object(self):
        return get_object_or_404(CustomUser, username=self.kwargs['username'])

    def get_context_data(self, **kwargs):

        context = super(UserDetailView, self).get_context_data(**kwargs)

        photos_bookmark = list(self.object.photo_bookmark.all()[:])
        photos_bookmark_active = []

        for photo in photos_bookmark:

            if photo.testimony_photo.all():
                photo_testimony = photo.testimony_photo.all()[0]
                if photo_testimony.get_valid_testimony_photo() is True:
                    photos_bookmark_active.append(photo)

        context['photos_bookmark'] = photos_bookmark_active

        user_schedule_list = list(ScheduleModel.objects.filter(schedule_costumer__username=self.kwargs['username']))
        user_schedule_list_future = []
        for user_schedule in user_schedule_list:
            if user_schedule.schedule_date >= datetime.now().date():
                if user_schedule.schedule_canceled is False:
                    if user_schedule.schedule_service_done is False:
                        time = ServiceEquipmentModel.service_equipment_total_time(user_schedule.schedule_service, user_schedule.schedule_service)
                        days, hours, minutes, seconds, microseconds = _get_duration_components(
                            time)
                        string = ''

                        if minutes:
                            string = '{:02d} minutos'.format(minutes)

                        if hours and minutes:
                            string = ' e ' + string

                        if hours == 1:
                            string = '{:2d} hora'.format(hours) + string

                        if hours > 1:
                            string = '{:2d} horas'.format(hours) + string

                        user_schedule_list_future.append([user_schedule, string])

        context['user_schedule_list_future'] = user_schedule_list_future
        return context


@method_decorator(login_required, name='dispatch')
class UserUpdate(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
        form_class = UpdateUserForm
        template_name = 'custom_user/profile.html'
        success_message = f"Suas informações foram salvas com sucesso!"

        def get_object(self, queryset=None):
            return self.request.user

        def get_success_url(self):

            return reverse('custom_user:user_detail', kwargs={'username': self.request.user})


@method_decorator(staff_member_required, name='dispatch')
class CustomUserListView(ListView):
    template_name = 'custom_user/custom_user_list.html'
    model = CustomUser

    def get_context_data(self, **kwargs):
        context = super(CustomUserListView, self).get_context_data(**kwargs)
        return context


@method_decorator(staff_member_required, name='dispatch')
class UserUpdateListView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    form_class = UpdateListUserForm
    template_name = 'custom_user/user_is_professional.html'
    success_message = f"As informações foram salvas com sucesso!"

    def get_object(self):
        return get_object_or_404(CustomUser, username=self.kwargs['username'])

    def get_success_url(self):
        return reverse_lazy('custom_user:custom_user_list')


