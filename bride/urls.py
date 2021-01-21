from django.conf.urls import url
from bride import views

app_name = 'bride'


urlpatterns = [
    url(r'^bride_detail/(?P<pk>\d+)/$', views.BrideDetailView.as_view(), name='bride_detail'),
    url(r'^bride_wizard_create/$', views.BrideWizardCreateView.as_view(), name='bride_wizard_create'),
    url(r'^bride_update/(?P<pk>\d+)/$', views.BrideUpdateView.as_view(), name='bride_update'),
    url(r'^bride_delete/(?P<pk>\d+)/$', views.BrideDeleteView.as_view(), name='bride_delete'),
    url(r'^bride_active_list/$', views.BrideActiveListView.as_view(), name='bride_active_list'),
    url(r'^bride_inactive_list/$', views.BrideInactiveListView.as_view(), name='bride_inactive_list'),

]
