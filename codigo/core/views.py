from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from .models import Ciudad, Resena, Evento, Etiqueta, Favorito, ResenaImagen, ReporteResena
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg
from django.http import JsonResponse
from django.contrib import messages


def home(request):
    return render(request, 'home.html')

def login_view(request):
    error = None
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")  # Cambia "home" por el nombre de tu url de inicio si es diferente
        else:
            error = "Usuario o contraseña incorrectos"
    return render(request, "login.html", {"error": error})

def registro_view(request):
    error = None
    ciudades = Ciudad.objects.all()
    if request.method == "POST":
        username = request.POST.get("username")
        name = request.POST.get("nombre")
        last_name = request.POST.get("apellidos")
        password = request.POST.get("password")
        email = request.POST.get("email")
        ciudad_id = request.POST.get("ciudad_local")
        ciudad_local = Ciudad.objects.get(id=ciudad_id) if ciudad_id else None

        User = get_user_model()
        if User.objects.filter(username=username).exists():
            error = "Ese nombre de usuario ya existe."
        elif User.objects.filter(email=email).exists():
            error = "Ese correo electrónico ya está en uso."
        else:
            user = User.objects.create_user(
                username=username,
                first_name=name,
                last_name=last_name,
                password=password,
                email=email,
                ciudad_local=ciudad_local
            )
            return redirect("login")
    return render(request, "registro.html", {"error": error, "ciudades": ciudades})

@login_required
def perfil_view(request):
    return render(request, "perfil.html")

def logout_view(request):
    logout(request)
    return redirect('login')

def explorar_view(request):
    busca = request.GET.get('busca', '').strip()
    etiquetas_ids = request.GET.getlist('etiquetas')
    etiquetas = Etiqueta.objects.all()

    ciudades = []
    eventos = Evento.objects.all().select_related('ciudad')

    if etiquetas_ids:
        eventos = eventos.filter(etiquetas__id__in=etiquetas_ids)
        if busca:
            eventos = eventos.filter(nombre__icontains=busca)
        ciudades_destacadas = []
        ciudades = []
    else:
        if not busca:
            ciudades_destacadas = Ciudad.objects.all()[:6]
        else:
            ciudades_destacadas = []
            ciudades = Ciudad.objects.filter(nombre__icontains=busca)
            eventos = eventos.filter(nombre__icontains=busca)

    eventos = eventos.distinct()

    return render(request, "explorar.html", {
        "ciudades": ciudades,
        "eventos": eventos,
        "etiquetas": etiquetas,
        "etiquetas_seleccionadas": etiquetas_ids,
        "busca": busca,
        "ciudades_destacadas": ciudades_destacadas,
    })

@login_required
def perfil_view(request):
    mis_resenas = Resena.objects.filter(usuario=request.user)
    favoritos = request.user.favoritos.all()  # Si tienes el campo favoritos en Usuario
    return render(request, "perfil.html", {
        "mis_resenas": mis_resenas,
        "favoritos": favoritos,
    })

@login_required
def editar_perfil_view(request):
    ciudades = Ciudad.objects.all()
    user = request.user
    mensaje = None
    if request.method == "POST":
        user.first_name = request.POST.get("nombre")
        user.last_name = request.POST.get("apellidos")
        user.email = request.POST.get("email")
        ciudad_id = request.POST.get("ciudad_local")
        user.ciudad_local = Ciudad.objects.get(id=ciudad_id) if ciudad_id else None
        user.save()
        mensaje = "Datos actualizados correctamente."
    return render(request, "editar_perfil.html", {"user": user, "ciudades": ciudades, "mensaje": mensaje})

@login_required
def mis_resenas_view(request):
    mis_resenas = Resena.objects.filter(usuario=request.user)
    return render(request, "mis_resenas.html", {"mis_resenas": mis_resenas})

@login_required
def resena_detalle_view(request, resena_id):
    resena = get_object_or_404(Resena, id=resena_id, usuario=request.user)
    return render(request, "resena_detalle.html", {"resena": resena})

def resenas_view(request):
    busca = request.GET.get('busca', '').strip()
    resenas = Resena.objects.select_related('evento', 'evento__ciudad', 'usuario')
    if busca:
        resenas = resenas.filter(
            Q(evento__nombre__icontains=busca) |
            Q(evento__ciudad__nombre__icontains=busca) |
            Q(usuario__username__icontains=busca)
        )
    resenas = resenas.order_by('-fecha')[:50]
    return render(request, "resenas.html", {
        "resenas": resenas,
        "busca": busca,
    })

def ciudades_view(request):
    busca = request.GET.get('busca', '').strip()
    if busca:
        ciudades = Ciudad.objects.filter(nombre__icontains=busca)
    else:
        ciudades = Ciudad.objects.all()
    return render(request, "ciudades.html", {"ciudades": ciudades, "busca": busca})

