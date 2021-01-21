from django.conf.urls import url
from . import views


app_name = 'schedule'


urlpatterns = [
    url(r'^schedule_detail/(?P<pk>\d+)/$', views.ScheduleDetailView.as_view(), name='schedule_detail'),

]