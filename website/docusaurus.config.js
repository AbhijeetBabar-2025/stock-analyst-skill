// @ts-check
import {themes as prismThemes} from 'prism-react-renderer';

const REPO = 'https://github.com/AbhijeetBabar-2025/stock-analyst-skill';

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Stock Analyst',
  tagline: 'An AI stock analyst that learns from its own track record',
  favicon: 'img/favicon.svg',

  future: {
    v4: true,
  },

  url: 'https://abhijeetbabar-2025.github.io',
  baseUrl: '/stock-analyst-skill/',
  organizationName: 'AbhijeetBabar-2025',
  projectName: 'stock-analyst-skill',
  trailingSlash: false,

  onBrokenLinks: 'throw',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: './sidebars.js',
          editUrl: `${REPO}/tree/main/website/`,
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      colorMode: {
        respectPrefersColorScheme: true,
      },
      navbar: {
        title: 'Stock Analyst',
        logo: {
          alt: 'Stock Analyst logo',
          src: 'img/logo.svg',
        },
        items: [
          {to: '/docs/install/what-you-need', label: 'Install', position: 'left'},
          {type: 'docSidebar', sidebarId: 'guide', position: 'left', label: 'Guide'},
          {href: REPO, label: 'GitHub', position: 'right'},
        ],
      },
      footer: {
        style: 'light',
        links: [
          {
            title: 'Start here',
            items: [
              {label: 'What you need', to: '/docs/install/what-you-need'},
              {label: 'Your first analysis', to: '/docs/first-analysis'},
              {label: 'Troubleshooting', to: '/docs/troubleshooting'},
            ],
          },
          {
            title: 'Project',
            items: [
              {label: 'GitHub', href: REPO},
              {label: 'Report a problem', href: `${REPO}/issues`},
            ],
          },
        ],
        copyright: `Research tool, not financial advice. MIT licensed. Built with Docusaurus.`,
      },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
        additionalLanguages: ['bash', 'powershell', 'json'],
      },
    }),
};

export default config;
