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
