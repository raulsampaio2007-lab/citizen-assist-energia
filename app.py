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


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    mensagem = (request.get_json(silent=True) or {}).get("mensagem", "").strip()
    if not mensagem:
        return jsonify({"erro": "Mensagem vazia"}), 400
    resposta = assistente.responder(mensagem[:500], pegar_perfil())
    session["perfil"] = resposta["perfil"]
    resposta["tabela"] = tabela(resposta["perfil"])
    return jsonify(resposta)


@app.route("/api/simular", methods=["POST"])
def simular():
    corpo = request.get_json(silent=True) or {}
    perfil = pegar_perfil()
    try:
        for campo in ["pessoas", "minutos", "pot_inverno", "pot_verao", "outros_kwh"]:
            if campo in corpo:
                perfil[campo] = float(corpo[campo])
    except (TypeError, ValueError):
        return jsonify({"erro": "Confira os números digitados"}), 400
    assistente.corrigir_limites(perfil)
    session["perfil"] = perfil
    return jsonify({"perfil": perfil, "tabela": tabela(perfil)})


@app.route("/api/limpar", methods=["POST"])
def limpar():
    session["perfil"] = calculos.perfil_padrao()
    return jsonify({"perfil": session["perfil"], "tabela": tabela(session["perfil"])})


if __name__ == "__main__":
    app.run(debug=False, port=5000)
