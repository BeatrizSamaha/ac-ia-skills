# Estoque controlado por lote, com consumo FEFO

O estoque é mantido por **lote** (medicamento + código + validade), não como um número único por medicamento, porque sem lote é impossível controlar validade e rastrear qual unidade foi para qual setor. Uma retirada consome lotes válidos em ordem FEFO e pode atravessar vários lotes; cada lote consumido fica registrado.

## Considered Options

- Quantidade única por medicamento: mais simples, mas não atende ao requisito de validade.
- Retirada obrigatoriamente de um único lote: simples, mas bloqueia retiradas quando o lote que vence primeiro está quase vazio.
