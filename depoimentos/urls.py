from django.urls import path

from . import views

app_name = "depoimentos"

urlpatterns = [
    path("novo/", views.novo, name="novo"),
]
