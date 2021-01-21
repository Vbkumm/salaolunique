from service.models import ServiceModel, ServiceCategoryModel
from professional.models import ProfessionalModel, ProfessionalCategoryModel
from bride.models import BrideModel
from itertools import chain
from django.views.generic import ListView
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from testimony.models import TestimonyModel, TestimonyDeletedModel
from photo.models import ServicePhotoModel
from price.models import PriceModel
from custom_user.models import CustomUser
from itertools import groupby
from combo.models import ComboModel
from equipment.models import EquipmentModel


''' SERCH VIEW - '''


class SearchView(ListView):
    template_name = 'main/search_view.html'
    count = 0

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['count'] = self.count or 0
        context['query'] = self.request.GET.get('q')
        return context

    def get_queryset(self):
        request = self.request
        query = request.GET.get('q', None)

        if query is not None:
            service_results = ServiceModel.objects.search(query)
            professional_results = ProfessionalModel.objects.search(query)
            bride_results = BrideModel.objects.search(query)

            # combine querysets
            queryset_chain = chain(
                service_results,
                professional_results,
                bride_results,

            )
            qs = sorted(queryset_chain,
                        key=lambda instance: instance.pk,
                        reverse=True)
            self.count = len(qs)  # since qs is actually a list
            return qs
        return ServiceModel.objects.none()  # just an empty queryset as default


''' Offer list and list w/ create apiview'''

''' Landing view home'''


class LandingView(ListView):
    template_name = 'home.html'
    context_object_name = 'category_list'
    model = ServiceCategoryModel

    def get_context_data(self, **kwargs):
        context = super(LandingView, self).get_context_data(**kwargs)
        bride_testimony_list = []
        bride_category_list = list(BrideModel.objects.filter(bride_active=True)[:])

        for bride in bride_category_list:
            if bride not in [i[0] for i in bride_testimony_list]:
                if bride.testimony_bride.all():
                    count = 0
                    for testimony in bride.testimony_bride.all():
                        if bride not in [i[0] for i in bride_testimony_list]:
                            count += 1
                            if testimony.get_last_photo() is True:
                                bride_testimony_list.append([bride, testimony])
                            else:
                                if count == len(bride.testimony_bride.all()):
                                    bride_testimony_list.append([bride, None])

                else:
                    bride_testimony_list.append([bride, None])

        context['bride_list'] = bride_testimony_list

        combo_list = list(ComboModel.objects.all()[:])
        combo_list_visible = []

        for combo in combo_list:
            if combo.combo_visible() is True:
                for service in combo.combo_service_quantity.all():
                    for photo in service.combo_service.service_photo.all():
                        if photo.get_valid_cover_photo() is True:

                            if combo not in [i[0] for i in combo_list_visible]:
                                combo_list_visible.append([combo, photo])

        context['combo_list'] = combo_list_visible

        professional_active_list = list(ProfessionalModel.objects.filter(professional_active=True))
        professional_true_active_list = []
        for user in professional_active_list:

            if user.professional_name.is_professional is True:
                professional_true_active_list.append(user)
        context['professional_list'] = professional_true_active_list

        testimony_list = []
        testimony_rating_list = list(TestimonyModel.objects.all().order_by('-testimony_published')[:])
        for testimony in testimony_rating_list:
            if testimony.testimony_rating == 5:
                if testimony.testimony_photo is None:
                    if testimony.testimony_bride is None:
                        if testimony.testimony_active is True:
                            testimony_list.append(testimony)

        if len(testimony_list) > 5:
            context['testimony_list'] = testimony_list

        photo_service_list = list(ServicePhotoModel.objects.filter(service_photo_cover=True)[:])
        if len(photo_service_list) > 5:
            context['photo_service_list'] = photo_service_list

        return context

    def get_queryset(self):
        photo_service_list = []
        old_photo_service_list = list(ServicePhotoModel.objects.filter(service_photo_cover=True).order_by('-photo_published')[:])

        for photo in old_photo_service_list:
            if photo.get_valid_cover_photo() is True:
                photo_service_list.append(photo)

        category_list = []
        old_category_list = list(ServiceCategoryModel.objects.all().order_by('category_service')[:])

        while photo_service_list:

            for photo in photo_service_list:
                photo_service = photo
                photo_service_list.remove(photo_service)
                if photo_service.service_photo.service_category in old_category_list:
                    photo_category = photo_service.service_photo.service_category
                    old_category_list.remove(photo_category)
                    for service in photo_category.service_category.all():
                        if service.service_active is False:
                            if photo_category not in [i[0] for i in category_list]:
                                category_list.append([photo_category, photo_service])

        if old_category_list:

            for service_category in old_category_list:

                photo_category = service_category
                for service in photo_category.service_category.all():
                    if service.service_active is False:
                        if photo_category not in [i[0] for i in category_list]:
                            category_list.append([photo_category, None])

        return category_list


''' DashBoard view'''


