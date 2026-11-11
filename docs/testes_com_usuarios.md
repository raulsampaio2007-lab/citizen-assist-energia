# Testes com usuários

Objetivo: ver se as pessoas entendem as orientações do assistente e se elas ajudam a decidir alguma coisa. Não anotamos nome, endereço, valor da conta real nem qualquer dado pessoal. Cada participante aparece só como P1, P2 e assim por diante.

## Como testamos

Cada pessoa usou o assistente sozinha, com a gente só observando, e depois respondeu às perguntas abaixo.

Situações testadas:

1. Descobrir quanto o chuveiro gasta na casa dela, informando os próprios dados.
2. Perguntar como economizar sem gastar dinheiro.
3. Perguntar se vale a pena colocar placa solar ou aquecedor.
4. Dizer que mora de aluguel, ou que tem R$ 5.000 para investir, e pedir uma recomendação.
5. Encontrar de onde vieram os números e o que eles não garantem.

Perguntas depois do teste:

- Com as suas palavras, o que o assistente recomendou?
- Teve alguma palavra ou conta que você não entendeu?
- Você acha que esse valor de economia é garantido? Por quê?
- Isso ajudaria você a decidir alguma coisa em casa? De 1 a 5, quanto?

## Registro dos testes

| Participante | Perfil geral | Data | Situações feitas | Entendeu a recomendação? | Utilidade (1 a 5) | Comentários |
|---|---|---|---|---|---|---|
| P1 | adulto, testou pelo link online | 10/11/2026 | Usou o chat, mudou os dados no painel e pediu recomendações | Sim, mas percebeu que a recomendação não batia com os números que ele tinha mudado | Não deu nota | "A tabela embaixo não está atualizando. O chatbot está." Disse que a recomendação usava o que estava na tabela e não o recálculo, e que as respostas do chat são instantâneas, o que achou adequado |
| P1, segunda vez | mesmo participante, depois do primeiro ajuste | 10/11/2026 | Mudou os dados no painel e olhou a tabela | Sim | Não deu nota | Viu o resumo de cima mudar sozinho, mas achou que a tabela comparativa continuava parada |
| P1, terceira vez | mesmo participante, depois do segundo ajuste | 10/11/2026 | Pediu recomendação e comparação das alternativas no chat | Sim | Não deu nota | Disse que a recomendação passou a vir com o valor certo, mas que na comparação das alternativas os valores de cada opção não batiam |
| P2 | PREENCHER | PREENCHER | PREENCHER | PREENCHER | PREENCHER | PREENCHER |
| P3 | PREENCHER | PREENCHER | PREENCHER | PREENCHER | PREENCHER | PREENCHER |

No perfil geral, escreva só algo como "adulto, mora de aluguel" ou "idoso, casa própria".

## Ajustes feitos depois dos testes

| O que aconteceu no teste | O que mudamos | Arquivo |
|---|---|---|
| P1 mudou números no painel sem clicar em Recalcular. A tabela não mudava e o chat respondia com os valores antigos, apagando o que ele tinha digitado | A tabela agora recalcula sozinha meio segundo depois de digitar, e o chat sempre usa os números que estão no painel | `static/chat.js`, `app.py`, `testes/test_projeto.py` |
| Na segunda vez, P1 achou que a tabela comparativa não mudava | A tabela já mudava, mas as colunas que ele olhava quase não mudam (o investimento é fixo e a economia da placa depende pouco do banho). Colocamos uma linha com a situação de hoje, a coluna Conta/ano, um destaque amarelo no que mudou e um aviso explicando o que não muda | `static/chat.js`, `static/style.css`, `templates/index.html` |
| Na terceira vez, P1 viu que a comparação do chat não batia com o esperado | A resposta mostrava "custo por kWh evitado", que não aparece na tabela. Trocamos pela conta por ano, para o chat e a tabela mostrarem as mesmas colunas. Também fizemos o navegador baixar a versão nova do código, porque o celular podia continuar com a antiga guardada | `assistente.py`, `templates/index.html` |
| PREENCHER | PREENCHER | PREENCHER |

## Testes automáticos

Os testes de código ficam em `testes/test_projeto.py` e não substituem os testes acima. Eles conferem as contas e se o assistente reconhece as perguntas.
