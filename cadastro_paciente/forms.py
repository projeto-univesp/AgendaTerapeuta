from django import forms
from .models import CadastroPaciente

class CadastroPacienteForm(forms.ModelForm):
    class Meta:
        model = CadastroPaciente
        fields = '__all__'