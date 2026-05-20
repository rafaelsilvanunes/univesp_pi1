from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone


class Sala(models.Model):
    nome = models.CharField(max_length=100)
    codigo = models.CharField(max_length=10, unique=True, db_index=True)
    ativa = models.BooleanField(default=True)
    criado = models.DateTimeField(auto_now_add=True)
    atualizado = models.DateTimeField(auto_now=True)

    professor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='salas'
    )

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f"{self.nome} ({self.codigo})"


class Questao(models.Model):

    TIPO_CHOICES = (
        ('aberta', 'Aberta'),
        ('objetiva', 'Objetiva'),
    )

    CORRECAO_CHOICES = (
        ('nenhuma', 'Sem correta'),
        ('unica', 'Uma correta'),
        ('multipla', 'Múltiplas corretas'),
    )

    sala = models.ForeignKey(
        'Sala',
        on_delete=models.CASCADE,
        related_name='questoes'
    )

    texto = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='objetiva')
    tipo_correcao = models.CharField(max_length=20, choices=CORRECAO_CHOICES, default='unica')
    alternativa_a = models.CharField(max_length=255, blank=True)
    alternativa_b = models.CharField(max_length=255, blank=True)
    alternativa_c = models.CharField(max_length=255, blank=True)
    alternativa_d = models.CharField(max_length=255, blank=True)
    alternativa_e = models.CharField(max_length=255, blank=True)
    correta_a = models.BooleanField(default=False)
    correta_b = models.BooleanField(default=False)
    correta_c = models.BooleanField(default=False)
    correta_d = models.BooleanField(default=False)
    correta_e = models.BooleanField(default=False)
    feedback = models.TextField(blank=True, null=True)
    criado = models.DateTimeField(auto_now_add=True)
    atualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.texto[:100]

    def respostas_corretas(self):
        corretas = []
        if self.correta_a:
            corretas.append('a')
        if self.correta_b:
            corretas.append('b')
        if self.correta_c:
            corretas.append('c')
        if self.correta_d:
            corretas.append('d')
        if self.correta_e:
            corretas.append('e')
        return corretas


class RespostaAluno(models.Model):

    questao = models.ForeignKey(
        Questao,
        on_delete=models.CASCADE,
        related_name='respostas'
    )

    aluno_nome = models.CharField(max_length=255, db_index=True)
    texto_resposta = models.TextField(blank=True, null=True)
    resposta = models.CharField(max_length=10, blank=True)
    correta = models.BooleanField(default=False)
    nota = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tempo_resposta = models.IntegerField(default=0)
    feedback_professor = models.TextField(blank=True, null=True)
    respondido = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'{self.aluno_nome} - {self.questao}'
