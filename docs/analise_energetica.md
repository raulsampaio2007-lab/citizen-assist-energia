# Análise energética

## Contexto

O chuveiro é um dos aparelhos de maior potência de uma casa. A Pesquisa de Posse e Hábitos de 2005 (Procel) encontrou chuveiro elétrico em 73% dos domicílios e atribuiu a ele cerca de 24% do consumo residencial. Esses números são antigos, então usamos só como ponto de partida.

O público do Citizen Assist AI são jovens de 14 a 24 anos procurando o primeiro emprego. Quando começam a ganhar, muitos passam a ajudar nas contas da casa da família ou vão morar sozinhos, e o banho é o gasto de energia que eles mais controlam. Fizemos as contas para São Paulo, atendida pela Enel SP, porque tarifa e sol dependem do lugar.

A necessidade analisada é a mesma para todas as alternativas: ter água quente para o banho durante 12 meses, e o que isso custa na conta de luz. O caso principal é o jovem que mora com a família, numa casa de 4 pessoas. No fim comparamos com o jovem que mora sozinho de aluguel.

## Dados e premissas

Todos os valores estão em [dados/premissas.csv](../dados/premissas.csv) e [dados/perfil_familia.csv](../dados/perfil_familia.csv), com unidade, período, origem e a marcação de real ou estimado. Os que mais influenciam o resultado:

| Dado | Valor | Tipo | Origem |
|---|---|---|---|
| Tarifa sem impostos | R$ 0,78938/kWh | real | Enel SP, REH ANEEL 3.596/2026, vale a partir de 04/07/2026 |
| ICMS em SP | 0% até 90 kWh, 12% até 200 kWh, 18% acima | real | Esfera Energia |
| PIS/Cofins | 5% | estimado | varia mês a mês na fatura |
| Custo mínimo bifásico | 50 kWh/mês | real | ANEEL REN 1.000/2021 |
| Irradiação em São Paulo | 4,53 kWh/m²/dia na média | real | NASA POWER, plano horizontal |
| Aquecedor solar, kit 200 L instalado | R$ 3.359,57 | real | SINAPI 103517, média nacional 09/2026 |
| Adaptação do encanamento e suporte | R$ 1.500,00 | estimado | SINAPI não inclui esses itens |
| Redução do consumo com aquecedor | 70% | real, de outra cidade | Altoé et al., simulação em Viçosa (MG) |
| Sistema fotovoltaico de 2 kW | R$ 3,62/W | real | Greener, junho de 2026 |
| Perdas do sistema fotovoltaico | fator 0,75 | estimado | valor comum em projetos |
| Fio B | R$ 0,28/kWh, 60% cobrado | estimado / real | valor estimado por nós, percentual da Lei 14.300 |
| Banho | 4 pessoas, 8 minutos, 1 por dia | estimado | casa de exemplo, duração do estudo Poli-USP |
| Chuveiro | 5.500 W no inverno, 3.500 W no verão | estimado | potências comuns, a pessoa pode trocar |
| Resto da casa | 147 kWh/mês | estimado | para o total ficar perto de 220 kWh/mês |

Não achamos o valor exato do fio B da Enel SP. Testamos R$ 0,40/kWh na sensibilidade e o retorno da placa muda de 3,9 para 4,0 anos, porque na maioria dos meses o valor cobrado é o custo mínimo.

Para a irradiação usamos a API da NASA POWER porque ela dá o valor mês a mês para a coordenada. O SunData do CRESESB é a referência brasileira e serve para conferir.

## Consumo atual

Energia é potência vezes tempo. Em um mês de 30 dias com a chave no inverno:

```
horas de chuveiro = 4 pessoas x 8 min x 30 dias / 60 = 16 h
energia = 5,5 kW x 16 h = 88 kWh
```

Consideramos chave no inverno de abril a setembro e no verão nos outros meses. O resultado por mês está em [resultados/consumo_mensal.csv](../resultados/consumo_mensal.csv).

| Item | kWh por ano |
|---|---|
| Chuveiro | 877 |
| Resto da casa | 1.764 |
| Total | 2.641 |

O chuveiro fica com 33% do total, acima dos 24% da pesquisa do Procel. Faz sentido, já que a casa de exemplo tem 4 pessoas e esse número é uma média de todas as casas, mas mostra que o exemplo não é a casa média.

A conta usa o preço com impostos, que muda conforme a faixa do ICMS:

```
preço = tarifa / (1 - ICMS - PIS/Cofins)
acima de 200 kWh: 0,78938 / (1 - 0,18 - 0,05) = R$ 1,0252/kWh
até 200 kWh:      0,78938 / (1 - 0,12 - 0,05) = R$ 0,9511/kWh
```

