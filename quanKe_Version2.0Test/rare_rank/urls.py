from django.conf.urls import url
from . import views

urlpatterns=[

url(r'^rare_rank/',views.dignos_predict,name='rare_rank'),
url(r'^$', views.index, name='index'),

]

