# models.py
from django.db import models
from django.contrib.auth.models import User

class PerfilPaciente(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=True)
    codigo_acesso = models.CharField(max_length=150, null=True)
    #terapeuta = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.usuario.username
