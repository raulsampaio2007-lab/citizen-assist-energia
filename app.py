# Tela do Citizen Assist AI, feita com Streamlit.
# Rode com: streamlit run app.py
import streamlit as st

import assistente
import calculos

CAMPOS = ["pessoas", "minutos", "pot_inverno", "pot_verao", "outros_kwh"]

# (texto do botão, pergunta que ele manda)
ATALHOS = [
    ("Gasto do chuveiro", "Quanto meu chuveiro gasta?"),
    ("Como economizar", "Como economizar no banho?"),
    ("Comparar opções", "Compare as alternativas"),
    ("Recomendação", "O que você recomenda?"),
    ("Limitações", "Quais são as limitações?"),
    ("Fontes", "Quais são as fontes?"),
]

BOAS_VINDAS = ("Oi! Eu ajudo a entender o gasto de energia em casa, principalmente o do chuveiro. "
               "Pode perguntar ou usar os botões abaixo.")


def comecar_do_zero():
    padrao = calculos.perfil_padrao()
    for campo in CAMPOS:
        st.session_state[campo] = int(padrao[campo])
    # coisas que o chat descobre e que não aparecem no painel (aluguel, orçamento...)
    st.session_state.extras = {}
    st.session_state.mensagens = [{"quem": "assistant", "texto": BOAS_VINDAS, "fontes": [], "aviso": ""}]


def perfil_atual():
    perfil = calculos.perfil_padrao()
    for campo in CAMPOS:
        perfil[campo] = float(st.session_state[campo])
    perfil.update(st.session_state.extras)
    return perfil


def conversar(pergunta):
    st.session_state.mensagens.append({"quem": "user", "texto": pergunta, "fontes": [], "aviso": ""})
    resposta = assistente.responder(pergunta, perfil_atual())

    # o que o chat entendeu na mensagem vai para o painel também
    novo = resposta["perfil"]
    for campo in CAMPOS:
        st.session_state[campo] = int(round(novo[campo]))
    # as barras de potência andam de 100 em 100
    for campo in ["pot_inverno", "pot_verao"]:
        st.session_state[campo] = int(round(novo[campo] / 100) * 100)
    for chave in ["sem_telhado", "cadunico", "orcamento"]:
        if chave in novo:
            st.session_state.extras[chave] = novo[chave]

    st.session_state.mensagens.append({"quem": "assistant", "texto": resposta["texto"],
                                       "fontes": resposta["fontes"], "aviso": resposta["aviso"]})


def mostrar_mensagem(msg):
    with st.chat_message(msg["quem"]):
        st.text(msg["texto"])
        if msg["aviso"]:
            st.caption(msg["aviso"])
        if msg["fontes"]:
            links = [f"[{fonte['titulo']}]({fonte['url']})" for fonte in msg["fontes"]]
            st.caption("Fontes: " + " · ".join(links))


def texto_retorno(alternativa):
    if alternativa["investimento"] == 0:
        return "Imediato"
    if alternativa["retorno_anos"] is None:
        return "Não se paga"
    return assistente.numero_br(alternativa["retorno_anos"], 1) + " anos"


def mostrar_tabela(perfil):
    dados = calculos.comparar(perfil)
    hoje = dados["hoje"]
    st.write(f"Hoje: {assistente.numero_br(hoje['consumo_ano'])} kWh por ano, sendo "
             f"{assistente.numero_br(hoje['chuveiro_ano'])} kWh do chuveiro. "
             f"Conta estimada de {assistente.reais(hoje['conta_ano'])} por ano.")

    linhas = [{"Situação": "Hoje, sem mudar nada", "Investimento": "R$ 0,00",
               "Conta/ano": assistente.reais(hoje["conta_ano"]), "Economia/ano": "-", "Retorno": "-"}]
    for alt in dados["alternativas"]:
        linhas.append({
            "Situação": alt["nome"],
            "Investimento": assistente.reais(alt["investimento"]),
            "Conta/ano": assistente.reais(alt["conta_ano"]),
            "Economia/ano": assistente.reais(alt["economia_ano"]),
            "Retorno": texto_retorno(alt),
        })
    st.table(linhas)
    st.caption("A tabela muda sozinha quando você altera os dados. O investimento não muda, e a economia da "
               "placa pode ficar parecida, porque ela gera sempre a mesma energia.")
    st.caption("Estimativas com tarifa da Enel SP (julho/2026) e bandeira verde. Não é garantia de economia, "
               "e as economias não podem ser somadas.")


st.set_page_config(page_title="Citizen Assist AI - Energia", layout="wide")
st.title("Citizen Assist AI")
st.caption("Energia em casa para quem está começando a trabalhar: quanto custa o banho e o que compensa")

if "mensagens" not in st.session_state:
    comecar_do_zero()

coluna_chat, coluna_dados = st.columns([3, 2], gap="large")

with coluna_chat:
    caixa = st.container(height=480)

    # os botões e o campo de texto vêm antes do painel, porque a resposta
    # pode mudar os números do painel (ex: "somos 3 pessoas")
    pergunta = None
    botoes = st.columns(3)
    for i, (rotulo, texto) in enumerate(ATALHOS):
        if botoes[i % 3].button(rotulo, use_container_width=True):
            pergunta = texto
    digitada = st.chat_input("Ex: moro sozinho de aluguel, banho de 10 minutos")
    if digitada:
        pergunta = digitada[:500]
    if pergunta:
        conversar(pergunta)

    with caixa:
        for msg in st.session_state.mensagens:
            mostrar_mensagem(msg)

with coluna_dados:
    st.subheader("Dados da sua casa")
    # teste com usuário: no campo de digitar, o número só valia depois do Enter,
    # e no celular a pessoa não apertava. A barra atualiza assim que solta.
    st.slider("Pessoas", min_value=1, max_value=15, key="pessoas")
    st.slider("Minutos por banho", min_value=1, max_value=60, key="minutos")
    st.slider("Chuveiro no inverno (W)", min_value=1000, max_value=12000, step=100, key="pot_inverno")
    st.slider("Chuveiro no verão (W)", min_value=500, max_value=12000, step=100, key="pot_verao")
    # teste com usuário: a pessoa não sabia o que colocar aqui
    st.caption("Não sabe a potência? Pode deixar como está, 5500 W e 3500 W são os valores mais comuns. "
               "Se quiser conferir, ela vem escrita em watts (W) na etiqueta ou na caixa do chuveiro. "
               "Volts (127 V ou 220 V) é outra coisa e não entra na conta.")
    st.slider("Resto da casa (kWh/mês)", min_value=0, max_value=3000, key="outros_kwh")
    st.button("Voltar ao exemplo", on_click=comecar_do_zero)

    st.subheader("Comparação em 12 meses")
    mostrar_tabela(perfil_atual())
