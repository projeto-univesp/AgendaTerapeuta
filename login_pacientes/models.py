# models.py
from django.db import models
from django.contrib.auth.models import User

class PerfilPaciente(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=True)
    codigo_acesso = models.CharField(max_length=150, null=True)
    terapeuta = models.ForeignKey(User, related_name='terapeuta_set', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.usuario.username
