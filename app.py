# Servidor do Citizen Assist AI. Rode com: python app.py
from flask import Flask, jsonify, render_template, request, session

import assistente
import calculos

app = Flask(__name__)
app.secret_key = "citizen-assist-trabalho-faculdade"  # só para rodar local


def pegar_perfil():
    if "perfil" not in session:
        session["perfil"] = calculos.perfil_padrao()
    return session["perfil"]


def tabela(perfil):
    dados = calculos.comparar(perfil)
    return {"hoje": dados["hoje"], "alternativas": dados["alternativas"]}


def aplicar_campos(perfil, campos):
    # junta o que a pessoa digitou no painel com o perfil da conversa
    for campo in ["pessoas", "minutos", "pot_inverno", "pot_verao", "outros_kwh"]:
        if campos.get(campo) not in (None, ""):
            perfil[campo] = float(campos[campo])
    assistente.corrigir_limites(perfil)
    return perfil


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    corpo = request.get_json(silent=True) or {}
    mensagem = corpo.get("mensagem", "").strip()
    if not mensagem:
        return jsonify({"erro": "Mensagem vazia"}), 400
    perfil = pegar_perfil()
    try:
        # o chat usa os números que estão no painel, mesmo sem clicar em Recalcular
        aplicar_campos(perfil, corpo.get("campos") or {})
    except (TypeError, ValueError):
        pass  # campo com texto estranho: fica com o valor anterior
    resposta = assistente.responder(mensagem[:500], perfil)
    session["perfil"] = resposta["perfil"]
    resposta["tabela"] = tabela(resposta["perfil"])
    return jsonify(resposta)


@app.route("/api/simular", methods=["POST"])
def simular():
    corpo = request.get_json(silent=True) or {}
    perfil = pegar_perfil()
    try:
        aplicar_campos(perfil, corpo)
    except (TypeError, ValueError):
        return jsonify({"erro": "Confira os números digitados"}), 400
    session["perfil"] = perfil
    return jsonify({"perfil": perfil, "tabela": tabela(perfil)})


@app.route("/api/limpar", methods=["POST"])
def limpar():
    session["perfil"] = calculos.perfil_padrao()
    return jsonify({"perfil": session["perfil"], "tabela": tabela(session["perfil"])})


if __name__ == "__main__":
    app.run(debug=False, port=5000)
