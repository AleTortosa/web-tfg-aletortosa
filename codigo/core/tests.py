from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Ciudad, Evento, Etiqueta, Resena, Favorito, ReporteResena
from django.core.files.uploadedfile import SimpleUploadedFile
import json

User = get_user_model()

class ModelosTestCase(TestCase):
    """Pruebas para los modelos de la aplicación"""
    
    def setUp(self):
        """Configuración inicial para cada prueba"""
        self.ciudad = Ciudad.objects.create(nombre="Valencia")
        self.usuario = User.objects.create_user(
            username="testuser",
            password="testpass123",
            email="test@example.com",
            ciudad_local=self.ciudad,
            verificado=True
        )
        self.etiqueta = Etiqueta.objects.create(nombre="Cultura")
        self.evento = Evento.objects.create(
            nombre="Museo de Bellas Artes",
            descripcion="Museo con arte clásico",
            ciudad=self.ciudad,
            ubicacion="Calle San Pío V, 9"
        )
        self.evento.etiquetas.add(self.etiqueta)
    
    def test_crear_ciudad(self):
        """Test creación de ciudad"""
        self.assertEqual(str(self.ciudad), "Valencia")
        self.assertEqual(Ciudad.objects.count(), 1)
    
    def test_crear_usuario(self):
        """Test creación de usuario personalizado"""
        self.assertEqual(str(self.usuario), "testuser (Valencia)")
        self.assertTrue(self.usuario.verificado)
        self.assertEqual(self.usuario.ciudad_local, self.ciudad)
    
    def test_crear_evento(self):
        """Test creación de evento"""
        self.assertEqual(str(self.evento), "Museo de Bellas Artes (Valencia)")
        self.assertEqual(self.evento.etiquetas.count(), 1)
        self.assertEqual(self.evento.etiquetas.first(), self.etiqueta)
    
    def test_crear_resena(self):
        """Test creación de reseña"""
        resena = Resena.objects.create(
            usuario=self.usuario,
            evento=self.evento,
            descripcion="Muy buen museo",
            puntuacion=5
        )
        self.assertEqual(str(resena), "testuser (Valencia) - Museo de Bellas Artes (Valencia) (5)") 
        self.assertEqual(resena.puntuacion, 5)
    
    def test_validacion_resena_usuario_no_verificado(self):
        """Test validación de reseña con usuario no verificado"""
        usuario_no_verificado = User.objects.create_user(
            username="noverificado",
            password="test123",
            ciudad_local=self.ciudad,
            verificado=False
        )
        
        with self.assertRaises(ValueError):
            Resena.objects.create(
                usuario=usuario_no_verificado,
                evento=self.evento,
                descripcion="No debería funcionar",
                puntuacion=3
            )
    
    def test_validacion_resena_ciudad_diferente(self):
        """Test validación de reseña de usuario de ciudad diferente"""
        otra_ciudad = Ciudad.objects.create(nombre="Madrid")
        usuario_madrid = User.objects.create_user(
            username="madrid_user",
            password="test123",
            ciudad_local=otra_ciudad,
            verificado=True
        )
        
        with self.assertRaises(ValueError):
            Resena.objects.create(
                usuario=usuario_madrid,
                evento=self.evento,
                descripcion="No debería funcionar",
                puntuacion=3
            )
    
    def test_favorito_unique_constraint(self):
        """Test restricción única en favoritos"""
        # Crear primer favorito
        Favorito.objects.create(usuario=self.usuario, evento=self.evento)
        
        # Intentar crear duplicado debería fallar
        with self.assertRaises(Exception):
            Favorito.objects.create(usuario=self.usuario, evento=self.evento)