No ano, a conta estimada fica em R$ 2.692,23.

## As alternativas

### Hábitos

Reduzir o banho para 5 minutos e deixar a chave no verão de setembro a abril. O consumo do chuveiro cai 369 kWh por ano (42%). A economia estimada é de R$ 471,29, e perto de R$ 93 disso vem de a conta passar para a faixa de 12% do ICMS. Uma casa que já está longe dos 200 kWh economizaria menos.

Também evita cerca de 18,4 mil litros de água por ano (3 minutos a menos x 4,2 L/min x 4 pessoas x 365 dias). A limitação é que depende de a família manter o hábito todos os dias.

### Aquecedor solar de água

É a fonte renovável que resolve direto o problema do banho. Usamos o kit de 200 L do SINAPI, indicado para 4 a 5 banhos por dia. Mantivemos a redução de 70% do estudo de Altoé et al., com o chuveiro de apoio nos dias sem sol.

```
energia evitada = 877 kWh x 0,70 = 614 kWh por ano
investimento = 3.359,57 + 1.500,00 = R$ 4.859,57
retorno = 4.859,57 / (764,46 de economia - 100,00 de manutenção) = 7,3 anos
```

### Solar fotovoltaica

Sistema de 2 kWp, o menor da pesquisa da Greener. A geração de cada mês é:

```
geração = 2 kW x irradiação x dias do mês x 0,75
janeiro = 2 x 5,2289 x 31 x 0,75 = 243 kWh
```

No ano são 2.479 kWh. Consideramos que 30% da geração é usada na hora e o resto vira crédito, com a cobrança de 60% do fio B sobre o que é compensado. Em cada mês a família paga o maior valor entre esse cálculo e o custo mínimo, como define a regra da ANEEL.

```
investimento = 2.000 W x R$ 3,62 = R$ 7.240,00
retorno = 7.240,00 / (1.994,58 de economia - 150,00 de manutenção) = 3,9 anos
```

## Comparação

Tudo no mesmo período de 12 meses, para a mesma casa, sem reajuste de tarifa. A tabela completa está em [resultados/comparacao.csv](../resultados/comparacao.csv).

| | Hábitos | Aquecedor solar | Fotovoltaica |
|---|---|---|---|
| Energia evitada da rede (kWh/ano) | 369 | 614 | 2.373 |
| Conta por ano | R$ 2.220,94 | R$ 1.927,76 | R$ 697,64 |
| Economia por ano | R$ 471,29 | R$ 764,46 | R$ 1.994,58 |
| Investimento | R$ 0,00 | R$ 4.859,57 | R$ 7.240,00 |
| Manutenção por ano (estimada) | R$ 0,00 | R$ 100,00 | R$ 150,00 |
| Retorno | imediato | 7,3 anos | 3,9 anos |
| Saldo em 10 anos | R$ 4.712,87 | R$ 1.785,07 | R$ 11.205,83 |
| Custo por kWh evitado | R$ 0,00 | R$ 0,95 | R$ 0,37 |
| CO2 evitado na operação (kg/ano) | 20 | 33 | 129 |
| Água (m³/ano) | -18,4 | até +49,1 | sem mudança |
| Atende quem mora de aluguel | sim | só com o dono | só com o dono |
| Reduz uso da rede no pico da noite | sim | sim | não |

A placa cobre mais do que o banho: gera 2.479 kWh e o chuveiro usa 877 kWh. Por isso a coluna de custo por kWh evitado é a mais justa para comparar. Mesmo assim ela sai na frente do aquecedor, o que nos surpreendeu, já que a nossa expectativa era a contrária.

## Jovem morando sozinho

Rodamos as mesmas funções com 1 pessoa, banho de 8 minutos e 80 kWh por mês no resto da casa (estimado, um apartamento pequeno). O chuveiro fica com 219 kWh por ano e a conta estimada com R$ 1.121,43.

| | Hábitos | Aquecedor solar | Fotovoltaica |
|---|---|---|---|
| Economia por ano | R$ 173,03 | R$ 269,11 | R$ 622,87 |
| Retorno | imediato | 28,7 anos | 15,3 anos |

Com pouca gente usando o chuveiro, os equipamentos não se pagam em 10 anos, e quem mora de aluguel nem pode instalar. Para esse jovem, o que serve é mudar o banho. O assistente chega nessa resposta quando a pessoa fala que mora sozinha de aluguel.

## Sensibilidade

Mudamos uma premissa por vez ([resultados/sensibilidade.csv](../resultados/sensibilidade.csv)).

