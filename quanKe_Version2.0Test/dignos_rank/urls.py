from django.conf.urls import  url
from . import  views

urlpatterns = [

     #pre /cdss/
    url(r'^dignos_rank/', views.dignos_predict, name='dignos_rank'),
    #add Operation
    url(r'^$', views.index, name='index'),

]
