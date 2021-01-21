from django.utils.decorators import method_decorator
from django.views.generic import UpdateView, CreateView, DetailView, DeleteView, ListView
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from .models import ProfessionalCategoryModel, ProfessionalModel, ProfessionalScheduleModel
from .forms import ProfessionalForm, ProfessionalCategoryForm, ProfessionalExtraSkillAddForm, ProfessionalNotSkillAddForm, ProfessionalScheduleForm, ProfessionalScheduleUpdateForm
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from photo.models import ServicePhotoModel
from service.models import ServiceModel, ProfessionalServicesSkillModel
from django.shortcuts import Http404
from django.shortcuts import HttpResponseRedirect
from schedule.models import ScheduleModel
from datetime import datetime
from equipment.models import ServiceEquipmentModel
from django.utils.duration import _get_duration_components


@method_decorator(staff_member_required, name='dispatch')
class ProfessionalUpdateView(SuccessMessageMixin, UpdateView):
    template_name = 'professional/professional_update.html'
    form_class = ProfessionalForm
    success_message = "Alterações feitas com sucesso!"

    def get_object(self):
        return get_object_or_404(ProfessionalModel, professional_name__username=self.kwargs['username'])

    def form_valid(self, form):
        form = ProfessionalForm(data=self.request.POST, instance=self.object)
        form.instance.professional_updated_at = timezone.now()
        form.instance.professional_updated_by = self.request.user
        form.instance.save()
        if form.is_valid():
            return super(ProfessionalUpdateView, self).form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('main:dashboard')


class ProfessionalDetailView(DetailView):
    model = ProfessionalModel
    template_name = 'professional/professional_detail.html'
    context_object_name = 'professional'

    def get_object(self):
        return get_object_or_404(ProfessionalModel, professional_name__username=self.kwargs['username'])

    def get_context_data(self, **kwargs):

        context = super(ProfessionalDetailView, self).get_context_data(**kwargs)
        category_list = []

        for category in self.object.professional_category.all():
            photo_service_list = []
            professional_service_skill = []
            professional_service_skill.extend(self.object.service_professional_skill.professional_service_in.all()[:])
            professional_service_skill = [x for x in professional_service_skill if x not in list(self.object.service_professional_skill.professional_service_out.all()[:])]
            for service in professional_service_skill:
                counter = 0
                if service.service_category.professional_category == category:
                    if len(service.service_photo.all()) < 1:
                        photo_service_list.append([service, None])
                    else:
                        photo_list = list(ServicePhotoModel.objects.filter(service_photo=service).order_by('-photo_published')[:])
                        for photo in photo_list:
                            counter += 1
                            if service not in [i[0] for i in photo_service_list]:
                                if photo.get_valid_cover_photo() is True:
                                    photo_last = photo
                                    photo_service_list.append([service, photo_last])
                                else:
                                    if counter == len(photo_list):
                                        photo_service_list.append([service, None])

                if category not in [i[0] for i in category_list]:
                    category_list.append([category, photo_service_list])
        context['testimony_photo_service_list'] = category_list
        professional_schedule_list = ScheduleModel.objects.filter(schedule_professional__professional_name__username=self.kwargs['username'])
        professional_schedule_list_future = []
        for professional_schedule in professional_schedule_list:
            if professional_schedule.schedule_date >= datetime.now().date():
                if professional_schedule.schedule_canceled is False:
                    if professional_schedule.schedule_service_done is False:
                        time = ServiceEquipmentModel.service_equipment_total_time(professional_schedule.schedule_service, professional_schedule.schedule_service)
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

                        professional_schedule_list_future.append([professional_schedule, string])

        context['professional_schedule_list_future'] = professional_schedule_list_future

        professional_extra_skill = list(self.object.service_professional_skill.professional_extra_service.all()[:])
        photo_extra_service_list = []
        for service in professional_extra_skill:
            counter = 0
            if len(service.service_photo.all()) < 1:
                photo_extra_service_list.append([service, None])
            else:
                photo_list = list(ServicePhotoModel.objects.filter(service_photo=service).order_by('-photo_published')[:])
                for photo in photo_list:
                    counter += 1
                    if service not in [i[0] for i in photo_extra_service_list]:
                        if photo.get_valid_cover_photo() is True:
                            photo_last = photo
                            photo_extra_service_list.append([service, photo_last])
                        else:
                            if counter == len(photo_list):
                                photo_extra_service_list.append([service, None])
        context['photo_extra_service_list'] = photo_extra_service_list

        service_list = list(ServiceModel.objects.filter(service_active=False)[:])
        professional_skill_list = []
        extra_service_list = [photo_extra_service_list]
        professional_skill_list.extend([i[1] for i in list(category_list[:])])
        professional_skill_list.extend([i for i in list(extra_service_list[:])])
        
        for professional_skill_category in professional_skill_list:
            for service in professional_skill_category:
                if service[0] in service_list:
                    service_list.remove(service[0])
        context['not_work_service_list'] = service_list

        schedule_professional_list = list(ProfessionalScheduleModel.objects.filter(professional_schedule=self.object)[:])
        context['schedule_professional_total'] = len(schedule_professional_list)
        context['schedule_professional_list'] = sorted(schedule_professional_list, key=lambda x: x.professional_schedule_days)

        session_key = 'viewed_professional_{}'.format(self.object.pk)
        if not self.request.session.get(session_key, False):
            self.object.professional_views += 1
            self.object.save()
            self.request.session[session_key] = True
        kwargs['professional_views'] = self.object.professional_views

        return context


