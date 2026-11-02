# Controle de Medicamentos Hospitalares

AC "Engenharia de Software + IA: desenvolvimento orientado por Skills". Disciplina Métodos e Aplicações de IA, Prof. Pedro Calais (Ibmec BH, 2026/02).
Equipe: Beatriz Samaha de Faria Garcia.

## Problema

Controlar o armazenamento, a retirada, a devolução e a reposição de medicamentos da farmácia central de um hospital, com:

- login e níveis de autorização: Administrador, Farmacêutico e Enfermeiro;
- estoque por lote, com retirada automática **FEFO** (sai primeiro o que vence primeiro);
- bloqueio de retirada acima do estoque disponível e de uso de lote vencido;
- regras para medicamentos controlados (só o Farmacêutico retira, e o paciente é obrigatório);
- alertas de reposição e de validade;
- trilha de auditoria imutável de todas as movimentações.

O vocabulário do domínio está em [`GLOSSARY.md`](GLOSSARY.md), e as decisões de arquitetura em [`docs/adr/`](docs/adr).

## Conjunto de skills

**Matt Pocock Skills**, em [`.claude/skills/`](.claude/skills). A justificativa está em [`docs/adr/0001-conjunto-de-skills.md`](docs/adr/0001-conjunto-de-skills.md).
Fluxo usado: `setup-matt-pocock-skills` → `grill-with-docs` → `to-spec` → `to-tickets` → `implement`/`tdd` → `code-review` → `retro`.

## Como executar

Requisitos: Python 3.11 ou mais recente.

```bash
git clone https://github.com/BeatrizSamaha/ac-ia-skills.git
cd ac-ia-skills
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m app
```

Depois, abra **http://localhost:8000**. A documentação interativa da API fica em **http://localhost:8000/docs**.

Na primeira execução, o sistema cria o banco `medicamentos.db` com dados de demonstração. A senha de todos os usuários de demonstração é `demo12345`:

| Perfil | E-mail |
|---|---|
| Administrador | `admin@hospital.demo` |
| Farmacêutico | `farmaceutico@hospital.demo` |
| Enfermeiro | `enfermeiro@hospital.demo` |

Para recomeçar do zero, apague o `medicamentos.db`. Variáveis de ambiente opcionais: `PORT`, `DATABASE_URL` e `JWT_SECRET` (se não for definida, o sistema gera um segredo aleatório em `.jwt_secret`).

## Como rodar os testes

```bash
pytest                          # 71 testes
pytest --cov=app                # cobertura (96%)
```

Os testes exercitam o sistema pela API HTTP (a seam combinada na spec), com banco em memória e relógio controlável, para testar a validade dos lotes.

## Estrutura

```
app/
  acesso/          login (JWT), funcionários, autorização por perfil
  estoque/         medicamentos, lotes, estoque disponível
  movimentacoes/   entrada, retirada FEFO, devolução, descarte, ajuste
  monitoramento/   alertas de reposição e de validade, trilha de auditoria
  web/             interface (HTML + JS) servida pela própria API
  models.py        modelo de dados compartilhado (ADR 0006)
  seed.py          dados de demonstração
tests/             um arquivo por ticket (test_01 ... test_10)
docs/adr/          decisões de arquitetura
docs/c4/           modelos C4 (Contexto, Container, Componentes, Código)
.scratch/          spec e tickets (tracker local das skills)
evidencias/        diário, rodadas do grill, revisões, logs red/green e prints
slides/            apresentação final
```

## Endpoints principais

| Método | Rota | Quem |
|---|---|---|
| POST | `/api/login` | todos |
| GET/POST | `/api/funcionarios`, `POST /api/funcionarios/{id}/desativar` | Administrador |
| GET | `/api/medicamentos`, `/api/medicamentos/{id}` | todos |
| POST/PATCH | `/api/medicamentos` | Administrador |
| POST | `/api/movimentacoes/entradas`, `/descartes`, `/ajustes` | Farmacêutico |
| POST | `/api/movimentacoes/retiradas`, `/devolucoes` | Farmacêutico, Enfermeiro |
| GET | `/api/alertas/reposicao`, `/api/alertas/validade`, `/api/auditoria` | Farmacêutico |
