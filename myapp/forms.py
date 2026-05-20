from django import forms
from .models import Sala, Questao


class SalaForm(forms.ModelForm):
    class Meta:
        model = Sala
        fields = ['nome', 'codigo', 'ativa']
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Nome da Sala'}),
            'codigo': forms.TextInput(attrs={'placeholder': 'Código'}),
        }


class QuestaoForm(forms.ModelForm):
    class Meta:
        model = Questao
        exclude = ['sala', 'criado', 'atualizado']
        widgets = {
            'texto': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Digite a pergunta'}),
            'feedback': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Explicação da resposta'}),
            'alternativa_a': forms.TextInput(attrs={'placeholder': 'Alternativa A'}),
            'alternativa_b': forms.TextInput(attrs={'placeholder': 'Alternativa B'}),
            'alternativa_c': forms.TextInput(attrs={'placeholder': 'Alternativa C'}),
            'alternativa_d': forms.TextInput(attrs={'placeholder': 'Alternativa D'}),
            'alternativa_e': forms.TextInput(attrs={'placeholder': 'Alternativa E'}),
        }

    def clean(self):
        cleaned = super().clean()
        tipo = cleaned.get('tipo')
        tipo_correcao = cleaned.get('tipo_correcao')

        if tipo == 'aberta':
            return cleaned

        alternativas = {
            'a': cleaned.get('alternativa_a'),
            'b': cleaned.get('alternativa_b'),
            'c': cleaned.get('alternativa_c'),
            'd': cleaned.get('alternativa_d'),
            'e': cleaned.get('alternativa_e'),
        }

        corretas = {
            'a': cleaned.get('correta_a'),
            'b': cleaned.get('correta_b'),
            'c': cleaned.get('correta_c'),
            'd': cleaned.get('correta_d'),
            'e': cleaned.get('correta_e'),
        }

        for k in alternativas:
            texto = alternativas[k]
            if not texto or not texto.strip():
                cleaned[f'correta_{k}'] = False

        total_corretas = sum(1 for k in alternativas if alternativas[k] and alternativas[k].strip() and corretas[k])

        if tipo_correcao == 'unica':
            if total_corretas != 1:
                raise forms.ValidationError('Selecione apenas UMA alternativa correta.')
        elif tipo_correcao == 'multipla':
            if total_corretas < 2:
                raise forms.ValidationError('Selecione pelo menos DUAS corretas.')
        elif tipo_correcao == 'nenhuma':
            if total_corretas > 0:
                raise forms.ValidationError('Questão sem correta não pode possuir respostas corretas.')
        return cleaned
