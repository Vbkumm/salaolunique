from django.conf.urls import url
from main import views


app_name = 'main'


urlpatterns = [
    url(r'^search/$', views.SearchView.as_view(), name='search_view'),
    url(r'^dashboard/$', views.DashBoardView.as_view(), name='dashboard'),

]
