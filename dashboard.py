```html
<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Dashboard - Sistema de Agenda</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      background-color: #f2f2f2;
      margin: 0;
      padding: 0;
    }
    
    .container {
      max-width: 1200px;
      margin: 0 auto;
      padding: 20px;
    }
    
    .header {
      background-color: #007bff;
      color: white;
      padding: 20px;
      text-align: center;
      border-radius: 5px 5px 0 0;
      margin-bottom: 20px;
    }
    
    .card-container {
      display: flex;
      flex-wrap: wrap;
      gap: 20px;
      margin-bottom: 30px;
    }
    
    .card {
      background-color: white;
      border-radius: 5px;
      padding: 20px;
      flex: 1;
      min-width: 200px;
      box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    .card-title {
      color: #555;
      font-size: 18px;
      margin-bottom: 10px;
    }
    
    .card-value {
      font-size: 36px;
      font-weight: bold;
      color: #007bff;
    }
    
    .chart-container {
      background-color: white;
      border-radius: 5px;
      padding: 20px;
      margin-bottom: 20px;
      box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    .chart-title {
      color: #333;
      font-size: 20px;
      margin-bottom: 20px;
      text-align: center;
    }
    
    .filter-controls {
      display: flex;
      justify-content: center;
      margin-bottom: 20px;
    }
    
    .filter-control {
      padding: 10px 15px;
      margin: 0 5px;
      background-color: #f8f9fa;
      border: 1px solid #ced4da;
      border-radius: 4px;
      cursor: pointer;
    }
    
    .filter-control.active {
      background-color: #007bff;
      color: white;
      border-color: #007bff;
    }
    
    .btn {
      background-color: #007bff;
      color: white;
      border: none;
      padding: 12px 20px;
      border-radius: 5px;
      cursor: pointer;
      font-size: 16px;
      text-decoration: none;
      display: inline-block;
      transition: background-color 0.3s;
    }
    
    .btn:hover {
      background-color: #0056b3;
    }
    
    .actions {
      display: flex;
      justify-content: space-between;
      margin-bottom: 20px;
    }
    
    @media (max-width: 768px) {
      .card-container {
        flex-direction: column;
      }
      
      .card {
        width: 100%;
      }
    }
  </style>
  <!-- Chart.js para gráficos -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>Dashboard</h1>
    </div>
    
    <div class="actions">
      <a href="{% url 'agenda' %}" class="btn">Voltar para Agenda</a>
      <div>
        <button class="btn" id="refresh-data">Atualizar Dados</button>
      </div>
    </div>
    
    <div class="card-container">
      <div class="card">
        <div class="card-title">Total de Pacientes</div>
        <div class="card-value">{{ total_pacientes }}</div>
      </div>
      <div class="card">
        <div class="card-title">Consultas do Mês</div>
        <div class="card-value">{{ consultas_mes }}</div>
      </div>
      <div class="card">
        <div class="card-title">Consultas Hoje</div>
        <div class="card-value">{{ consultas_hoje }}</div>
      </div>
      <div class="card">
        <div class="card-title">Faturamento do Mês</div>
        <div class="card-value">R$ {{ faturamento_mes|floatformat:2 }}</div>
      </div>
    </div>
    
    <div class="chart-container">
      <div class="chart-title">Histórico de Consultas</div>
      <div class="filter-controls">
        <div class="filter-control active" data-months="3">3 Meses</div>
        <div class="filter-control" data-months="6">6 Meses</div>
        <div class="filter-control" data-months="12">12 Meses</div>
      </div>
      <canvas id="consultasChart" height="300"></canvas>
    </div>
    
    <div class="chart-container">
      <div class="chart-title">Histórico de Faturamento</div>
      <canvas id="faturamentoChart" height="300"></canvas>
    </div>
  </div>
  
  <script>
    // Configurações iniciais
    let mesesHistorico = 3;
    let dadosHistoricos = [];
    let consultasChart, faturamentoChart;
    
    // Função para carregar dados do servidor
    async function carregarDados() {
      try {
        const response = await fetch(`{% url 'dashboard_data' %}?meses=${mesesHistorico}`);
        const dados = await response.json();
        dadosHistoricos = dados.data;
        
        atualizarGraficos();
      } catch (error) {
        console.error('Erro ao carregar dados:', error);
      }
    }
    
    // Função para atualizar os gráficos
    function atualizarGraficos() {
      // Preparar dados para os gráficos
      const labels = dadosHistoricos.map(item => {
        const data = new Date(item.data);
        return data.toLocaleDateString('pt-BR', {month: 'short', year: 'numeric'});
      });
      
      const consultas = dadosHistoricos.map(item => item.consultas);
      const faturamento = dadosHistoricos.map(item => item.faturamento);
      
      // Criar/atualizar gráfico de consultas
      if (consultasChart) {
        consultasChart.data.labels = labels;
        consultasChart.data.datasets[0].data = consultas;
        consultasChart.update();
      } else {
        const ctxConsultas = document.getElementById('consultasChart').getContext('2d');
        consultasChart = new Chart(ctxConsultas, {
          type: 'line',
          data: {
            labels: labels,
            datasets: [{
              label: 'Número de Consultas',
              data: consultas,
              backgroundColor: 'rgba(0, 123, 255, 0.1)',
              borderColor: 'rgba(0, 123, 255, 1)',
              borderWidth: 2,
              tension: 0.3,
              fill: true
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
                    return `Consultas: ${context.raw}`;
                  }
                }
              }
            },
            scales: {
              y: {
                beginAtZero: true,
                ticks: {
                  precision: 0
                }
              }
            }
          }
        });
      }
      
      // Criar/atualizar gráfico de faturamento
      if (faturamentoChart) {
        faturamentoChart.data.labels = labels;
        faturamentoChart.data.datasets[0].data = faturamento;
        faturamentoChart.update();
      } else {
        const ctxFaturamento = document.getElementById('faturamentoChart').getContext('2d');
        faturamentoChart = new Chart(ctxFaturamento, {
          type: 'bar',
          data: {
            labels: labels,
            datasets: [{
              label: 'Faturamento (R$)',
              data: faturamento,
              backgroundColor: 'rgba(40, 167, 69, 0.7)',
              borderColor: 'rgba(40, 167, 69, 1)',
              borderWidth: 1
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
                    return `R$ ${context.raw.toFixed(2)}`;
                  }
                }
              }
            },
            scales: {
              y: {
                beginAtZero: true,
                ticks: {
                  callback: function(value) {
                    return 'R$ ' + value;
                  }
                }
              }
            }
          }
        });
      }
    }
    
    // Eventos para os filtros de período
    document.querySelectorAll('.filter-control').forEach(filtro => {
      filtro.addEventListener('click', function() {
        // Atualizar UI
        document.querySelector('.filter-control.active').classList.remove('active');
        this.classList.add('active');
        
        // Atualizar período e recarregar dados
        mesesHistorico = parseInt(this.getAttribute('data-months'));
        carregarDados();
      });
    });
    
    // Evento para botão de atualizar
    document.getElementById('refresh-data').addEventListener('click', carregarDados);
    
    // Inicializar
    document.addEventListener('DOMContentLoaded', carregarDados);
  </script>
</body>
</html>
```