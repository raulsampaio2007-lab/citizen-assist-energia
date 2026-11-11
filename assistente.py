# Parte de conversa do Citizen Assist AI.
# A gente preferiu regras em vez de um modelo de linguagem porque aqui o número
# precisa ser igual ao da análise. O assistente só entende a pergunta e chama
# as funções de calculos.py, então ele nunca inventa um valor.
import re
import unicodedata

import calculos

AVISO = ("Isso é uma estimativa feita com os dados informados, não uma garantia de economia. "
         "Tarifa, clima, preço e uso da casa mudam o resultado.")

PALAVRAS = {
    "referencias": ["fonte", "referencia", "de onde", "origem dos dados"],
    "limitacoes": ["limitac", "garantia", "garantid", "certeza", "premissa", "confiavel", "estimativa"],
    "tarifa_social": ["tarifa social", "cadunico", "baixa renda", "bolsa familia", "luz do povo"],
    "ambiente": ["co2", "carbono", "meio ambiente", "ambiental", "poluicao", "sustentavel", "impacto"],
    "aquecedor": ["aquecedor", "boiler", "agua quente", "coletor"],
    "fotovoltaica": ["placa", "painel", "paineis", "fotovolt", "solar"],
    "comparar": ["compar", "diferenca", "alternativa", "opcoes", "melhor opcao"],
    "recomendar": ["recomend", "o que fazer", "o que eu faco", "vale a pena", "compensa", "sugest", "devo"],
    "habitos": ["economizar", "reduzir", "dica", "diminuir", "gastar menos", "pagar menos", "posicao verao"],
    "gasto_banho": ["quanto gasta", "quanto custa", "consumo", "chuveiro", "banho", "gasto", "conta de luz"],
    "ajuda": ["ajuda", "o que voce faz", "como funciona", "o que voce sabe"],
}

SUGESTOES = ("Você pode me perguntar quanto o chuveiro gasta, como economizar no banho, "
             "se vale a pena aquecedor solar ou placa solar, comparar as opções, tarifa social, "
             "impacto ambiental, limitações e fontes. Também dá para falar seus dados, tipo: "
             "\"moro sozinho de aluguel, banho de 10 minutos\".")


def normalizar(texto):
    texto = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn").strip()


def reais(valor):
    texto = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return "R$ " + texto


def numero_br(valor, casas=0):
    texto = f"{valor:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return texto


def texto_retorno(anos):
    if anos is None:
        return "não se paga com esses dados"
    if anos > calculos.PREMISSAS["horizonte"]:
        return f"cerca de {numero_br(anos, 1)} anos, ou seja, não compensa em 10 anos"
    return f"cerca de {numero_br(anos, 1)} anos"


def ler_valor(texto):
    # aceita 5500, 5.500 e 5,5
    texto = texto.replace(" ", "")
    if re.fullmatch(r"\d{1,3}(\.\d{3})+", texto):
        texto = texto.replace(".", "")
    return float(texto.replace(",", "."))


def corrigir_limites(perfil):
    # evita conta maluca se alguem digitar um valor fora da realidade
    limites = {
        "pessoas": (1, 15),
        "minutos": (1, 60),
        "pot_inverno": (1000, 12000),
        "pot_verao": (500, 12000),
        "outros_kwh": (0, 3000),
    }
    for campo, (menor, maior) in limites.items():
        perfil[campo] = min(max(float(perfil[campo]), menor), maior)
    return perfil