class VistasTestCase(TestCase):
    """Pruebas para las vistas de la aplicación"""
    
    def setUp(self):
        """Configuración inicial para cada prueba"""
        self.client = Client()
        self.ciudad = Ciudad.objects.create(nombre="Valencia")
        self.usuario = User.objects.create_user(
            username="testuser",
            password="testpass123",
            email="test@example.com",
            ciudad_local=self.ciudad,
            verificado=True
        )
        self.evento = Evento.objects.create(
            nombre="Museo de Bellas Artes",
            descripcion="Museo con arte clásico",
            ciudad=self.ciudad,
            ubicacion="Calle San Pío V, 9"
        )
    
    def test_home_view(self):
        """Test vista home"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Home')
    
    def test_login_view_get(self):
        """Test vista login GET"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Iniciar sesión')
    
    def test_login_view_post_valido(self):
        """Test login con credenciales válidas"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirección
        self.assertRedirects(response, reverse('home'))
    
    def test_login_view_post_invalido(self):
        """Test login con credenciales inválidas"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Usuario o contraseña incorrectos')
    
    def test_registro_view_get(self):
        """Test vista registro GET"""
        response = self.client.get(reverse('registro'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Valencia')  # Debe mostrar ciudades
    
    def test_registro_view_post_valido(self):
        """Test registro con datos válidos"""
        response = self.client.post(reverse('registro'), {
            'username': 'newuser',
            'nombre': 'Nuevo',
            'apellidos': 'Usuario',
            'password': 'newpass123',
            'email': 'new@example.com',
            'ciudad_local': self.ciudad.id
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_registro_username_duplicado(self):
        """Test registro con username ya existente"""
        response = self.client.post(reverse('registro'), {
            'username': 'testuser',  # Ya existe
            'nombre': 'Nuevo',
            'apellidos': 'Usuario',
            'password': 'newpass123',
            'email': 'new@example.com',
            'ciudad_local': self.ciudad.id
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ese nombre de usuario ya existe')
    
    def test_explorar_view(self):
        """Test vista explorar"""
        response = self.client.get(reverse('explorar'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.evento.nombre)
    
    def test_explorar_view_con_busqueda(self):
        """Test vista explorar con búsqueda"""
        response = self.client.get(reverse('explorar'), {'busca': 'Museo'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.evento.nombre)
    
    def test_detalle_evento_view(self):
        """Test vista detalle evento"""
        response = self.client.get(reverse('detalle_evento', args=[self.evento.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.evento.nombre)
        self.assertContains(response, self.evento.descripcion)
    
    def test_favoritos_view_sin_autenticar(self):
        """Test vista favoritos sin autenticar"""
        response = self.client.get(reverse('favoritos'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Inicia sesión para ver tus favoritos')
    
    def test_favoritos_view_autenticado(self):
        """Test vista favoritos autenticado"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('favoritos'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Mis eventos favoritos')
    
    def test_toggle_favorito_ajax(self):
        """Test funcionalidad AJAX de favoritos"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('toggle_favorito', args=[self.evento.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['es_favorito'])
        
        # Verificar que se creó el favorito
        self.assertTrue(Favorito.objects.filter(
            usuario=self.usuario, 
            evento=self.evento
        ).exists())
    
    def test_perfil_view_requiere_login(self):
        """Test que perfil requiere login"""
        response = self.client.get(reverse('perfil'))
        self.assertEqual(response.status_code, 302)  # Redirección a login
    
    def test_perfil_view_autenticado(self):
        """Test vista perfil autenticado"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('perfil'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')
    
    def test_crear_resena_requiere_login(self):
        """Test que crear reseña requiere login"""
        response = self.client.get(reverse('crear_resena'))
        self.assertEqual(response.status_code, 302)  # Redirección a login
    
    def test_crear_resena_post_valido(self):
        """Test creación de reseña válida"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('crear_resena'), {
            'evento': self.evento.id,
            'puntuacion': 5,
            'descripcion': 'Excelente museo'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Resena.objects.filter(
            usuario=self.usuario,
            evento=self.evento
        ).exists())


class IntegracionTestCase(TestCase):
    """Pruebas de integración"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        self.ciudad = Ciudad.objects.create(nombre="Valencia")
        self.usuario = User.objects.create_user(
            username="testuser",
            password="testpass123",
            email="test@example.com",
            ciudad_local=self.ciudad,
            verificado=True
        )
        self.evento = Evento.objects.create(
            nombre="Museo de Bellas Artes",
            descripcion="Museo con arte clásico",
            ciudad=self.ciudad,
            ubicacion="Calle San Pío V, 9"
        )
    
    def test_flujo_completo_usuario(self):
        """Test flujo completo: registro -> login -> crear reseña -> favoritos"""
        # 1. Registro
        response = self.client.post(reverse('registro'), {
            'username': 'newuser',
            'nombre': 'Nuevo',
            'apellidos': 'Usuario',
            'password': 'newpass123',
            'email': 'new@example.com',
            'ciudad_local': self.ciudad.id
        })
        self.assertEqual(response.status_code, 302)
        
        # 2. Login
        response = self.client.post(reverse('login'), {
            'username': 'newuser',
            'password': 'newpass123'
        })
        self.assertEqual(response.status_code, 302)
        
        # 3. Verificar usuario y crear reseña
        nuevo_usuario = User.objects.get(username='newuser')
        nuevo_usuario.verificado = True
        nuevo_usuario.save()
        
        self.client.login(username='newuser', password='newpass123')
        
        response = self.client.post(reverse('crear_resena'), {
            'evento': self.evento.id,
            'puntuacion': 4,
            'descripcion': 'Muy buen museo'
        })
        self.assertEqual(response.status_code, 302)
        
        # 4. Verificar reseña creada
        self.assertTrue(Resena.objects.filter(
            usuario=nuevo_usuario,
            evento=self.evento
        ).exists())
        
        # 5. Añadir a favoritos
        response = self.client.post(
            reverse('toggle_favorito', args=[self.evento.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        
        # 6. Verificar favorito
        self.assertTrue(Favorito.objects.filter(
            usuario=nuevo_usuario,
            evento=self.evento
        ).exists())
        
        # 7. Ver favoritos
        response = self.client.get(reverse('favoritos'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.evento.nombre)