from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic import CreateView, DeleteView, UpdateView
from django.contrib.messages.views import SuccessMessageMixin
from .models import ServicePhotoModel
from service.models import ServiceModel
from .forms import ServicePhotoForm, ServicePhotoCoverForm
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse


@method_decorator(staff_member_required, name='dispatch')
class ServicePhotoCreateView(SuccessMessageMixin, CreateView):

    def get(self, request, *args, **kwargs):
        service = get_object_or_404(ServiceModel, pk=self.kwargs.get('pk'))
        service_photo_list = ServicePhotoModel.objects.filter(service_photo=service)

        return render(self.request, 'photo/service_photo_create.html', {'service': service, 'service_photo_list': service_photo_list})

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(photo_author=self.request.user)

    def post(self, request, *args, **kwargs):
        service = get_object_or_404(ServiceModel, pk=self.kwargs.get('pk'))
        if request.method == 'POST':
            form = ServicePhotoForm(self.request.POST, self.request.FILES)
            if form.is_valid():
                service_photo = form.save(commit=False)
                service_photo.photo_author = self.request.user
                service_photo.service_photo = service
                service_photo.save()
                data = {'is_valid': True,
                        'name': service_photo.service_photo_file.name.replace("img/service_photo_file/", ""),
                        'url': service_photo.service_photo_file.url,
                        }

            else:
                data = {'is_valid': False}

            return JsonResponse(data)


@method_decorator(staff_member_required, name='dispatch')
class ServicePhotoDeleteView(DeleteView):
    template_name = 'photo/service_photo_delete.html'
    model = ServicePhotoModel
    success_message = "Imagem deletada com sucesso!"

    def get_object(self, queryset=None, *args, **kwargs):
        service_photo_pk = self.kwargs.get("service_photo_pk")
        service_pk = ServiceModel.objects.get(id=self.kwargs.get('pk'))
        return get_object_or_404(ServicePhotoModel, service_photo=service_pk, id=service_photo_pk)

    def delete(self, request, *args, **kwargs):
        service_pk = self.kwargs['pk']
        service_photo_pk = self.kwargs['service_photo_pk']
        photo = ServicePhotoModel.objects.get(service_photo=service_pk, id=service_photo_pk)
        photo.delete()
        messages.success(self.request, self.success_message)

        return HttpResponseRedirect(reverse("photo:service_photo_create", kwargs={'pk': service_pk}))


@method_decorator(staff_member_required, name='dispatch')
class ServicePhotoCoverUpdateView(SuccessMessageMixin, UpdateView):
    model = ServicePhotoModel
    form_class = ServicePhotoCoverForm
    pk_url_kwarg = 'service_photo_pk'
    context_object_name = 'service_photo'
    template_name = 'photo/service_photo_cover_update.html'
    success_message = "Alterações feitas com sucesso!"

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(photo_author=self.request.user)

    def form_valid(self, form):
        service_photo = self.get_form()
        form.instance.photo_updated_at = timezone.now()
        form.instance.photo_updated_by = self.request.user
        service_photo.save()
        form = ServicePhotoCoverForm(data=self.request.POST, instance=self.object)
        if form.is_valid():
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self, *args, **kwargs):
        service = ServiceModel.objects.get(id=self.kwargs.get('pk'))

        return reverse("photo:service_photo_create", kwargs={'pk': service.pk})
