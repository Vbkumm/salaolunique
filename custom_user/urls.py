from django.urls import path
from django.conf.urls import url
from . import views

app_name = 'custom_user'


urlpatterns = [
    path('custom_user_list/', views.CustomUserListView.as_view(), name='custom_user_list'),
    url(r'^user_is_professional/(?P<username>.+)/', views.UserUpdateListView.as_view(), name='user_is_professional'),
    url(r'^user_detail/(?P<username>.+)/', views.UserDetailView.as_view(), name='user_detail'),

]