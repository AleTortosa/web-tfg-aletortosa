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
    path('resena/<int:resena_id>/', views.resena_detalle_view, name='resena_detalle'),
    path('ciudades/', views.ciudades_view, name='ciudades'),
    path('ciudad/<int:ciudad_id>/eventos/', views.eventos_por_ciudad_view, name='eventos_por_ciudad'),
    path('evento/<int:evento_id>/', views.detalle_evento_view, name='detalle_evento'),
    path('evento/<int:evento_id>/favorito/', views.toggle_favorito, name='toggle_favorito'),
    path('favoritos/', views.favoritos_view, name='favoritos'),
    path('resenas/crear/', views.crear_resena_view, name='crear_resena'),
    path('resena/<int:resena_id>/borrar/', views.borrar_resena_view, name='borrar_resena'),
    path('resena/<int:resena_id>/editar/', views.editar_resena_view, name='editar_resena'),
]