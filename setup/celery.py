import os
from celery import Celery

# Defina o módulo Django padrão para o Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AgendaTerapeuta.settings')

app = Celery('AgendaTerapeuta')

# Carrega as configurações do Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Descobre e registra automaticamente as tarefas dos apps Django
app.autodiscover_tasks()