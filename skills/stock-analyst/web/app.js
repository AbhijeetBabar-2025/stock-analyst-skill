// Stock Analyst dashboard. Plain JS, no build step.
// Every value from the server is escaped with esc() before it reaches innerHTML.

const $ = (sel) => document.querySelector(sel);
const TICKER = /^\^?[A-Z0-9][A-Z0-9.\-=]{0,14}$/;
const SUGGEST = ['AAPL', 'NVDA', 'MSFT', 'GLD', 'SPY', 'RELIANCE.NS', 'TCS.NS', 'BTC-USD'];
const LABELS = {
  valuation: 'Valuation', growth: 'Growth', profitability: 'Profitability', health: 'Health',
  momentum: 'Momentum', analysts: 'Analysts', earnings: 'Earnings',
  track_record: 'Track record', risk: 'Risk', cost: 'Cost', liquidity: 'Liquidity',
};
const HEAT = ['--heat-1', '--heat-1', '--heat-2', '--heat-2', '--heat-3',
  '--heat-3', '--heat-4', '--heat-4', '--heat-5', '--heat-5'];

const state = { chips: [], results: [], sort: 'score', scanning: false };

// ---------- helpers ----------
function esc(v) {
  return String(v ?? '').replace(/[&<>"']/g, (c) => (
    { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}
function pct(v, d = 1) {
  if (v == null) return 'n/a';
  const s = (v * 100).toFixed(d);
  if (Number(s) === 0) return `${(0).toFixed(d)}%`; // avoid "-0.0%"
  return `${v > 0 ? '+' : ''}${s}%`;
}
const num = (v, d = 2) => (v == null ? 'n/a' : Number(v).toLocaleString(undefined, {
  minimumFractionDigits: d, maximumFractionDigits: d }));
function money(v, cur) {
  if (v == null) return 'n/a';
  try {
    return new Intl.NumberFormat(undefined, { style: 'currency', currency: cur || 'USD' }).format(v);
  } catch { return num(v); }
}
const big = (v) => (v == null ? 'n/a' : Intl.NumberFormat(undefined, {
  notation: 'compact', maximumFractionDigits: 1 }).format(v));

function toast(msg) {
  const t = $('#toast');
  t.textContent = msg;
  t.classList.add('show');
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => t.classList.remove('show'), 2600);
}

async function api(path, opts = {}) {
  const res = await fetch(path, {
    ...opts,
    headers: opts.body ? { 'Content-Type': 'application/json' } : undefined,
  });
  let data = {};
  try { data = await res.json(); } catch { /* handled below */ }
  if (!res.ok) throw new Error(data.error || `Request failed (${res.status})`);
  return data;
}

function verdictClass(v) {
  if (v.startsWith('BUY')) return 'pill--up';
  if (v.startsWith('SELL')) return 'pill--down';
  return 'pill--neutral';
}

// ---------- theme ----------
$('#theme').addEventListener('click', () => {
  const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
  document.documentElement.dataset.theme = next;
  try { localStorage.setItem('sa-theme', next); } catch { /* private mode */ }
});

// ---------- views ----------
function showView() {
  const view = location.hash === '#journal' ? 'journal' : 'scanner';
  document.querySelectorAll('.tab').forEach((t) =>
    t.setAttribute('aria-selected', String(t.dataset.view === view)));
  $('#view-scanner').hidden = view !== 'scanner';
  $('#view-journal').hidden = view !== 'journal';
  if (view === 'journal') loadJournal();
}
window.addEventListener('hashchange', showView);

// ---------- chips ----------
const input = $('#ticker-input');

function renderChips() {
  document.querySelectorAll('#chips .chip').forEach((c) => c.remove());
  state.chips.forEach((t) => {
    const chip = document.createElement('span');
    chip.className = 'chip';
    chip.innerHTML = `${esc(t)}<button aria-label="Remove ${esc(t)}"><i class="ph ph-x"></i></button>`;
    chip.querySelector('button').addEventListener('click', () => removeChip(t));
    $('#chips').insertBefore(chip, input);
  });
  $('#suggest').innerHTML = SUGGEST.filter((s) => !state.chips.includes(s))
    .map((s) => `<button data-t="${esc(s)}">${esc(s)}</button>`).join('');
}

function addChips(text) {
  const bad = [];
  text.split(/[\s,;]+/).map((t) => t.trim().toUpperCase()).filter(Boolean).forEach((t) => {
    if (!TICKER.test(t)) bad.push(t);
    else if (!state.chips.includes(t) && state.chips.length < 20) state.chips.push(t);
  });
  $('#hint').textContent = bad.length ? `Not a valid symbol: ${bad.join(', ')}` : '';
  renderChips();
  saveWatchlist();
}

function removeChip(t) {
  state.chips = state.chips.filter((c) => c !== t);
  renderChips();
  saveWatchlist();
}

let saveTimer;
function saveWatchlist() {
  clearTimeout(saveTimer);
  saveTimer = setTimeout(() => {
    api('/api/watchlist', { method: 'POST', body: JSON.stringify({ tickers: state.chips }) })
      .catch((e) => toast(`Couldn't save your list: ${e.message}`));
  }, 400);
}

input.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' || e.key === ',' || e.key === ' ') {
    e.preventDefault();
    if (input.value.trim()) { addChips(input.value); input.value = ''; } else if (e.key === 'Enter') scan();
  } else if (e.key === 'Backspace' && !input.value && state.chips.length) {
    removeChip(state.chips[state.chips.length - 1]);
  }
});
input.addEventListener('paste', (e) => {
  e.preventDefault();
  addChips(e.clipboardData.getData('text'));
});
input.addEventListener('blur', () => { if (input.value.trim()) { addChips(input.value); input.value = ''; } });
$('#chips').addEventListener('click', () => input.focus());
$('#suggest').addEventListener('click', (e) => {
  const t = e.target.closest('button')?.dataset.t;
  if (t) addChips(t);
});

