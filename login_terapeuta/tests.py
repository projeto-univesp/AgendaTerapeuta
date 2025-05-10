from django.test import TestCase
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from django.db import transaction

class UsuarioUnicoTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create(username="usuario_teste", email="teste@email.com", password="senha123")

    def test_nao_permitir_usuario_duplicado(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                User.objects.create(username="usuario_teste", email="teste@email.com", password="senha123")

    def test_usuario_nao_criado_em_caso_de_erro(self):
        before_count = User.objects.count()

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                User.objects.create(username="usuario_teste", email="teste@email.com", password="senha123")

        after_count = User.objects.count()
        self.assertEqual(before_count, after_count, "Usuário foi salvo mesmo com erro na criação")