def extrair_dados(texto, perfil):
    """Procura dados da família na mensagem e devolve o que entendeu."""
    entendi = []

    achou = re.search(r"(\d+)\s*(pessoas|moradores)", texto)
    if achou:
        perfil["pessoas"] = int(achou.group(1))
        entendi.append(f"{achou.group(1)} pessoas na casa")
    elif "moro sozinh" in texto:
        perfil["pessoas"] = 1
        entendi.append("1 pessoa na casa")

    achou = re.search(r"(\d+)\s*min", texto)
    if achou:
        perfil["minutos"] = int(achou.group(1))
        entendi.append(f"banho de {achou.group(1)} minutos")

    achou = re.search(r"(\d[\d.,]*)\s*(kw|w|watts?)\b", texto)
    if achou and ("chuveiro" in texto or "ducha" in texto):
        potencia = ler_valor(achou.group(1))
        if achou.group(2) == "kw":
            potencia = potencia * 1000
        perfil["pot_inverno"] = potencia
        # mesma proporção entre verão e inverno do chuveiro de 5500 W
        perfil["pot_verao"] = round(potencia * 3500 / 5500)
        entendi.append(f"chuveiro de {numero_br(potencia)} W")

    chuveiro_mes = calculos.cenario_hoje(perfil)["chuveiro"]
    media_chuveiro = sum(chuveiro_mes) / 12

    achou = re.search(r"(\d[\d.,]*)\s*kwh", texto)
    achou_conta = re.search(r"conta[^.\d]*r\$\s*(\d[\d.,]*)", texto)
    if achou:
        total = ler_valor(achou.group(1))
        perfil["outros_kwh"] = max(total - media_chuveiro, 0)
        entendi.append(f"consumo total de {numero_br(total)} kWh por mês")
    elif achou_conta:
        valor = ler_valor(achou_conta.group(1))
        total = valor / calculos.preco_kwh(220)
        perfil["outros_kwh"] = max(total - media_chuveiro, 0)
        entendi.append(f"conta de {reais(valor)}, perto de {numero_br(total)} kWh por mês")

    if any(p in texto for p in ["aluguel", "alugad", "alugo", "apartamento", "apto", "predio"]):
        perfil["sem_telhado"] = True
        entendi.append("imóvel de aluguel ou apartamento")
    if any(p in texto for p in ["casa propria", "casa e minha", "imovel proprio", "tenho telhado"]):
        perfil["sem_telhado"] = False
        entendi.append("casa própria com telhado")

    if any(p in texto for p in ["cadunico", "bolsa familia", "baixa renda"]):
        perfil["cadunico"] = True

    achou = re.search(r"(tenho|temos|guardad\w*|orcamento|investir|gastar)[^.\d]*r?\$?\s*(\d[\d.,]*)\s*(mil)?", texto)
    if achou and "kwh" not in achou.group(0) and "min" not in achou.group(0):
        valor = ler_valor(achou.group(2))
        if achou.group(3):
            valor = valor * 1000
        if valor >= 100:
            perfil["orcamento"] = valor
            entendi.append(f"orçamento de {reais(valor)}")

    return entendi


def detectar_intencao(texto):
    pontos = {}
    for intencao, lista in PALAVRAS.items():
        pontos[intencao] = sum(1 for p in lista if p in texto)

    # perguntou dos dois solares juntos, então quer comparar
    if pontos["aquecedor"] and re.search(r"placa|painel|paineis|fotovolt", texto):
        return "comparar"
    # "aquecedor solar" não e sobre placa fotovoltaica
    if pontos["aquecedor"]:
        pontos["fotovoltaica"] = 0

    melhor = max(pontos, key=pontos.get)
    if pontos[melhor] > 0:
        return melhor
    if re.search(r"\b(oi|ola|bom dia|boa tarde|boa noite|e ai)\b", texto):
        return "saudacao"
    return None


def resposta_gasto(perfil):
    dados = calculos.comparar(perfil)["hoje"]
    media = dados["chuveiro_ano"] / 12
    parte = dados["chuveiro_ano"] / dados["consumo_ano"] * 100
    custo = dados["conta_ano"] * dados["chuveiro_ano"] / dados["consumo_ano"]
    texto = (f"Com {perfil['pessoas']:.0f} pessoas e banho de {perfil['minutos']:.0f} minutos, o chuveiro "
             f"gasta perto de {numero_br(media)} kWh por mês. Em um ano são {numero_br(dados['chuveiro_ano'])} kWh, "
             f"mais ou menos {numero_br(parte)}% da energia da casa e {reais(custo)} da conta.\n\n"
             f"A conta é energia = potência x tempo. Usei {perfil['pot_inverno']:.0f} W de abril a setembro "
             f"e {perfil['pot_verao']:.0f} W nos outros meses. Se o seu chuveiro for diferente, me fala a "
             "potência que está na etiqueta.")
    return texto, ["enel", "cirra"]


