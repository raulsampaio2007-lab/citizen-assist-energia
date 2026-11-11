const mensagens = document.getElementById("mensagens");
const campo = document.getElementById("campo");
const formDados = document.getElementById("form-dados");

function reais(valor) {
  return valor.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function adicionarMensagem(texto, tipo, aviso, fontes) {
  const caixa = document.createElement("div");
  caixa.className = "msg " + tipo;
  caixa.textContent = texto;

  if (aviso) {
    const a = document.createElement("span");
    a.className = "aviso";
    a.textContent = aviso;
    caixa.appendChild(a);
  }

  if (fontes && fontes.length > 0) {
    const lista = document.createElement("div");
    lista.className = "fontes";
    lista.textContent = "Fontes:";
    fontes.forEach(function (fonte) {
      const link = document.createElement("a");
      link.href = fonte.url;
      link.target = "_blank";
      link.rel = "noopener";
      link.textContent = fonte.titulo;
      lista.appendChild(link);
    });
    caixa.appendChild(lista);
  }

  mensagens.appendChild(caixa);
  mensagens.scrollTop = mensagens.scrollHeight;
}

function atualizarPainel(perfil, tabela) {
  ["pessoas", "minutos", "pot_inverno", "pot_verao", "outros_kwh"].forEach(function (nome) {
    formDados.elements[nome].value = Math.round(perfil[nome]);
  });

  const hoje = tabela.hoje;
  document.getElementById("resumo").textContent =
    "Hoje: " + Math.round(hoje.consumo_ano) + " kWh por ano, sendo " + Math.round(hoje.chuveiro_ano) +
    " kWh do chuveiro. Conta estimada de " + reais(hoje.conta_ano) + " por ano.";

  const corpo = document.getElementById("corpo-tabela");
  corpo.innerHTML = "";
  tabela.alternativas.forEach(function (alt) {
    const linha = document.createElement("tr");
    let retorno = "Não se paga";
    if (alt.investimento === 0) {
      retorno = "Imediato";
    } else if (alt.retorno_anos !== null) {
      retorno = alt.retorno_anos.toFixed(1).replace(".", ",") + " anos";
    }
    [alt.nome, reais(alt.investimento), reais(alt.economia_ano), retorno].forEach(function (valor) {
      const celula = document.createElement("td");
      celula.textContent = valor;
      linha.appendChild(celula);
    });
    corpo.appendChild(linha);
  });
}

async function enviar(url, corpo) {
  const resposta = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(corpo),
  });
  return resposta.json();
}

async function perguntar(texto) {
  adicionarMensagem(texto, "usuario");
  try {
    const dados = await enviar("/api/chat", { mensagem: texto });
    adicionarMensagem(dados.texto, "bot", dados.aviso, dados.fontes);
    atualizarPainel(dados.perfil, dados.tabela);
  } catch (erro) {
    adicionarMensagem("Não consegui falar com o servidor. Veja se o app.py está rodando.", "bot");
  }
}

document.getElementById("form-chat").addEventListener("submit", function (evento) {
  evento.preventDefault();
  const texto = campo.value.trim();
  if (texto) {
    campo.value = "";
    perguntar(texto);
  }
});

document.querySelectorAll("#atalhos button").forEach(function (botao) {
  botao.addEventListener("click", function () {
    perguntar(botao.dataset.pergunta);
  });
});

formDados.addEventListener("submit", async function (evento) {
  evento.preventDefault();
  const corpo = Object.fromEntries(new FormData(formDados));
  const dados = await enviar("/api/simular", corpo);
  if (dados.erro) {
    adicionarMensagem(dados.erro, "bot");
    return;
  }
  atualizarPainel(dados.perfil, dados.tabela);
  adicionarMensagem("Recalculei com os seus dados. A tabela ao lado já mudou, e as próximas respostas usam esses números.", "bot");
});

document.getElementById("limpar").addEventListener("click", async function () {
  const dados = await enviar("/api/limpar", {});
  atualizarPainel(dados.perfil, dados.tabela);
  adicionarMensagem("Voltei para a casa do exemplo: 4 pessoas e banho de 8 minutos.", "bot");
});

adicionarMensagem(
  "Oi! Eu ajudo a entender o gasto de energia em casa, principalmente o do chuveiro. Pode perguntar ou usar os botões abaixo.",
  "bot"
);

enviar("/api/limpar", {}).then(function (dados) {
  atualizarPainel(dados.perfil, dados.tabela);
});
