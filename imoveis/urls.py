from django.urls import path

from . import views

app_name = "imoveis"

urlpatterns = [
    path("", views.vitrine, name="vitrine"),
    path("<slug:slug>/", views.detalhe, name="detalhe"),
]