def resposta_habitos(perfil):
    a = calculos.cenario_habitos(perfil)
    texto = (f"O que dá mais resultado sem gastar nada é o banho. Reduzindo para {min(perfil['minutos'], 5):.0f} "
             "minutos e deixando a chave no verão de setembro a abril, a estimativa é evitar "
             f"{numero_br(a['kwh_evitados'])} kWh por ano e pagar {reais(a['economia_ano'])} a menos.\n\n"
             f"De quebra economiza uns {numero_br(-a['agua_m3_ano'], 1)} mil litros de água por ano. "
             "Parte dessa economia vem do ICMS, que cai de 18% para 12% quando a conta fica em até 200 kWh, "
             "então o valor muda bastante se sua casa já estiver longe dessa faixa.")
    return texto, ["enel", "icms_sp", "cirra"]


def resposta_aquecedor(perfil):
    a = calculos.cenario_aquecedor(perfil)
    texto = (f"O aquecedor solar de 200 L atende 4 a 5 banhos por dia. Contando kit e adaptação, o custo fica "
             f"perto de {reais(a['investimento'])}. Com ele a estimativa é economizar {reais(a['economia_ano'])} "
             f"por ano, com retorno em {texto_retorno(a['retorno_anos'])}.\n\n"
             "O ponto bom é que ele diminui o uso do chuveiro no horário de pico, no começo da noite, o que a placa "
             "fotovoltaica não faz. Os cuidados: precisa de telhado com sol e laje ou estrutura que aguente o "
             "peso, e a casa precisa de encanamento de água quente. Se a instalação for de uma ducha mais forte, "
             f"o gasto de água pode subir uns {numero_br(a['agua_m3_ano'], 0)} mil litros por ano.")
    if perfil.get("sem_telhado"):
        texto += "\n\nComo você falou que mora de aluguel ou em apartamento, isso depende do dono ou do condomínio."
    return texto, ["sinapi", "ufrgs", "cirra", "abrasol"]


def resposta_fotovoltaica(perfil):
    a = calculos.cenario_fotovoltaico(perfil)
    texto = (f"Um sistema de 2 kWp custa perto de {reais(a['investimento'])} e gera em torno de "
             f"{numero_br(a['geracao_ano'])} kWh por ano em São Paulo, mais do que o chuveiro usa, então ele "
             f"abate a conta da casa toda. A estimativa é economizar {reais(a['economia_ano'])} por ano, com "
             f"retorno em {texto_retorno(a['retorno_anos'])}.\n\n"
             "A conta não zera: você continua pagando o mínimo da distribuidora (50 kWh em ligação bifásica) e "
             "uma parte do fio B sobre a energia compensada. Precisa de telhado próprio com sol, projeto "
             "feito por profissional e aprovação da Enel.")
    if perfil.get("sem_telhado"):
        texto += "\n\nComo você falou que mora de aluguel ou em apartamento, essa opcao não serve direto para o seu caso."
    return texto, ["greener", "nasa", "ren1000", "lei14300"]


def resposta_comparar(perfil):
    dados = calculos.comparar(perfil)
    linhas = [f"Hoje a conta estimada é de {reais(dados['hoje']['conta_ano'])} por ano. Comparando as opções em 12 meses:"]
    for a in dados["alternativas"]:
        linhas.append(f"\n{a['nome']}\nInvestimento: {reais(a['investimento'])}\n"
                      f"Economia por ano: {reais(a['economia_ano'])}\n"
                      f"Retorno: {'imediato' if a['investimento'] == 0 else texto_retorno(a['retorno_anos'])}\n"
                      f"Custo por kWh evitado: {reais(a['custo_kwh_evitado'] or 0)}")
    linhas.append("\nAs economias não podem ser somadas: se o banho já gasta menos, o aquecedor tem menos para economizar. "
                  "A placa também cobre o resto da casa, por isso a economia dela parece maior.")
    return "\n".join(linhas), ["enel", "sinapi", "greener", "ufrgs", "nasa"]


