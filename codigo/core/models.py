from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings

class Ciudad(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

class Etiqueta(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre

class Usuario(AbstractUser):
    ciudad_local = models.ForeignKey(Ciudad, on_delete=models.SET_NULL, null=True, blank=True)
    verificado = models.BooleanField(default=False)
    favoritos = models.ManyToManyField('Evento', blank=True, related_name='usuarios_favoritos')
    dni_foto_frontal = models.ImageField(upload_to='dni_fotos/', null=True, blank=True)
    dni_foto_trasera = models.ImageField(upload_to='dni_fotos/', null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.ciudad_local})"

class Evento(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    ciudad = models.ForeignKey(Ciudad, on_delete=models.CASCADE)
    ubicacion = models.CharField(max_length=255)
    imagen = models.ImageField(upload_to='eventos/', null=True, blank=True)
    etiquetas = models.ManyToManyField(Etiqueta, blank=True)  # Relación con etiquetas

    def __str__(self):
        return f"{self.nombre} ({self.ciudad})"

class Resena(models.Model):
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE)
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    descripcion = models.TextField()
    puntuacion = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)])
    fecha = models.DateTimeField(auto_now_add=True)
    #imagen = models.ImageField(upload_to='resenas/', null=True, blank=True) # De momento comentada por la creación de ResenaImagen

    def save(self, *args, **kwargs):
        # Solo permitir reseñas de usuarios verificados y de su ciudad
        if not self.usuario.verificado or self.usuario.ciudad_local != self.evento.ciudad:
            raise ValueError("Solo puedes reseñar eventos de tu ciudad y si estás verificado.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.usuario} - {self.evento} ({self.puntuacion})"
    
class ResenaImagen(models.Model):
    resena = models.ForeignKey(Resena, related_name='imagenes', on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='resenas/')

    def __str__(self):
        return f"Imagen de {self.resena}"
    
class Favorito(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('usuario', 'evento')