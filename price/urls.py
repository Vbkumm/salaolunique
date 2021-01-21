from django.conf.urls import url
from price import views

app_name = 'price'


urlpatterns = [
    url(r'^service_detail/(?P<pk>\d+)/price_service_detail/(?P<price_pk>\d+)/$', views.PriceServiceDetailView.as_view(), name='price_service_detail'),
    url(r'^service_detail/(?P<pk>\d+)/price_service_update/(?P<price_pk>\d+)/$', views.PriceServiceUpdateView.as_view(), name='price_service_update'),
    url(r'^combo_detail/(?P<pk>\d+)/price_combo_update/(?P<price_pk>\d+)/$', views.PriceComboUpdateView.as_view(), name='price_combo_update'),

]