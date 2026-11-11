# Todas as contas do trabalho ficam aqui. O assistente e a análise usam estas
# funções, assim o número que aparece no chat e o mesmo do relatorio.
import csv
import os

PASTA = os.path.dirname(os.path.abspath(__file__))

MESES_INVERNO_HOJE = ["Abr", "Mai", "Jun", "Jul", "Ago", "Set"]
MESES_INVERNO_HABITO = ["Mai", "Jun", "Jul", "Ago"]


def ler_csv(nome):
    caminho = os.path.join(PASTA, "dados", nome)
    with open(caminho, encoding="utf-8", newline="") as arq:
        return list(csv.DictReader(arq))


def carregar_premissas():
    premissas = {}
    for linha in ler_csv("premissas.csv"):
        premissas[linha["chave"]] = float(linha["valor"])
    return premissas


PREMISSAS = carregar_premissas()
IRRADIACAO = ler_csv("irradiacao_sao_paulo.csv")


def perfil_padrao():
    perfil = {}
    for linha in ler_csv("perfil_familia.csv"):
        perfil[linha["campo"]] = float(linha["valor"])
    return perfil


def preco_kwh(consumo_mes, p=PREMISSAS):
    # O ICMS de SP depende da faixa de consumo e vale para a conta inteira.
    if consumo_mes <= 90:
        icms = p["icms_ate_90"]
    elif consumo_mes <= 200:
        icms = p["icms_ate_200"]
    else:
        icms = p["icms_acima_200"]
    tarifa = p["tarifa_te"] + p["tarifa_tusd"]
    return tarifa / (1 - icms - p["pis_cofins"])


def valor_conta(consumo_mes, p=PREMISSAS):
    # Abaixo do mínimo a distribuidora cobra o custo de disponibilidade.
    faturado = max(consumo_mes, p["minimo_bifasico"])
    return faturado * preco_kwh(consumo_mes, p)


def consumo_chuveiro(potencia_w, minutos, pessoas, dias, banhos=1):
    # E = P x t, com a potência em kW e o tempo em horas.
    horas = pessoas * banhos * minutos / 60 * dias
    return potencia_w / 1000 * horas


def consumo_aparelho(potencia_w, horas_dia, dias=30):
    return potencia_w / 1000 * horas_dia * dias


def chuveiro_por_mes(perfil, minutos, meses_inverno):
    resultado = []
    for mes in IRRADIACAO:
        if mes["mes"] in meses_inverno:
            potencia = perfil["pot_inverno"]
        else:
            potencia = perfil["pot_verao"]
        kwh = consumo_chuveiro(potencia, minutos, perfil["pessoas"],
                               int(mes["dias"]), perfil.get("banhos_por_dia", 1))
        resultado.append(kwh)
    return resultado


def resumir(nome, contas, consumo_rede, conta_hoje, consumo_hoje, investimento,
            manutencao, p=PREMISSAS):
    conta_ano = sum(contas)
    economia = conta_hoje - conta_ano
    ganho_liquido = economia - manutencao
    anos = p["horizonte"]
    kwh_evitados = consumo_hoje - sum(consumo_rede)

    if investimento == 0:
        retorno = 0
    elif ganho_liquido > 0:
        retorno = investimento / ganho_liquido
    else:
        retorno = None  # não se paga

    custo_kwh = None
    if kwh_evitados > 0:
        custo_kwh = (investimento + manutencao * anos) / (kwh_evitados * anos)

    return {
        "nome": nome,
        "consumo_rede_ano": sum(consumo_rede),
        "kwh_evitados": kwh_evitados,
        "conta_ano": conta_ano,
        "economia_ano": economia,
        "investimento": investimento,
        "manutencao_ano": manutencao,
        "retorno_anos": retorno,
        "saldo_horizonte": ganho_liquido * anos - investimento,
        "custo_kwh_evitado": custo_kwh,
        "co2_evitado_kg": kwh_evitados * p["fator_co2"],
        "agua_m3_ano": 0.0,
    }


def cenario_hoje(perfil, p=PREMISSAS):
    chuveiro = chuveiro_por_mes(perfil, perfil["minutos"], MESES_INVERNO_HOJE)
    consumos = [c + perfil["outros_kwh"] for c in chuveiro]
    contas = [valor_conta(c, p) for c in consumos]
    return {"chuveiro": chuveiro, "consumos": consumos, "contas": contas}


