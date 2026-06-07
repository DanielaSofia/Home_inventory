document.addEventListener('DOMContentLoaded', function () {
  // Inicializa qualquer canvas que tenha data-labels/data-values
  document.querySelectorAll('canvas[data-labels][data-values]').forEach(function (canvas) {
    try {
      const labels = JSON.parse(canvas.dataset.labels || '[]');
      const data = JSON.parse(canvas.dataset.values || '[]');
      new Chart(canvas.getContext('2d'), {
        type: 'bar',
        data: { labels: labels, datasets: [{ label: 'Dados', data: data, backgroundColor: 'rgba(54,162,235,0.6)' }] },
        options: { responsive: true }
      });
    } catch (e) { console.error('charts.js parse error', e); }
  });
});
