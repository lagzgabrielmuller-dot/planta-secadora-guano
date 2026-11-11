// Imprime un HTML a PDF A4 con Chrome headless (lo usa calculos/memoria_docx.py).
//   node imprimir_pdf.js <archivo.html> <salida.pdf>
// Requiere puppeteer-core (npm i puppeteer-core) y Google Chrome instalado.
const puppeteer = require("puppeteer-core");
const path = require("path");
const [, , html, pdf] = process.argv;

(async () => {
  const browser = await puppeteer.launch({
    executablePath: require("./navegador").rutaNavegador(), headless: "new",
    args: ["--allow-file-access-from-files", ...require("./navegador").SIN_SANDBOX],
  });
  const page = await browser.newPage();
  await page.goto(require("url").pathToFileURL(path.resolve(html)).href, { waitUntil: "load" });
  await page.pdf({ path: pdf, format: "A4", printBackground: true, preferCSSPageSize: true });
  await browser.close();
})();
