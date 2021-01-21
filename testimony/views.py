import os
from django.contrib.auth.decorators import login_required
from django.shortcuts import HttpResponseRedirect
from django.utils import timezone
from custom_user.forms import PhotoBookmarkForm
from django.shortcuts import Http404
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic import UpdateView, CreateView, ListView, DetailView, DeleteView
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404
from django.contrib.messages.views import SuccessMessageMixin
from formtools.wizard.views import SessionWizardView
from django.core.files.storage import FileSystemStorage
from service.models import ServiceModel
from professional.models import ProfessionalModel
from .forms import (TestimonyServiceForm1,
                    TestimonyServiceForm2,
                    TestimonyServiceForm3,
                    TestimonyUpdateForm,
                    TestimonyPhotoForm1,
                    TestimonyPhotoForm2,
                    TestimonyPhotoUpdateForm,
                    TestimonyPhotoCommentForm,
                    TestimonyBrideUpdateForm)
from .models import TestimonyModel, TestimonyDeletedModel
from photo.models import ServicePhotoModel
from bride.models import BrideModel
from django.forms.models import construct_instance
from custom_user.models import CustomUser
from salaolunique import settings
from django.http import JsonResponse


@method_decorator(login_required, name='dispatch')
class TestimonyServiceWizardCreateView(SuccessMessageMixin, SessionWizardView):
    form_list = [TestimonyServiceForm1, TestimonyServiceForm2, TestimonyServiceForm3]
    template_name = 'testimony/testimony_service_wizard_create.html'
    prefix = 'request'
    success_message = "Depoimento criado com sucesso!"
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'testimony_service_storage'))

    def get_context_data(self, **kwargs):
        context = super(TestimonyServiceWizardCreateView, self).get_context_data(**kwargs)
        service = ServiceModel.objects.get(pk=self.kwargs['pk'])
        professional_list = list(ProfessionalModel.objects.filter(professional_active=True)[:])
        professional_category_list = []

        for professional in professional_list:
            for category in professional.professional_category.all():
                if category == service.service_category.professional_category:
                    professional_category_list.append(professional.professional_name.username)
        context['service'] = service
        context['professional_list'] = professional_category_list
        return context

    def done(self, form_list, **kwargs):
        form_data = [form.cleaned_data for form in form_list]
        testimony = TestimonyModel()
        testimony.testimony_user = self.request.user
        for form in form_list:
            testimony = construct_instance(form, testimony, form._meta.fields, form._meta.exclude)

            testimony.save()
            # Select the tags from the form data and set the related tags after the instance is saved
            testimony.testimony_professional.set(form_data[1]['testimony_professional'])
            testimony.testimony_rating = (form_data[2]['testimony_rating'])

            service_list = self.kwargs.items()
            for k, v in service_list:
                service = ServiceModel.objects.get(id=v)
                testimony.testimony_service = service
                testimony.save()

                return HttpResponseRedirect(reverse_lazy("service:service_detail", kwargs={'pk': self.kwargs['pk']}))


# TestimonyDetailView not in use-------------------------
class TestimonyDetailView(DetailView):
    model = TestimonyModel
    template_name = 'testimony/testimony_detail.html'
    context_object_name = 'testimony'

    def get_context_data(self, **kwargs):

        context = super(TestimonyDetailView, self).get_context_data(**kwargs)
        context['service'] = ServiceModel.objects.filter(testimony_service=self.kwargs['pk'])
        context['professional_list'] = ProfessionalModel.objects.filter(testimony_professional=self.object)

        return context


@method_decorator(login_required, name='dispatch')
class TestimonyUpdateView(SuccessMessageMixin, UpdateView):
    template_name = 'testimony/testimony_update.html'
    model = TestimonyModel
    form_class = TestimonyUpdateForm
    success_message = "Alterações feitas com sucesso!"

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(testimony_user=self.request.user)

    def form_valid(self, form):
        form = TestimonyUpdateForm(data=self.request.POST, instance=self.object)
        form.instance.testimony_updated_at = timezone.now()
        form.instance.testimony_updated_by = self.request.user
        form.instance.save()
        if form.is_valid():
            return super(TestimonyUpdateView, self).form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self, *args, **kwargs):
        services = ServiceModel.objects.filter(testimony_service=self.kwargs['pk'])
        for service in services:
            service_testimony = service.pk
            return reverse_lazy("service:service_detail", kwargs={'pk': service_testimony})


