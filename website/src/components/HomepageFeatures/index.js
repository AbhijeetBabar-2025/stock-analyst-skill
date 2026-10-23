import clsx from 'clsx';
import Heading from '@theme/Heading';
import {
  Brain,
  Briefcase,
  FileText,
  GlobeHemisphereWest,
  Lightning,
  LockSimple,
} from '@phosphor-icons/react';
import styles from './styles.module.css';

const ICON = {size: 20, weight: 'regular'};

function Cell({icon: Icon, title, children, wide, tinted}) {
  return (
    <article className={clsx(styles.cell, wide && styles.wide, tinted && styles.tinted)}>
      <div className={styles.icon}>
        <Icon {...ICON} aria-hidden="true" />
      </div>
      <Heading as="h3" className={styles.title}>{title}</Heading>
      {children}
    </article>
  );
}

// Illustrative rows; labelled as an example on the page.
const REVIEW = [
  ['AAPL', 'BUY-lean', '+6.4%', '+2.1%', true],
  ['TCS.NS', 'SELL-lean', '-3.7%', '+0.8%', true],
  ['NVDA', 'BUY-lean', '-1.9%', '+2.1%', false],
];

const TICKERS = ['AAPL', 'MSFT', 'NVDA', 'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'HSBA.L', 'BTC-USD'];

export default function HomepageFeatures() {
  return (
    <section className={styles.section}>
      <div className="container">
        <Heading as="h2" className={styles.heading}>
          Everything a careful investor does, on request
        </Heading>

        <div className={styles.grid}>
          <Cell icon={Brain} title="Learns from its own calls" wide tinted>
            <p className={styles.text}>
              Every call is logged. After 30 days it checks the result against the market and
              writes down what it got wrong, then reads those lessons before the next analysis.
            </p>
            <div className={styles.review}>
              <div className={styles.reviewHead}>Example review</div>
              {REVIEW.map(([t, call, ret, bench, right]) => (
                <div key={t} className={styles.reviewRow}>
                  <span className={styles.mono}>{t}</span>
                  <span className={styles.muted}>{call}</span>
                  <span className={styles.mono}>{ret}</span>
                  <span className={styles.muted}>vs {bench}</span>
                  <span className={clsx('sa-pill', right ? 'sa-pill--up' : 'sa-pill--down')}>
                    {right ? 'Right' : 'Wrong'}
                  </span>
                </div>
              ))}
            </div>
          </Cell>

          <Cell icon={Lightning} title="A score in seconds">
            <div className={styles.bigStat}>
              <span className={styles.bigNumber}>+77</span>
              <span className="sa-pill sa-pill--up">BUY-lean</span>
            </div>
            <p className={styles.text}>NVDA on 23 Oct 2026, from seven factors.</p>
          </Cell>

          <Cell icon={FileText} title="Researched reports">
            <p className={styles.text}>
              Bull and bear cases, valuation, technicals and risks, with every number sourced and dated.
            </p>
          </Cell>

          <Cell icon={GlobeHemisphereWest} title="US, India, UK and crypto" wide>
            <p className={styles.text}>
              Any Yahoo Finance ticker works, and each call is compared with its own market index.
            </p>
            <div className={styles.tickers}>
              {TICKERS.map((t) => (
                <span key={t} className="sa-pill sa-pill--neutral">{t}</span>
              ))}
            </div>
          </Cell>

          <Cell icon={LockSimple} title="Private and free" wide>
            <p className={styles.text}>
              No API keys or data subscriptions. Your journal, lessons and holdings stay in
              <code>~/.stock-analyst</code> on your own computer.
            </p>
          </Cell>

          <Cell icon={Briefcase} title="Portfolio tracker">
            <p className={styles.text}>
              Tell it what you bought. It tracks profit and loss and flags any holding above 30%.
            </p>
          </Cell>
        </div>
      </div>
    </section>
  );
}
