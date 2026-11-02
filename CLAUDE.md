# CLAUDE.md

Projeto acadêmico (AC — Métodos e Aplicações de IA, Ibmec BH): sistema de controle de medicamentos e materiais hospitalares, desenvolvido com o conjunto **Matt Pocock Skills** (`.claude/skills/`).

Idioma do projeto: português (documentação, glossário, ADRs, tickets). Código e nomes técnicos podem ficar em inglês, desde que consistentes com o `GLOSSARY.md`.

Toda sessão de trabalho deve gerar uma entrada em `evidencias/diario.md` (skill usada, resultado, se mudou rota, o que foi manual).

## Agent skills

### Issue tracker

Issues e specs ficam como arquivos markdown em `.scratch/` (o `gh issue` não funciona nesta sessão). See `docs/agents/issue-tracker.md`.

### Triage labels

Os cinco papéis canônicos com os nomes padrão (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: um `GLOSSARY.md` na raiz e ADRs em `docs/adr/`. See `docs/agents/domain.md`.
