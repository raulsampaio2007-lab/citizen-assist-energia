# Rode na pasta do projeto com: python -m unittest discover testes
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import assistente
import calculos
from app import app


class TestCalculos(unittest.TestCase):
    def setUp(self):
        self.perfil = calculos.perfil_padrao()

    def test_energia_do_chuveiro(self):
        # 5,5 kW x (4 pessoas x 8 min x 30 dias / 60) = 88 kWh, feito na mão
        kwh = calculos.consumo_chuveiro(5500, 8, 4, 30)
        self.assertAlmostEqual(kwh, 88, places=2)

    def test_faixas_do_icms(self):
        tarifa = 0.78938
        self.assertAlmostEqual(calculos.preco_kwh(80), tarifa / 0.95, places=4)
        self.assertAlmostEqual(calculos.preco_kwh(150), tarifa / 0.83, places=4)
        self.assertAlmostEqual(calculos.preco_kwh(250), tarifa / 0.77, places=4)

    def test_conta_respeita_o_minimo(self):
        self.assertAlmostEqual(calculos.valor_conta(10), calculos.valor_conta(50), places=2)

    def test_geracao_de_janeiro(self):
        # 2 kW x 5,2289 h x 31 dias x 0,75 = 243,1 kWh
        janeiro = calculos.IRRADIACAO[0]
        self.assertAlmostEqual(calculos.geracao_fv_mes(janeiro), 243.14, places=1)

    def test_alternativas_reduzem_a_conta(self):
        dados = calculos.comparar(self.perfil)
        for alternativa in dados["alternativas"]:
            self.assertLess(alternativa["conta_ano"], dados["hoje"]["conta_ano"])

    def test_habitos_nao_tem_custo_e_economizam_agua(self):
        r = calculos.cenario_habitos(self.perfil)
        self.assertEqual(r["investimento"], 0)
        self.assertLess(r["agua_m3_ano"], 0)

    def test_banho_de_tres_minutos_nao_aumenta_o_tempo(self):
        self.perfil["minutos"] = 3
        r = calculos.cenario_habitos(self.perfil)
        self.assertGreaterEqual(r["economia_ano"], 0)
        self.assertEqual(r["agua_m3_ano"], 0)

    def test_placa_com_preco_alto_demora_mais(self):
        p = dict(calculos.PREMISSAS)
        p["fv_preco_w"] = 6
        caro = calculos.cenario_fotovoltaico(self.perfil, p)
        normal = calculos.cenario_fotovoltaico(self.perfil)
        self.assertGreater(caro["retorno_anos"], normal["retorno_anos"])


class TestAssistente(unittest.TestCase):
    def setUp(self):
        self.perfil = calculos.perfil_padrao()

    def perguntar(self, texto):
        return assistente.responder(texto, self.perfil)

    def test_entende_as_perguntas_principais(self):
        casos = {
            "quanto meu chuveiro gasta?": "gasto_banho",
            "como economizar no banho": "habitos",
            "vale a pena colocar placa solar?": "fotovoltaica",
            "aquecedor solar compensa?": "aquecedor",
            "placa ou aquecedor, o que é melhor?": "comparar",
            "quais sao as fontes": "referencias",
            "tenho direito a tarifa social?": "tarifa_social",
            "qual o impacto ambiental": "ambiente",
            "isso e garantido?": "limitacoes",
        }
        for pergunta, esperado in casos.items():
            with self.subTest(pergunta=pergunta):
                self.assertEqual(assistente.detectar_intencao(assistente.normalizar(pergunta)), esperado)

    def test_resposta_usa_os_mesmos_numeros_da_analise(self):
        r = self.perguntar("Compare as alternativas")
        economia = calculos.cenario_fotovoltaico(self.perfil)["economia_ano"]
        self.assertIn(assistente.reais(economia), r["texto"])

    def test_pega_dados_da_mensagem(self):
        r = self.perguntar("Somos 3 pessoas, banho de 10 minutos, chuveiro de 7500 W")
        self.assertEqual(r["perfil"]["pessoas"], 3)
        self.assertEqual(r["perfil"]["minutos"], 10)
        self.assertEqual(r["perfil"]["pot_inverno"], 7500)

    def test_aluguel_muda_a_recomendacao(self):
        r = self.perguntar("Moro de aluguel, o que voce recomenda?")
        self.assertTrue(r["perfil"]["sem_telhado"])
        self.assertIn("dono", r["texto"])

    def test_so_dados_vira_recomendacao(self):
        r = self.perguntar("Somos 3 pessoas, banho de 10 minutos, moro de aluguel")
        self.assertIn("dono", r["texto"])

    def test_orcamento_baixo(self):
        r = self.perguntar("Tenho R$ 2000 para investir, o que voce recomenda?")
        self.assertEqual(r["perfil"]["orcamento"], 2000)
        self.assertIn("ainda não dá", r["texto"])

    def test_aparelho_comum(self):
        r = self.perguntar("Um ventilador de 100 W ligado 8 horas por dia")
        self.assertIn("24,0 kWh", r["texto"])

    def test_resposta_com_calculo_tem_aviso_e_fonte(self):
        r = self.perguntar("Vale a pena placa solar?")
        self.assertTrue(r["aviso"])
        self.assertGreater(len(r["fontes"]), 0)

    def test_assunto_fora_do_escopo(self):
        r = self.perguntar("Quem ganhou a copa?")
        self.assertIn("não sei", r["texto"])
        self.assertEqual(r["fontes"], [])

    def test_valor_absurdo_e_corrigido(self):
        r = self.perguntar("Somos 900 pessoas")
        self.assertEqual(r["perfil"]["pessoas"], 15)


class TestRotas(unittest.TestCase):
    def setUp(self):
        self.cliente = app.test_client()

    def test_pagina_abre(self):
        self.assertEqual(self.cliente.get("/").status_code, 200)

    def test_chat(self):
        r = self.cliente.post("/api/chat", json={"mensagem": "quanto meu chuveiro gasta?"})
        self.assertEqual(r.status_code, 200)
        self.assertIn("kWh", r.get_json()["texto"])

    def test_chat_vazio(self):
        self.assertEqual(self.cliente.post("/api/chat", json={"mensagem": " "}).status_code, 400)

    def test_simular_com_texto_errado(self):
        self.assertEqual(self.cliente.post("/api/simular", json={"pessoas": "abc"}).status_code, 400)

    def test_perfil_fica_salvo_na_conversa(self):
        self.cliente.post("/api/chat", json={"mensagem": "somos 2 pessoas"})
        r = self.cliente.post("/api/chat", json={"mensagem": "quanto meu chuveiro gasta?"})
        self.assertEqual(r.get_json()["perfil"]["pessoas"], 2)


if __name__ == "__main__":
    unittest.main()
