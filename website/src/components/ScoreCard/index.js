import clsx from 'clsx';
import styles from './styles.module.css';

// Real output from scripts/score.py for AAPL on 23 Oct 2026.
const SAMPLE = {
  ticker: 'AAPL',
  name: 'Apple Inc.',
  price: '$346.61',
  sixMonth: '+29.8%',
  score: 35,
  verdict: 'HOLD (wait for earnings)',
  confidence: 'High',
  flag: 'Earnings in 10 days',
  factors: [
    ['Valuation', -0.59],
    ['Growth', 0.68],
    ['Profitability', 1.0],
    ['Health', 0.09],
    ['Momentum', 0.62],
    ['Analysts', -0.18],
    ['Earnings', 0.76],
  ],
};

const HEAT = ['--sa-heat-1', '--sa-heat-1', '--sa-heat-2', '--sa-heat-2', '--sa-heat-3',
  '--sa-heat-3', '--sa-heat-4', '--sa-heat-4', '--sa-heat-5', '--sa-heat-5'];

function Blocks({value}) {
  const filled = Math.round((value + 1) * 5); // -1..1 -> 0..10
  return (
    <span className={styles.blocks} aria-hidden="true">
      {HEAT.map((v, i) => (
        <span
          key={i}
          className={styles.block}
          style={i < filled ? {background: `var(${v})`} : undefined}
        />
      ))}
    </span>
  );
}

function Gauge({score}) {
  // Semicircle from -100 (left) to +100 (right).
  const pct = ((score + 100) / 200) * 100;
  const arc = 'M 10 60 A 50 50 0 0 1 110 60';
  return (
    <svg viewBox="0 0 120 68" className={styles.gauge} role="img" aria-label={`Score ${score} out of 100`}>
      <path d={arc} pathLength="100" className={styles.gaugeTrack} />
      <path d={arc} pathLength="100" className={styles.gaugeValue} strokeDasharray={`${pct} 100`} />
    </svg>
  );
}

export default function ScoreCard() {
  const s = SAMPLE;
  return (
    <figure className={styles.wrap}>
      <div className={styles.card}>
        <div className={styles.head}>
          <div className={styles.mark} aria-hidden="true">{s.ticker[0]}</div>
          <div>
            <div className={styles.ticker}>{s.ticker}</div>
            <div className={styles.name}>{s.name}</div>
          </div>
          <div className={styles.price}>
            <div className={styles.priceValue}>{s.price}</div>
            <span className="sa-pill sa-pill--up">{s.sixMonth} 6m</span>
          </div>
        </div>

        <div className={styles.body}>
          <div className={styles.scorePanel}>
            <Gauge score={s.score} />
            <div className={styles.scoreValue}>+{s.score}</div>
            <div className={styles.scoreLabel}>{s.verdict}</div>
          </div>

          <ul className={styles.factors}>
            {s.factors.map(([label, v]) => (
              <li key={label} className={styles.factor}>
                <span className={styles.factorLabel}>{label}</span>
                <Blocks value={v} />
                <span className={clsx(styles.factorValue, v < 0 && styles.neg)}>
                  {v > 0 ? '+' : ''}{v.toFixed(2)}
                </span>
              </li>
            ))}
          </ul>
        </div>

        <div className={styles.foot}>
          <span className="sa-pill sa-pill--accent">Confidence {s.confidence}</span>
          <span className="sa-pill sa-pill--down">{s.flag}</span>
        </div>
      </div>
      <figcaption className={styles.caption}>Real quick-score output for AAPL, 23 Oct 2026</figcaption>
    </figure>
  );
}
