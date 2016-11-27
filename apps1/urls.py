from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^nextWord/', views.nextWord, name='nextWord'),
    url(r'^firstWord/', views.firstWord, name='firstWord'),
]
