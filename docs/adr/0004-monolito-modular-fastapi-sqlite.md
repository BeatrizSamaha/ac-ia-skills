# Monólito modular em FastAPI + SQLite, com interface web estática

Uma única aplicação Python (FastAPI) com quatro módulos de domínio (acesso, estoque, movimentações, monitoramento) que só conversam pelas interfaces de serviço uns dos outros. O SQLite foi escolhido para que qualquer pessoa rode o sistema e os testes sem instalar um servidor de banco; o acesso é via SQLAlchemy, o que mantém viável trocar para PostgreSQL. A interface web é HTML/JS servida pela própria API (a equipe não domina React).

## Considered Options

- Microsserviços por módulo: sem ganho para um sistema deste porte, e complica a demo.
- PostgreSQL desde o início: mais realista, mas piora a reprodutibilidade (critério de avaliação).
