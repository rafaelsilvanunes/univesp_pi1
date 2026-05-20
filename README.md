# Univesp - Projeto Integrador 1 - Voz para Todos (Beta)
Aplicação web para interação professor–aluno com **perguntas em tempo real** e **registro de respostas** para acompanhamento pedagógico.

## Contexto e Problema
Em aulas presenciais, é comum que apenas alguns alunos respondam às perguntas feitas pelo professor, enquanto parte significativa da turma permanece silenciosa por timidez, receio de errar ou pela dinâmica do tempo. Métodos tradicionais para coletar respostas de todos (papel, chamada oral, discussões longas) são lentos e dificultam decisões imediatas do docente durante a aula.

**O projeto busca um meio simples e rápido de coletar respostas de toda a turma em tempo real**, com visualização imediata e histórico para análise posterior.

## Objetivo
Desenvolver e validar um **protótipo funcional** de aplicação web que permita ao professor:
- criar e publicar perguntas em tempo real para a turma;
- permitir que alunos respondam via celular;
- apresentar resultados consolidados imediatamente (inclusive para projeção);
- registrar respostas em banco de dados para consulta e análise posteriores.

## Escopo
O Produto Mínimo Viável (MVP) contempla:
- Criação de salas;
- Acesso do Aluno a sala por QRCode;
- Publicação de pergunta (múltipla escolha e/ou resposta curta);
- Resposta do aluno via interface mobile (web responsivo);
- Painel do professor com resultados ao vivo (contagens, percentuais e lista);
- Persistência e consulta básica do histórico da sala e do aluno.

## Tecnologias Utilizadas
Para o teste real em sala de aula foi utilizado a seguinte estrutura:
- Hospedagem Oracle Cloud: Instância AMD, 1Gb RAM, Oracle Linux e SSL;
- Backend: Django + Gunicorn + Nginx;
- Frontend: HTML + CSS + JS;
- Banco de dados: PostgreSQL.

## Quer realizar o teste do MVP?
Siga esses passos:
- O MVP está em funcionamento no endereço https://157.151.14.23.nip.io/ visite o portal;
- Solicite a criação do login professor pelo e-mail rafaelsilv@gmail.com enviando nome, instituição, cidade e email (se diferente);
- Crie as salas e questões como professor;
- Para responder deve acessar a opção Aluno na home ou via QRCode disponibilizado pelo professor (gerado ao criar a sala);
- Lembre que a chave unica é o nome do aluno então utilize RA para evitar duplicidade;
- A revisita apresenta o resultado.
