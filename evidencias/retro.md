# Retrospectiva — skill `retro` (sessão de 01–02/11/2026)

Candidatos a melhoria do ambiente do agente, do mais grave para o menos grave.

1. **Automated checks: o repositório não tinha nenhum guardrail.** Não havia CI nem pre-commit. Durante a sessão, o lint (pyflakes) só rodou porque o agente lembrou de chamá-lo. **Feito:** `.github/workflows/ci.yml` roda pyflakes, a checagem do glossário e o pytest, com cobertura mínima de 90%.
2. **Coding standards → checagem mecânica.** A violação mais frequente no `code-review` foi o uso de termos que o `GLOSSARY.md` manda evitar ("usuário", "saldo", "operação", "saída"). Essa regra é mecânica, então virou um script determinístico (`scripts/checa_glossario.py`) em vez de mais uma linha de instrução. Limitação: termos genéricos ("item", "log", "edição") geram falso positivo e ficaram numa lista de ignorados.
3. **Tool economy: os testes estavam lentos.** A suíte levava 77 s porque o bcrypt rodava com 12 rounds em cada teste. Reduzir para 4 rounds nos testes baixou para cerca de 4 s, o que tornou viável rodar o ciclo red → green a cada ticket.
4. **Information access: o agente não conseguia criar repositório nem issues.** A API do GitHub (GraphQL e criação de repositórios) não está disponível no ambiente. O repositório foi criado pelo navegador, com a usuária logada, e o tracker passou a ser local (`.scratch/`). A configuração ficou registrada em `CLAUDE.md` para as próximas sessões não tentarem `gh issue`.
5. **Information access: o Swagger UI depende de CDN.** O print de `/docs` falhou no ambiente do agente, que não tem acesso à internet externa. Não afeta o uso real, mas a verificação visual da documentação da API ficou manual.
6. **Navigation: tudo bem.** Com o `CLAUDE.md` curto apontando para `docs/agents/*`, o glossário e os ADRs, o agente achou o contexto sem buscas extras.