def resposta_recomendar(perfil):
    dados = calculos.comparar(perfil)
    habitos, aquecedor, placa = dados["alternativas"]

    partes = [f"Primeiro passo para qualquer casa: mudar o banho. Não custa nada e a estimativa é de "
              f"{reais(habitos['economia_ano'])} a menos por ano."]
    fontes = ["enel", "sinapi", "greener"]

    if perfil.get("cadunico"):
        partes.append("Como você citou CadÚnico ou baixa renda, veja antes se a tarifa social já está na sua conta. "
                      "Com ela o retorno de qualquer investimento demora mais, porque a energia sai mais barata, "
                      "e meus cálculos usam a tarifa normal.")
        fontes.append("tarifa_social")

    if perfil.get("sem_telhado"):
        partes.append("Morando de aluguel ou em apartamento, instalar aquecedor ou placa depende do dono ou do "
                      "condomínio. Eu ficaria nos hábitos e levaria esses números para essa conversa.")
    else:
        orcamento = perfil.get("orcamento")
        if orcamento is None:
            partes.append(f"Se puder investir: a placa solar ({reais(placa['investimento'])}) tem retorno em "
                          f"{texto_retorno(placa['retorno_anos'])} e reduz mais a conta. O aquecedor "
                          f"({reais(aquecedor['investimento'])}) custa menos, com retorno em "
                          f"{texto_retorno(aquecedor['retorno_anos'])}, e ajuda mais no horário de pico. "
                          "Me fala quanto você tem para investir que eu fecho a sugestão.")
        elif orcamento < aquecedor["investimento"]:
            partes.append(f"Com {reais(orcamento)} ainda não dá para o aquecedor com adaptação "
                          f"({reais(aquecedor['investimento'])}). Eu começaria pelos hábitos e juntaria a economia. "
                          "Se a casa já tiver encanamento de água quente, vale pedir orçamento mesmo assim.")
        elif orcamento < placa["investimento"]:
            partes.append(f"Com {reais(orcamento)} o que cabe é o aquecedor solar, com retorno em "
                          f"{texto_retorno(aquecedor['retorno_anos'])}, desde que o telhado tenha sol.")
        else:
            partes.append(f"Com {reais(orcamento)} a placa cabe no orçamento e, com esses dados, tem o melhor retorno: "
                          f"{texto_retorno(placa['retorno_anos'])}. Peça pelo menos três orçamentos antes de fechar.")

    if dados["hoje"]["consumo_ano"] / 12 < 100:
        partes.append("Seu consumo é baixo. Com o mínimo que a distribuidora cobra, a placa rende pouco nesse caso.")
    return "\n\n".join(partes), fontes


def resposta_tarifa_social(perfil):
    texto = ("A tarifa social é para famílias no CadÚnico. Quem tem renda de até meio salário mínimo por pessoa não "
             "paga os primeiros 80 kWh do mês. Quem passa disso paga a tarifa normal sobre o excedente, e taxas como a "
             "iluminação pública continuam na fatura.\n\nEla costuma entrar automático, mas vale olhar a conta e manter "
             "o CadÚnico atualizado no CRAS. Confirme as regras com a Enel, porque meus cálculos usam a tarifa normal e "
             "não esse desconto.")
    return texto, ["tarifa_social", "enel"]


def resposta_ambiente(perfil):
    dados = calculos.comparar(perfil)
    habitos, aquecedor, placa = dados["alternativas"]
    texto = (f"Em CO2 o ganho é pequeno, porque a energia do Brasil já é bem renovável. Usando o fator de 2024 "
             f"(0,0545 kg por kWh): hábitos evitam {numero_br(habitos['co2_evitado_kg'])} kg por ano, o aquecedor "
             f"{numero_br(aquecedor['co2_evitado_kg'])} kg e a placa {numero_br(placa['co2_evitado_kg'])} kg. "
             f"Descontando a fabricação da placa (41 g por kWh, segundo o IPCC), sobram uns "
             f"{numero_br(placa['co2_liquido_kg'])} kg.\n\n"
             "O que mais pesa é outra coisa: o banho mais curto economiza água, e o chuveiro responde por 7% do uso de "
             "energia na hora de pico, segundo a Abrasol. O aquecedor alivia esse horário. Placa e coletor também "
             "geram resíduo no fim da vida útil, e isso não entrou nas contas.")
    return texto, ["bradesco", "mcti", "ipcc", "abrasol", "cirra"]


def resposta_limitacoes(perfil):
    texto = ("Tudo aqui é estimativa. Os principais pontos:\n"
             "- A tarifa é da Enel SP com bandeira verde, sem iluminação pública. Bandeira amarela ou vermelha aumenta a conta.\n"
             "- Duração do banho, potência e consumo do resto da casa são exemplos até você trocar pelos seus.\n"
             "- A redução de 70% do aquecedor vem de uma simulação feita em Viçosa (MG), não em São Paulo.\n"
             "- A geração solar usa médias da NASA para o plano horizontal, sem contar sombra no telhado.\n"
             "- Os preços são médias. Instalação real depende de orçamento na sua região.\n"
             "- Não considerei inflação, reajuste de tarifa nem juros de financiamento.\n"
             "- Isso não substitui avaliação de eletricista ou instalador. Não troque chuveiro por um mais forte sem conferir a fiação.")
    return texto, ["enel", "ufrgs", "nasa", "bandeira"]


