import os
from django.urls import reverse_lazy
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView, CreateView, ListView, DetailView, DeleteView
from django.urls import reverse
from django.utils import timezone
from django.contrib.messages.views import SuccessMessageMixin
from formtools.wizard.views import SessionWizardView
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from service.models import ServiceModel, ServiceCategoryModel, ProfessionalServicesSkillModel
from service.forms import ServiceForm1, ServiceForm2, ServiceUpdateForm, ServiceCategoryForm, DashboardServiceCategoryForm
from price.models import PriceModel
from testimony.models import TestimonyModel
from photo.models import ServicePhotoModel
from equipment.models import ServiceEquipmentModel
from datetime import timedelta
from django.utils.duration import _get_duration_components


@method_decorator(staff_member_required, name='dispatch')
class ServiceWizardCreateView(SuccessMessageMixin, SessionWizardView):
    form_list = [ServiceForm1, ServiceForm2]
    template_name = 'service/service_wizard_create.html'
    success_message = "Serviço criado com sucesso!"
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'service_storage'))

    def done(self, form_list, **kwargs):
        # get merged dictionary from all fields
        form_dict = self.get_all_cleaned_data()
        service = ServiceModel()
        service.service_author = self.request.user
        for k, v in form_dict.items():
            if k != 'tags':
                setattr(service, k, v)
        service.save()

        return HttpResponseRedirect(reverse("service:equipment_service_first_create", kwargs={'pk': service.pk}))


class ServiceDetailView(DetailView):
    model = ServiceModel
    template_name = 'service/service_detail.html'
    context_object_name = 'service'

    def get_context_data(self, **kwargs):

        context = super(ServiceDetailView, self).get_context_data(**kwargs)

        service_equipment_time_list = ServiceEquipmentModel.objects.filter(equipment_service__pk=self.kwargs.get('pk'))
        service_equipment_total_time = []
        equipment_exact_time = False

        for service_equipment in service_equipment_time_list:
            if service_equipment.equipment_replaced is None:
                service_equipment_time = service_equipment.equipment_time
                service_equipment_total_time.append(service_equipment_time)
                if service_equipment.equipment_time_exact is True:
                    equipment_exact_time = True

        context['equipment_exact_time'] = equipment_exact_time

        days, hours, minutes, seconds, microseconds = _get_duration_components(
            sum(service_equipment_total_time, timedelta()))
        string = ''

        if minutes:
            string = '{:02d} minutos'.format(minutes)

        if hours and minutes:
            string = ' e ' + string

        if hours == 1:
            string = '{:2d} hora'.format(hours) + string

        if hours > 1:
            string = '{:2d} horas'.format(hours) + string

        context['service_equipment_total_time'] = string

        professional_list = []
        professional_list_active = []

        professional_skill_list = ProfessionalServicesSkillModel.objects.all()
        for professional_skill in professional_skill_list:
            if self.object in professional_skill.professional_service_in.all():
                professional_list.append(professional_skill.service_professional_skill)
            if self.object in professional_skill.professional_service_out.all():
                professional_list.remove(professional_skill.service_professional_skill)
            if self.object in professional_skill.professional_extra_service.all():
                professional_list.append(professional_skill.service_professional_skill)

        for professional in professional_list:
            if professional.professional_active is True and professional.professional_name.is_professional is True:
                professional_list_active.append(professional)

        service_equipment_list = ServiceEquipmentModel.objects.filter(equipment_service=self.object)

        context['service_equipment_list'] = service_equipment_list
        context['professional_list'] = professional_list_active
        context['price_list'] = PriceModel.objects.filter(price_service=self.object)
        context['testimony_list'] = TestimonyModel.objects.filter(testimony_service=self.object).order_by('-testimony_published')
        session_key = 'viewed_service_{}'.format(self.object.pk)
        if not self.request.session.get(session_key, False):
            self.object.service_views += 1
            self.object.save()
            self.request.session[session_key] = True
        kwargs['service_views'] = self.object.service_views
        return context


@method_decorator(staff_member_required, name='dispatch')
class ServiceUpdateView(SuccessMessageMixin, UpdateView):
    template_name = 'service/service_update.html'
    model = ServiceModel
    form_class = ServiceUpdateForm
    success_message = "Alterações feitas com sucesso!"

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(service_author=self.request.user)

    def form_valid(self, form):
        form = ServiceUpdateForm(data=self.request.POST, instance=self.object)
        form.instance.service_updated_at = timezone.now()
        form.instance.service_updated_by = self.request.user
        form.instance.save()
        if form.is_valid():
            return super(ServiceUpdateView, self).form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self, *args, **kwargs):

        return reverse("service:service_detail", kwargs={'pk': self.object.pk})


