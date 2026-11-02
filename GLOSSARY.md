# Controle de Medicamentos Hospitalares

Controle do armazenamento, retirada, devolução e reposição de medicamentos da farmácia central de um hospital, com rastreabilidade de quem fez cada movimentação.

## Pessoas e acesso

**Funcionário**:
Pessoa do hospital com credenciais de acesso ao sistema e exatamente um perfil.
_Avoid_: usuário, colaborador

**Perfil**:
Nível de autorização de um funcionário: Administrador, Farmacêutico ou Enfermeiro.
_Avoid_: papel, cargo, role

**Funcionário inativo**:
Funcionário desligado do sistema; não acessa, mas permanece no histórico.
_Avoid_: funcionário excluído

## Itens e estoque

**Medicamento**:
Item farmacêutico cadastrado, identificado por nome e apresentação, com uma classe de controle e um estoque mínimo.
_Avoid_: produto, item, remédio

**Classe de controle**:
Classificação do medicamento quanto à restrição de retirada: comum ou controlado.
_Avoid_: categoria, tipo

**Medicamento controlado**:
Medicamento cuja retirada exige o perfil Farmacêutico e a indicação de paciente.
_Avoid_: tarja preta, restrito

**Lote**:
Quantidade de um medicamento recebida junto, com código de lote e data de validade próprios.
_Avoid_: remessa, pacote

**Lote vencido**:
Lote cuja data de validade já passou; não pode ser retirado nem receber devolução.

**Estoque disponível**:
Soma das quantidades dos lotes não vencidos de um medicamento.
_Avoid_: saldo, estoque total

**Estoque mínimo**:
Quantidade abaixo da qual o estoque disponível de um medicamento exige reposição.
_Avoid_: ponto de pedido

**FEFO**:
Regra de consumo em que a retirada sai primeiro do lote válido que vence primeiro.
_Avoid_: FIFO

## Movimentações

**Movimentação**:
Registro imutável de uma alteração de quantidade em um lote, com funcionário e data/hora.
_Avoid_: transação, lançamento, operação

**Entrada**:
Movimentação que cria um lote na farmácia central.
_Avoid_: recebimento, compra

**Retirada**:
Movimentação que tira unidades de um ou mais lotes para um setor.
_Avoid_: saída, dispensação, baixa

**Devolução**:
Movimentação que retorna ao mesmo lote unidades de uma retirada anterior.
_Avoid_: estorno, retorno

**Descarte**:
Movimentação que remove unidades de um lote, tipicamente vencido ou danificado.
_Avoid_: perda, baixa

**Ajuste**:
Movimentação que corrige a quantidade de um lote após uma conferência física.
_Avoid_: edição, correção de lançamento

**Setor**:
Unidade do hospital destinatária de uma retirada (UTI, Pronto-Socorro, etc.).
_Avoid_: ala, departamento

**Paciente**:
Pessoa (simulada) a quem se destina uma retirada de medicamento controlado.

## Monitoramento

**Alerta de reposição**:
Aviso de que o estoque disponível de um medicamento está abaixo do estoque mínimo.
_Avoid_: alerta de estoque baixo

**Alerta de validade**:
Aviso de que um lote com unidades vence em até 30 dias.

**Trilha de auditoria**:
Histórico completo de movimentações, consultável por medicamento, lote, funcionário e período.
_Avoid_: log
