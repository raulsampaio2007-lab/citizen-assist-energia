# Gera as tabelas da pasta resultados. Rode com: python análise.py
import csv
import os

from calculos import (IRRADIACAO, PASTA, PREMISSAS, cenario_aquecedor, cenario_fotovoltaico,
                      cenario_habitos, cenario_hoje, comparar, geracao_fv_mes, perfil_padrao)


def salvar(nome, cabecalho, linhas):
    pasta = os.path.join(PASTA, "resultados")
    os.makedirs(pasta, exist_ok=True)
    with open(os.path.join(pasta, nome), "w", encoding="utf-8", newline="") as arq:
        escritor = csv.writer(arq)
        escritor.writerow(cabecalho)
        escritor.writerows(linhas)


def tabela_mensal(perfil):
    hoje = cenario_hoje(perfil)
    linhas = []
    for i, mes in enumerate(IRRADIACAO):
        linhas.append([mes["mes"], round(hoje["chuveiro"][i], 1), round(hoje["consumos"][i], 1),
                       round(hoje["contas"][i], 2), round(geracao_fv_mes(mes), 1)])
    salvar("consumo_mensal.csv",
           ["mes", "chuveiro_kwh", "consumo_total_kwh", "conta_rs", "geracao_fv_2kwp_kwh"], linhas)


def tabela_comparacao(perfil):
    dados = comparar(perfil)
    linhas = []
    for a in dados["alternativas"]:
        retorno = "" if a["retorno_anos"] is None else round(a["retorno_anos"], 1)
        linhas.append([a["nome"], round(a["kwh_evitados"]), round(a["conta_ano"], 2),
                       round(a["economia_ano"], 2), round(a["investimento"], 2),
                       a["manutencao_ano"], retorno, round(a["saldo_horizonte"], 2),
                       round(a["custo_kwh_evitado"], 2), round(a["co2_evitado_kg"], 1),
                       round(a["agua_m3_ano"], 1)])
    salvar("comparacao.csv",
           ["alternativa", "kwh_evitados_ano", "conta_ano_rs", "economia_ano_rs", "investimento_rs",
            "manutencao_ano_rs", "retorno_anos", "saldo_10_anos_rs", "custo_por_kwh_evitado_rs",
            "co2_evitado_kg_ano", "variacao_agua_m3_ano"], linhas)
    return dados


def tabela_sensibilidade(perfil):
    # Muda uma premissa de cada vez para ver o quanto o resultado depende dela.
    testes = [
        ("Aquecedor", "fracao_solar", 0.50, cenario_aquecedor),
        ("Aquecedor", "fracao_solar", 0.85, cenario_aquecedor),
        ("Aquecedor", "solar_adaptacao", 0, cenario_aquecedor),
        ("Aquecedor", "solar_adaptacao", 5640.43, cenario_aquecedor),
        ("Fotovoltaico", "fv_pr", 0.65, cenario_fotovoltaico),
        ("Fotovoltaico", "fv_pr", 0.80, cenario_fotovoltaico),
        ("Fotovoltaico", "fv_preco_w", 2.91, cenario_fotovoltaico),
        ("Fotovoltaico", "fv_preco_w", 4.50, cenario_fotovoltaico),
        ("Fotovoltaico", "fio_b", 0.40, cenario_fotovoltaico),
        ("Fotovoltaico", "minimo_bifasico", 100, cenario_fotovoltaico),
        ("Habitos", "hab_minutos", 6, cenario_habitos),
        ("Habitos", "hab_minutos", 7, cenario_habitos),
    ]
    linhas = []
    for nome, chave, valor, funcao in testes:
        p = dict(PREMISSAS)
        p[chave] = valor
        r = funcao(perfil, p)
        retorno = "" if r["retorno_anos"] is None else round(r["retorno_anos"], 1)
        linhas.append([nome, chave, valor, round(r["economia_ano"], 2), retorno,
                       round(r["saldo_horizonte"], 2)])
    salvar("sensibilidade.csv",
           ["alternativa", "premissa_alterada", "novo_valor", "economia_ano_rs", "retorno_anos",
            "saldo_10_anos_rs"], linhas)
    return linhas


def main():
    perfil = perfil_padrao()
    tabela_mensal(perfil)
    dados = tabela_comparacao(perfil)
    linhas_sens = tabela_sensibilidade(perfil)

    h = dados["hoje"]
    print(f"Hoje: chuveiro {h['chuveiro_ano']:.0f} kWh/ano, casa {h['consumo_ano']:.0f} kWh/ano, "
          f"conta R$ {h['conta_ano']:.2f}/ano")
    for a in dados["alternativas"]:
        print(a["nome"])
        print(f"  evita {a['kwh_evitados']:.0f} kWh/ano | conta R$ {a['conta_ano']:.2f} | "
              f"economia R$ {a['economia_ano']:.2f} | investimento R$ {a['investimento']:.2f}")
        print(f"  retorno {a['retorno_anos']} anos | saldo 10 anos R$ {a['saldo_horizonte']:.2f} | "
              f"R$ {a['custo_kwh_evitado']:.2f}/kWh | CO2 {a['co2_evitado_kg']:.0f} kg | "
              f"agua {a['agua_m3_ano']:.1f} m3")
    fv = dados["alternativas"][2]
    print(f"Geracao FV {fv['geracao_ano']:.0f} kWh/ano, creditos sobrando {fv['creditos_sobrando']:.0f}, "
          f"CO2 liquido {fv['co2_liquido_kg']:.0f} kg")
    print("Sensibilidade:")
    for linha in linhas_sens:
        print(" ", linha)


if __name__ == "__main__":
    main()
