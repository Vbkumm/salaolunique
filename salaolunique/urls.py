"""salaolunique URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url
from custom_user import views as custon_user_view
from main import views as main_view

from django.contrib.auth.views import auth_logout
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', main_view.LandingView.as_view(), name='home'),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^bride/', include('bride.urls')),
    url(r'^combo/', include('combo.urls')),
    url(r'^equipment/', include('equipment.urls')),
    url(r'^main/', include('main.urls')),
    url(r'^service/', include('service.urls')),
    url(r'^schedule/', include('schedule.urls')),
    url(r'^professional/', include('professional.urls')),
    url(r'^price/', include('price.urls')),
    url(r'^testimony/', include('testimony.urls')),
    url(r'^photo/', include('photo.urls')),
    url(r'^custom_user/', include('custom_user.urls')),
    url(r'^accounts/profile/(?P<username>.+)/$', custon_user_view.UserUpdate.as_view(), name='profile'),
    path('accounts/terms/', custon_user_view.TermsView.as_view(), name="terms"),
    path('accounts/cookies/', custon_user_view.CookiesView.as_view(), name="cookies"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
