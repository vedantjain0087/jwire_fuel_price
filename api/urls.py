from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^track/', views.get_package_details, name='get_package_details'),
    url(r'^$', views.index, name='index'),
]