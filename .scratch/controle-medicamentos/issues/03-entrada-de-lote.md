# 03: Entrada de lote

**What to build:** Farmacêutico registra a entrada de um lote; o lote passa a compor o estoque disponível e a entrada aparece como movimentação.

**Blocked by:** 02

**Status:** ready-for-agent

- [ ] Lote vencido ou quantidade ≤ 0 → recusado
- [ ] Código de lote repetido para o mesmo medicamento → 409
- [ ] Só Farmacêutico
- [ ] Gera movimentação do tipo Entrada
