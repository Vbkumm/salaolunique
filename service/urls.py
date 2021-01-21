from django.conf.urls import url
from service import views
from equipment import views as equipment_views
from schedule import views as schedule_views

app_name = 'service'


urlpatterns = [
    url(r'^service_detail/(?P<pk>\d+)/$', views.ServiceDetailView.as_view(), name='service_detail'),
    url(r'^service_wizard_create/$', views.ServiceWizardCreateView.as_view(), name='service_wizard_create'),
    url(r'^service_update/(?P<pk>\d+)/$', views.ServiceUpdateView.as_view(), name='service_update'),
    url(r'^service_category_create/$', views.ServiceCategoryCreateView.as_view(), name='service_category_create'),
    url(r'^dashboard_service_category_create/$', views.DashboardServiceCategoryCreateView.as_view(), name='dashboard_service_category_create'),
    url(r'^service_category_update/(?P<pk>\d+)/$', views.ServiceCategoryUpdateView.as_view(), name='service_category_update'),
    url(r'^service_category_delete/(?P<pk>\d+)/$', views.ServiceCategoryDeleteView.as_view(), name='service_category_delete'),
    url(r'^category/(?P<pk>\d+)/$', views.ServiceListView.as_view(), name='service_list'),
    url(r'^service_delete/(?P<pk>\d+)/$', views.ServiceDeleteView.as_view(), name='service_delete'),
    url(r'^service_category_list/$', views.ServiceCategoryListView.as_view(), name='service_category_list'),
    url(r'^service_inactive_list/$', views.ServiceInactiveListView.as_view(), name='service_inactive_list'),
    url(r'^service_active_list/$', views.ServiceActiveListView.as_view(), name='service_active_list'),

    url(r'^service_detail/(?P<pk>\d+)/equipment_wizard_create/$', equipment_views.EquipmentWizardCreateView.as_view(), name='equipment_wizard_create'),
    url(r'^service_detail/(?P<pk>\d+)/equipment_service_create/$', equipment_views.ServiceEquipmentCreateView.as_view(), name='equipment_service_create'),
    url(r'^service_detail/(?P<pk>\d+)/equipment_service_first_create/$', equipment_views.ServiceEquipmentFirstCreateView.as_view(), name='equipment_service_first_create'),
    url(r'^service_detail/(?P<pk>\d+)/equipment_service_list/$', equipment_views.ServiceEquipmentListView.as_view(), name='equipment_service_list'),
    url(r'^service_detail/(?P<pk>\d+)/equipment_service_update/(?P<equipment_service_pk>\d+)/$', equipment_views.ServiceEquipmentUpdateView.as_view(), name='equipment_service_update'),
    url(r'^service_detail/(?P<pk>\d+)/equipment_service_delete/(?P<equipment_service_pk>\d+)/$', equipment_views.ServiceEquipmentDeleteView.as_view(), name='equipment_service_delete'),

    url(r'^service_detail/(?P<pk>\d+)/schedule_wizard_create/$', schedule_views.ScheduleWizardCreateView.as_view(), name='schedule_wizard_create'),

]
