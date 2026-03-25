# FBA AI Analysis Report
**Source:** fba_financial_report_20260117_131403.csv
**Total Rows Analyzed:** 14
**Tiers Included:** ['TIER_1_VERIFIED', 'TIER_2_LIKELY', 'TIER_3_NEEDS_REVIEW']
**Model:** kimi-for-coding
**Generated:** 2026-03-17T03:48:43.398487

---

## Batch 1

ERROR: <!DOCTYPE html><html lang="en" dir="ltr" data-locale="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta property="og:image" content="/social-share.png"><meta property="twitter:image" content="/social-share.png"><style>[data-component="top"]{min-height:80px;display:flex;align-items:center}</style><script>window._$HY||(e=>{let t=e=>e&&e.hasAttribute&&(e.hasAttribute("data-hk")?e:t(e.host&&e.host.nodeType?e.host:e.parentNode));["click", "input"].forEach((o=>document.addEventListener(o,(o=>{if(!e.events)return;let s=t(o.composedPath&&o.composedPath()[0]||o.target);s&&!e.completed.has(s)&&e.events.push([s,o])}))))})(_$HY={events:[],completed:new WeakSet,r:{},fe(){}});</script><script>self.$R=self.$R||[];_$HY.r["000000010000000000010"]=$R[0]=($R[2]=r=>(r.p=new Promise((s,f)=>{r.s=s,r.f=f})))($R[1]={p:0,s:0,f:0});($R[3]=(r,d)=>{r.s(d),r.p.s=1,r.p.v=d})($R[1],!0);</script><!--xs--><link href="/_build/assets/entry-client-VF7ouASi.css" rel="stylesheet" /><link href="/_build/assets/i18n-W42HN4_r.js" rel="modulepreload" /><link href="/_build/assets/index-COhlHHzS.js" rel="modulepreload" /><link href="/_build/assets/query-DQzojglR.js" rel="modulepreload" /><link href="/_build/assets/action-Cmm6tPtl.js" rel="modulepreload" /><link href="/_build/assets/HttpStatusCode-qYNerCsA.js" rel="modulepreload" /><link href="/_build/assets/entry-client-Cq-S80tr.js" rel="modulepreload" /><meta data-sm="0000000100000000000010" name="description" content="OpenCode - The open source coding agent."/><link data-sm="00000001000000000000200" rel="icon" type="image/png" href="/favicon-96x96-v3.png" sizes="96x96"/><link data-sm="00000001000000000000210" rel="shortcut icon" href="/favicon-v3.ico"/><link data-sm="00000001000000000000220" rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon-v3.png"/><link data-sm="00000001000000000000230" rel="manifest" href="/site.webmanifest"/><meta data-sm="00000001000000000000240" name="apple-mobile-web-app-title" content="OpenCode"/><style data-sm="00000001000000000000300">
        @font-face {
          font-family: "Inter";
          src: url("/_build/assets/inter-FIwubZjA.woff2") format("woff2-variations");
          font-display: swap;
          font-style: normal;
          font-weight: 100 900;
        }
        @font-face {
          font-family: "Inter Fallback";
          src: local("Arial");
          size-adjust: 100%;
          ascent-override: 97%;
          descent-override: 25%;
          line-gap-override: 1%;
        }
        @font-face {
          font-family: "IBM Plex Mono";
          src: url("/_build/assets/BlexMonoNerdFontMono-Regular-DSJ7IWr2.woff2") format("woff2");
          font-display: swap;
          font-style: normal;
          font-weight: 400;
        }
        @font-face {
          font-family: "IBM Plex Mono";
          src: url("/_build/assets/BlexMonoNerdFontMono-Medium-BvtJB5kd.woff2") format("woff2");
          font-display: swap;
          font-style: normal;
          font-weight: 500;
        }
        @font-face {
          font-family: "IBM Plex Mono";
          src: url("/_build/assets/BlexMonoNerdFontMono-Bold-B8jzonSj.woff2") format("woff2");
          font-display: swap;
          font-style: normal;
          font-weight: 700;
        }
        @font-face {
          font-family: "IBM Plex Mono Fallback";
          src: local("Courier New");
          size-adjust: 100%;
          ascent-override: 97%;
          descent-override: 25%;
          line-gap-override: 1%;
        }

        @font-face {
          font-family: "JetBrains Mono Nerd Font";
          src: url("/_build/assets/JetBrainsMonoNerdFontMono-Regular-QVq88ZfU.woff2") format("woff2");
          font-display: swap;
          font-style: normal;
          font-weight: 400;
        }
        @font-face {
          font-family: "JetBrains Mono Nerd Font";
          src: url("/_build/assets/JetBrainsMonoNerdFontMono-Bold-CU80ifuM.woff2") format("woff2");
          font-display: swap;
          font-style: normal;
          font-weight: 700;
        }
        @font-face {
          font-family: "Fira Code Nerd Font";
          src: url("/_build/assets/FiraCodeNerdFontMono-Regular-io3c92n9.woff2") format("woff2");
          font-display: swap;
          font-style: normal;
          font-weight: 400;
        }
        @font-face {
          font-family: "Fira Code Nerd Font";
          src: url("/_build/assets/FiraCodeNerdFontMono-Bold-BjAeM3gJ.woff2") format("woff2");
          font-display: swap;
          font-style: normal;
          font-weight: 700;
        }
        @font-face {
          font-family: "Cascadia Code Nerd Font";
          src: url("/_build/assets/CaskaydiaCoveNerdFontMono-Regular-C_H0OSLN.woff2") format("woff2");
          font-display: swap;
          font-style: normal;
          font-weight: 400;
        }
        @font-face {
          font-family: "Cascadia Code Nerd Font";
          src: url("/_build/assets/CaskaydiaCoveNerdFontMono-Bold-CxABrWmj.woff2") format("woff2");
          font-display: swap;
          font-style: normal;
          font-weight: 700;
        }
        @font-face {
          font-family: "Hack Nerd Font";
          src: url("/_build/assets/HackNerdFontMono-Regular-IcpSchWC.woff2") format("woff2");
          font-display: swap;
          font-style: normal;
          font-weight: 400;
        }
        @font-face {
          font-family: "Hack Nerd Font";
          src: url("/_build/assets/HackNerdFontMono-Bold-BNG4kp7w.woff2") format("woff2");
          font-display: swap;
          font-style: normal;
          font-weight: 700;
        }
        @font-face {
          font-family: "Source Code Pro Nerd Font";
          src: url("/_build/assets/SauceCodeProNerdFontMono-Regular-Ba96Bdne.woff2") format("woff2");
          font-display: swap;
          font-style: normal;
          font-weight: 400;
        }
        @font-face {
          font-family: "Source Code Pro Nerd Font";
          src: url("/_build/assets/SauceCodeProNerdFontMono-Bold-DloEeUVQ.woff2") format("woff2");
          font-display: swap;
          font-style: normal;
          font-weight: 700;
        }
        @font-face {
          font-family: "Inconsolata Nerd Font";
          src: url("/_build/assets/InconsolataNerdFontMono-Regular-CRHGEvh2.woff2") format("woff2");
          font-display: swap;
          font-style: normal;
          font-weight: 400;
        }
        @font-face {
          font-family: "Inconsolata Nerd Font";
          src: url("/_build/assets/InconsolataNerdFontMono-Bold-oTRjQesI.woff2") format("woff2");
          font-display: swap;
          font-style: normal;
          font-weight: 700;
        }
        @font-face {
          font-family: "Roboto Mono Nerd Font";
          src: url("/_build/assets/RobotoMonoNerdFontMono-Regular-DvxS3QZC.woff2") format("woff2");
          font-display: swap;
          font-style: normal;
          font-weight: 400;
        }
        @font-face {
          font-family: "Roboto Mono Nerd Font";
          src: url("/_build/assets/RobotoMonoNerdFontMono-Bold-DNxuDepp.woff2") format("woff2");
          font-display: swap;
          font-style: normal;
          font-weight: 700;
        }
        @font-face {
          font-family: "Ubuntu Mono Nerd Font";
          src: url("/_build/assets/UbuntuMonoNerdFontMono-Regular-tdnXLyap.woff2") format("woff2");
          font-display: swap;
          font-style: normal;
          font-weight: 400;
        }
        @font-face {
          font-family: "Ubuntu Mono Nerd Font";
          src: url("/_build/assets/UbuntuMonoNerdFontMono-Bold-wLXUURqB.woff2") format("woff2");
          font-display: swap;
          font-style: normal;
          font-weight: 700;
        }
        @font-face {
          font-family: "Intel One Mono Nerd Font";
          src: url("/_build/assets/IntoneMonoNerdFontMono-Regular-BwjBdmsJ.woff2") format("woff2");
          font-display: swap;
          font-style: normal;
          font-weight: 400;
        }
        @font-face {
          font-family: "Intel One Mono Nerd Font";
          src: url("/_build/assets/IntoneMonoNerdFontMono-Bold-BL6LrHzx.woff2") format("woff2");
          font-display: swap;
          font-style: normal;
          font-weight: 700;
        }
        @font-face {
          font-family: "Meslo LGS Nerd Font";
          src: url("/_build/assets/MesloLGSNerdFontMono-Regular-j-nTZDWZ.woff2") format("woff2");
          font-display: swap;
          font-style: normal;
          font-weight: 400;
        }
        @font-face {
          font-family: "Meslo LGS Nerd Font";
          src: url("/_build/assets/MesloLGSNerdFontMono-Bold-CrpVO3ec.woff2") format("woff2");
          font-display: swap;
          font-style: normal;
          font-weight: 700;
        }
        @font-face {
          font-family: "Iosevka Nerd Font";
          src: url("/_build/assets/iosevka-nerd-font-DKH7rjGs.woff2") format("woff2");
          font-display: swap;
          font-style: normal;
          font-weight: 400;
        }
        @font-face {
          font-family: "Iosevka Nerd Font";
          src: url("/_build/assets/iosevka-nerd-font-bold-BObfzjZJ.woff2") format("woff2");
          font-display: swap;
          font-style: normal;
          font-weight: 700;
        }
        @font-face {
          font-family: "GeistMono Nerd Font";
          src: url("/_build/assets/GeistMonoNerdFontMono-Regular-DE7-1zdA.woff2") format("woff2");
          font-display: swap;
          font-style: normal;
          font-weight: 400;
        }
        @font-face {
          font-family: "GeistMono Nerd Font";
          src: url("/_build/assets/GeistMonoNerdFontMono-Bold-BUWrnNa7.woff2") format("woff2");
          font-display: swap;
          font-style: normal;
          font-weight: 700;
        }
      </style><link data-sm="000000010000000000003100" rel="preload" href="/_build/assets/inter-FIwubZjA.woff2" as="font" type="font/woff2" crossorigin="anonymous"/><link data-sm="000000010000000000003110" rel="preload" href="/_build/assets/BlexMonoNerdFontMono-Regular-DSJ7IWr2.woff2" as="font" type="font/woff2" crossorigin="anonymous"/><title data-sm="000000010000000000010000010">Not Found | opencode</title><link href="/_build/assets/_..-BfykJ4fq.css" rel="stylesheet" /><link href="/_build/assets/logo-ornate-dark-DH7mkrML.js" rel="modulepreload" /><link href="/_build/assets/_...404_-B7879tWP.js" rel="modulepreload" /></head><body><div id="app"><!--!$e000000--><main data-hk="00000001000000000001000000" data-page="not-found"><!--$--><!--/--><!--$--><!--/--><div data-component="content"><section data-component="top"><a href="/" data-slot="logo-link"><img data-slot="logo light" src="data:image/svg+xml,%3csvg%20width='234'%20height='42'%20viewBox='0%200%20234%2042'%20fill='none'%20xmlns='http://www.w3.org/2000/svg'%3e%3cpath%20d='M18%2030H6V18H18V30Z'%20fill='%23CFCECD'/%3e%3cpath%20d='M18%2012H6V30H18V12ZM24%2036H0V6H24V36Z'%20fill='%23656363'/%3e%3cpath%20d='M48%2030H36V18H48V30Z'%20fill='%23CFCECD'/%3e%3cpath%20d='M36%2030H48V12H36V30ZM54%2036H36V42H30V6H54V36Z'%20fill='%23656363'/%3e%3cpath%20d='M84%2024V30H66V24H84Z'%20fill='%23CFCECD'/%3e%3cpath%20d='M84%2024H66V30H84V36H60V6H84V24ZM66%2018H78V12H66V18Z'%20fill='%23656363'/%3e%3cpath%20d='M108%2036H96V18H108V36Z'%20fill='%23CFCECD'/%3e%3cpath%20d='M108%2012H96V36H90V6H108V12ZM114%2036H108V12H114V36Z'%20fill='%23656363'/%3e%3cpath%20d='M144%2030H126V18H144V30Z'%20fill='%23CFCECD'/%3e%3cpath%20d='M144%2012H126V30H144V36H120V6H144V12Z'%20fill='%23211E1E'/%3e%3cpath%20d='M168%2030H156V18H168V30Z'%20fill='%23CFCECD'/%3e%3cpath%20d='M168%2012H156V30H168V12ZM174%2036H150V6H174V36Z'%20fill='%23211E1E'/%3e%3cpath%20d='M198%2030H186V18H198V30Z'%20fill='%23CFCECD'/%3e%3cpath%20d='M198%2012H186V30H198V12ZM204%2036H180V6H198V0H204V36Z'%20fill='%23211E1E'/%3e%3cpath%20d='M234%2024V30H216V24H234Z'%20fill='%23CFCECD'/%3e%3cpath%20d='M216%2012V18H228V12H216ZM234%2024H216V30H234V36H210V6H234V24Z'%20fill='%23211E1E'/%3e%3c/svg%3e" alt="opencode logo light"><img data-slot="logo dark" src="data:image/svg+xml,%3csvg%20width='234'%20height='42'%20viewBox='0%200%20234%2042'%20fill='none'%20xmlns='http://www.w3.org/2000/svg'%3e%3cpath%20d='M18%2030H6V18H18V30Z'%20fill='%234B4646'/%3e%3cpath%20d='M18%2012H6V30H18V12ZM24%2036H0V6H24V36Z'%20fill='%23B7B1B1'/%3e%3cpath%20d='M48%2030H36V18H48V30Z'%20fill='%234B4646'/%3e%3cpath%20d='M36%2030H48V12H36V30ZM54%2036H36V42H30V6H54V36Z'%20fill='%23B7B1B1'/%3e%3cpath%20d='M84%2024V30H66V24H84Z'%20fill='%234B4646'/%3e%3cpath%20d='M84%2024H66V30H84V36H60V6H84V24ZM66%2018H78V12H66V18Z'%20fill='%23B7B1B1'/%3e%3cpath%20d='M108%2036H96V18H108V36Z'%20fill='%234B4646'/%3e%3cpath%20d='M108%2012H96V36H90V6H108V12ZM114%2036H108V12H114V36Z'%20fill='%23B7B1B1'/%3e%3cpath%20d='M144%2030H126V18H144V30Z'%20fill='%234B4646'/%3e%3cpath%20d='M144%2012H126V30H144V36H120V6H144V12Z'%20fill='%23F1ECEC'/%3e%3cpath%20d='M168%2030H156V18H168V30Z'%20fill='%234B4646'/%3e%3cpath%20d='M168%2012H156V30H168V12ZM174%2036H150V6H174V36Z'%20fill='%23F1ECEC'/%3e%3cpath%20d='M198%2030H186V18H198V30Z'%20fill='%234B4646'/%3e%3cpath%20d='M198%2012H186V30H198V12ZM204%2036H180V6H198V0H204V36Z'%20fill='%23F1ECEC'/%3e%3cpath%20d='M234%2024V30H216V24H234Z'%20fill='%234B4646'/%3e%3cpath%20d='M216%2012V18H228V12H216ZM234%2024H216V30H234V36H210V6H234V24Z'%20fill='%23F1ECEC'/%3e%3c/svg%3e" alt="opencode logo dark"></a><h1 data-slot="title">404 - Page Not Found</h1></section><section data-component="actions"><div data-slot="action"><a href="/">Home</a></div><div data-slot="action"><a href="/docs">Docs</a></div><div data-slot="action"><a href="https://github.com/anomalyco/opencode">GitHub</a></div><div data-slot="action"><a href="/discord">Discord</a></div></section></div></main><!--!$/e000000--></div><!--$--><script type="module" async src="/_build/assets/entry-client-Cq-S80tr.js"></script><!--/--></body></html>

---

