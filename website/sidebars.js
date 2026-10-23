// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  guide: [
    'intro',
    'whats-new',
    {
      type: 'category',
      label: 'Installation',
      collapsed: false,
      items: [
        'install/what-you-need',
        'install/install-claude-code',
        'install/install-tools',
        'install/install-skill',
      ],
    },
    'first-analysis',
    {
      type: 'category',
      label: 'User guide',
      collapsed: false,
      items: [
        'guide/quick-score',
        'guide/full-reports',
        'guide/comparing',
        'guide/portfolio',
        'guide/journal-and-reviews',
        'guide/tickers',
        'guide/understanding-the-score',
        'guide/dashboard',
      ],
    },
    'your-data',
    'updating',
    'troubleshooting',
    'glossary',
  ],
};

export default sidebars;
