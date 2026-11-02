# ADR 0001 — Usar o conjunto Matt Pocock Skills

- **Data:** 2026-11-02
- **Status:** aceita
- **Origem:** decisão da equipe

## Contexto

A atividade exige escolher um conjunto principal de agent skills e justificá-lo pelas características da aplicação. A aplicação é um sistema de controle de medicamentos hospitalares com muitas regras de negócio (estoque, validade, níveis de autorização, devoluções, auditoria) e requisitos ambíguos que precisam ser esclarecidos antes do código.

## Decisão

Usar **Matt Pocock Skills** (`mattpocock/skills`), copiadas para `.claude/skills/` (commit de origem em `.claude/skills/SOURCE-COMMIT`). Fluxo: `grill-with-docs` → `to-spec` → `to-tickets` → `implement`/`tdd` → `code-review`, com `diagnosing-bugs` quando necessário e `retro` ao fim das sessões.

## Alternativas consideradas

- **Superpowers:** forte em planejamento e execução, mas menos focado em modelagem de domínio e glossário.
- **Addy Osmani Agent Skills:** cobre o ciclo completo, mas 25 skills, muitas de front-end, performance e deploy, pouco relevantes aqui.
- **pstack:** repositório jovem, orientado a TypeScript e a delegação para o Grok por padrão.
- **GSD Core:** fases, ondas e subagentes; sobrecarga excessiva para o porte do sistema.

## Consequências

- O `grill-with-docs` gera `GLOSSARY.md` e ADRs durante o esclarecimento de requisitos, o que alimenta diretamente o critério de especificação e modelagem.
- Cada etapa produz artefatos rastreáveis (spec, tickets, testes, revisões), usados como evidência.
- Adaptação necessária: o tracker padrão (GitHub Issues via `gh`) não funciona no ambiente do agente; usamos o tracker local em `.scratch/`.
- Possível comparação: `security-and-hardening` (Addy Osmani) no módulo de autenticação, com e sem a skill.
