from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class PasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if request.user.is_authenticated:

            # 🔥 Recargar usuario desde BD para actualizar password_must_change
            request.user = User.objects.get(pk=request.user.pk)

            if request.user.password_must_change:

                allowed = [
                    reverse('usuarios:cambiar_contrasena'),
                    reverse('logout'),
                ]

                if request.path not in allowed:
                    return redirect('usuarios:cambiar_contrasena')

        return self.get_response(request)
