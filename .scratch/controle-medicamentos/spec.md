# Spec: Controle de Medicamentos Hospitalares

**Status:** ready-for-agent
**Gerado por:** `/to-spec` (síntese da sessão `/grill-with-docs`; ver `evidencias/grill-rodadas.md`)

## Problem Statement

Na farmácia central do hospital, o controle de medicamentos é manual: não se sabe com precisão quanto há de cada medicamento, quais lotes estão perto de vencer, quem retirou o quê e para qual setor. Medicamentos controlados podem ser retirados por quem não deveria, lotes vencidos podem chegar ao paciente e a reposição só acontece quando o item já acabou.

## Solution

Um sistema web em que cada funcionário entra com seu login e só vê e faz o que o seu perfil permite. O estoque é mantido por lote; toda retirada consome automaticamente o lote válido que vence primeiro, é recusada se não houver estoque disponível suficiente e fica registrada com funcionário, setor e (para controlados) paciente. Devoluções retornam ao mesmo lote. O Farmacêutico vê alertas de reposição e de validade e consulta a trilha de auditoria completa.

## User Stories

1. Como Funcionário, quero entrar com e-mail e senha, para que só eu use meu acesso.
2. Como Funcionário, quero que minha sessão expire, para que um terminal esquecido aberto não fique liberado indefinidamente.
3. Como Funcionário inativo, quero ser impedido de entrar, para que desligados não acessem o sistema.
4. Como Administrador, quero cadastrar funcionários com um perfil, para que cada um tenha o nível de autorização certo.
5. Como Administrador, quero desativar um funcionário sem apagar o histórico dele, para preservar a auditoria.
6. Como Administrador, quero listar os funcionários e seus perfis, para revisar acessos.
7. Como Administrador, quero cadastrar medicamentos com nome, apresentação, classe de controle e estoque mínimo.
8. Como Administrador, quero ser impedido de cadastrar dois medicamentos com mesmo nome e apresentação, para evitar duplicidade.
9. Como Administrador, quero alterar o estoque mínimo de um medicamento.
10. Como Farmacêutico, quero registrar a entrada de um lote (medicamento, código, validade, quantidade), para que ele passe a compor o estoque.
11. Como Farmacêutico, quero ser impedido de dar entrada em lote já vencido ou com quantidade não positiva.
12. Como Farmacêutico, quero ser impedido de registrar o mesmo código de lote duas vezes para o mesmo medicamento.
13. Como Funcionário, quero consultar o estoque disponível de cada medicamento e seus lotes com validade.
14. Como Enfermeiro, quero retirar uma quantidade de um medicamento comum para um setor, para atender os pacientes.
15. Como Enfermeiro, quero que a retirada consuma primeiro o lote que vence primeiro (FEFO), sem precisar escolher o lote.
16. Como Enfermeiro, quero que a retirada possa usar mais de um lote quando o primeiro não basta.
17. Como Enfermeiro, quero que a retirada seja recusada quando o estoque disponível for menor que o pedido, com uma mensagem clara.
18. Como Enfermeiro, quero ser impedido de retirar medicamento controlado.
19. Como Farmacêutico, quero retirar medicamento controlado informando o paciente.
20. Como Farmacêutico, quero que retirada de controlado sem paciente seja recusada.
21. Como Funcionário, quero que lotes vencidos nunca sejam usados numa retirada.
22. Como Enfermeiro, quero devolver unidades não usadas de uma retirada minha, para que voltem ao estoque.
23. Como Funcionário, quero que a devolução volte ao mesmo lote de onde saiu.
24. Como Funcionário, quero ser impedido de devolver mais do que foi retirado (descontando devoluções anteriores).
25. Como Funcionário, quero ser impedido de devolver para um lote já vencido.
26. Como Enfermeiro, quero ser impedido de devolver retirada feita por outro funcionário; o Farmacêutico pode devolver qualquer uma.
27. Como Farmacêutico, quero descartar unidades de um lote (vencido ou danificado) informando o motivo.
28. Como Farmacêutico, quero ajustar a quantidade de um lote após conferência física, informando o motivo.
29. Como Farmacêutico, quero ver alertas de reposição dos medicamentos abaixo do estoque mínimo.
30. Como Farmacêutico, quero ver alertas de validade dos lotes que vencem em até 30 dias.
31. Como Farmacêutico, quero consultar a trilha de auditoria filtrando por medicamento, funcionário, tipo e período.
32. Como Farmacêutico, quero ver em cada movimentação quem fez, quando, quanto, de qual lote e para qual setor/paciente.
33. Como qualquer Funcionário, quero que nenhuma movimentação possa ser editada ou apagada.
34. Como Enfermeiro, quero ser impedido de registrar entradas, descartes, ajustes e de ver a auditoria.
35. Como Administrador, quero ser impedido de movimentar estoque (separação de funções).
36. Como avaliador, quero subir o sistema com um comando e ter usuários de demonstração já criados.

## Implementation Decisions

- **Módulos** (ADR 0004), cada um com uma interface de serviço; rotas HTTP finas por cima:
  - **Acesso**: funcionários, hash de senha, emissão e validação de token JWT, dependência de autorização por perfil.
  - **Estoque**: medicamentos e lotes; consulta de estoque disponível.
  - **Movimentações**: entrada, retirada (FEFO multi-lote), devolução, descarte, ajuste. Cada operação roda numa transação única que grava a movimentação e atualiza a quantidade do lote (ADR 0003).
  - **Monitoramento**: alertas de reposição e validade; trilha de auditoria com filtros.
- **Modelo de dados**: Funcionário(id, nome, e-mail único, hash, perfil, ativo); Medicamento(id, nome, apresentação, classe, estoque_mínimo; único por nome+apresentação); Lote(id, medicamento, código, validade, quantidade; único por medicamento+código); Movimentação(id, tipo, funcionário, data/hora, setor?, paciente?, motivo?, retirada_origem?); ItemMovimentação(movimentação, lote, quantidade). Uma retirada multi-lote é uma Movimentação com vários itens.
- **Data de referência** ("hoje") é injetável no serviço, para testar validade de forma determinística.
- **Erros de negócio** viram respostas HTTP: 400/409/422 para regra violada (com mensagem em português), 401 sem token, 403 perfil não autorizado, 404 inexistente.
- **API REST JSON** sob `/api`; documentação automática OpenAPI (`/docs`). A interface web estática é servida em `/`.
- **Seed** opcional cria 3 funcionários de demonstração (um por perfil), medicamentos e lotes.

## Testing Decisions

- Um bom teste verifica **comportamento externo**: chama a API como o cliente faria e checa resposta e efeito (estoque, auditoria), sem depender de detalhes internos.
- **Seam principal: a API HTTP** (FastAPI TestClient com banco SQLite em memória por teste). Cobre autenticação, autorização e todas as regras de negócio.
- **Seam secundária: o serviço de movimentações**, só para cenários de data (validade) com "hoje" injetado.
- Ferramentas: pytest + pytest-cov. Meta: todas as user stories com pelo menos um teste; cobertura ≥ 85% no pacote da aplicação.
- Não há código prévio (projeto novo): não há prior art.

## Out of Scope

- Estoque por setor ou transferências entre estoques (ADR 0005).
- Compras, fornecedores, notas fiscais.
- Prontuário eletrônico: o paciente é só um identificador textual.
- Notificações por e-mail/SMS; os alertas ficam no painel.
- Integração com o dispensário físico (hardware).

## Further Notes

- Dados são simulados; nada de informação real de paciente.
- Se houver tempo, comparar `security-and-hardening` (Addy Osmani) no módulo Acesso.
