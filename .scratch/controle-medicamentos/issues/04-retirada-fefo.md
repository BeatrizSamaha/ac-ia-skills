# 04: Retirada FEFO com regras de controlados

**What to build:** Funcionário retira uma quantidade de um medicamento para um setor; o sistema consome lotes válidos em FEFO (podendo usar vários), recusa se não houver estoque disponível suficiente e aplica as regras de medicamento controlado.

**Blocked by:** 03

**Status:** ready-for-agent

- [ ] FEFO, multi-lote, ignora vencidos
- [ ] Quantidade > disponível → recusada sem alterar nada
- [ ] Enfermeiro + controlado → 403; controlado sem paciente → 422
- [ ] Administrador não retira
- [ ] Movimentação registra funcionário, setor, paciente e lotes consumidos
