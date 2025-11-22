from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

Usuario = get_user_model()


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=False)  # ❗ quitar required=True

    class Meta:
        model = Usuario
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Nombre de usuario"
        })

        self.fields["email"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Correo electrónico"
        })

        self.fields["password1"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Contraseña"
        })

        self.fields["password2"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Confirmar contraseña"
        })

    def clean_email(self):
        email = self.cleaned_data.get("email")

        # 1️⃣ Campo vacío
        if not email:
            raise forms.ValidationError("Debe ingresar un correo electrónico.")

        # 2️⃣ Formato inválido
        try:
            forms.EmailField().clean(email)
        except forms.ValidationError:
            raise forms.ValidationError("Ingrese un correo electrónico válido.")

        # 3️⃣ Email repetido
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo ya está registrado.")

        return email