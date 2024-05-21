from django.db import models

class LoginTerapeuta(models.Model):
    idTerapeuta = models.AutoField(primary_key=True, null=False, blank=False)
    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20)
    email = models.EmailField(null=False, blank=False)
    senha = models.CharField(max_length=100, null=False, blank=False)