from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic import UpdateView, CreateView, DetailView
from django.urls import reverse
from django.contrib.messages.views import SuccessMessageMixin
from .models import PriceModel
from .forms import PriceForm
from django.utils import timezone
from combo.models import ComboModel
from service.models import ServiceModel


@method_decorator(staff_member_required, name='dispatch')
class PriceServiceUpdateView(SuccessMessageMixin, UpdateView):

    form_class = PriceForm
    model = PriceModel
    pk_url_kwarg = 'price_pk'
    context_object_name = 'price'
    template_name = 'price/price_service_update.html'
    success_message = "Alterações no preçø feitas com sucesso!"

    def form_valid(self, form):
        price = self.get_form()
        price.instance.price_service = ServiceModel.objects.get(id=self.kwargs.get('pk'))
        price.instance.old_price_value = price.instance.price_value_tracker.previous('price_value')
        price.instance.price_updated_at = timezone.now()
        price.instance.price_updated_by = self.request.user
        price.save()
        form = PriceForm(data=self.request.POST, instance=self.object)
        if form.is_valid():
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self, *args, **kwargs):
        service = ServiceModel.objects.get(id=self.kwargs.get('pk'))
        return reverse("service:service_detail", kwargs={'pk': service.pk})


@method_decorator(staff_member_required, name='dispatch')
class PriceServiceDetailView(DetailView):
    model = PriceModel
    template_name = 'price/price_service_detail.html'
    pk_url_kwarg = 'price_pk'
    context_object_name = 'price'

    def get_success_url(self, *args, **kwargs):
        service = ServiceModel.objects.get(id=self.kwargs.get('pk'))
        return reverse("service:service_detail", kwargs={'pk': service.pk})


@method_decorator(staff_member_required, name='dispatch')
class PriceComboUpdateView(SuccessMessageMixin, UpdateView):

    form_class = PriceForm
    model = PriceModel
    pk_url_kwarg = 'price_pk'
    context_object_name = 'price'
    template_name = 'price/price_combo_update.html'
    success_message = "Alterações no preçø feitas com sucesso!"

    def form_valid(self, form):
        price = self.get_form()
        price.instance.price_combo = ComboModel.objects.get(id=self.kwargs.get('pk'))
        price.instance.old_price_value = price.instance.price_value_tracker.previous('price_value')
        price.instance.price_updated_at = timezone.now()
        price.instance.price_updated_by = self.request.user
        price.save()
        form = PriceForm(data=self.request.POST, instance=self.object)
        if form.is_valid():
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self, *args, **kwargs):
        combo = ComboModel.objects.get(id=self.kwargs.get('pk'))
        return reverse("combo:combo_detail", kwargs={'pk': combo.pk})