def professional_extra_skill_add(request, username):
    professional_skill = get_object_or_404(ProfessionalServicesSkillModel, service_professional_skill__professional_name__username=username)
    professional_extra_service_add_form = ProfessionalExtraSkillAddForm(request.POST or None)

    if request.method == 'POST' and professional_extra_service_add_form.is_valid():
        professional_add_skill = professional_extra_service_add_form.cleaned_data['professional_extra_service']
        if professional_add_skill in professional_skill.professional_extra_service.all():
            professional_skill.professional_extra_service.remove(professional_add_skill)

        else:
            professional_skill.professional_extra_service.add(professional_add_skill)

        professional_skill.save()

        return HttpResponseRedirect(reverse_lazy("professional:professional_detail",  kwargs={'username': username}))

    raise Http404()


def professional_not_skill_add(request, username):
    professional_skill = get_object_or_404(ProfessionalServicesSkillModel, service_professional_skill__professional_name__username=username)
    professional_not_service_add_form = ProfessionalNotSkillAddForm(request.POST or None)

    if request.method == 'POST' and professional_not_service_add_form.is_valid():
        professional_not_skill = professional_not_service_add_form.cleaned_data['professional_service_out']
        if professional_not_skill in professional_skill.professional_service_out.all():
            professional_skill.professional_service_out.remove(professional_not_skill)
        else:
            professional_skill.professional_service_out.add(professional_not_skill)

        professional_skill.save()

        return HttpResponseRedirect(reverse_lazy("professional:professional_detail",  kwargs={'username': username}))

    raise Http404()


@method_decorator(staff_member_required, name='dispatch')
class ProfessionalCategoryCreateView(SuccessMessageMixin, CreateView):
    model = ProfessionalCategoryModel
    template_name = 'professional/professional_category_create.html'
    form_class = ProfessionalCategoryForm
    success_message = "Categoria de profissional criada com sucesso!"

    def form_valid(self, model):
        model.instance.category_professional_author = self.request.user
        return super().form_valid(model)

    def get_success_url(self):
        return reverse_lazy('service:service_category_create')


@method_decorator(staff_member_required, name='dispatch')
class DashboardProfessionalCategoryCreateView(SuccessMessageMixin, CreateView):
    model = ProfessionalCategoryModel
    template_name = 'professional/dashboard_professional_category_create.html'
    form_class = ProfessionalCategoryForm
    success_message = "Categoria de profissional criada com sucesso!"

    def form_valid(self, model):
        model.instance.category_professional_author = self.request.user
        return super().form_valid(model)

    def get_success_url(self):
        return reverse_lazy('professional:professional_category_list')


@method_decorator(staff_member_required, name='dispatch')
class ProfessionalCategoryUpdateView(SuccessMessageMixin, UpdateView):
    template_name = 'professional/professional_category_update.html'
    model = ProfessionalCategoryModel
    form_class = ProfessionalCategoryForm
    success_message = "Alterações feitas com sucesso!"
    pk_url_kwarg = 'pk'

    def form_valid(self, form):
        form = ProfessionalCategoryForm(data=self.request.POST, instance=self.object)
        form.instance.category_professional_updated_at = timezone.now()
        form.instance.category_professional_updated_by = self.request.user
        form.instance.save()
        if form.is_valid():
            return super(ProfessionalCategoryUpdateView, self).form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('professional:professional_category_list')