// ---------- scanning ----------
$('#scan-btn').addEventListener('click', () => {
  if (input.value.trim()) { addChips(input.value); input.value = ''; }
  scan();
});
$('#sort').addEventListener('change', (e) => { state.sort = e.target.value; renderResults(); });

async function scan() {
  if (!state.chips.length) { toast('Add a symbol first, e.g. AAPL'); input.focus(); return; }
  if (state.scanning) return;
  state.scanning = true;
  const btn = $('#scan-btn');
  btn.disabled = true;
  btn.innerHTML = '<i class="ph-bold ph-circle-notch"></i> Scanning';
  $('#empty').hidden = true;
  $('#results').innerHTML = state.chips.map(skeleton).join('');
  try {
    const data = await api(`/api/scan?t=${encodeURIComponent(state.chips.join(','))}`);
    state.results = data.results;
    renderResults();
  } catch (e) {
    $('#results').innerHTML = errorCard('Scan failed', e.message);
  } finally {
    state.scanning = false;
    btn.disabled = false;
    btn.innerHTML = '<i class="ph-bold ph-magnifying-glass"></i> Scan';
  }
}

function sorted(results) {
  const ok = results.filter((r) => r.ok);
  const key = {
    score: (r) => -r.result.composite,
    momentum: (r) => -(r.result.factors.momentum ?? -9),
    ticker: (r) => r.ticker,
  }[state.sort];
  ok.sort((a, b) => (key(a) < key(b) ? -1 : key(a) > key(b) ? 1 : 0));
  return [...ok, ...results.filter((r) => !r.ok)];
}

