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
  atualizarTabela(tabela);
}

// separado do atualizarPainel para não apagar o campo enquanto a pessoa digita
function atualizarTabela(tabela) {
  const hoje = tabela.hoje;
  document.getElementById("resumo").textContent =
    "Hoje: " + Math.round(hoje.consumo_ano) + " kWh por ano, sendo " + Math.round(hoje.chuveiro_ano) +
    " kWh do chuveiro. Conta estimada de " + reais(hoje.conta_ano) + " por ano.";

  // primeira linha é a situação de hoje, para dar para comparar com as alternativas
  const linhas = [["Hoje, sem mudar nada", "R$ 0,00", reais(hoje.conta_ano), "-", "-"]];
  tabela.alternativas.forEach(function (alt) {
    let retorno = "Não se paga";
    if (alt.investimento === 0) {
      retorno = "Imediato";
    } else if (alt.retorno_anos !== null) {
      retorno = alt.retorno_anos.toFixed(1).replace(".", ",") + " anos";
    }
    linhas.push([alt.nome, reais(alt.investimento), reais(alt.conta_ano), reais(alt.economia_ano), retorno]);
  });

  const corpo = document.getElementById("corpo-tabela");
  // guarda os valores antigos para pintar o que mudou
  const antigos = [...corpo.querySelectorAll("td")].map(function (celula) {
    return celula.textContent;
  });
  corpo.innerHTML = "";

  let posicao = 0;
  linhas.forEach(function (valores, i) {
    const linha = document.createElement("tr");
    if (i === 0) {
      linha.className = "linha-hoje";
    }
    valores.forEach(function (valor) {
      const celula = document.createElement("td");
      celula.textContent = valor;
      if (antigos.length > 0 && antigos[posicao] !== valor) {
        celula.className = "mudou";
      }
      posicao++;
      linha.appendChild(celula);
    });
    corpo.appendChild(linha);
  });

  setTimeout(function () {
    corpo.querySelectorAll(".mudou").forEach(function (celula) {
      celula.classList.remove("mudou");
    });
  }, 1500);
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
    const dados = await enviar("/api/chat", { mensagem: texto, campos: lerCampos() });
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

function lerCampos() {
  return Object.fromEntries(new FormData(formDados));
}

async function recalcular(avisarNoChat) {
  const dados = await enviar("/api/simular", lerCampos());
  if (dados.erro) {
    adicionarMensagem(dados.erro, "bot");
    return;
  }
  atualizarTabela(dados.tabela);
  if (avisarNoChat) {
    adicionarMensagem("Recalculei com os seus dados. A tabela já mudou, e as próximas respostas usam esses números.", "bot");
  }
}

formDados.addEventListener("submit", function (evento) {
  evento.preventDefault();
  recalcular(true);
});

// teste com usuário: a pessoa mudava o número e esperava a tabela mudar sozinha,
// sem clicar em Recalcular. Agora recalcula uns instantes depois de digitar.
let espera = null;
formDados.addEventListener("input", function () {
  clearTimeout(espera);
  espera = setTimeout(function () {
    recalcular(false);
  }, 500);
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