@method_decorator(staff_member_required, name='dispatch')
class ProfessionalCategoryDeleteView(DeleteView):
    template_name = 'professional/professional_category_delete.html'
    model = ProfessionalCategoryModel
    pk_url_kwarg = 'pk'
    success_message = "Categoria de profissional deletado com sucesso!"

    def get_success_url(self, *args, **kwargs):

        return reverse_lazy('professional:professional_category_list')


@method_decorator(staff_member_required, name='dispatch')
class ProfessionalActiveListView(ListView):
    template_name = 'professional/professional_active_list.html'
    model = ProfessionalModel
    context_object_name = 'professional_active_list'

    def get_queryset(self):
        user_list = super().get_queryset().filter(professional_active=True)
        queryset = []
        for user in user_list.all():
            if user.professional_name.is_professional:
                queryset.append(user)
        return queryset


@method_decorator(staff_member_required, name='dispatch')
class ProfessionalInactiveListView(ListView):
    template_name = 'professional/professional_inactive_list.html'
    model = ProfessionalModel
    context_object_name = 'professional_inactive_list'

    def get_queryset(self):
        user_list = super().get_queryset().filter(professional_active=False)
        queryset = []
        for user in user_list.all():
            if user.professional_name.is_professional is True:
                queryset.append(user)
        return queryset


@method_decorator(staff_member_required, name='dispatch')
class ProfessionalCategoryListView(ListView):
    template_name = 'professional/professional_category_list.html'
    model = ProfessionalCategoryModel
    context_object_name = 'professional_category_list'

    def get_queryset(self):
        queryset = super().get_queryset().all()
        return queryset


@method_decorator(staff_member_required, name='dispatch')
class ProfessionalScheduleCreateView(SuccessMessageMixin, CreateView):
    model = ProfessionalScheduleModel
    template_name = 'professional/professional_schedule_create.html'
    form_class = ProfessionalScheduleForm
    success_message = "Dia da semana adicionado ao profissional com sucesso!"

    def get_context_data(self, **kwargs):

        context = super(ProfessionalScheduleCreateView, self).get_context_data(**kwargs)
        context['professional'] = ProfessionalModel.objects.filter(professional_name__username=self.kwargs.get('username'))
        return context

    def get_form_kwargs(self):
        kwargs = super(ProfessionalScheduleCreateView, self).get_form_kwargs()
        professional = ProfessionalModel.objects.filter(professional_name__username=self.kwargs.get('username'))
        schedule_day_list = []

        for professional_schedule in professional:
            if professional_schedule.professional_schedule:
                for schedule_day in professional_schedule.professional_schedule.all():
                    schedule_day_list.append(schedule_day.professional_schedule_days)
            kwargs['professional_schedule_days'] = schedule_day_list

            return kwargs

    def form_valid(self, form):
        professional = get_object_or_404(ProfessionalModel, professional_name__username=self.kwargs.get('username'))
        form.instance.professional_schedule = professional
        form.instance.professional_schedule_author = self.request.user
        form.instance.professional_schedule_published = timezone.now()

        if form.is_valid():
            return super(ProfessionalScheduleCreateView, self).form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        username = self.kwargs['username']
        return reverse_lazy('professional:professional_detail',  kwargs={'username': username})


@method_decorator(staff_member_required, name='dispatch')
class ProfessionalScheduleUpdateView(SuccessMessageMixin, UpdateView):
    template_name = 'professional/professional_schedule_update.html'
    model = ProfessionalScheduleModel
    form_class = ProfessionalScheduleUpdateForm
    success_message = "Alterações nos horários feitas com sucesso!"
    pk_url_kwarg = 'professional_schedule_pk'

    def form_valid(self, form):
        form = ProfessionalScheduleUpdateForm(data=self.request.POST, instance=self.object)
        form.instance.professional_schedule_updated_at = timezone.now()
        form.instance.professional_schedule_updated_by = self.request.user
        form.instance.save()
        if form.is_valid():
            return super(ProfessionalScheduleUpdateView, self).form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        username = self.kwargs['username']
        return reverse_lazy('professional:professional_detail', kwargs={'username': username})


@method_decorator(staff_member_required, name='dispatch')
class ProfessionalScheduleDeleteView(DeleteView):
    template_name = 'professional/professional_schedule_delete.html'
    model = ProfessionalScheduleModel
    pk_url_kwarg = 'professional_schedule_pk'
    success_message = "Dia da agenda retirado com sucesso!"

    def get_success_url(self, *args, **kwargs):
        username = self.kwargs['username']
        return reverse_lazy('professional:professional_detail', kwargs={'username': username})

