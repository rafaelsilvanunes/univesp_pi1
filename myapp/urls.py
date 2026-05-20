from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('lgpd/', views.lgpd, name='lgpd'),

    # auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # professor
    path('salas/', views.salas, name='salas'),
    path('sala/nova/', views.sala_create, name='nova_sala'),
    path('sala/<int:sala_id>/dashboard/', views.sala_resultado, name='resultado_sala'),
    path('sala/<int:sala_id>/editar/', views.sala_edit, name='editar_sala'),
    path('sala/<int:sala_id>/excluir/', views.sala_delete, name='excluir_sala'),
    path('sala/<int:sala_id>/questoes/', views.questoes, name='questoes'),
    path('sala/<int:sala_id>/questao/nova/', views.questao_create, name='nova_questao'),
    path('sala/<int:sala_id>/questao/<int:questao_id>/editar/', views.questao_edit, name='editar_questao'),
    path('sala/<int:sala_id>/questao/<int:questao_id>/excluir/', views.questao_delete, name='excluir_questao'),
    path('sala/<int:sala_id>/qrcode/', views.qrcode_sala, name='qrcode'),

    # aluno
    path('aluno/', views.aluno_login, name='login_aluno'),
    path('aluno/responder/<str:codigo>/', views.aluno_responder, name='responder_aluno'),
    path('aluno/resultado/<str:codigo>/', views.aluno_resultado, name='resultado_aluno'),
]