@method_decorator(staff_member_required, name='dispatch')
class DashBoardView(ListView):
    template_name = 'main/dashboard.html'
    context_object_name = 'service_list'
    model = ServiceModel

    def get_context_data(self, **kwargs):
        context = super(DashBoardView, self).get_context_data(**kwargs)

        service_comment_list_old = list(ServiceModel.objects.all()[:])
        service_comment_list = []

        for service_comment in service_comment_list_old:
            if service_comment.testimony_service:
                service = service_comment
                for testimony_service in service.testimony_service.all():
                    if testimony_service.get_testimony_user() is True:
                        service_comment_list.append([service.service_tittle, service.pk])

        service_comment_list_new = [(key, len(list(group))) for key, group in groupby(sorted(service_comment_list))]
        context['testimony_service_list'] = sorted(service_comment_list_new, key=lambda x: x[1], reverse=True)[:5]

        rating_service_list = list(ServiceModel.objects.all()[:])
        rating_list = []

        for rating_service in rating_service_list:
            if rating_service.testimony_service:
                service = rating_service
                rating_average = []

                for testimony_service in service.testimony_service.all():
                    if testimony_service.get_testimony_user() is True:
                        rating = testimony_service.testimony_rating
                        if rating is not None:
                            rating_average.append(int(rating))

                if len(rating_average) >= 1:
                    rating_ave = sum(rating_average)/len(rating_average)
                    rating_list.append([service, rating_ave])
        if len(rating_list) == 0:
            rating_list_new = 1
        else:
            rating_list_new = len(rating_list)
        context['service_rating_list'] = sorted(rating_list, key=lambda x: x[1], reverse=True)[:5]
        context['service_rating_average'] = sum(i[1] for i in rating_list)/rating_list_new

        photo_comment_list = list(ServicePhotoModel.objects.all()[:])
        photo_testimony = []

        for photo_comment in photo_comment_list:
            if photo_comment.testimony_photo:
                photo = photo_comment
                for testimony_photo in photo.testimony_photo.all():
                    if testimony_photo is not None:
                        testimony = 0
                        testimony_list = len(photo.testimony_photo.all())
                        for testimony in range(0, testimony_list-1):
                            testimony += 1
                        if photo not in [i[0] for i in photo_testimony]:
                            photo_testimony.append([photo, testimony])

        context['testimony_photo_list'] = sorted(photo_testimony, key=lambda x: x[1], reverse=True)[:5]

        total_equipment_qtd = list(EquipmentModel.objects.all()[:])
        total_equipment = 0

        for equipment in total_equipment_qtd:
            total_equipment += equipment.equipment_quantity

        context['total_equipment'] = total_equipment

        combo_list = list(ComboModel.objects.all()[:])
        combo_list_visible = []
        combo_list_invisible = []
        for combo in combo_list:
            if combo.combo_visible() is True:
                combo_list_visible.append(combo)
            else:
                combo_list_invisible.append(combo)
        context['total_combo_visible'] = len(combo_list_visible)
        context['total_combo_invisible'] = len(combo_list_invisible)

        price_offer_list = list(PriceModel.objects.all()[:])
        service_price_offer_list = []

        for service_price_offer in price_offer_list:
            if service_price_offer.price_service:
                if service_price_offer.price_service.service_active is False:
                    if service_price_offer.price_value and service_price_offer.old_price_value:
                        if service_price_offer.price_value <= service_price_offer.old_price_value:
                            service_price_offer_list.append(service_price_offer)
        context['service_price_active_list'] = len(service_price_offer_list)

        custom_user_list = list(CustomUser.objects.all()[:])
        context['total_users'] = len(custom_user_list)

        professional_active_list = list(ProfessionalModel.objects.filter(professional_active=True))
        professional_true_active_list = []
        for user in professional_active_list:
            if user.professional_name.is_professional is True:
                professional_true_active_list.append(user)
        context['total_professional_active'] = len(professional_true_active_list)

        professional_inactive_list = list(ProfessionalModel.objects.filter(professional_active=False))
        professional_true_active_list = []
        for user in professional_inactive_list:
            if user.professional_name.is_professional is True:
                professional_true_active_list.append(user)
        context['total_professional_inactive'] = len(professional_true_active_list)

        total_testimony_deleted = list(TestimonyDeletedModel.objects.all().order_by('-testimony_deleted_date'))

        context['total_testimony_deleted'] = len(total_testimony_deleted)

        photo_views_list_old = list(ServicePhotoModel.objects.all().order_by('-photo_views')[:])
        photo_views_list = []

        for photo_view in photo_views_list_old:
            for photo in photo_view.testimony_photo.all():
                if photo.testimony_photo is not None:
                    if photo_view not in photo_views_list:
                        photo_views_list.append(photo_view)

        context['photo_views_list'] = photo_views_list[:5]

        context.update({
            'total_professional_category': len(ProfessionalCategoryModel.objects.all()),
            'total_service_category': len(ServiceCategoryModel.objects.all()),
            'service_views_list': ServiceModel.objects.all().order_by('-service_views')[:5],
            'bride_views_list': BrideModel.objects.all().order_by('-bride_views')[:5],
            'total_service_inactive': len(ServiceModel.objects.filter(service_active=True)),
            'total_service_active': len(ServiceModel.objects.filter(service_active=False)),
            'total_bride_inactive': len(BrideModel.objects.filter(bride_active=False)),
            'total_bride_active': len(BrideModel.objects.filter(bride_active=True)),

        })

        return context