@method_decorator(login_required, name='dispatch')
class TestimonyServiceDeleteView(DeleteView):
    template_name = 'testimony/testimony_service_delete.html'
    model = TestimonyModel
    success_message = "Avaliação deletada com sucesso!"

    def get_object(self, queryset=None):
        obj = super(TestimonyServiceDeleteView, self).get_object()
        obj.testimony_updated_by = self.request.user
        return obj

    def get_success_url(self, *args, **kwargs):
        services = ServiceModel.objects.filter(testimony_service=self.kwargs['pk'])
        for service in services:
            service_testimony = service.pk
            return reverse_lazy("service:service_detail", kwargs={'pk': service_testimony})


@method_decorator(staff_member_required, name='dispatch')
class TestimonyPhotoCreateView(SuccessMessageMixin, SessionWizardView):
    form_list = [TestimonyPhotoForm1, TestimonyPhotoForm2, ]
    template_name = 'testimony/testimony_photo_create.html'
    prefix = 'request'
    success_message = "Comentario criado com sucesso!"
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'testimony_photo_storage'))

    def get_context_data(self, **kwargs):
        context = super(TestimonyPhotoCreateView, self).get_context_data(**kwargs)
        context['service_photo'] = ServicePhotoModel.objects.filter(id=self.kwargs.get('service_photo_pk'))
        context['professional_list'] = ProfessionalModel.objects.filter(professional_category__service_professional__service_category=self.kwargs['pk'])
        return context

    def done(self, form_list, **kwargs):
        form_data = [form.cleaned_data for form in form_list]
        testimony_photo = TestimonyModel()
        testimony_photo.testimony_user = self.request.user

        for form in form_list:
            testimony_photo = construct_instance(form, testimony_photo, form._meta.fields, form._meta.exclude)
            testimony_photo.save()
            # Select the tags from the form data and set the related tags after the instance is saved
            testimony_photo.testimony_professional.set(form_data[1]['testimony_professional'])
            testimony_photo.testimony_bride = form_data[1]['testimony_bride']

            service_list = self.kwargs.items()
            for k, v in service_list:
                if k == 'pk':
                    service = ServiceModel.objects.get(id=v)
                    testimony_photo.testimony_service = service
                    testimony_photo.save()

                if k == 'service_photo_pk':
                    photo = ServicePhotoModel.objects.get(id=v)
                    testimony_photo.testimony_photo = photo
                    testimony_photo.testimony_title = f'service_photo: {v}'
                    testimony_photo.save()

            return HttpResponseRedirect(reverse_lazy("testimony:testimony_photo_detail", kwargs={'pk': self.kwargs['pk'], 'service_photo_pk': self.kwargs['service_photo_pk'], 'testimony_photo_pk': testimony_photo.pk}))


@method_decorator(staff_member_required, name='dispatch')
class TestimonyPhotoUpdateView(SuccessMessageMixin, UpdateView):
    template_name = 'testimony/testimony_photo_update.html'
    model = TestimonyModel
    form_class = TestimonyPhotoUpdateForm
    pk_url_kwarg = 'testimony_photo_pk'
    context_object_name = 'service_photo'
    success_message = "Alterações feitas com sucesso!"

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(testimony_user=self.request.user)

    def form_valid(self, form):
        form = TestimonyPhotoUpdateForm(data=self.request.POST, instance=self.object)
        form.instance.testimony_updated_at = timezone.now()
        form.instance.testimony_updated_by = self.request.user
        form.instance.save()
        if form.is_valid():
            return super(TestimonyPhotoUpdateView, self).form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self, *args, **kwargs):
        print(self)
        service_photo = ServiceModel.objects.get(id=self.kwargs.get('pk'))
        return reverse("photo:service_photo_create", kwargs={'pk': service_photo.pk})


class TestimonyPhotoDetailView(DetailView):
    model = TestimonyModel
    template_name = 'testimony/testimony_photo_detail.html'
    context_object_name = 'testimony_photo'
    pk_url_kwarg = 'testimony_photo_pk'

    def get_context_data(self, **kwargs):
        context = super(TestimonyPhotoDetailView, self).get_context_data(**kwargs)
        context['service_photo'] = ServicePhotoModel.objects.filter(id=self.kwargs.get('service_photo_pk'))
        service_photo = context['service_photo']
        photo = service_photo[0]
        session_key = 'viewed_photo_{}'.format(photo)
        if not self.request.session.get(session_key, False):
            photo.photo_views += 1
            photo.save()
            self.request.session[session_key] = True
        context['photo_views'] = photo.photo_views
        context['service'] = ServiceModel.objects.filter(id=photo.service_photo.pk)
        context['testimony_list'] = TestimonyModel.objects.filter(testimony_photo=photo)

        return context


