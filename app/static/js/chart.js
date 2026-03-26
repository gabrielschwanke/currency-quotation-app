let chart;
let carregado = false;

async function carregarGrafico() {
    const moeda = document.getElementById("moeda").value;
    const dias = document.getElementById("periodo").value;

    try {
        const response = await fetch(`/api/historico/${moeda}/${dias}`);
        const dados = await response.json();

        const labels = dados.map(item => {
            const data = new Date(item.data * 1000);
            return data.toLocaleDateString();
        });

        const valores = dados.map(item => item.valor);

        // 📊 cálculo de variação
        const inicial = valores[0];
        const final = valores[valores.length - 1];
        const variacao = ((final - inicial) / inicial) * 100;

        // 🎨 cor dinâmica
        const cor = variacao >= 0 ? "#00ff88" : "#ff4d4d";

        // 📈 texto de tendência
        const tendencia = variacao >= 0 ? "↑ Up" : "↓ Down";

        // 🔥 Atualiza texto na tela
        document.getElementById("infoVariacao").innerHTML =
            `${tendencia} ${variacao.toFixed(2)}%`;

        document.getElementById("infoVariacao").style.color = cor;

        const ctx = document.getElementById("grafico").getContext("2d");

        if (chart) {
            chart.destroy();
        }

        chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    data: valores,
                    borderColor: cor,
                    backgroundColor: cor + "33",
                    borderWidth: 3,
                    tension: 0.3,
                    fill: true,
                    pointRadius: 3
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return "R$ " + context.raw.toFixed(2);
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        ticks: {
                            callback: function(value) {
                                return "R$ " + value;
                            }
                        }
                    }
                }
            }
        });

    } catch (error) {
        console.error("Erro ao carregar gráfico:", error);
    }
}

// carregar ao rolar
window.addEventListener("scroll", () => {
    const section = document.getElementById("chart");
    const posicao = section.getBoundingClientRect().top;

    if (posicao < window.innerHeight && !carregado) {
        carregarGrafico();
        carregado = true;
    }
});

setInterval(() => {
    carregarGrafico();
}, 10000); // atualiza a cada 10 segundos
