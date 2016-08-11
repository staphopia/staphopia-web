from django.conf.urls import url

from autofill import views

urlpatterns = [
    url(r'^$', views.index, name='home')
]
