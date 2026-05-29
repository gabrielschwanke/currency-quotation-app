let chart = null;
let carregado = false;
let atualizando = false;
let autoRefreshId = null;

const canvas = document.getElementById("grafico");
const infoVariacao = document.getElementById("infoVariacao");
const selectMoeda = document.getElementById("moeda");
const selectPeriodo = document.getElementById("periodo");
const botaoCarregar = document.querySelector(".chart-controls button");

function formatarMoeda(valor) {
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  }).format(valor);
}

function formatarData(timestamp) {
  return new Date(timestamp * 1000).toLocaleDateString("pt-BR");
}

function formatarVariacaoTexto(variacao) {
  if (!Number.isFinite(variacao)) {
    return {
      texto: "Não foi possível calcular a variação.",
      cor: "#f8fafc",
    };
  }

  if (variacao > 0) {
    return {
      texto: `↑ Alta de ${variacao.toFixed(2)}% no período`,
      cor: "#22c55e",
    };
  }

  if (variacao < 0) {
    return {
      texto: `↓ Queda de ${Math.abs(variacao).toFixed(2)}% no período`,
      cor: "#ef4444",
    };
  }

  return {
    texto: "→ Estável no período (0,00%)",
    cor: "#facc15",
  };
}

function atualizarInfoVariacao(texto, cor = "#f8fafc") {
  if (!infoVariacao) return;
  infoVariacao.textContent = texto;
  infoVariacao.style.color = cor;
}

function definirEstadoBotao(carregando) {
  if (!botaoCarregar) return;

  botaoCarregar.disabled = carregando;
  botaoCarregar.style.opacity = carregando ? "0.75" : "1";
  botaoCarregar.textContent = carregando
    ? "Carregando..."
    : "Carregar gráfico";
}

function criarGradiente(ctx, area, cor) {
  const gradient = ctx.createLinearGradient(0, area.top, 0, area.bottom);
  gradient.addColorStop(0, `${cor}55`);
  gradient.addColorStop(1, `${cor}08`);
  return gradient;
}

async function carregarGrafico() {
  if (atualizando || !canvas || !selectMoeda || !selectPeriodo) return;

  const moeda = selectMoeda.value;
  const dias = selectPeriodo.value;

  try {
    atualizando = true;
    definirEstadoBotao(true);

    const response = await fetch(`/api/historico/${moeda}/${dias}`, {
      cache: "no-store",
    });

    if (!response.ok) {
      throw new Error(`Erro HTTP: ${response.status}`);
    }

    const dados = await response.json();

    console.log("DADOS BRUTOS DA API:", dados);

    if (!Array.isArray(dados) || dados.length === 0) {
      if (chart) {
        chart.destroy();
        chart = null;
      }

      atualizarInfoVariacao("Nenhum dado encontrado para o período selecionado.");
      carregado = true;
      iniciarAutoRefresh();
      return;
    }

    const historico = dados
      .filter(
        (item) =>
          item &&
          item.data !== undefined &&
          item.valor !== undefined &&
          Number.isFinite(Number(item.valor))
      )
      .sort((a, b) => a.data - b.data);

    if (historico.length === 0) {
      if (chart) {
        chart.destroy();
        chart = null;
      }

      atualizarInfoVariacao("Os dados recebidos são inválidos.");
      carregado = true;
      iniciarAutoRefresh();
      return;
    }

    const labels = historico.map((item) => formatarData(item.data));
    const valores = historico.map((item) => Number(item.valor));

    const inicial = valores[0];
    const final = valores[valores.length - 1];

    let variacao = 0;
    if (inicial !== 0) {
      variacao = ((final - inicial) / inicial) * 100;
    } else {
      variacao = NaN;
    }

    const variacaoFormatada = formatarVariacaoTexto(variacao);
    atualizarInfoVariacao(variacaoFormatada.texto, variacaoFormatada.cor);

    const ctx = canvas.getContext("2d");

    if (chart) {
      chart.destroy();
    }

    chart = new Chart(ctx, {
      type: "line",
      data: {
        labels,
        datasets: [
          {
            label: `${moeda}/BRL`,
            data: valores,
            borderColor: variacaoFormatada.cor,
            borderWidth: 3,
            tension: 0.35,
            fill: true,
            pointRadius: 3,
            pointHoverRadius: 6,
            pointBackgroundColor: variacaoFormatada.cor,
            pointBorderColor: variacaoFormatada.cor,
            pointHoverBackgroundColor: "#ffffff",
            pointHoverBorderColor: variacaoFormatada.cor,
            backgroundColor: (context) => {
              const chartArea = context.chart.chartArea;
              if (!chartArea) return `${variacaoFormatada.cor}22`;
              return criarGradiente(ctx, chartArea, variacaoFormatada.cor);
            },
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
          duration: 700,
        },
        interaction: {
          mode: "index",
          intersect: false,
        },
        plugins: {
          legend: {
            display: false,
          },
          tooltip: {
            backgroundColor: "rgba(15, 23, 42, 0.95)",
            titleColor: "#f8fafc",
            bodyColor: "#e2e8f0",
            borderColor: "rgba(255, 255, 255, 0.10)",
            borderWidth: 1,
            padding: 12,
            displayColors: false,
            callbacks: {
              label: function (context) {
                return `Cotação: ${formatarMoeda(context.raw)}`;
              },
            },
          },
        },
        scales: {
          x: {
            grid: {
              color: "rgba(255, 255, 255, 0.05)",
              drawBorder: false,
            },
            ticks: {
              color: "#cbd5e1",
            },
          },
          y: {
            grid: {
              color: "rgba(255, 255, 255, 0.06)",
              drawBorder: false,
            },
            ticks: {
              color: "#cbd5e1",
              callback: function (value) {
                return formatarMoeda(value);
              },
            },
          },
        },
      },
    });

    carregado = true;
    iniciarAutoRefresh();
  } catch (error) {
    console.error("Erro ao carregar gráfico:", error);
    atualizarInfoVariacao("Erro ao carregar os dados do gráfico.", "#f87171");
  } finally {
    atualizando = false;
    definirEstadoBotao(false);
  }
}

function iniciarAutoRefresh() {
     return;
}

function observarSecaoGrafico() {
  const section = document.getElementById("chart");
  if (!section) return;

  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && !carregado) {
            carregarGrafico();
          }
        });
      },
      {
        threshold: 0.25,
      }
    );

    observer.observe(section);
  } else {
    window.addEventListener("scroll", () => {
      const posicao = section.getBoundingClientRect().top;

      if (posicao < window.innerHeight && !carregado) {
        carregarGrafico();
      }
    });
  }
}

if (selectMoeda) {
  selectMoeda.addEventListener("change", () => {
    if (carregado) carregarGrafico();
  });
}

if (selectPeriodo) {
  selectPeriodo.addEventListener("change", () => {
    if (carregado) carregarGrafico();
  });
}

observarSecaoGrafico();

window.carregarGrafico = carregarGrafico;