@method_decorator(staff_member_required, name='dispatch')
class ServiceDeleteView(DeleteView):
    template_name = 'service/service_delete.html'
    model = ServiceModel
    pk_url_kwarg = 'pk'
    success_message = "Serviço deletado com sucesso!"

    def get_success_url(self, *args, **kwargs):

        return reverse("service:service_list", kwargs={'pk': self.object.pk})


class ServiceListView(ListView):
    model = ServiceModel
    context_object_name = 'service_list'
    template_name = 'service/service_list.html'

    def get_context_data(self, **kwargs):

        context = super(ServiceListView, self).get_context_data(**kwargs)
        photo_service_list = []
        service_list = list(self.object_list.filter(service_active=False)[:])

        for service in service_list:
            counter = 0
            photo_list = list(ServicePhotoModel.objects.filter(service_photo=service).order_by('-photo_published')[:])
            if len(service.service_photo.all()) < 1:
                photo_service_list.append([service, None])
            else:
                for photo in photo_list:
                    counter += 1
                    if service not in [i[0] for i in photo_service_list]:
                        if photo.get_valid_cover_photo() is True:
                            photo_last = photo
                            photo_service_list.append([service, photo_last])
                        else:
                            if counter == len(photo_list):
                                photo_service_list.append([service, None])

        context['testimony_photo_service_list'] = photo_service_list

        return context

    def get_queryset(self, *args, **kwargs):

        service_category = ServiceModel.objects.filter(service_category__id=self.kwargs['pk'])

        return service_category


@method_decorator(staff_member_required, name='dispatch')
class ServiceCategoryCreateView(SuccessMessageMixin, CreateView):
    model = ServiceCategoryModel
    template_name = 'service/service_category_create.html'
    form_class = ServiceCategoryForm
    success_message = "Categoria de serviço criada com sucesso!"

    def form_valid(self, model):

        model.instance.category_service_author = self.request.user
        return super(ServiceCategoryCreateView, self).form_valid(model)

    def get_success_url(self):
        return reverse_lazy('service:service_wizard_create')


@method_decorator(staff_member_required, name='dispatch')
class DashboardServiceCategoryCreateView(SuccessMessageMixin, CreateView):
    model = ServiceCategoryModel
    template_name = 'service/dashboard_service_category_create.html'
    form_class = DashboardServiceCategoryForm
    success_message = "Categoria de serviço criada com sucesso!"

    def form_valid(self, model):

        model.instance.category_service_author = self.request.user

        return super(DashboardServiceCategoryCreateView, self).form_valid(model)

    def get_success_url(self):
        return reverse_lazy('service:service_category_list')


@method_decorator(staff_member_required, name='dispatch')
class ServiceCategoryUpdateView(SuccessMessageMixin, UpdateView):
    template_name = 'service/service_category_update.html'
    model = ServiceCategoryModel
    form_class = ServiceCategoryForm
    success_message = "Alterações feitas com sucesso!"

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(category_service_author=self.request.user)

    def form_valid(self, form):
        form = ServiceCategoryForm(data=self.request.POST, instance=self.object)
        form.instance.category_service_updated_at = timezone.now()
        form.instance.category_service_updated_by = self.request.user
        form.instance.save()
        if form.is_valid():
            return super(ServiceCategoryUpdateView, self).form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self, *args, **kwargs):

        return reverse_lazy('service:service_category_list')


@method_decorator(staff_member_required, name='dispatch')
class ServiceCategoryDeleteView(DeleteView):
    template_name = 'service/service_category_delete.html'
    model = ServiceCategoryModel
    pk_url_kwarg = 'pk'
    success_message = "Categoria de serviço deletado com sucesso!"

    def get_success_url(self, *args, **kwargs):

        return reverse_lazy('service:service_category_list')


@method_decorator(staff_member_required, name='dispatch')
class ServiceCategoryListView(ListView):
    template_name = 'service/service_category_list.html'
    model = ServiceCategoryModel
    context_object_name = 'service_category_list'

    def get_queryset(self):
        queryset = super().get_queryset().all().order_by('-professional_category')
        return queryset


@method_decorator(staff_member_required, name='dispatch')
class ServiceInactiveListView(ListView):
    template_name = 'service/service_inactive_list.html'
    model = ServiceModel
    context_object_name = 'service_inactive_list'

    def get_queryset(self):
        queryset = super().get_queryset().filter(service_active=True).order_by('-service_category')
        return queryset


@method_decorator(staff_member_required, name='dispatch')
class ServiceActiveListView(ListView):
    template_name = 'service/service_active_list.html'
    model = ServiceModel
    context_object_name = 'service_active_list'

    def get_queryset(self):
        queryset = super().get_queryset().filter(service_active=False).order_by('-service_category')
        return queryset
