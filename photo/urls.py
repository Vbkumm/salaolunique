from django.conf.urls import url
from photo import views

app_name = 'photo'


urlpatterns = [

    url(r'service_detail/(?P<pk>\d+)/service_photo_create/$',
        views.ServicePhotoCreateView.as_view(), name='service_photo_create'),
    url(r'^service_detail/(?P<pk>\d+)/service_photo_delete/(?P<service_photo_pk>\d+)/$', views.ServicePhotoDeleteView.as_view(),
        name='service_photo_delete'),
    url(r'^service_detail/(?P<pk>\d+)/service_photo_cover_update/(?P<service_photo_pk>\d+)/$', views.ServicePhotoCoverUpdateView.as_view(),
        name='service_photo_cover_update'),
    ]







