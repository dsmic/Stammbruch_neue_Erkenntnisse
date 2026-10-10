// node pdf_drucken.js eingabe.html ausgabe.pdf
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const [ein, aus] = process.argv.slice(2);
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM || '/opt/pw-browsers/chromium' })
                    .catch(() => chromium.launch());
  const page = await browser.newPage({ colorScheme: 'light' });
  await page.goto('file://' + path.resolve(ein));
  await page.pdf({ path: aus, format: 'A4', printBackground: true, preferCSSPageSize: true,
                   displayHeaderFooter: true, headerTemplate: '<span></span>',
                   footerTemplate: '<div style="font-size:8pt;width:100%;text-align:center;color:#777">' +
                                   '<span class="pageNumber"></span> / <span class="totalPages"></span></div>' });
  await browser.close();
})();
