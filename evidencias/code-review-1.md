# Code review 1 — skill `code-review` (fixed point 0595cd9, dois subagentes em paralelo)

Relatórios dos dois eixos, como entregues pelos subagentes (sem reordenar).
Resumo: Standards — 3 violações de padrão documentado (ADR 0004, glossário) + 10 smells + 4 achados de segurança; pior: segredo JWT padrão no código. Spec — 2 lacunas, 5 pontos fora do escopo, 3 discutíveis; pior: README sem instruções de execução.

## Standards

- **ADR 0004 violado:** Monitoramento importa rotas de Movimentações (`MovimentacaoOut, saida`); serviços consultam Lote/Movimentacao direto. Tensão ADR 0003 × 0004 não registrada.
- **Glossário violado (_Avoid_):** "usuário" (`__main__.py`, `#usuario`), "saldo" (nome de teste), "operação" (`name="operacao"`), "saída" (`saida()`, `_saida()`). Lacuna: `ItemMovimentacao`, `variacao`, `devolvivel` fora do glossário.
- **Smells:** Duplicated Code (`f"{nome} {apresentacao}"` 3x; cálculo de "já devolvido" 2x; laço `min(falta, ...)` 2x); Message Chains (`l.medicamento.nome`); Repeated Switches (regras de perfil em rota, serviço e HTML); Data Clumps (`s, funcionario, agora`); Primitive Obsession (setor/paciente/email como `str`); Mysterious Name (`s, f, l, c, q, d`); conftest altera global no import; `HOJE`/`AGORA` duplicados.
- **Segurança:** segredo JWT padrão hard-coded em `create_app`; enumeração de e-mails por tempo (bcrypt só roda se e-mail existe), sem rate limiting; admin pode se autodesativar via API; XSS: nada explorável encontrado.

## Spec

- **Faltando/parcial:** README sem "como executar/testar" (ticket 10, US36), e "Estrutura" cita `src/`; erros de validação do Pydantic em inglês (spec pede mensagens em português).
- **Fora do escopo:** `GET /api/eu` e `GET /movimentacoes/retiradas` (apoio à UI); senha ≥ 8 e token de 8h; duplicidade case-insensitive; alerta de validade inclui lotes já vencidos; `.jwt_secret` em arquivo.
- **Discutível:** devolução multi-lote **pula** lote vencido em vez de recusar, e o sistema escolhe o lote; 403 antes de 404 na devolução; admin pode se autodesativar.
- **Verificado correto:** FEFO, lote que vence hoje, rejeição sem efeito parcial, controlados, expiração de token, desativação, reposição, filtro de período, imutabilidade. Cobertura 96%.

## Decisão sobre cada achado

| Achado | Ação |
|---|---|
| Segredo JWT padrão | **Corrigido**: `create_app` exige segredo |
| Enumeração de e-mail por tempo | **Corrigido**: bcrypt roda contra hash fictício |
| Admin se autodesativa | **Corrigido** (teste novo) |
| Erros de validação em inglês | **Corrigido**: handler em português (teste novo) |
| README | **Corrigido** |
| ADR 0004 × imports | **Corrigido** parcialmente: serializador movido para `movimentacoes/esquemas.py` (interface pública); **ADR 0006** registra que módulos leem o modelo compartilhado e só Movimentações altera quantidades |
| Termos _Avoid_ | **Corrigido** (renomeações) + termos novos no glossário |
| Duplicação `nome apresentacao` | **Corrigido**: `Medicamento.descricao` |
| Duplicação "já devolvido" / laço FEFO | **Corrigido**: funções `_devolvido_por_lote` e `_distribuir` |
| Devolução pula lote vencido | **Mantido** e documentado no glossário/spec — a decisão foi tomada por delegação; **pendente de confirmação da Beatriz** |
| Alerta inclui vencidos | **Mantido** (útil para descarte) e documentado na spec |
| Rate limiting, Primitive Obsession, nomes curtos, Data Clumps | **Não corrigido** — fora do escopo acadêmico; registrado como trabalho futuro |
