from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
import random
from .forms import RegisterForm

Usuario = get_user_model()  # Usa tu modelo real

@login_required
def profile(request):
    return render(request, "accounts/profile.html", {"user": request.user})

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Inicia sesión al registrarse
            return redirect("dashboard")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})

# Para guardar temporalmente los códigos
reset_codes = {}

def password_reset_request(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = Usuario.objects.get(email=email)
            # Generar código de 5 dígitos
            codigo = str(random.randint(10000, 99999))
            request.session["reset_email"] = email
            request.session["reset_code"] = codigo

            # Enviar el código (por ahora en consola)
            print(f"🔐 Código de recuperación para {email}: {codigo}")

            messages.success(request, "Se ha enviado un código de verificación a tu correo.")
            return redirect("account:password_reset_code")

        except Usuario.DoesNotExist:
            messages.error(request, "No existe una cuenta registrada con ese correo.")
            return redirect("account:password_reset_request")

    return render(request, "accounts/password_reset_request.html")

def password_reset_code(request):
    email = request.session.get("reset_email")
    if not email:
        return redirect("account:password_reset_request")

    if request.method == "POST":
        code = request.POST.get("code")
        if reset_codes.get(email) == code:
            messages.success(request, "Código verificado correctamente.")
            return redirect("account:password_reset_confirm")
        messages.error(request, "Código incorrecto. Intenta nuevamente.")
    return render(request, "accounts/password_reset_code.html")


def password_reset_confirm(request):
    email = request.session.get("reset_email")
    if not email:
        return redirect("account:password_reset_request")

    user = User.objects.get(email=email)

    if request.method == "POST":
        new_password1 = request.POST.get("new_password1")
        new_password2 = request.POST.get("new_password2")

        if new_password1 != new_password2:
            messages.error(request, "Las contraseñas no coinciden.")
        else:
            user.set_password(new_password1)
            user.save()
            reset_codes.pop(email, None)
            del request.session['reset_email']
            messages.success(request, "Contraseña actualizada correctamente.")
            return redirect("login")
    return render(request, "accounts/password_reset_confirm.html")
# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.contrib.auth import get_user_model
import random

from .forms import RegisterForm

Usuario = get_user_model()  # Usa tu modelo personalizado de usuarios

# Diccionario temporal para guardar códigos de recuperación
reset_codes = {}

# ================================
# PERFIL
# ================================
@login_required
def profile(request):
    return render(request, "accounts/profile.html", {"user": request.user})


# ================================
# REGISTRO
# ================================
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Inicia sesión al registrarse
            messages.success(request, "Registro exitoso. Bienvenido.")
            return redirect("dashboard")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})


# ================================
# RECUPERAR CONTRASEÑA (PASO 1)
# ================================
def password_reset_request(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = Usuario.objects.get(email=email)
            
            # Generar y guardar código de 5 dígitos
            codigo = str(random.randint(10000, 99999))
            reset_codes[email] = codigo  # ✅ ahora sí se guarda
            request.session["reset_email"] = email

            # Enviar el código por consola (o correo si luego activas send_mail)
            print(f"🔐 Código de recuperación para {email}: {codigo}")

            messages.success(request, "Se ha enviado un código de verificación a tu correo.")
            return redirect("password_reset_code")

        except Usuario.DoesNotExist:
            messages.error(request, "No existe una cuenta registrada con ese correo.")
            return redirect("password_reset_request")

    return render(request, "accounts/password_reset_request.html")


# ================================
# VERIFICAR CÓDIGO (PASO 2)
# ================================
def password_reset_code(request):
    email = request.session.get("reset_email")
    if not email:
        return redirect("password_reset_request")

    if request.method == "POST":
        code = request.POST.get("code")
        if reset_codes.get(email) == code:
            messages.success(request, "Código verificado correctamente.")
            return redirect("password_reset_confirm")
        else:
            messages.error(request, "Código incorrecto. Intenta nuevamente.")
    return render(request, "accounts/password_reset_code.html")


# ================================
# CAMBIAR CONTRASEÑA (PASO 3)
# ================================
def password_reset_confirm(request):
    email = request.session.get("reset_email")
    if not email:
        return redirect("password_reset_request")

    try:
        user = Usuario.objects.get(email=email)
    except Usuario.DoesNotExist:
        messages.error(request, "El usuario no existe.")
        return redirect("password_reset_request")

    if request.method == "POST":
        new_password1 = request.POST.get("new_password1")
        new_password2 = request.POST.get("new_password2")

        if new_password1 != new_password2:
            messages.error(request, "Las contraseñas no coinciden.")
        else:
            user.set_password(new_password1)
            user.save()

            # Limpiar sesión y código
            reset_codes.pop(email, None)
            request.session.pop("reset_email", None)

            messages.success(request, "Contraseña actualizada correctamente. Ahora puedes iniciar sesión.")
            return redirect("login")

    return render(request, "accounts/password_reset_confirm.html")