function renderResults() {
  const list = sorted(state.results);
  $('#toolbar').hidden = !list.length;
  $('#empty').hidden = list.length > 0;
  const ok = list.filter((r) => r.ok);
  const count = (p) => ok.filter((r) => r.result.verdict.startsWith(p)).length;
  $('#summary').innerHTML = [
    `<span class="pill pill--neutral">${ok.length} scanned</span>`,
    `<span class="pill pill--up">${count('BUY')} buy-lean</span>`,
    `<span class="pill pill--neutral">${count('HOLD')} hold</span>`,
    `<span class="pill pill--down">${count('SELL')} sell-lean</span>`,
  ].join('');
  $('#results').innerHTML = list.map((r) => (r.ok ? card(r) : errorCard(r.ticker, r.error))).join('');
  $('#results').querySelectorAll('[data-act]').forEach((b) => b.addEventListener('click', onCardAction));
  $('#results').querySelectorAll('.card--click').forEach((c) => {
    c.addEventListener('click', (e) => { if (!e.target.closest('button')) openDetail(c.dataset.ticker); });
    c.addEventListener('keydown', (e) => {
      if ((e.key === 'Enter' || e.key === ' ') && e.target === c) { e.preventDefault(); openDetail(c.dataset.ticker); }
    });
  });
}

// ---------- cards ----------
function gauge(score) {
  const pctFill = ((score + 100) / 200) * 100;
  const arc = 'M 10 60 A 50 50 0 0 1 110 60';
  return `<svg class="gauge" viewBox="0 0 120 68" aria-hidden="true">
    <path class="track" d="${arc}" pathLength="100"/>
    <path class="value" d="${arc}" pathLength="100" stroke-dasharray="${pctFill} 100"/></svg>`;
}

function blocks(v) {
  const filled = v == null ? 0 : Math.round((v + 1) * 5);
  return `<span class="blocks">${HEAT.map((h, i) =>
    `<span class="block"${i < filled ? ` style="background:var(${h})"` : ''}></span>`).join('')}</span>`;
}

function keyNumbers(m) {
  const rows = m.asset_type === 'etf'
    ? [
      ['Category', m.category || 'n/a'], ['Asset class', m.asset_class],
      ['Expense ratio', m.expense_ratio == null ? 'n/a' : `${(m.expense_ratio * 100).toFixed(2)}%`],
      ['Assets', big(m.aum)], ['3y avg return', pct(m.return_3y)], ['5y avg return', pct(m.return_5y)],
      ['Volatility', pct(m.volatility_1y).replace('+', '')], ['Price vs NAV', pct(m.premium)],
    ]
    : [
      ['P/E (fwd)', num(m.forward_pe ?? m.trailing_pe, 1)], ['PEG', num(m.peg)],
      ['Revenue growth', pct(m.revenue_growth)], ['Profit margin', pct(m.profit_margin)],
      ['ROE', pct(m.roe)], ['Debt/equity', num(m.debt_to_equity)],
      ['Analyst target', money(m.target_price, m.currency)], ['Next earnings', m.next_earnings || 'n/a'],
    ];
  rows.push(
    ['RSI', num(m.rsi, 0)], ['50 / 200-day avg', `${num(m.ma50, 0)} / ${num(m.ma200, 0)}`],
    ['52w range', `${num(m.low_52w)} to ${num(m.high_52w)}`], ['From 52w high', pct(m.drawdown)],
    ['Compared against', m.benchmark || 'own return'], ['Scanned at', m.scanned_at || 'just now'],
  );
  return `<dl class="kv">${rows.map(([k, v]) => `<div><dt>${esc(k)}</dt><dd>${esc(v)}</dd></div>`).join('')}</dl>`;
}

