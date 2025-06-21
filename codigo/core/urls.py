from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('', views.home, name='home'),
    path('perfil/', views.perfil_view, name='perfil'),
    path('logout/', views.logout_view, name='logout'),
    path('resenas/', views.resenas_view, name='resenas'),
    path('explorar/', views.explorar_view, name='explorar'),
    path('favoritos/', views.favoritos_view, name='favoritos'),
    path('registro/', views.registro_view, name='registro'),
    path('perfil/editar/', views.editar_perfil_view, name='editar_perfil'),
    path('perfil/resenas/', views.mis_resenas_view, name='mis_resenas'),
]