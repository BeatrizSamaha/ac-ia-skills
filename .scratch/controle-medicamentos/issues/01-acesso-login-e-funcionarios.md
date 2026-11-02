# 01: Login e gestão de funcionários

**What to build:** Funcionário entra com e-mail e senha e recebe um token; o Administrador cadastra, lista e desativa funcionários. Inativos não entram. Rotas protegidas recusam quem não tem token (401) ou perfil (403).

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] Login válido devolve token; senha errada e inativo → 401
- [ ] Só Administrador cria/lista/desativa funcionários (outros → 403)
- [ ] E-mail duplicado → 409
- [ ] Senha guardada como hash