function card(r) {
  const m = r.metrics;
  const s = r.result;
  const six = m.return_6m;
  const factors = Object.entries(s.factors).map(([k, v]) => `
    <li class="factor">
      <span class="factor__label">${esc(LABELS[k] || k)}</span>
      ${blocks(v)}
      <span class="factor__value ${v == null ? 'na' : v < 0 ? 'neg' : ''}">${v == null ? 'n/a' : (v > 0 ? '+' : '') + v.toFixed(2)}</span>
    </li>`).join('');
  const flags = s.flags.map((f) => `<span class="pill pill--warn"><i class="ph ph-warning"></i>${esc(f)}</span>`).join('');
  return `
  <article class="card card--click" data-ticker="${esc(r.ticker)}" tabindex="0"
           aria-label="Open analysis for ${esc(r.ticker)}">
    <div class="card__head">
      <div class="mark" aria-hidden="true">${esc(r.ticker.replace('^', '')[0])}</div>
      <div style="min-width:0">
        <div class="card__ticker">${esc(r.ticker)}
          <span class="pill pill--neutral">${m.asset_type === 'etf' ? 'ETF' : 'Stock'}</span></div>
        <div class="card__name" title="${esc(m.name)}">${esc(m.name)}</div>
      </div>
      <div class="card__price">
        <strong>${esc(money(m.price, m.currency))}</strong>
        <span class="pill ${six == null ? 'pill--neutral' : six >= 0 ? 'pill--up' : 'pill--down'}">${esc(pct(six))} 6m</span>
      </div>
    </div>
    <div class="card__body">
      <div class="score">
        ${gauge(s.composite)}
        <div class="score__num">${s.composite > 0 ? '+' : ''}${Math.round(s.composite)}</div>
        <span class="pill ${verdictClass(s.verdict)}">${esc(s.verdict)}</span>
      </div>
      <ul class="factors">${factors}</ul>
    </div>
    ${flags ? `<div class="flags">${flags}</div>` : ''}
    <div class="card__foot">
      <span class="pill pill--accent">Confidence ${esc(s.confidence)}</span>
      <span class="spacer"></span>
      <span class="open-hint">Open analysis <i class="ph ph-arrow-right"></i></span>
      <button class="btn btn--small" data-act="log"><i class="ph ph-notebook"></i> Log call</button>
    </div>
  </article>`;
}

function errorCard(title, msg) {
  return `<article class="card card--error"><i class="ph ph-warning-circle"></i>
    <div><strong>${esc(title)}</strong><p>${esc(msg)}</p></div></article>`;
}

function skeleton() {
  return `<article class="card skeleton" aria-hidden="true">
    <div class="card__head"><div class="mark sk"></div>
      <div><div class="sk" style="height:18px;width:70px"></div><div class="sk" style="height:12px;width:120px;margin-top:6px"></div></div>
      <div class="sk" style="height:22px;width:80px"></div></div>
    <div class="card__body"><div class="sk" style="height:120px"></div>
      <div style="display:grid;gap:8px">${'<div class="sk" style="height:10px"></div>'.repeat(6)}</div></div>
  </article>`;
}

async function onCardAction(e) {
  e.stopPropagation();
  const btn = e.currentTarget;
  const el = btn.closest('[data-ticker]');
  const r = state.results.find((x) => x.ticker === el.dataset.ticker) || state.detail;
  btn.disabled = true;
  try {
    const { entry } = await api('/api/journal', {
      method: 'POST',
      body: JSON.stringify({
        ticker: r.ticker, price: r.metrics.price, verdict: r.result.verdict,
        score: r.result.composite, benchmark: r.metrics.benchmark || 'none',
        thesis: `Dashboard quick score ${Math.round(r.result.composite)}`,
      }),
    });
    btn.innerHTML = '<i class="ph ph-check"></i> Logged';
    toast(`Logged ${entry.ticker}: ${entry.verdict} at ${num(entry.price)}`);
  } catch (err) {
    btn.disabled = false;
    toast(`Couldn't log: ${err.message}`);
  }
}

// ---------- detail drawer ----------
const drawer = $('#drawer');
let lastFocus = null;
let hideTimer = null; // pending hide from the close animation

function list(items, cls = '') {
  return `<ul class="blist ${cls}">${items.map((i) => `<li>${esc(i)}</li>`).join('')}</ul>`;
}

function section(icon, title, body, extra = '') {
  return `<section class="dsec ${extra}"><h3><i class="ph ${icon}"></i>${esc(title)}</h3>${body}</section>`;
}

