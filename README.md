# Citizen Assist AI: parte de energia

Trabalho da Global Solution de Ciência da Computação (turmas 1CC), disciplina de Soluções em Energias Renováveis e Sustentáveis. Tudo neste repositório é a contribuição dessa disciplina ao Citizen Assist AI.

O assistente principal, com as orientações de documentos e trabalho, foi feito em Pensamento Computacional e está em https://github.com/raulsampaio2007-lab/citizen-assist-ai. Aqui fica só a parte de energia, que usa o mesmo nome e o mesmo público.

## Integrantes

| Nome completo | RM |
|---|---|
| Raul Sampaio Mochnacs Arruda | 573523 |
| Pedro Sampaio Mochnacs Arruda | 573522 |

## Público e problema

O público é o mesmo do Citizen Assist AI: jovens de 14 a 24 anos procurando o primeiro emprego. Fizemos as contas para a cidade de São Paulo, atendida pela Enel SP. Com o primeiro salário, muita gente começa a ajudar nas contas de casa ou vai dividir um aluguel, e a conta de luz vira problema dela também. O banho no chuveiro elétrico é o maior gasto que o jovem consegue mudar sozinho, e tem muita propaganda de energia solar sem ninguém explicar se compensa.

A necessidade que escolhemos foi a água quente do banho. Analisamos dois casos: o jovem que mora com a família, numa casa de 4 pessoas, onde o chuveiro usa 877 kWh por ano (33% da energia da casa), e o jovem que mora sozinho de aluguel. O assistente mostra esse gasto com os dados da pessoa e compara três caminhos, com custo, viabilidade e limitações.

## O que o assistente faz na parte de energia

- Calcula o consumo e o custo do chuveiro com os dados da casa (pessoas, minutos, potência).
- Compara, no mesmo período de 12 meses, a mudança de hábitos, o aquecedor solar de água e a energia solar fotovoltaica.
- Recomenda um caminho conforme a situação da pessoa: aluguel ou casa própria, orçamento e CadÚnico.
- Calcula o gasto de outros aparelhos a partir da potência e das horas de uso.
- Explica tarifa social e impacto ambiental, e mostra fontes e limitações das contas.

As respostas usam as mesmas funções da análise (`calculos.py`). Escolhemos fazer o chat com regras de palavras-chave, sem modelo de linguagem, para o assistente não inventar número. Isso tem um custo: ele só entende os assuntos que programamos, e fora disso avisa que não sabe.

## Como executar

Precisa de Python 3.10 ou mais novo. No Windows:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Depois é só abrir http://localhost:5000 no navegador.

Para gerar de novo as tabelas da análise e rodar os testes automáticos:

```bash
python analise.py
python -m unittest discover testes
```

Perguntas para testar no chat:

- Quanto meu chuveiro gasta?
- Moro sozinho de aluguel, banho de 10 minutos
- Tenho R$ 5000 para investir, o que você recomenda?
- Compare as alternativas
- Quais são as limitações?

## Resultado da comparação

Casa de 4 pessoas onde o jovem mora com a família, 12 meses, tarifa da Enel SP de julho de 2026 e bandeira verde. A conta estimada hoje é de R$ 2.692,23 por ano.

| Alternativa | Investimento | Economia por ano | Retorno | Saldo em 10 anos | Custo por kWh evitado |
|---|---|---|---|---|---|
| Hábitos (banho de 5 min e chave no verão) | R$ 0,00 | R$ 471,29 | imediato | R$ 4.712,87 | R$ 0,00 |
| Aquecedor solar de água (200 L) | R$ 4.859,57 | R$ 764,46 | 7,3 anos | R$ 1.785,07 | R$ 0,95 |
| Solar fotovoltaica (2 kWp) | R$ 7.240,00 | R$ 1.994,58 | 3,9 anos | R$ 11.205,83 | R$ 0,37 |

São estimativas, e as economias não podem ser somadas. A placa parece muito melhor em parte porque cobre a casa toda, não só o banho. Para o jovem que mora sozinho de aluguel a conta muda bastante. Os hábitos economizam cerca de R$ 173 por ano, e o aquecedor (28,7 anos) e a placa (15,3 anos) não se pagam em 10 anos, além de dependerem do dono do imóvel. Para ele a recomendação é só mudar o banho.

A explicação completa está em [docs/analise_energetica.md](docs/analise_energetica.md).

## Organização do repositório

| Caminho | O que tem |
|---|---|
| `app.py` | Servidor web (Flask) |
| `assistente.py` | Entende a pergunta e monta a resposta |
| `calculos.py` | Contas de energia, conta de luz e alternativas |
| `analise.py` | Gera as tabelas da pasta `resultados` |
| `dados/` | Premissas, irradiação e perfil da casa de exemplo, com origem e tipo (real ou estimado) |
| `resultados/` | Consumo mensal, comparação e sensibilidade |
| `docs/analise_energetica.md` | Contexto, cálculos, justificativas e limitações |
| `docs/referencias.md` | Fontes usadas |
| `docs/testes_com_usuarios.md` | Registro dos testes com usuários e ajustes |
| `testes/` | Testes automáticos do código |
| `templates/` e `static/` | Tela do assistente |
