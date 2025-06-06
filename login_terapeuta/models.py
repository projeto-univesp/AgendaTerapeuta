# models.py
from django.db import models
from django.contrib.auth.models import User

class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=True)
    cpf = models.CharField(max_length=20, unique=True)
    celular = models.CharField(max_length=20)

    def __str__(self):
        return self.usuario.username