function renderMarkdown(md) {
  if (window.marked && window.DOMPurify) {
    return DOMPurify.sanitize(marked.parse(md), { USE_PROFILES: { html: true } });
  }
  return `<pre class="raw">${esc(md)}</pre>`; // libraries failed to load: show plain text
}

async function openDetail(ticker) {
  lastFocus = document.activeElement;
  clearTimeout(hideTimer); // reopening during the close animation must not get hidden
  drawer.hidden = false;
  document.body.classList.add('locked');
  requestAnimationFrame(() => drawer.classList.add('open'));
  $('#drawer-body').innerHTML = `<div class="dskel">${'<div class="sk" style="height:16px"></div>'.repeat(10)}</div>`;
  $('#drawer-title').textContent = ticker;
  $('#drawer-close').focus();
  try {
    const d = await api(`/api/detail?t=${encodeURIComponent(ticker)}`);
    if (!d.ok) throw new Error(d.error);
    state.detail = d;
    renderDetail(d);
  } catch (e) {
    $('#drawer-body').innerHTML = errorCard(`Couldn't load ${ticker}`, e.message);
  }
}

function closeDetail() {
  drawer.classList.remove('open');
  document.body.classList.remove('locked');
  hideTimer = setTimeout(() => { drawer.hidden = true; }, 200);
  if (lastFocus) lastFocus.focus();
}

$('#drawer-close').addEventListener('click', closeDetail);
$('#drawer-backdrop').addEventListener('click', closeDetail);
document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && !drawer.hidden) closeDetail(); });

function renderDetail(d) {
  const { metrics: m, result: s, brief: b } = d;
  $('#drawer-title').innerHTML = `${esc(d.ticker)} <span class="pill pill--neutral">${m.asset_type === 'etf' ? 'ETF' : 'Stock'}</span>`;
  const headlines = d.news.length
    ? `<ul class="news">${d.news.map((n) => `<li><a href="${esc(n.url)}" target="_blank" rel="noopener noreferrer">${esc(n.title)}</a>
        <span class="muted">${esc(n.source)}${n.date ? `, ${esc(n.date)}` : ''}</span></li>`).join('')}</ul>`
    : `<p class="muted">${esc(d.news_error || 'No headlines in the last 7 days.')}</p>`;
  const watch = `<ul class="watch">${b.watch.map((w) => `<li><strong>${esc(w.what)}</strong><span>${esc(w.why)}</span></li>`).join('')}</ul>`;
  const report = d.report
    ? `<div class="report">${renderMarkdown(d.report.markdown)}</div>`
    : `<div class="report-empty"><p>No full report saved for ${esc(d.ticker)} yet.</p>
        <p>Ask Claude: <code>full report on ${esc(d.ticker)}</code>. It will appear here.</p></div>`;
  $('#drawer-body').innerHTML = `
    <div class="dhead">
      <div><div class="dname">${esc(m.name)}</div>
        <div class="dprice">${esc(money(m.price, m.currency))}
          <span class="pill ${(m.return_6m ?? 0) >= 0 ? 'pill--up' : 'pill--down'}">${esc(pct(m.return_6m))} 6m</span></div></div>
      <div class="dscore">${gauge(s.composite)}<div class="score__num">${s.composite > 0 ? '+' : ''}${Math.round(s.composite)}</div>
        <span class="pill ${verdictClass(s.verdict)}">${esc(s.verdict)}</span></div>
    </div>
    <p class="dsummary">${esc(b.summary)}</p>
    ${section('ph-trend-up', "Why it's moving", list(b.why_moving))}
    ${section('ph-newspaper', 'Latest headlines', headlines)}
    <div class="cases">
      ${section('ph-arrow-up-right', 'Bull case', list(b.bull), 'dsec--bull')}
      ${section('ph-arrow-down-right', 'Bear case', list(b.bear), 'dsec--bear')}
    </div>
    ${section('ph-binoculars', "What I'd watch", watch)}
    ${section('ph-warning', 'Cautions', list(b.cautions), 'dsec--warn')}
    ${section('ph-puzzle-piece', 'Gaps in this research', list(b.gaps))}
    ${section('ph-graduation-cap', 'Trading practice notes', `<p class="learn">For learning only. General education, not advice for your situation.</p>${list(b.practices)}`, 'dsec--learn')}
    ${section('ph-list-numbers', 'Key numbers', keyNumbers({ ...m, scanned_at: state.results.find((x) => x.ticker === d.ticker)?.scanned_at }))}
    ${section('ph-file-text', d.report ? `Full report (${d.report.date})` : 'Full report', report)}
    <div class="dfoot">
      <button class="btn" data-act="log" data-ticker="${esc(d.ticker)}"><i class="ph ph-notebook"></i> Log call</button>
      <span class="muted">Research tool, not financial advice.</span>
    </div>`;
  $('#drawer-body').querySelector('[data-act="log"]').addEventListener('click', onCardAction);
}

