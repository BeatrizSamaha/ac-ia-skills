# Movimentações imutáveis; a quantidade do lote é atualizada na mesma transação

Toda alteração de quantidade é uma **movimentação** que nunca é editada nem excluída; erros são corrigidos com uma nova movimentação (ajuste ou devolução). A quantidade atual do lote é guardada no próprio lote e atualizada na mesma transação de banco que grava a movimentação, para que as consultas de estoque sejam rápidas e a trilha de auditoria seja sempre consistente com o estoque.

## Considered Options

- Event sourcing puro (estoque recalculado somando movimentações): mais elegante, mas exagerado para o porte e mais lento de consultar.
- CRUD com edição de quantidades: quebra a auditoria, que é requisito.
