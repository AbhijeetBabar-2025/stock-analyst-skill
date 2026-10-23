import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

const FeatureList = [
  {
    icon: '⚡',
    title: 'Quick score in seconds',
    description: (
      <>
        Ask “quick score on NVDA” and get a -100 to +100 score built from seven factors,
        with warnings like “earnings in 5 days”.
      </>
    ),
  },
  {
    icon: '📑',
    title: 'Full research reports',
    description: (
      <>
        Bull and bear cases, valuation, technicals and risks, researched live from the web
        with sources and dates.
      </>
    ),
  },
  {
    icon: '🧠',
    title: 'Learns from its track record',
    description: (
      <>
        Every call goes into a journal. After 30 days it checks what really happened and
        turns its mistakes into lessons it reads next time.
      </>
    ),
  },
  {
    icon: '💼',
    title: 'Portfolio tracker',
    description: <>Tell it what you bought. It tracks profit and loss and warns when one stock is too big a slice.</>,
  },
  {
    icon: '🌍',
    title: 'US, India and more',
    description: <>Works with any Yahoo Finance ticker: AAPL, RELIANCE.NS, TCS.BO, HSBA.L, BTC-USD.</>,
  },
  {
    icon: '🔒',
    title: 'Private and free',
    description: <>No API keys or accounts for market data. Your journal and portfolio stay on your computer.</>,
  },
];

function Feature({icon, title, description}) {
  return (
    <div className={clsx('col col--4', styles.feature)}>
      <div className={styles.icon} aria-hidden="true">{icon}</div>
      <Heading as="h3">{title}</Heading>
      <p>{description}</p>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
