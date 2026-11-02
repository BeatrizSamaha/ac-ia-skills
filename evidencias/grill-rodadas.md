# Registro do `/grill-with-docs`

Skills: `grilling` + `domain-modeling`. O formato segue a skill: perguntas numeradas, cada uma com uma resposta recomendada.

**Observação de processo (para a análise crítica):** a Beatriz respondeu à rodada 1 delegando: "quero que você faça tudo, faça todas as etapas, aí depois eu confiro". Por isso, a partir daí as recomendações do agente foram adotadas como decisão e ficaram marcadas aqui para ela revisar. A skill foi feita para que o humano decida ("The decisions are the user's"), então este é um desvio consciente do processo previsto.

## Rodada 1 (perguntas feitas à usuária)

| # | Pergunta | Decisão |
|---|---|---|
| Q1 | Perfis de usuário | Administrador, Farmacêutico, Enfermeiro |
| Q2 | Unidade do estoque | Por **lote** (medicamento + lote + validade + quantidade), retirada **FEFO** |
| Q3 | Locais de estoque | Só a **farmácia central**; a retirada registra o **setor** de destino |
| Q4 | Paciente na retirada | Obrigatório para **controlados**, opcional para **comuns** |
| Q5 | Medicamento controlado | Classe **comum** ou **controlado**; controlado exige o perfil Farmacêutico |
| Q6 | Tecnologia | Python + FastAPI + SQLite + web em HTML/JS; testes em pytest |

## Rodada 2 (fronteira aberta pelas respostas da rodada 1; decidida pelo agente sob delegação)

| # | Pergunta | Decisão | Motivo |
|---|---|---|---|
| Q7 | Retirada de quantidade maior que o disponível | **Rejeitar a retirada inteira**, sem atendimento parcial | Evita estado ambíguo; o funcionário decide se retira menos |
| Q8 | A retirada pode consumir vários lotes? | **Sim**, FEFO entre lotes válidos; a movimentação registra cada lote consumido | Sem isso, um lote quase vazio bloquearia a retirada |
| Q9 | Lote vencido | **Nunca** é retirado; só pode sair por **descarte** (Farmacêutico) | Segurança do paciente |
| Q10 | Devolução | Referencia uma retirada; quantidade ≤ retirado − já devolvido; volta ao **mesmo lote**; recusada se o lote venceu | Rastreabilidade por lote |
| Q11 | Estoque mínimo | Definido por medicamento; o **alerta de reposição** surge quando o estoque disponível (lotes válidos) fica abaixo do mínimo | Pedido do enunciado |
| Q12 | Alerta de validade | Lotes que vencem em até **30 dias** | Prazo usual de farmácia hospitalar |
| Q13 | Correção de erro | Movimentações são **imutáveis**; a correção é feita com uma nova movimentação (ajuste) | Auditoria confiável |
| Q14 | Permissões por perfil | Admin: funcionários e cadastro de medicamentos. Farmacêutico: entrada, descarte, ajuste, qualquer retirada/devolução, relatórios. Enfermeiro: retirada/devolução de comuns, consulta de estoque | Menor privilégio |
| Q15 | Funcionário desligado | É **desativado** (nunca excluído); não consegue logar; o histórico é preservado | Auditoria |
| Q16 | Notificação | Alertas aparecem no **painel** do Farmacêutico (sem e-mail) | Escopo |

## Cenários de borda usados para testar o modelo (domain-modeling)

- O enfermeiro pede 10 unidades de dipirona, o lote A (vence antes) tem 4 e o lote B tem 20 → consome 4 de A e 6 de B.
- Pedido de 30, com 24 disponíveis em lotes válidos e 50 em um lote vencido → **rejeitado** (o vencido não conta).
- Devolução de 5 de uma retirada de 3 → **rejeitada**.
- Enfermeiro tenta retirar morfina (controlado) → **403**.
- Farmacêutico retira morfina sem paciente → **rejeitado**.
- Administrador desativa um enfermeiro com retiradas no histórico → o histórico continua intacto.