def cenario_habitos(perfil, p=PREMISSAS):
    hoje = cenario_hoje(perfil, p)
    minutos = min(perfil["minutos"], p["hab_minutos"])
    chuveiro = chuveiro_por_mes(perfil, minutos, MESES_INVERNO_HABITO)
    consumos = [c + perfil["outros_kwh"] for c in chuveiro]
    contas = [valor_conta(c, p) for c in consumos]
    r = resumir("Hábitos (banho mais curto e chave no verão)", contas, consumos,
                sum(hoje["contas"]), sum(hoje["consumos"]), 0, 0, p)
    dias = sum(int(m["dias"]) for m in IRRADIACAO)
    litros = (perfil["minutos"] - minutos) * p["vazao_eletrico"] * perfil["pessoas"] * dias
    r["agua_m3_ano"] = -litros / 1000
    return r


def cenario_aquecedor(perfil, p=PREMISSAS):
    hoje = cenario_hoje(perfil, p)
    # o chuveiro continua de apoio nos dias sem sol, por isso sobra parte do consumo
    chuveiro = [c * (1 - p["fracao_solar"]) for c in hoje["chuveiro"]]
    consumos = [c + perfil["outros_kwh"] for c in chuveiro]
    contas = [valor_conta(c, p) for c in consumos]
    investimento = p["solar_kit"] + p["solar_adaptacao"]
    r = resumir("Aquecedor solar de água (200 L)", contas, consumos,
                sum(hoje["contas"]), sum(hoje["consumos"]), investimento,
                p["solar_manutencao"], p)
    dias = sum(int(m["dias"]) for m in IRRADIACAO)
    litros = (p["vazao_solar"] - p["vazao_eletrico"]) * perfil["minutos"] * perfil["pessoas"] * dias
    r["agua_m3_ano"] = litros / 1000
    return r


def geracao_fv_mes(mes, p=PREMISSAS):
    # E = potência x horas de sol pleno x dias x perdas
    return p["fv_potencia"] * float(mes["irradiacao_kwh_m2_dia"]) * int(mes["dias"]) * p["fv_pr"]


def cenario_fotovoltaico(perfil, p=PREMISSAS):
    hoje = cenario_hoje(perfil, p)
    contas = []
    consumo_rede = []
    creditos = 0.0

    for i, mes in enumerate(IRRADIACAO):
        consumo = hoje["consumos"][i]
        geracao = geracao_fv_mes(mes, p)

        # parte da geração e usada na hora, o resto vai para a rede e vira credito
        na_hora = min(geracao * p["fv_simultaneo"], consumo)
        da_rede = consumo - na_hora
        creditos += geracao - na_hora

        compensado = min(creditos, da_rede)
        creditos -= compensado
        sobra = da_rede - compensado

        preco = preco_kwh(da_rede, p)
        fatura_fio_b = sobra * preco + compensado * p["fio_b"] * p["fio_b_pago"]
        fatura_minima = p["minimo_bifasico"] * preco

        # paga o maior dos dois, nunca os dois juntos
        contas.append(max(fatura_fio_b, fatura_minima))
        consumo_rede.append(sobra)

    investimento = p["fv_potencia"] * 1000 * p["fv_preco_w"]
    r = resumir("Energia solar fotovoltaica (2 kWp)", contas, consumo_rede,
                sum(hoje["contas"]), sum(hoje["consumos"]), investimento,
                p["fv_manutencao"], p)
    r["geracao_ano"] = sum(geracao_fv_mes(m, p) for m in IRRADIACAO)
    r["creditos_sobrando"] = creditos
    r["co2_liquido_kg"] = r["kwh_evitados"] * (p["fator_co2"] - p["co2_ciclo_vida_fv"])
    return r


def comparar(perfil, p=PREMISSAS):
    hoje = cenario_hoje(perfil, p)
    return {
        "hoje": {
            "chuveiro_ano": sum(hoje["chuveiro"]),
            "consumo_ano": sum(hoje["consumos"]),
            "conta_ano": sum(hoje["contas"]),
        },
        "alternativas": [
            cenario_habitos(perfil, p),
            cenario_aquecedor(perfil, p),
            cenario_fotovoltaico(perfil, p),
        ],
    }
