from django.shortcuts import render, redirect
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
    if request.method == "POST":
        user.first_name = request.POST.get("nombre")
        user.last_name = request.POST.get("apellidos")
        user.email = request.POST.get("email")
        ciudad_id = request.POST.get("ciudad_local")
        nueva_ciudad = Ciudad.objects.get(id=ciudad_id) if ciudad_id else None
        # Si cambia de ciudad, pierde la verificación
        if user.ciudad_local != nueva_ciudad:
            user.verificado = False
        user.ciudad_local = nueva_ciudad
        # Solo guarda la foto si se sube y no está verificado
        if not user.verificado:
            if request.FILES.get("dni_foto_frontal"):
                user.dni_foto_frontal = request.FILES["dni_foto_frontal"]
            if request.FILES.get("dni_foto_trasera"):
                user.dni_foto_trasera = request.FILES["dni_foto_trasera"]
        user.save()        
        return redirect("perfil")
    return render(request, "editar_perfil.html", {"user": user, "ciudades": ciudades})

@login_required
def mis_resenas_view(request):
    mis_resenas = Resena.objects.filter(usuario=request.user)
    return render(request, "mis_resenas.html", {"mis_resenas": mis_resenas})