// ---------- journal ----------
async function loadJournal() {
  const box = $('#journal');
  box.innerHTML = `<div style="padding:18px;display:grid;gap:10px">${'<div class="sk" style="height:18px"></div>'.repeat(4)}</div>`;
  $('#journal-notes').innerHTML = '';
  try {
    const { rows, notes, min_age_days: minAge } = await api('/api/journal');
    $('#journal-notes').innerHTML = notes.map((n) => `<div class="note">${esc(n)}</div>`).join('');
    if (!rows.length) {
      box.innerHTML = `<div class="empty"><i class="ph ph-notebook"></i><h2>No calls yet</h2>
        <p>Scan a stock and press “Log call”, or ask Claude to analyse one.</p></div>`;
      $('#hit-rate').innerHTML = '';
      return;
    }
    const judged = rows.filter((r) => r.outcome === 'right' || r.outcome === 'wrong');
    const right = judged.filter((r) => r.outcome === 'right').length;
    $('#hit-rate').innerHTML = judged.length
      ? `<strong>${Math.round((right / judged.length) * 100)}%</strong><span>hit rate, ${right} of ${judged.length} reviewed</span>`
      : `<strong>-</strong><span>calls are reviewed after ${esc(minAge)} days</span>`;
    const outcome = (o) => ({ right: 'pill--up', wrong: 'pill--down' }[o] || 'pill--neutral');
    box.innerHTML = `<table>
      <thead><tr><th>Date</th><th>Symbol</th><th>Call</th><th>Score</th><th>Then</th><th>Now</th>
        <th>Return</th><th>vs index</th><th>Outcome</th></tr></thead>
      <tbody>${rows.map((r) => `<tr>
        <td class="num">${esc(r.date)}</td>
        <td><div class="t-ticker">${esc(r.ticker)}</div>${r.thesis ? `<div class="thesis">${esc(r.thesis)}</div>` : ''}</td>
        <td><span class="pill ${verdictClass(r.verdict)}">${esc(r.verdict)}</span></td>
        <td class="num">${r.score == null ? '' : esc(Math.round(r.score))}</td>
        <td class="num">${esc(num(r.price))}</td>
        <td class="num">${esc(num(r.current))}</td>
        <td class="num">${esc(pct(r.return))}</td>
        <td class="num">${r.benchmark ? `${esc(pct(r.bench_return))} <span class="muted">${esc(r.benchmark)}</span>` : '<span class="muted">own return</span>'}</td>
        <td><span class="pill ${outcome(r.outcome)}">${esc(r.outcome)}</span></td>
      </tr>`).join('')}</tbody></table>`;
  } catch (e) {
    box.innerHTML = errorCard("Couldn't load the journal", e.message);
  }
}

// ---------- start ----------
(async function init() {
  renderChips();
  showView();
  try {
    const { tickers } = await api('/api/watchlist');
    state.chips = tickers;
    renderChips();
    if (tickers.length && location.hash !== '#journal') scan();
  } catch (e) {
    toast(`Couldn't load your saved list: ${e.message}`);
  }
}());
