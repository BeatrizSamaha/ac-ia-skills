# Diário de bordo — uso das skills

Uma entrada por sessão de trabalho. Alimenta os slides (seções 3, 5, 6, 7 e 8 da apresentação).

## Modelo de entrada

### AAAA-MM-DD — Fase: <requisitos | design | plano | TDD | implementação | revisão | debug>
- **Skill usada:**
- **O que pedi:**
- **O que a skill fez:**
- **Resultado / artefato:** (link para print/log)
- **Mudou rota ou decisão?** sim/não — qual:
- **Funcionou / não funcionou:**
- **Precisei fazer manualmente:**
- **Adaptação necessária (instrução/config):**
- **Defeitos evitados ou retrabalho:**

---

## Entradas

### 2026-11-01 — Fase 0: organização
- Repositório criado com estrutura de pastas, README e este diário.
- Pendências: confirmar com o professor as seções 4, 6 e 7 (ausentes no PDF) e se há relatório técnico separado dos slides.

### 2026-11-02 — Fases 1 e 2: problema e conjunto de skills
- **Problema escolhido:** sistema de controle de medicamentos hospitalares (entre 3 ideias: GlowCheck, FitCheck e este). Motivo: cobre todos os critérios de complexidade sem depender de OCR/visão computacional.
- **Skills:** análise dos 5 conjuntos → Matt Pocock Skills (ADR 0001).
- **Skill usada:** `setup-matt-pocock-skills` (configuração do repo: tracker, labels, domain docs).
- **Precisei adaptar:** o tracker padrão (GitHub Issues via `gh`) não funciona no ambiente do agente (GraphQL bloqueado) → tracker local em `.scratch/`.

### 2026-11-02 — Delegação total ao agente
- A Beatriz pediu: "quero que você faça tudo, faça todas as etapas, aí depois eu confiro". A partir daqui, as decisões de domínio foram tomadas pelo agente a partir das próprias recomendações e marcadas para revisão (`evidencias/grill-rodadas.md`).
- **Impacto no processo:** a skill `grilling` prevê que as decisões são do humano. Sem ele, ela perde a função de reduzir ambiguidade *do humano*. Ainda assim, ela forçou o agente a explicitar 16 decisões e 6 cenários de borda antes do código.

### 2026-11-02 — `/grill-with-docs` (grilling + domain-modeling)
- **Resultado:** `GLOSSARY.md` (22 termos; 25 após o code review), ADRs 0002–0005 e 6 cenários de borda que viraram testes.
- **Mudou rota?** Sim. A pergunta Q8 (retirada multi-lote) mostrou que "retirar de um lote" bloquearia retiradas comuns, e virou o ADR 0002. A Q13 (correção de erro) levou às movimentações imutáveis (ADR 0003).
- **Adaptação:** o ADR 0001 foi escrito no formato do nosso template antes de lermos o `ADR-FORMAT.md` da skill, que é mais enxuto. Os ADRs seguintes já usaram o formato da skill.

### 2026-11-02 — C4 Contexto e Container (antes do código)
- Feitos em Mermaid e renderizados em PNG (`docs/c4/`). **Manual:** nenhuma skill do conjunto gera C4. A prática foi feita sem skill.

### 2026-11-02 — `/to-spec` e `/to-tickets`
- **Resultado:** spec com 36 user stories, uma seam combinada (API HTTP) e 10 tickets com dependências (`.scratch/controle-medicamentos/`).
- **Desvio:** a skill pede para o usuário aprovar as seams e a divisão em tickets. Pela delegação, isso não aconteceu. O ticket 09 (interface) ficou como fatia horizontal, contrariando a regra de "vertical slices", porque fazer UI em cada ticket encareceria cada ciclo.

### 2026-11-02 — `/implement` + `/tdd` (tickets 01–10)
- Ciclo red → green por ticket, com logs em `evidencias/logs/tdd-NN-{red,green}.txt`.
- **Desvio da skill:** a `tdd` pede 1 teste → 1 implementação. Fizemos 1 ticket (5–11 testes) → 1 implementação. Ainda é vertical por ticket, mas não por teste.
- **Defeitos que os testes pegaram durante o desenvolvimento:**
  1. A expiração do token comparava horários em fusos diferentes (`fromtimestamp` local × `exp` UTC). Corrigido antes de qualquer teste passar.
  2. Os testes de validade avançavam o relógio 31 dias e o token expirava. Era um defeito do teste, e foi corrigido fazendo login de novo.
- **Defeitos que só a verificação visual pegou (Playwright):** o cartão de login continuava visível depois de entrar (CSS `display:grid` sobrescrevia `[hidden]`), e os campos dos formulários estavam desalinhados. Nenhum teste de API pegaria isso.
- **Produtividade:** a suíte caiu de 77 s para 4 s ao reduzir os rounds de bcrypt nos testes.

### 2026-11-02 — `/code-review` (2 subagentes em paralelo)
- **Resultado:** `evidencias/code-review-1.md`. Eixo Standards: violações do ADR 0004 e do glossário, 10 smells e 4 achados de segurança. Eixo Spec: README incompleto, mensagens em inglês e 3 pontos discutíveis.
- **Mudou rota?** Sim. Surgiu o ADR 0006 (modelo compartilhado + escrita só por Movimentações). Foram corrigidos o segredo JWT padrão, a enumeração de e-mails por tempo de resposta e a autodesativação do admin, com 3 testes novos.
- **O que a skill fez melhor que um "revise o código":** separar Standards de Spec. O revisor de Spec achou o README vazio e a devolução que pula lote vencido, coisas que uma revisão "de código" não olharia. O de Standards cobrou o glossário, que nenhum linter conhece.

### 2026-11-02 — C4 Componentes e Código; `/retro`
- C4 nível 3 e 4 gerados a partir do código final.
- A retro (`evidencias/retro.md`) gerou dois guardrails: CI e `scripts/checa_glossario.py`.

### 2026-11-02 — Apresentação: revisão contra o enunciado
- A Beatriz pediu que o PowerPoint cobrisse cada etapa do PDF com exemplos. O deck passou de 16 para 21 slides: um slide de roteiro ligando cada slide ao item do enunciado, os critérios de complexidade um a um, 4 slides de exemplo com prints reais dos artefatos (grill, spec→ticket, red→green, achado do review→diff) e as 7 perguntas da seção 5 respondidas uma a uma.