# TestimonyPhotoDetailView not in use-------------------------
class TestimonyPhotoCommentCreateView(SuccessMessageMixin, CreateView):
    model = TestimonyModel
    form_class = TestimonyPhotoCommentForm
    template_name = 'testimony/testimony_photo_comment_create.html'
    success_message = "Comentario criado com sucesso!"

    def get_context_data(self, **kwargs):

        context = super(TestimonyPhotoCommentCreateView, self).get_context_data(**kwargs)
        context['service_photo'] = ServicePhotoModel.objects.filter(id=self.kwargs.get('service_photo_pk'))
        service_photo = context['service_photo']
        photo = service_photo[0]
        session_key = 'viewed_photo_{}'.format(photo)
        if not self.request.session.get(session_key, False):
            photo.photo_views += 1
            photo.save()
            self.request.session[session_key] = True
        context['photo_views'] = photo.photo_views
        context['service'] = ServiceModel.objects.filter(id=photo.service_photo.pk)
        context['testimony_list'] = TestimonyModel.objects.filter(testimony_photo=photo)

        return context

    def form_valid(self, form):
        form = TestimonyPhotoCommentForm(data=self.request.POST, instance=self.object)
        form.instance.testimony_title = ServicePhotoModel.objects.get(id=self.kwargs.get('service_photo_pk'))
        form.instance.testimony_photo = ServicePhotoModel.objects.get(id=self.kwargs.get('service_photo_pk'))
        form.instance.testimony_user = self.request.user
        if form.is_valid():
            return super(TestimonyPhotoCommentCreateView, self).form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self, *args, **kwargs):

        service = ServiceModel.objects.get(id=self.kwargs.get('pk'))
        testimony = TestimonyModel.objects.filter(testimony_photo=self.kwargs.get('service_photo_pk')).order_by('testimony_published')[:1]
        photo = ServicePhotoModel.objects.filter(testimony_photo=testimony)

        return reverse_lazy("testimony:testimony_photo_comment_create",  kwargs={'pk': service.pk, 'service_photo_pk': photo[0].pk, 'testimony_photo_pk': testimony[0].pk})
#---------------------------------------------


@method_decorator(login_required, name='dispatch')
class TestimonyPhotoCommentUpdateView(SuccessMessageMixin, UpdateView):
    template_name = 'testimony/testimony_photo_comment_update.html'
    model = TestimonyModel
    form_class = TestimonyPhotoCommentForm
    pk_url_kwarg = 'testimony_photo_pk'
    success_message = "Alterações feitas com sucesso!"

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(testimony_user=self.request.user)

    def form_valid(self, form):
        form = TestimonyPhotoCommentForm(data=self.request.POST, instance=self.object)
        form.instance.testimony_updated_at = timezone.now()
        form.instance.testimony_updated_by = self.request.user
        if form.is_valid():
            return super(TestimonyPhotoCommentUpdateView, self).form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self, *args, **kwargs):
        service = ServiceModel.objects.get(id=self.kwargs.get('pk'))
        testimony = TestimonyModel.objects.filter(testimony_photo=self.kwargs.get('service_photo_pk')).order_by('testimony_published')[:1]
        photo = ServicePhotoModel.objects.filter(testimony_photo=testimony)

        return reverse_lazy("testimony:testimony_photo_detail",
                            kwargs={'pk': service.pk, 'service_photo_pk': photo[0].pk,
                                    'testimony_photo_pk': testimony[0].pk})


@method_decorator(login_required, name='dispatch')
class TestimonyPhotoCommentDeleteView(DeleteView):
    template_name = 'testimony/testimony_photo_comment_delete.html'
    model = TestimonyModel
    pk_url_kwarg = 'testimony_photo_pk'
    success_message = "Comentario deletado com sucesso!"

    def get_object(self, queryset=None):
        obj = super(TestimonyPhotoCommentDeleteView, self).get_object()
        obj.testimony_updated_by = self.request.user
        return obj

    def get_success_url(self, *args, **kwargs):
        service = ServiceModel.objects.get(id=self.kwargs.get('pk'))
        testimony = TestimonyModel.objects.filter(testimony_photo=self.kwargs.get('service_photo_pk')).order_by(
            'testimony_published')[:1]
        photo = ServicePhotoModel.objects.filter(testimony_photo=testimony)

        return reverse_lazy("testimony:testimony_photo_detail",
                            kwargs={'pk': service.pk, 'service_photo_pk': photo[0].pk,
                                    'testimony_photo_pk': testimony[0].pk})


