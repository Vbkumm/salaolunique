import os
from .models import ComboModel, ComboServiceModel
from django.views.generic import UpdateView, CreateView, ListView, DetailView, DeleteView
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib.messages.views import SuccessMessageMixin
from .forms import ComboForm1, ComboForm2, ComboServiceForm, ComboUpdateForm
from formtools.wizard.views import SessionWizardView
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone

# Create your views here.


@method_decorator(staff_member_required, name='dispatch')
class ComboWizardCreateView(SuccessMessageMixin, SessionWizardView):
    form_list = [ComboForm1, ComboForm2]
    template_name = 'combo/combo_wizard_create.html'
    success_message = "Pacote criado com sucesso!"
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'combo_storage'))

    def done(self, form_list, **kwargs):
        form_dict = self.get_all_cleaned_data()
        combo = ComboModel()
        combo.combo_author = self.request.user
        for k, v in form_dict.items():
            if k != 'tags':
                setattr(combo, k, v)
        combo.save()

        return HttpResponseRedirect(reverse("combo:combo_detail", kwargs={'pk': combo.pk}))


class ComboDetailView(DetailView):
    model = ComboModel
    template_name = 'combo/combo_detail.html'
    context_object_name = 'combo'

    def get_context_data(self, **kwargs):

        context = super(ComboDetailView, self).get_context_data(**kwargs)
        service_price_list = []
        service_combo = self.object

        for service in service_combo.combo_service_quantity.all():
            service_photo = []
            if service.combo_service.price_service is not None:
                service_quantity = service.service_quantity
                for service_price in service.combo_service.price_service.all():
                    if service_price.price_value is not None:
                        price = service_price
                        price_combo_original = price.price_value * service_quantity
                        for photo in service.combo_service.service_photo.all():
                            if photo.get_valid_cover_photo() is True:
                                service_photo.append(photo)
                        if service_photo:
                            photo = service_photo[0]
                        else:
                            photo = None
                        service_price_list.append([service, photo, price, service_quantity, price_combo_original])
                    else:
                        price = service_price
                        price_combo_original = 0
                        for photo in service.combo_service.service_photo.all():
                            if photo.get_valid_cover_photo() is True:
                                service_photo.append(photo)
                        if service_photo:
                            photo = service_photo[0]
                        else:
                            photo = None
                        service_price_list.append([service, photo, price, service_quantity, price_combo_original])

        context['service_list'] = service_price_list
        total_combo_price_value = sum(n[4] for n in service_price_list)
        context['total_combo_price_value'] = total_combo_price_value

        if total_combo_price_value is not None:
            for combo_price in self.object.price_combo.all():
                price = combo_price.price_value
                if price is not None:
                    discount = 100 - ((price * 100) / total_combo_price_value)

                    context['discount'] = discount

        session_key = 'viewed_combo_{}'.format(self.object.pk)
        if not self.request.session.get(session_key, False):
            self.object.combo_views += 1
            self.object.save()
            self.request.session[session_key] = True
        kwargs['combo_views'] = self.object.combo_views
        return context


@method_decorator(staff_member_required, name='dispatch')
class ComboListView(ListView):
    template_name = 'combo/combo_list.html'
    model = ComboModel
    context_object_name = 'combo_list'

    def get_queryset(self):
        queryset = super().get_queryset().all().order_by('-combo_active')
        return queryset


@method_decorator(staff_member_required, name='dispatch')
class ComboUpdateView(SuccessMessageMixin, UpdateView):
    template_name = 'combo/combo_update.html'
    model = ComboModel
    form_class = ComboUpdateForm
    success_message = "Alterações feitas com sucesso!"

    def form_valid(self, form):
        form = ComboUpdateForm(data=self.request.POST, instance=self.object)
        form.instance.combo_updated_at = timezone.now()
        form.instance.combo_updated_by = self.request.user
        form.instance.save()
        if form.is_valid():
            return super(ComboUpdateView, self).form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self, *args, **kwargs):

        return reverse("combo:combo_detail", kwargs={'pk': self.object.pk})


@method_decorator(staff_member_required, name='dispatch')
class ComboDeleteView(DeleteView):
    template_name = 'combo/combo_delete.html'
    model = ComboModel
    pk_url_kwarg = 'pk'
    success_message = "Produção deletada com sucesso!"

    def get_success_url(self, *args, **kwargs):

        return reverse_lazy('combo:combo_list')


@method_decorator(staff_member_required, name='dispatch')
class ComboServiceCreateView(SuccessMessageMixin, CreateView):
    model = ComboServiceModel
    template_name = 'combo/combo_service_create.html'
    form_class = ComboServiceForm
    success_message = "Categoria de serviço criada com sucesso!"

    def get_context_data(self, **kwargs):

        context = super(ComboServiceCreateView, self).get_context_data(**kwargs)
        context["combo"] = ComboModel.objects.filter(pk=self.kwargs.get('pk'))

        return context

    def form_valid(self, model):
        combo = get_object_or_404(ComboModel, pk=self.kwargs.get('pk'))
        model.instance.combo_service_quantity = combo
        combo.combo_updated_at = timezone.now()
        combo.combo_updated_by = self.request.user
        combo.save()
        model.instance.combo_service_author = self.request.user
        return super(ComboServiceCreateView, self).form_valid(model)

    def get_success_url(self):
        combo = self.object.combo_service_quantity
        return reverse_lazy("combo:combo_detail", kwargs={'pk': combo.pk})


@method_decorator(staff_member_required, name='dispatch')
class ComboServiceUpdateView(SuccessMessageMixin, UpdateView):
    template_name = 'combo/combo_service_update.html'
    model = ComboServiceModel
    form_class = ComboServiceForm
    pk_url_kwarg = 'service_pk'
    success_message = "Alterações feitas com sucesso!"

    def form_valid(self, form):
        combo = get_object_or_404(ComboModel, pk=self.kwargs.get('pk'))
        form = ComboServiceForm(data=self.request.POST, instance=self.object)
        combo.combo_updated_at = timezone.now()
        combo.combo_updated_by = self.request.user
        combo.save()
        form.instance.combo_service_updated_by = self.request.user
        if form.is_valid():
            return super(ComboServiceUpdateView, self).form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self, *args, **kwargs):

        return reverse_lazy("combo:combo_detail", kwargs={'pk': self.object.combo_service_quantity.pk})


@method_decorator(staff_member_required, name='dispatch')
class ComboServiceDeleteView(DeleteView):
    template_name = 'combo/combo_service_delete.html'
    model = ComboServiceModel
    pk_url_kwarg = 'service_pk'
    success_message = "Serviço deletado do pacote com sucesso!"

    def delete(self, *args, **kwargs):
        combo = get_object_or_404(ComboModel, pk=self.kwargs.get('pk'))
        combo.combo_updated_at = timezone.now()
        combo.combo_updated_by = self.request.user
        combo.save()
        return super(ComboServiceDeleteView, self).delete(*args, **kwargs)

    def get_success_url(self, *args, **kwargs):

        return reverse_lazy("combo:combo_detail", kwargs={'pk': self.object.combo_service_quantity.pk})