def eventos_por_ciudad_view(request, ciudad_id):
    ciudad = get_object_or_404(Ciudad, id=ciudad_id)
    busca = request.GET.get('busca', '').strip()
    etiquetas_ids = request.GET.getlist('etiquetas')
    eventos = ciudad.evento_set.all()
    etiquetas = Etiqueta.objects.all()

    if busca:
        eventos = eventos.filter(nombre__icontains=busca)
    if etiquetas_ids:
        eventos = eventos.filter(etiquetas__id__in=etiquetas_ids).distinct()

    return render(request, "eventos_por_ciudad.html", {
        "ciudad": ciudad,
        "eventos": eventos,
        "busca": busca,
        "etiquetas": etiquetas,
        "etiquetas_seleccionadas": etiquetas_ids,
    })

def detalle_evento_view(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    reseñas = evento.resena_set.all()
    es_favorito = False
    if request.user.is_authenticated:
        es_favorito = Favorito.objects.filter(usuario=request.user, evento=evento).exists()
    puntuacion_media = reseñas.aggregate(Avg('puntuacion'))['puntuacion__avg']
    return render(request, "detalle_evento.html", {
        "evento": evento,
        "reseñas": reseñas,
        "es_favorito": es_favorito,
        "puntuacion_media": puntuacion_media,
    })

@login_required
def toggle_favorito(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    favorito, created = Favorito.objects.get_or_create(usuario=request.user, evento=evento)
    if not created:
        favorito.delete()
        es_favorito = False
    else:
        es_favorito = True
    return JsonResponse({'es_favorito': es_favorito})

def favoritos_view(request):
    if request.user.is_authenticated:
        favoritos = Favorito.objects.filter(usuario=request.user).select_related('evento', 'evento__ciudad')
    else:
        favoritos = []
    return render(request, "favoritos.html", {"favoritos": favoritos})

@login_required
def crear_resena_view(request):
    eventos = Evento.objects.filter(ciudad=request.user.ciudad_local)
    error = ""
    if request.method == "POST":
        evento_id = request.POST.get("evento")
        puntuacion = request.POST.get("puntuacion")
        descripcion = request.POST.get("descripcion")
        imagenes = request.FILES.getlist("imagenes")
        try:
            evento = Evento.objects.get(id=evento_id, ciudad=request.user.ciudad_local)
            resena = Resena.objects.create(
                usuario=request.user,
                evento=evento,
                puntuacion=puntuacion,
                descripcion=descripcion
            )
            for img in imagenes:
                ResenaImagen.objects.create(resena=resena, imagen=img)
            return redirect('mis_resenas')
        except Exception as e:
            error = str(e)
    return render(request, "crear_resena.html", {"eventos": eventos, "error": error})

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

@login_required
def borrar_resena_view(request, resena_id):
    resena = get_object_or_404(Resena, id=resena_id, usuario=request.user)
    if request.method == "POST":
        resena.delete()
        return redirect('mis_resenas')
    return redirect('resena_detalle', resena_id=resena_id)

@login_required
def editar_resena_view(request, resena_id):
    resena = get_object_or_404(Resena, id=resena_id, usuario=request.user)
    eventos = Evento.objects.filter(ciudad=request.user.ciudad_local)
    error = ""
    if request.method == "POST":
        puntuacion = request.POST.get("puntuacion")
        descripcion = request.POST.get("descripcion")
        imagenes = request.FILES.getlist("imagenes")
        # Borrar imágenes seleccionadas
        ids_borrar = request.POST.getlist("borrar_imagenes")
        if ids_borrar:
            for img_id in ids_borrar:
                img = resena.imagenes.filter(id=img_id).first()
                if img:
                    img.delete()
        resena.puntuacion = puntuacion
        resena.descripcion = descripcion
        resena.save()
        # Añadir nuevas imágenes si se suben
        for img in imagenes:
            ResenaImagen.objects.create(resena=resena, imagen=img)
        return redirect('resena_detalle', resena_id=resena.id)
    return render(request, "editar_resena.html", {
        "resena": resena,
        "eventos": eventos,
        "error": error,
    })

def perfil_publico(request, user_id):
    User = get_user_model()
    usuario = get_object_or_404(User, id=user_id)
    resenas = usuario.resena_set.all()
    return render(request, "perfil_publico.html", {"usuario": usuario, "resenas": resenas})

def resena_publica_detalle(request, resena_id):
    resena = get_object_or_404(Resena, id=resena_id)
    return render(request, "resena_publica_detalle.html", {"resena": resena})

def reportar_resena(request, resena_id):
    if request.method == "POST":
        messages.success(request, "¡Reseña reportada! Gracias por tu colaboración.")
    return redirect('resena_publica_detalle', resena_id=resena_id)

def reportar_resena(request, resena_id):
    resena = get_object_or_404(Resena, id=resena_id)
    if request.method == "POST":
        motivo = request.POST.get("motivo", "")
        ReporteResena.objects.create(
            resena=resena,
            reportado_por=request.user if request.user.is_authenticated else None,
            motivo=motivo
        )
        messages.success(request, "¡Reseña reportada! El equipo de administración la revisará.")
    return redirect('resena_publica_detalle', resena_id=resena_id)