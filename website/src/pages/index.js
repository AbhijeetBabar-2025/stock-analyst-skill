import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import CodeBlock from '@theme/CodeBlock';
import HomepageFeatures from '@site/src/components/HomepageFeatures';

import Heading from '@theme/Heading';
import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <Heading as="h1" className="hero__title">
          {siteConfig.title}
        </Heading>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.install}>
          <CodeBlock language="bash">
            npx skills add AbhijeetBabar-2025/stock-analyst-skill
          </CodeBlock>
        </div>
        <div className={styles.buttons}>
          <Link className="button button--secondary button--lg" to="/docs/install/what-you-need">
            Install step by step
          </Link>
          <Link className="button button--outline button--secondary button--lg" to="/docs/intro">
            What is this?
          </Link>
        </div>
      </div>
    </header>
  );
}

export default function Home() {
  return (
    <Layout
      title="AI stock analyst skill"
      description="A stock analyst skill for Claude Code: quick scores, full reports, portfolio tracking and a journal that learns from past calls.">
      <HomepageHeader />
      <main>
        <HomepageFeatures />
      </main>
    </Layout>
  );
}
