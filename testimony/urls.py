from django.conf.urls import url
from django.urls import path
from testimony import views

app_name = 'testimony'


urlpatterns = [
    url(r'^testimony_detail/(?P<pk>\d+)/$', views.TestimonyDetailView.as_view(), name='testimony_detail'),#not in use
    url(r'^service/(?P<pk>\d+)/$', views.TestimonyServiceListView.as_view(), name='testimony_service_list'),#not in use

    url(r'^service_detail/(?P<pk>\d+)/testimony_service_wizard_create/$', views.TestimonyServiceWizardCreateView.as_view(), name='testimony_service_wizard_create'),
    url(r'^testimony_update/(?P<pk>\d+)/$', views.TestimonyUpdateView.as_view(), name='testimony_update'),
    url(r'^testimony_service_delete/(?P<pk>\d+)/$', views.TestimonyServiceDeleteView.as_view(), name='testimony_service_delete'),
    url(r'^service_detail/(?P<pk>\d+)/service_photo/(?P<service_photo_pk>\d+)/testimony_photo_create/$',
        views.TestimonyPhotoCreateView.as_view(), name='testimony_photo_create'),
    url(r'^service_detail/(?P<pk>\d+)/service_photo/(?P<service_photo_pk>\d+)/testimony_photo_update/(?P<testimony_photo_pk>\d+)/$',
        views.TestimonyPhotoUpdateView.as_view(), name='testimony_photo_update'),
    url(r'^service_detail/(?P<pk>\d+)/service_photo/(?P<service_photo_pk>\d+)/testimony_photo_detail/(?P<testimony_photo_pk>\d+)/$', views.TestimonyPhotoDetailView.as_view(), name='testimony_photo_detail'),
    url(r'^service_detail/(?P<pk>\d+)/service_photo/(?P<service_photo_pk>\d+)/testimony_photo_comment_create/(?P<testimony_photo_pk>\d+)/$',views.TestimonyPhotoCommentCreateView.as_view(), name='testimony_photo_comment_create'),
    url(r'^service_detail/(?P<pk>\d+)/service_photo/(?P<service_photo_pk>\d+)/testimony_photo_comment_update/(?P<testimony_photo_pk>\d+)/$', views.TestimonyPhotoCommentUpdateView.as_view(), name='testimony_photo_comment_update'),
    url(r'^service_detail/(?P<pk>\d+)/service_photo/(?P<service_photo_pk>\d+)/testimony_photo_comment_delete/(?P<testimony_photo_pk>\d+)/$',views.TestimonyPhotoCommentDeleteView.as_view(), name='testimony_photo_comment_delete'),
    url(r'^bride_detail/(?P<pk>\d+)/testimony_bride_update/(?P<testimony_bride_pk>\d+)/$', views.TestimonyBrideUpdateView.as_view(), name='testimony_bride_update'),
    url(r'^testimony_deleted_list/$', views.TestimonyDeletedListView.as_view(), name='testimony_deleted_list'),
    url(r'^testimony_deleted_detail/(?P<pk>\d+)/$', views.TestimonyDeletedDetailView.as_view(), name='testimony_deleted_detail'),  # not in use
    path('service_detail/(<pk>)/service_photo/(<service_photo_pk>)/user_photo_bookmark_add/', views.user_photo_bookmark_add, name='user_photo_bookmark_add'),
    url(r'^service_detail/(?P<pk>\d+)/service_photo/(?P<service_photo_pk>\d+)/user_photo_comment_add/$', views.user_photo_comment_add, name='user_photo_comment_add'),

]