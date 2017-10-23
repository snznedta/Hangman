from django.conf.urls import include, url
from django.contrib.auth import views as auth_views
from hangman import views

urlpatterns = [
    url(r'^$', views.home),
    url(r'^login$', auth_views.login, {'template_name':'login.html'}, name='login'),
    url(r'^logout$', auth_views.logout_then_login),
    url(r'^register$', views.register),
    url(r'^game$', views.start_game)
]