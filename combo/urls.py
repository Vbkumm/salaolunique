from django.conf.urls import url
from . import views


app_name = 'combo'


urlpatterns = [
    url(r'^combo_detail/(?P<pk>\d+)/$', views.ComboDetailView.as_view(), name='combo_detail'),
    url(r'^combo_wizard_create/$', views.ComboWizardCreateView.as_view(), name='combo_wizard_create'),
    url(r'^combo_detail/(?P<pk>\d+)/combo_service_create/$', views.ComboServiceCreateView.as_view(), name='combo_service_create'),
    url(r'^combo_update/(?P<pk>\d+)/$', views.ComboUpdateView.as_view(), name='combo_update'),
    url(r'^combo_delete/(?P<pk>\d+)/$', views.ComboDeleteView.as_view(), name='combo_delete'),
    url(r'^combo_list/$', views.ComboListView.as_view(), name='combo_list'),
    url(r'^combo_detail/(?P<pk>\d+)/combo_service_update/(?P<service_pk>\d+)/$', views.ComboServiceUpdateView.as_view(),name='combo_service_update'),
    url(r'^combo_detail/(?P<pk>\d+)/combo_service_delete/(?P<service_pk>\d+)/$', views.ComboServiceDeleteView.as_view(),name='combo_service_delete'),

]