def resposta_referencias(perfil):
    return "Essas são as fontes que usamos nas contas. Os dados que são estimativa do grupo estão marcados no arquivo dados/premissas.csv.", list(REFERENCIAS.keys())


def resposta_aparelho(texto):
    achou = re.search(r"(\d[\d.,]*)\s*(kw|w|watts?)\b", texto)
    potencia = ler_valor(achou.group(1))
    if achou.group(2) == "kw":
        potencia = potencia * 1000
    horas = re.search(r"(\d+[.,]?\d*)\s*h", texto)
    if not horas:
        return (f"Entendi {numero_br(potencia)} W. Quantas horas por dia ele fica ligado? "
                "Pode mandar assim: 100 W, 8 horas por dia."), []
    horas_dia = ler_valor(horas.group(1))
    kwh = calculos.consumo_aparelho(potencia, horas_dia)
    custo = kwh * calculos.preco_kwh(220)
    return (f"Ligado {numero_br(horas_dia, 1)} h por dia, um aparelho de {numero_br(potencia)} W gasta "
            f"{numero_br(kwh, 1)} kWh em 30 dias, perto de {reais(custo)} no mês. Geladeira e ar-condicionado "
            "ligam e desligam o motor, então gastam menos do que essa conta mostra."), ["enel"]


REFERENCIAS = {linha["id"]: linha for linha in calculos.ler_csv("referencias.csv")}

RESPOSTAS = {
    "referencias": resposta_referencias,
    "limitacoes": resposta_limitacoes,
    "tarifa_social": resposta_tarifa_social,
    "ambiente": resposta_ambiente,
    "aquecedor": resposta_aquecedor,
    "fotovoltaica": resposta_fotovoltaica,
    "comparar": resposta_comparar,
    "recomendar": resposta_recomendar,
    "habitos": resposta_habitos,
    "gasto_banho": resposta_gasto,
}


def responder(mensagem, perfil):
    texto = normalizar(mensagem)
    # copia para não mexer no perfil antigo caso alguma conta de erro
    perfil = dict(perfil)

    tem_potencia = re.search(r"\d\s*(kw|w|watts?)\b", texto)
    if tem_potencia and "chuveiro" not in texto and "ducha" not in texto:
        resposta, ids = resposta_aparelho(texto)
        return montar(resposta, ids, perfil)

    entendi = extrair_dados(texto, perfil)
    corrigir_limites(perfil)
    intencao = detectar_intencao(texto)

    # a pessoa só passou os dados, sem perguntar nada: "banho de 10 minutos, moro de aluguel"
    if entendi and intencao == "gasto_banho" and "quanto" not in texto and "?" not in texto:
        intencao = "recomendar"

    if intencao == "saudacao" and not entendi:
        return montar("Oi! Sou o Citizen Assist AI, na parte de energia. " + SUGESTOES, [], perfil, com_aviso=False)
    if intencao == "ajuda":
        return montar(SUGESTOES, [], perfil, com_aviso=False)

    if intencao in RESPOSTAS:
        resposta, ids = RESPOSTAS[intencao](perfil)
    elif entendi:
        resposta, ids = resposta_recomendar(perfil)
    else:
        return montar("Essa eu não sei responder, meu assunto aqui é energia em casa. " + SUGESTOES,
                      [], perfil, com_aviso=False)

    if entendi:
        resposta = "Anotei: " + ", ".join(entendi) + ".\n\n" + resposta
    return montar(resposta, ids, perfil, com_aviso=intencao != "referencias")


def montar(texto, ids_fontes, perfil, com_aviso=True):
    fontes = [{"titulo": REFERENCIAS[i]["titulo"], "url": REFERENCIAS[i]["url"]} for i in ids_fontes]
    return {"texto": texto, "fontes": fontes, "aviso": AVISO if com_aviso and ids_fontes else "", "perfil": perfil}