# TestimonyServiceListView not in use-------------------------
class TestimonyServiceListView(ListView):
    model = TestimonyModel
    context_object_name = 'testimony_service_list'
    template_name = 'testimony/testimony_service_list.html'

    def get_queryset(self, *args, **kwargs):
        testimony_service_list = []
        service = ServiceModel.objects.filter(id=self.kwargs['pk'])
        old_testimony_services = list(TestimonyModel.objects.filter(testimony_services__in=service).order_by('-testimony_published')[:])

        for testimony_service in old_testimony_services:
            if testimony_service.get_testimony_user() is True:
                testimony_service_list.append(testimony_service)

        return testimony_service_list


@method_decorator(staff_member_required, name='dispatch')
class TestimonyBrideUpdateView(SuccessMessageMixin, UpdateView):
    template_name = 'testimony/testimony_bride_update.html'
    model = TestimonyModel
    form_class = TestimonyBrideUpdateForm
    pk_url_kwarg = 'testimony_bride_pk'
    context_object_name = 'testimony_bride'
    success_message = "Alterações salvas com sucesso!"

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(testimony_user=self.request.user)

    def form_valid(self, form):
        form = TestimonyBrideUpdateForm(data=self.request.POST, instance=self.object)
        form.instance.testimony_updated_at = timezone.now()
        form.instance.testimony_updated_by = self.request.user
        form.instance.save()
        if form.is_valid():
            return super(TestimonyBrideUpdateView, self).form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self, *args, **kwargs):
        bride = BrideModel.objects.get(id=self.object.testimony_bride.id)

        return reverse_lazy("bride:bride_detail", kwargs={'pk': bride.pk})


@method_decorator(staff_member_required, name='dispatch')
class TestimonyDeletedListView(ListView):
    model = TestimonyDeletedModel
    context_object_name = 'testimony_deleted_list'
    template_name = 'testimony/testimony_deleted_list.html'

    def get_queryset(self):
        queryset = super().get_queryset().all().order_by('-testimony_deleted_date')
        return queryset


@method_decorator(staff_member_required, name='dispatch')
class TestimonyDeletedDetailView(DetailView):
    model = TestimonyDeletedModel
    template_name = 'testimony/testimony_deleted_detail.html'
    context_object_name = 'testimony_deleted'
    pk_url_kwarg = 'pk'


@login_required
def user_photo_comment_add(request, pk, service_photo_pk):
    service = get_object_or_404(ServiceModel, pk=pk)
    service_photo = get_object_or_404(ServicePhotoModel, pk=service_photo_pk)
    user_photo_comment_form = TestimonyPhotoCommentForm(request.POST or None)
    if request.method == 'GET':
        return HttpResponseRedirect((reverse_lazy("testimony:testimony_photo_detail",  kwargs={'pk': service.pk, 'service_photo_pk': service_photo.pk, 'testimony_photo_pk': service_photo.testimony_photo.all()[0].pk})))
    else:
        if request.method == 'POST' and user_photo_comment_form.is_valid():
            form = TestimonyPhotoCommentForm(request.POST)
            comment = form.save(commit=False)
            comment.testimony_title = service_photo
            comment.testimony_photo = service_photo
            comment.testimony_user = request.user
            testimony = user_photo_comment_form.cleaned_data['testimony_description']
            comment.testimony_description = testimony
            comment.save()

            return HttpResponseRedirect(reverse_lazy("testimony:testimony_photo_detail",  kwargs={'pk': service.pk, 'service_photo_pk': service_photo.pk, 'testimony_photo_pk': service_photo.testimony_photo.all()[0].pk}))

        raise Http404()


@login_required
def user_photo_bookmark_add(request, pk, service_photo_pk):
    service = get_object_or_404(ServiceModel, pk=pk)
    service_photo = get_object_or_404(ServicePhotoModel, pk=service_photo_pk)
    user_photo_bookmark_form = PhotoBookmarkForm(request.POST or None)
    if request.method == 'GET':
        return HttpResponseRedirect((reverse_lazy("testimony:testimony_photo_detail",  kwargs={'pk': service.pk, 'service_photo_pk': service_photo.pk, 'testimony_photo_pk': service_photo.testimony_photo.all()[0].pk})))
    else:
        if request.method == 'POST' and user_photo_bookmark_form.is_valid():
            photo = user_photo_bookmark_form.cleaned_data['photo_bookmark']
            if photo in request.user.photo_bookmark.all():
                request.user.photo_bookmark.remove(photo)

            else:
                request.user.photo_bookmark.add(photo)

            request.user.save()

            return HttpResponseRedirect(reverse_lazy("testimony:testimony_photo_detail",  kwargs={'pk': service.pk, 'service_photo_pk': service_photo.pk, 'testimony_photo_pk': photo.testimony_photo.all()[0].pk}))

        raise Http404()
