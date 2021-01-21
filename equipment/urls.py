from django.conf.urls import url
from . import views


app_name = 'equipment'


urlpatterns = [
    url(r'^equipment_detail/(?P<pk>\d+)/$', views.EquipmentDetailView.as_view(), name='equipment_detail'),
    url(r'^dashboard_equipment_wizard_create/$', views.DashboardEquipmentWizardCreateView.as_view(), name='dashboard_equipment_wizard_create'),
    url(r'^equipment_update/(?P<pk>\d+)/$', views.EquipmentUpdateView.as_view(), name='equipment_update'),
    url(r'^equipment_delete/(?P<pk>\d+)/$', views.EquipmentDeleteView.as_view(), name='equipment_delete'),
    url(r'^equipment_list/$', views.EquipmentListView.as_view(), name='equipment_list'),

]
