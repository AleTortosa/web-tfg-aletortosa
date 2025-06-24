from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from .models import Ciudad, Resena, Evento, Etiqueta, Favorito
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse


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

def favoritos_view(request):
    return render(request, "favoritos.html")

def explorar_view(request):
    return render(request, "explorar.html")

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
    etiquetas_ids = request.GET.getlist('etiquetas')
    etiquetas = Etiqueta.objects.all()

    ciudades = []
    eventos = Evento.objects.all().select_related('ciudad')

    if etiquetas_ids:
        # Si hay etiquetas seleccionadas, solo filtramos eventos por etiquetas (y opcionalmente por nombre)
        eventos = eventos.filter(etiquetas__id__in=etiquetas_ids)
        if busca:
            eventos = eventos.filter(nombre__icontains=busca)
        ciudades_destacadas = []
        ciudades = []
    else:
        # Si no hay etiquetas, mostramos ciudades y eventos según búsqueda
        if not busca:
            ciudades_destacadas = Ciudad.objects.all()[:6]
        else:
            ciudades_destacadas = []
            ciudades = Ciudad.objects.filter(nombre__icontains=busca)
            eventos = eventos.filter(nombre__icontains=busca)

    eventos = eventos.distinct()

    return render(request, "resenas.html", {
        "ciudades": ciudades,
        "eventos": eventos,
        "etiquetas": etiquetas,
        "etiquetas_seleccionadas": etiquetas_ids,
        "busca": busca,
        "ciudades_destacadas": ciudades_destacadas,
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
    return render(request, "detalle_evento.html", {
        "evento": evento,
        "reseñas": reseñas,
        "es_favorito": es_favorito,
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

@login_required
def favoritos_view(request):
    favoritos = Favorito.objects.filter(usuario=request.user).select_related('evento', 'evento__ciudad')
    return render(request, "favoritos.html", {"favoritos": favoritos})