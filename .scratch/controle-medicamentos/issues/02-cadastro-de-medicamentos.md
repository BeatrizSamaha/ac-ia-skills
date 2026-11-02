# 02: Cadastro de medicamentos e consulta de estoque

**What to build:** Administrador cadastra medicamentos (nome, apresentação, classe de controle, estoque mínimo) e altera o estoque mínimo; qualquer funcionário consulta medicamentos com estoque disponível e lotes.

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] Nome+apresentação duplicados → 409
- [ ] Estoque mínimo negativo → 422
- [ ] Só Administrador cadastra/altera
- [ ] Consulta mostra estoque disponível (ignora lotes vencidos)
