async function fetchJson(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

function actionBadge(action) {
  return `<span class="badge ${action}">${action}</span>`;
}

async function loadSummary() {
  const data = await fetchJson('/api/market-summary');
  const el = document.getElementById('summary');
  el.innerHTML = `
    <div class="kpi"><div class="small">Assets</div><strong>${data.total_assets}</strong></div>
    <div class="kpi"><div class="small">BUY</div><strong>${data.buy_signals}</strong></div>
    <div class="kpi"><div class="small">SELL</div><strong>${data.sell_signals}</strong></div>
    <div class="kpi"><div class="small">Avg Confidence</div><strong>${data.avg_confidence}%</strong></div>
  `;
}

async function loadSignals() {
  const signals = await fetchJson('/api/signals');
  signals.sort((a, b) => b.confidence - a.confidence);
  const rows = signals.map(s => `
    <tr>
      <td>${s.symbol}</td>
      <td>${actionBadge(s.action)}</td>
      <td>${s.confidence}%</td>
      <td>${s.score}</td>
    </tr>`).join('');

  document.getElementById('signalTable').innerHTML = `
    <table>
      <thead><tr><th>Symbol</th><th>Signal</th><th>Conf.</th><th>Score</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>
  `;
}

async function initSymbols() {
  const watchlist = await fetchJson('/api/watchlist');
  const select = document.getElementById('symbolSelect');
  select.innerHTML = watchlist
    .map(item => `<option value="${item.symbol}">${item.symbol} - ${item.name}</option>`)
    .join('');
}

async function analyzeSelected() {
  const symbol = document.getElementById('symbolSelect').value;
  const data = await fetchJson(`/api/analysis/${symbol}`);
  document.getElementById('analysisBox').textContent = JSON.stringify(data, null, 2);
}

async function refreshAll() {
  await Promise.all([loadSummary(), loadSignals()]);
}

document.getElementById('refreshBtn').addEventListener('click', refreshAll);
document.getElementById('analyzeBtn').addEventListener('click', analyzeSelected);

initSymbols().then(refreshAll);
