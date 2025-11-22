# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.utils import timezone
import random

from .forms import RegisterForm

Usuario = get_user_model()

# Códigos de recuperación temporales
reset_codes = {}

# CONFIGURACIÓN DE SEGURIDAD
MAX_INTENTOS = 5
BLOQUEO_MINUTOS = 10


# ====================================
# LOGIN PERSONALIZADO
# ====================================
def login_view(request):
    if request.method == "POST":
        username_or_email = request.POST.get("username")
        password = request.POST.get("password")

        # Buscar usuario por username o email
        user_obj = (
            Usuario.objects.filter(username=username_or_email).first()
            or Usuario.objects.filter(email=username_or_email).first()
        )

        # Usuario no existe
        if not user_obj:
            messages.error(request, "Usuario o contraseña incorrectos.")
            return render(request, "accounts/login.html")

        # Cuenta desactivada
        if not user_obj.estado:
            messages.error(request, "Tu cuenta está inactiva. Contacta al administrador.")
            return render(request, "accounts/login.html")

        # Cuenta bloqueada
        if user_obj.bloqueado_hasta and user_obj.bloqueado_hasta > timezone.now():
            minutos_restantes = (user_obj.bloqueado_hasta - timezone.now()).seconds // 60
            messages.error(
                request,
                f"Tu cuenta está bloqueada. Intenta nuevamente en {minutos_restantes} minutos."
            )
            return render(request, "accounts/login.html")

        # Autenticación
        user = authenticate(request, username=user_obj.username, password=password)

        if user is None:
            # Registrar intento fallido
            user_obj.intentos_fallidos += 1

            # Excedió intentos
            if user_obj.intentos_fallidos >= MAX_INTENTOS:
                user_obj.bloquear(BLOQUEO_MINUTOS)
                messages.error(
                    request,
                    f"Tu cuenta ha sido bloqueada por {BLOQUEO_MINUTOS} minutos."
                )
                return render(request, "accounts/login.html")

            user_obj.save()

            intentos_restantes = MAX_INTENTOS - user_obj.intentos_fallidos
            messages.error(
                request,
                f"Credenciales incorrectas. Intentos restantes: {intentos_restantes}."
            )
            return render(request, "accounts/login.html")

        # LOGIN EXITOSO
        user_obj.resetear_intentos()
        user_obj.ultimo_acceso = timezone.now()
        user_obj.save()

        login(request, user)
        return redirect("dashboard")

    return render(request, "accounts/login.html")


# ====================================
# PERFIL
# ====================================
@login_required
def profile(request):
    return render(request, "accounts/profile.html", {"user": request.user})


# ====================================
# REGISTRO
# ====================================
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():

            usuario = form.save(commit=False)
            usuario.estado = True
            usuario.intentos_fallidos = 0
            usuario.bloqueado_hasta = None
            usuario.save()

            login(request, usuario)
            messages.success(request, "Registro exitoso. Bienvenido.")
            return redirect("dashboard")

        messages.error(request, "Corrige los errores del formulario.")

    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


# ====================================
# RECUPERAR CONTRASEÑA — PASO 1
# ====================================
def password_reset_request(request):
    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            messages.error(request, "No existe una cuenta registrada con ese correo.")
            return redirect("password_reset_request")

        # Generar y guardar código
        codigo = str(random.randint(10000, 99999))
        reset_codes[email] = codigo
        request.session["reset_email"] = email

        print(f"🔐 Código enviado a {email}: {codigo}")

        messages.success(request, "Se ha enviado un código de verificación a tu correo.")
        return redirect("password_reset_code")

    return render(request, "accounts/password_reset_request.html")


# ====================================
# RECUPERAR CONTRASEÑA — PASO 2
# ====================================
def password_reset_code(request):
    email = request.session.get("reset_email")

    if not email:
        return redirect("password_reset_request")

    if request.method == "POST":
        code = request.POST.get("code")

        if reset_codes.get(email) == code:
            messages.success(request, "Código verificado correctamente.")
            return redirect("password_reset_confirm")

        messages.error(request, "Código incorrecto.")

    return render(request, "accounts/password_reset_code.html")


# ====================================
# RECUPERAR CONTRASEÑA — PASO 3
# ====================================
def password_reset_confirm(request):
    email = request.session.get("reset_email")

    if not email:
        return redirect("password_reset_request")

    try:
        user = Usuario.objects.get(email=email)
    except Usuario.DoesNotExist:
        messages.error(request, "Ocurrió un error con la cuenta.")
        return redirect("password_reset_request")

    if request.method == "POST":
        new_password1 = request.POST.get("new_password1")
        new_password2 = request.POST.get("new_password2")

        # Validaciones
        if new_password1 != new_password2:
            messages.error(request, "Las contraseñas no coinciden.")
            return redirect("password_reset_confirm")

        if len(new_password1) < 8:
            messages.error(request, "La contraseña debe tener al menos 8 caracteres.")
            return redirect("password_reset_confirm")

        if not any(c.isupper() for c in new_password1):
            messages.error(request, "Debe incluir al menos una mayúscula.")
            return redirect("password_reset_confirm")

        if not any(c.isdigit() for c in new_password1):
            messages.error(request, "Debe incluir al menos un número.")
            return redirect("password_reset_confirm")

        if not any(c in "@$!%*?&" for c in new_password1):
            messages.error(request, "Debe incluir un símbolo especial.")
            return redirect("password_reset_confirm")

        if " " in new_password1:
            messages.error(request, "La contraseña no puede contener espacios.")
            return redirect("password_reset_confirm")

        # Guardar nueva contraseña
        user.set_password(new_password1)
        user.save()

        # Limpiar código
        reset_codes.pop(email, None)
        request.session.pop("reset_email", None)

        messages.success(request, "Contraseña actualizada correctamente.")
        return redirect("login")

    return render(request, "accounts/password_reset_confirm.html")
