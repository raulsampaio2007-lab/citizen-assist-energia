# Citizen Assist AI: parte de energia

Global Solution do 1º ano de Ciência da Computação (turma 1CC), disciplina de Soluções em Energias Renováveis e Sustentáveis. Este repositório tem só o que fizemos para essa disciplina.

O Citizen Assist AI principal, que orienta sobre documentos e trabalho, foi feito em Pensamento Computacional e está em https://github.com/raulsampaio2007-lab/citizen-assist-ai. A parte de energia usa o mesmo nome e o mesmo público, mas fica separada aqui.

## Integrantes

| Nome completo | RM |
|---|---|
| Raul Sampaio Mochnacs Arruda | 573523 |
| Pedro Sampaio Mochnacs Arruda | 573522 |

## Público e problema

O público é o mesmo do assistente principal: jovens de 14 a 24 anos procurando o primeiro emprego. Quando começa a trabalhar, o jovem costuma ajudar nas contas de casa ou vai dividir um aluguel, e a conta de luz passa a ser problema dele também. Fizemos as contas para São Paulo, com a tarifa da Enel SP.

Escolhemos a água quente do banho porque o chuveiro elétrico é o gasto que o jovem consegue mudar sozinho. Numa casa de 4 pessoas com banho de 8 minutos, ele gasta 877 kWh por ano, 33% da energia da casa. A gente também via muita propaganda de placa solar e pouca gente explicando se compensa ou não para quem está começando.

Olhamos dois casos. O principal é o jovem que mora com a família. O outro é o jovem que mora sozinho de aluguel, onde a resposta muda bastante.

## O que o assistente faz

- Calcula quanto o chuveiro gasta com os dados da casa (pessoas, minutos de banho e potência).
- Compara três opções nos mesmos 12 meses: mudar o hábito do banho, colocar aquecedor solar de água e colocar placa solar fotovoltaica.
- Recomenda uma delas de acordo com a situação da pessoa, olhando se é aluguel ou casa própria, quanto ela tem para investir e se está no CadÚnico.
- Calcula o gasto de outros aparelhos pela potência e pelas horas de uso.
- Responde sobre tarifa social e impacto ambiental, e mostra de onde vieram os números e o que eles não garantem.

Fizemos tudo em Python. A tela usa Streamlit, que monta a página a partir do próprio código Python. O chat funciona com palavras-chave, sem modelo de linguagem, porque queríamos que todo número viesse das funções de `calculos.py`, as mesmas usadas na análise. A desvantagem é que ele só entende os assuntos que programamos. Quando a pergunta foge disso, ele avisa que não sabe.

## Vídeo

https://youtu.be/5HIHjlFEe3I (não listado, menos de 3 minutos)

## Como executar

A versão online está em https://citizen-assist-energia.onrender.com. Ela fica no plano grátis do Render, então se ninguém abriu nos últimos minutos ela demora uns 50 segundos para carregar.

Para rodar no computador é preciso ter Python 3.10 ou mais novo. No Windows:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

O navegador abre em http://localhost:8501.

Para gerar de novo as tabelas da análise e rodar os testes:

```bash
python analise.py
python -m unittest discover testes
```

Algumas perguntas para testar no chat:

- Quanto meu chuveiro gasta?
- Moro sozinho de aluguel, banho de 10 minutos
- Tenho R$ 5000 para investir, o que você recomenda?
- Compare as alternativas
- Quais são as limitações?

## Resultado da comparação

Casa de 4 pessoas, 12 meses, tarifa da Enel SP de julho de 2026 com bandeira verde. Sem mudar nada, a conta estimada fica em R$ 2.692,23 por ano.

| Alternativa | Investimento | Economia por ano | Retorno | Saldo em 10 anos | Custo por kWh evitado |
|---|---|---|---|---|---|
| Hábitos (banho de 5 min e chave no verão) | R$ 0,00 | R$ 471,29 | imediato | R$ 4.712,87 | R$ 0,00 |
| Aquecedor solar de água (200 L) | R$ 4.859,57 | R$ 764,46 | 7,3 anos | R$ 1.785,07 | R$ 0,95 |
| Solar fotovoltaica (2 kWp) | R$ 7.240,00 | R$ 1.994,58 | 3,9 anos | R$ 11.205,83 | R$ 0,37 |

São estimativas e as economias não se somam, porque cada linha compara com a situação de hoje. A placa sai bem na frente em parte porque ela abate a conta da casa inteira, e não só o banho.

Para o jovem que mora sozinho (1 pessoa, banho de 8 minutos) a história é outra. Mudar o banho economiza uns R$ 173 por ano, o aquecedor levaria 28,7 anos para se pagar e a placa 15,3 anos. Como ele mora de aluguel, também dependeria do dono do imóvel para instalar. Para esse caso o assistente recomenda só mudar o banho.

A explicação das contas, das premissas e das limitações está em [docs/analise_energetica.md](docs/analise_energetica.md). As fontes estão em [docs/referencias.md](docs/referencias.md) e os testes que fizemos com pessoas, junto com o que mudamos depois deles, estão em [docs/testes_com_usuarios.md](docs/testes_com_usuarios.md).

## Organização do repositório

| Caminho | O que tem |
|---|---|
| `app.py` | Tela do assistente (Streamlit): chat, dados da casa e tabela |
| `assistente.py` | Entende a pergunta e monta a resposta |
| `calculos.py` | Contas de energia, conta de luz e alternativas |
| `analise.py` | Gera as tabelas da pasta `resultados` |
| `dados/` | Premissas, irradiação e perfil da casa de exemplo, com origem e tipo (real ou estimado) |
| `resultados/` | Consumo mensal, comparação e sensibilidade |
| `docs/analise_energetica.md` | Contexto, cálculos, justificativas e limitações |
| `docs/referencias.md` | Fontes usadas |
| `docs/testes_com_usuarios.md` | Registro dos testes com usuários e dos ajustes |
| `testes/` | Testes automáticos do código |
| `render.yaml` | Configuração da versão online no Render |
