from django.conf.urls import url
from professional import views

app_name = 'professional'


urlpatterns = [
    url(r'^professional_detail/(?P<username>[\w.@+-]+)/$', views.ProfessionalDetailView.as_view(), name='professional_detail'),
    url(r'^professional_update/(?P<username>[\w.@+-]+)/$', views.ProfessionalUpdateView.as_view(), name='professional_update'),
    url(r'^professional_category_create/$', views.ProfessionalCategoryCreateView.as_view(), name='professional_category_create'),
    url(r'^dashboard_professional_category_create/$', views.DashboardProfessionalCategoryCreateView.as_view(), name='dashboard_professional_category_create'),
    url(r'^professional_category_update/(?P<pk>\d+)/$', views.ProfessionalCategoryUpdateView.as_view(), name='professional_category_update'),
    url(r'^professional_category_delete/(?P<pk>\d+)/$', views.ProfessionalCategoryDeleteView.as_view(), name='professional_category_delete'),
    url(r'^professional_active_list/$', views.ProfessionalActiveListView.as_view(), name='professional_active_list'),
    url(r'^professional_inactive_list/$', views.ProfessionalInactiveListView.as_view(), name='professional_inactive_list'),
    url(r'^professional_category_list/$', views.ProfessionalCategoryListView.as_view(), name='professional_category_list'),
    url(r'^professional_detail/(?P<username>[\w.@+-]+)/professional_extra_skill_add/', views.professional_extra_skill_add, name='professional_extra_skill_add'),
    url(r'^professional_detail/(?P<username>[\w.@+-]+)/professional_not_skill_add/', views.professional_not_skill_add, name='professional_not_skill_add'),
    url(r'^professional_detail/(?P<username>[\w.@+-]+)/professional_schedule_create/$', views.ProfessionalScheduleCreateView.as_view(), name='professional_schedule_create'),
    url(r'^professional_detail/(?P<username>[\w.@+-]+)/professional_schedule_update/(?P<professional_schedule_pk>\d+)/$', views.ProfessionalScheduleUpdateView.as_view(), name='professional_schedule_update'),
    url(r'^professional_detail/(?P<username>[\w.@+-]+)/professional_schedule_delete/(?P<professional_schedule_pk>\d+)/$', views.ProfessionalScheduleDeleteView.as_view(), name='professional_schedule_delete'),

]
