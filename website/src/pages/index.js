import Link from '@docusaurus/Link';
import Layout from '@theme/Layout';
import CodeBlock from '@theme/CodeBlock';
import Heading from '@theme/Heading';
import {ArrowRight} from '@phosphor-icons/react';
import HomepageFeatures from '@site/src/components/HomepageFeatures';
import ScoreCard from '@site/src/components/ScoreCard';

import styles from './index.module.css';

const STEPS = [
  {
    verb: 'Install',
    text: 'Set up Claude Code, Node.js and uv, then add the skill with one command.',
    to: '/docs/install/what-you-need',
    link: 'Installation guide',
  },
  {
    verb: 'Ask',
    text: 'Type “quick score on Apple” or “full report on TCS.NS” in plain English.',
    to: '/docs/first-analysis',
    link: 'Your first analysis',
  },
  {
    verb: 'Review',
    text: 'Once a month, ask how past calls did. It turns misses into lessons.',
    to: '/docs/guide/journal-and-reviews',
    link: 'How it learns',
  },
];

function Hero() {
  return (
    <header className={styles.hero}>
      <div className={`container ${styles.heroGrid}`}>
        <div className={styles.heroCopy}>
          <Heading as="h1" className={styles.title}>
            A stock analyst that learns from every call
          </Heading>
          <p className={styles.subtitle}>
            Ask Claude Code about any stock. Get a score in seconds, and a researched report when you need one.
          </p>
          <div className={styles.install}>
            <CodeBlock language="bash">npx skills add AbhijeetBabar-2025/stock-analyst-skill</CodeBlock>
          </div>
          <div className={styles.buttons}>
            <Link className="button button--primary button--lg" to="/docs/install/what-you-need">
              Install guide
            </Link>
            <Link className="button button--secondary button--lg" to="/docs/intro">
              What it does
            </Link>
          </div>
        </div>
        <div className={styles.heroVisual}>
          <ScoreCard />
        </div>
      </div>
    </header>
  );
}

function Steps() {
  return (
    <section className={styles.steps}>
      <div className="container">
        <Heading as="h2" className={styles.stepsHeading}>
          From zero to your first score in about 20 minutes
        </Heading>
        <div className={styles.stepsPanel}>
          {STEPS.map((s) => (
            <div key={s.verb} className={styles.step}>
              <Heading as="h3" className={styles.stepVerb}>{s.verb}</Heading>
              <p className={styles.stepText}>{s.text}</p>
              <Link to={s.to} className={styles.stepLink}>
                {s.link}
                <ArrowRight size={14} weight="bold" aria-hidden="true" />
              </Link>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default function Home() {
  return (
    <Layout
      title="AI stock analyst skill"
      description="A stock analyst skill for Claude Code: quick scores, researched reports, portfolio tracking and a journal that learns from past calls.">
      <Hero />
      <main>
        <HomepageFeatures />
        <Steps />
      </main>
    </Layout>
  );
}