| Alternativa | O que mudou | Retorno | Saldo em 10 anos |
|---|---|---|---|
| Aquecedor | redução de 50% em vez de 70% | 9,8 anos | R$ 117,80 |
| Aquecedor | redução de 85% | 6,2 anos | R$ 3.035,52 |
| Aquecedor | casa já pronta, sem adaptação | 5,1 anos | R$ 3.285,07 |
| Aquecedor | total de R$ 9.000 com obra | 13,5 anos | R$ -2.355,36 |
| Fotovoltaica | perdas maiores (fator 0,65) | 4,3 anos | R$ 9.494,27 |
| Fotovoltaica | preço de R$ 2,91/W | 3,2 anos | R$ 12.625,83 |
| Fotovoltaica | preço de R$ 4,50/W | 4,9 anos | R$ 9.445,83 |
| Fotovoltaica | custo mínimo de 100 kWh (trifásico) | 5,2 anos | R$ 6.707,46 |
| Hábitos | banho de 7 minutos em vez de 5 | imediato | R$ 2.714,11 |

O aquecedor é a opção mais sensível. Se a casa precisar de obra, ele pode não se pagar em 10 anos.

## Impacto ambiental

Em CO2 o ganho é pequeno. Usamos 0,0545 kg de CO2 por kWh, o fator médio de 2024 do Sistema Interligado Nacional, porque a matriz brasileira já tem muita fonte renovável. A placa evita 129 kg por ano na operação, mas a fabricação dela tem cerca de 41 g de CO2 equivalente por kWh gerado (mediana do IPCC). Descontando isso, sobram uns 32 kg por ano. Não calculamos esse número para o coletor por falta de um dado comparável, e também não entrou o descarte de placas e coletores.

Dois efeitos pesam mais para o nosso público:

A água, porque banho mais curto economiza litros. O aquecedor pode ir para o outro lado: o estudo da Poli-USP e do Cirra mediu 8,4 L/min em aquecedor solar contra 4,2 L/min no chuveiro elétrico, o que daria até 49 m³ a mais por ano se a família mudar para uma ducha mais forte. Esse estudo é de 2010, e nele o banho com aquecedor solar saía mais caro que o elétrico quando a água entrava na conta. Por isso orientamos a manter vazão baixa, e não colocamos a água em reais porque a conta da Sabesp não entrou no escopo.

O horário de pico, porque o chuveiro responde por 7% da energia no pico segundo a Abrasol. O aquecedor reduz esse uso. A placa gera de dia e o banho costuma ser à noite, então ela reduz a conta, mas o chuveiro continua puxando da rede nessa hora.

## Recomendações e justificativa

Primeiro, hábitos para todo mundo. Não têm custo, funcionam em imóvel alugado e ainda economizam água. É o que o assistente sempre fala primeiro.

Para jovens de família de baixa renda, conferir se a casa já tem a tarifa social antes de investir. Com os primeiros 80 kWh gratuitos, o retorno de qualquer equipamento demora mais.

Para quem mora de aluguel ou em apartamento, que é o caso de muitos jovens, ficar nos hábitos e levar os números ao dono ou ao condomínio, já que nenhuma das duas fontes renováveis se instala sem autorização.

Para o jovem que mora com a família em casa própria com telhado, a decisão é da família. Com R$ 7 mil ou mais, a fotovoltaica teve o melhor retorno. Com orçamento entre R$ 5 mil e R$ 7 mil, o aquecedor é a opção que cabe, principalmente se a casa já tiver encanamento de água quente. Se a preocupação for o pico da rede, ele também faz mais sentido que a placa.

O assistente aplica essas regras na função `resposta_recomendar` de `assistente.py`, com os valores recalculados para cada casa.

## Limitações

- Todos os valores são estimativas, nenhum é garantia de economia ou geração.
- A conta não inclui iluminação pública nem bandeira. Base em bandeira verde; a amarela soma R$ 1,88 a cada 100 kWh e a vermelha patamar 2, R$ 7,87.
- A redução de 70% do aquecedor foi simulada em Viçosa (MG). Não achamos um número medido em São Paulo.
- A irradiação é no plano horizontal e não considera sombra, inclinação nem orientação do telhado.
- O preço do SINAPI é média nacional. O preço da Greener é médio e o sistema real depende de orçamento.
- O fio B e o PIS/Cofins são estimados, e consideramos o ICMS só pelas faixas. Não analisamos como o ICMS incide sobre a energia compensada.
- A troca de inversor e o custo do financiamento não entraram. Também não aplicamos reajuste de tarifa nem inflação.
- A ANEEL abriu em 2026 uma proposta para mudar a cobrança do custo mínimo. Se mudar, a conta da fotovoltaica muda.
- O fator de CO2 de 2024 veio de um inventário que cita o MCTI, não da planilha oficial. Os valores mensais de 2025 estão perto de 0,025 kg/kWh, e essa série mudou de metodologia.
