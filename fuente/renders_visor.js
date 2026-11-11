// Renders del modelo 3D (Rev. D) para el plano P10, sacados del visor en Chrome headless.
//   node renders_visor.js <visor.html> <carpeta_salida>
// Requiere puppeteer-core (npm i puppeteer-core) y Google Chrome instalado.
const puppeteer = require("puppeteer-core");
const path = require("path");
const [, , html, outDir] = process.argv;

(async () => {
  const browser = await puppeteer.launch({
    executablePath: require("./navegador").rutaNavegador(), headless: "new",
    args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--allow-file-access-from-files", ...require("./navegador").SIN_SANDBOX],
    protocolTimeout: 600000,
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 2400, height: 1500 });
  await page.goto(require("url").pathToFileURL(path.resolve(html)).href, { waitUntil: "load", timeout: 180000 });
  await page.waitForFunction(() => !document.getElementById("loading"), { timeout: 240000 });
  await new Promise((r) => setTimeout(r, 3000));
  // sin paneles ni barras: solo el modelo y los globos
  await page.addStyleTag({ content: ".top,.panel,.tools,.hint,.toast,.scale,.compass,.info,.tip,.sec-tag{display:none!important}" });
  await page.evaluate(() => window.dispatchEvent(new Event("resize")));
  await new Promise((r) => setTimeout(r, 2500));
  const set = async (sel, val) => page.evaluate((s, v) => { const e = document.querySelector(s); if (!e) return; if (e.type === "checkbox") { if (e.checked !== v) e.click(); } else { e.value = v; e.dispatchEvent(new Event("input", { bubbles: true })); e.dispatchEvent(new Event("change", { bubbles: true })); } }, sel, val);
  const foto = async (nombre) => { await new Promise((r) => setTimeout(r, 4000)); await page.screenshot({ path: path.join(outDir, nombre), timeout: 300000 }); console.log(nombre); };

  // A: vista general desde el Sudoeste (cámara inicial del visor)
  await page.evaluate(() => { const b = document.getElementById("b-reset"); b && b.click(); });
  await foto("P10_A_general.png");
  // A2: predio ampliado
  await page.evaluate(() => window.__revD.vista("ubicacion"));
  await foto("P10_A2_predio.png");
  // C: ubicación en Crespo (RN 12, Parque Industrial y planta de biogás vecina) para el informe
  await page.evaluate(() => window.__revD.vista("crespo"));
  await foto("P10_C_crespo.png");
  // B: secador solo, abierto y en despiece
  await page.evaluate(() => window.__revD.solo(true));
  await set("#c-rd-flu", false);
  await set("#c-abrir", true);
  await set("#expv", "1");
  await foto("P10_B_despiece.png");
  await browser.close();
})();
