from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from .models import Ciudad, Resena
from django.contrib.auth.decorators import login_required


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

def resenas_view(request):
    return render(request, "resenas.html")

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