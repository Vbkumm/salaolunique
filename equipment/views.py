import os
from .models import EquipmentModel
from django.views.generic import UpdateView, CreateView, ListView, DetailView, DeleteView
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib.messages.views import SuccessMessageMixin
from .forms import EquipmentForm1, EquipmentForm2, EquipmentUpdateForm, ServiceEquipmentUpdateForm, ServiceEquipmentFirstForm
from formtools.wizard.views import SessionWizardView
from django.utils import timezone
from django.urls import reverse_lazy
from equipment.models import ServiceEquipmentModel
from equipment.forms import ServiceEquipmentForm
from django.shortcuts import get_object_or_404
from service.models import ServiceModel
from datetime import timedelta
from django.utils.duration import _get_duration_components


@method_decorator(staff_member_required, name='dispatch')
class DashboardEquipmentWizardCreateView(SuccessMessageMixin, SessionWizardView):
    form_list = [EquipmentForm1, EquipmentForm2]
    template_name = 'equipment/equipment_wizard_create.html'
    success_message = "Equipamento criado com sucesso!"
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'equipment_storage'))

    def done(self, form_list, **kwargs):
        form_dict = self.get_all_cleaned_data()
        equipment = EquipmentModel()
        equipment.equipment_author = self.request.user
        for k, v in form_dict.items():
            if k != 'tags':
                setattr(equipment, k, v)
        equipment.save()

        return HttpResponseRedirect(reverse("equipment:equipment_detail", kwargs={'pk': equipment.pk}))


@method_decorator(staff_member_required, name='dispatch')
class EquipmentWizardCreateView(SuccessMessageMixin, SessionWizardView):
    form_list = [EquipmentForm1, EquipmentForm2]
    template_name = 'equipment/equipment_wizard_create.html'
    success_message = "Equipamento criado com sucesso!"
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'equipment_storage'))

    def done(self, form_list, **kwargs):
        service = get_object_or_404(ServiceModel, pk=self.kwargs.get('pk'))
        form_dict = self.get_all_cleaned_data()
        equipment = EquipmentModel()
        equipment.equipment_author = self.request.user
        for k, v in form_dict.items():
            if k != 'tags':
                setattr(equipment, k, v)
        equipment.save()

        return HttpResponseRedirect(reverse_lazy("service:equipment_service_create", kwargs={'pk': service.pk}))


@method_decorator(staff_member_required, name='dispatch')
class EquipmentUpdateView(SuccessMessageMixin, UpdateView):
    template_name = 'equipment/equipment_update.html'
    model = EquipmentModel
    form_class = EquipmentUpdateForm
    context_object_name = 'equipment'
    success_message = "Alterações feitas com sucesso!"

    def form_valid(self, form):
        form = EquipmentUpdateForm(data=self.request.POST, instance=self.object)
        form.instance.equipment_updated_at = timezone.now()
        form.instance.equipment_updated_by = self.request.user
        form.instance.save()
        if form.is_valid():
            return super(EquipmentUpdateView, self).form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self, *args, **kwargs):

        return reverse("equipment:equipment_detail", kwargs={'pk': self.object.pk})


@method_decorator(staff_member_required, name='dispatch')
class EquipmentDeleteView(DeleteView):
    template_name = 'equipment/equipment_delete.html'
    model = EquipmentModel
    pk_url_kwarg = 'pk'
    success_message = "Equipamento deletado com sucesso!"

    def get_success_url(self, *args, **kwargs):

        return reverse_lazy('equipment:equipment_list')


@method_decorator(staff_member_required, name='dispatch')
class EquipmentListView(ListView):
    template_name = 'equipment/equipment_list.html'
    model = EquipmentModel
    context_object_name = 'equipment_list'

    def get_queryset(self):
        queryset = super().get_queryset().all()
        return queryset


@method_decorator(staff_member_required, name='dispatch')
class EquipmentDetailView(DetailView):
    model = EquipmentModel
    template_name = 'equipment/equipment_detail.html'
    context_object_name = 'equipment'
    pk_url_kwarg = 'pk'


