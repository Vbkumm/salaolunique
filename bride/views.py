from .forms import BrideForm1, BrideForm2, BrideUpdateForm
import os
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.urls import reverse, reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from formtools.wizard.views import SessionWizardView
from django.utils import timezone
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .models import BrideModel
from django.views.generic import DetailView, UpdateView, DeleteView, ListView
from testimony.models import TestimonyModel

# Create your views here.


@method_decorator(staff_member_required, name='dispatch')
class BrideWizardCreateView(SuccessMessageMixin, SessionWizardView):
    form_list = [BrideForm1, BrideForm2,]
    template_name = 'bride/bride_wizard_create.html'
    success_message = "Noiva registrada com sucesso!"
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'bride_storage'))

    def done(self, form_list, **kwargs):
        # get merged dictionary from all fields
        form_dict = self.get_all_cleaned_data()
        bride = BrideModel()
        bride.bride_register_user = self.request.user
        for k, v in form_dict.items():
            if k != 'tags':
                setattr(bride, k, v)
        bride.save()
        testimony_bride = TestimonyModel.objects.filter(testimony_bride=bride)

        return HttpResponseRedirect(reverse("testimony:testimony_bride_update", kwargs={'pk': bride.pk, 'testimony_bride_pk': testimony_bride[0].pk}))


class BrideDetailView(DetailView):
    model = BrideModel
    template_name = 'bride/bride_detail.html'
    context_object_name = 'bride'

    def get_context_data(self, **kwargs):

        context = super(BrideDetailView, self).get_context_data(**kwargs)
        session_key = 'viewed_bride_{}'.format(self.object.pk)
        if not self.request.session.get(session_key, False):
            self.object.bride_views += 1
            self.object.save()
            self.request.session[session_key] = True
        kwargs['bride_views'] = self.object.bride_views
        return context


@method_decorator(staff_member_required, name='dispatch')
class BrideUpdateView(SuccessMessageMixin, UpdateView):
    template_name = 'bride/bride_update.html'
    model = BrideModel
    form_class = BrideUpdateForm
    success_message = "Alterações feitas com sucesso!"

    def form_valid(self, form):
        form = BrideUpdateForm(data=self.request.POST, instance=self.object)
        form.instance.bride_updated_at = timezone.now()
        form.instance.bride_updated_by = self.request.user
        form.instance.save()
        if form.is_valid():
            return super(BrideUpdateView, self).form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self, *args, **kwargs):

        return reverse("bride:bride_detail", kwargs={'pk': self.object.pk})


@method_decorator(staff_member_required, name='dispatch')
class BrideDeleteView(DeleteView):
    template_name = 'bride/bride_delete.html'
    model = BrideModel
    pk_url_kwarg = 'pk'
    success_message = "Produção deletada com sucesso!"

    def get_success_url(self, *args, **kwargs):

        return reverse_lazy('main:dashboard')


@method_decorator(staff_member_required, name='dispatch')
class BrideActiveListView(ListView):
    template_name = 'bride/bride_active_list.html'
    model = BrideModel
    context_object_name = 'bride_active_list'

    def get_queryset(self):
        queryset = super().get_queryset().filter(bride_active=True).order_by('-bride_category')
        return queryset


@method_decorator(staff_member_required, name='dispatch')
class BrideInactiveListView(ListView):
    template_name = 'bride/bride_inactive_list.html'
    model = BrideModel
    context_object_name = 'bride_inactive_list'

    def get_queryset(self):
        queryset = super().get_queryset().filter(bride_active=False).order_by('-bride_category')
        return queryset
