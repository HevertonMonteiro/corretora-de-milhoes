from django.urls import path

from . import views

app_name = "painel"

urlpatterns = [
    path("login/", views.PainelLoginView.as_view(), name="login"),
    path("logout/", views.PainelLogoutView.as_view(), name="logout"),
    path("", views.dashboard, name="dashboard"),
    path("imoveis/", views.imovel_list, name="imovel_list"),
    path("imoveis/novo/", views.imovel_form, name="imovel_create"),
    path("imoveis/<int:pk>/editar/", views.imovel_form, name="imovel_edit"),
    path("imoveis/<int:pk>/excluir/", views.imovel_delete, name="imovel_delete"),
    path("imoveis/<int:pk>/status/", views.imovel_status, name="imovel_status"),
    path("realizacoes/nova/", views.realizacao_create, name="realizacao_create"),
    path("depoimentos/", views.depoimentos_moderar, name="depoimentos_moderar"),
    path("leads/", views.leads_list, name="leads_list"),
    path("perfil/", views.perfil_editar, name="perfil_editar"),
]