@method_decorator(staff_member_required, name='dispatch')
class ServiceEquipmentCreateView(SuccessMessageMixin, CreateView):
    model = ServiceEquipmentModel
    template_name = 'equipment/service_equipment_create.html'
    form_class = ServiceEquipmentForm
    success_message = "Equipamento adicinado ao serviço com sucesso!"

    def get_context_data(self, **kwargs):
        context = super(ServiceEquipmentCreateView, self).get_context_data(**kwargs)
        context['service'] = ServiceModel.objects.filter(pk=self.kwargs.get('pk'))

        return context

    def get_form_kwargs(self):
        kwargs = super(ServiceEquipmentCreateView, self).get_form_kwargs()
        service = self.kwargs['pk']
        kwargs['equipment_replaced'] = EquipmentModel.objects.filter(equipment__equipment_service=service)
        return kwargs

    def form_valid(self, model):
        service = get_object_or_404(ServiceModel, pk=self.kwargs.get('pk'))
        model.instance.equipment_service = service
        service.service_updated_at = timezone.now()
        service.service_updated_by = self.request.user
        service.save()
        model.instance.equipment_service_author = self.request.user
        model.instance.equipment_service_published = timezone.now()

        return super(ServiceEquipmentCreateView, self).form_valid(model)

    def get_success_url(self):
        service = self.object.equipment_service
        return reverse_lazy("service:equipment_service_list", kwargs={'pk': service.pk})


@method_decorator(staff_member_required, name='dispatch')
class ServiceEquipmentFirstCreateView(SuccessMessageMixin, CreateView):
    model = ServiceEquipmentModel
    template_name = 'equipment/service_equipment_create.html'
    form_class = ServiceEquipmentFirstForm
    success_message = "Equipamento adicinado ao serviço com sucesso!"

    def get_context_data(self, **kwargs):
        context = super(ServiceEquipmentFirstCreateView, self).get_context_data(**kwargs)
        context['service'] = ServiceModel.objects.filter(pk=self.kwargs.get('pk'))

        return context

    def form_valid(self, form):
        service = get_object_or_404(ServiceModel, pk=self.kwargs.get('pk'))
        form.instance.equipment_service = service
        service.service_updated_at = timezone.now()
        service.service_updated_by = self.request.user
        service.save()
        form.instance.equipment_service_author = self.request.user
        form.instance.equipment_service_published = timezone.now()

        return super(ServiceEquipmentFirstCreateView, self).form_valid(form)

    def get_success_url(self):
        service = self.object.equipment_service
        return reverse_lazy("service:equipment_service_list", kwargs={'pk': service.pk})


@method_decorator(staff_member_required, name='dispatch')
class ServiceEquipmentListView(ListView):
    template_name = 'equipment/service_equipment_list.html'
    model = ServiceEquipmentModel
    context_object_name = 'service_equipment_list'
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        queryset = super().get_queryset().filter(equipment_service=self.kwargs.get('pk'))
        return queryset

    def get_context_data(self, **kwargs):
        context = super(ServiceEquipmentListView, self).get_context_data(**kwargs)

        service_equipment_time_list = ServiceEquipmentModel.objects.filter(equipment_service__pk=self.kwargs.get('pk'))
        service_equipment_total_time = []

        for service_equipment in service_equipment_time_list:
            if service_equipment.equipment_replaced is None:
                service_equipment_time = service_equipment.equipment_time
                service_equipment_total_time.append(service_equipment_time)

        days, hours, minutes, seconds, microseconds = _get_duration_components(sum(service_equipment_total_time, timedelta()))
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

        return context


@method_decorator(staff_member_required, name='dispatch')
class ServiceEquipmentUpdateView(SuccessMessageMixin, UpdateView):
    template_name = 'equipment/service_equipment_update.html'
    model = ServiceEquipmentModel
    form_class = ServiceEquipmentUpdateForm
    context_object_name = 'service_equipment'
    pk_url_kwarg = 'equipment_service_pk'
    success_message = "Alterações feitas com sucesso!"

    def form_valid(self, form):
        service = get_object_or_404(ServiceModel, pk=self.kwargs.get('pk'))
        form = ServiceEquipmentUpdateForm(data=self.request.POST, instance=self.object)
        service.service_updated_at = timezone.now()
        service.service_updated_by = self.request.user
        service.save()
        form.instance.equipment_service_updated_at = timezone.now()
        form.instance.equipment_service_updated_by = self.request.user
        form.instance.save()
        if form.is_valid():
            return super(ServiceEquipmentUpdateView, self).form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self, *args, **kwargs):

        return reverse_lazy("service:equipment_service_list", kwargs={'pk': self.object.equipment_service.pk})


@method_decorator(staff_member_required, name='dispatch')
class ServiceEquipmentDeleteView(DeleteView):
    template_name = 'equipment/service_equipment_delete.html'
    model = ServiceEquipmentModel
    pk_url_kwarg = 'equipment_service_pk'
    success_message = " Equipamento retirado com sucesso!"

    def get_success_url(self, *args, **kwargs):

        return reverse_lazy("service:equipment_service_list", kwargs={'pk': self.object.equipment_service.pk})
