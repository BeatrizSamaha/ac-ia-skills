# Módulos leem o modelo compartilhado; só Movimentações altera quantidades

Origem: apontamento da skill `code-review` (eixo Standards), que encontrou importações cruzadas que violavam a leitura estrita do ADR 0004.

O ADR 0004 diz que os módulos conversam pelas interfaces de serviço, mas o ADR 0003 exige que a quantidade do lote seja alterada na mesma transação da movimentação. Para conciliar os dois: as entidades (`app/models.py`) são um **modelo compartilhado** que qualquer módulo pode **ler**; a **escrita** de `Lote.quantidade` acontece **somente** no serviço de Movimentações; e a representação pública de uma movimentação mora em `movimentacoes/esquemas.py` (não nas rotas), que é o que o Monitoramento importa.

## Considered Options

- Um serviço de Estoque com `debitar/creditar` chamado por Movimentações: separação mais pura, mas espalha a transação por dois módulos sem ganho real neste porte.
