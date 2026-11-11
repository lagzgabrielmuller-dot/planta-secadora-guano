// Capturas sueltas de la escena en tiempos elegidos, para revisar encuadres y textos.
//   node muestras.js <carpeta> <t1> <t2> ... [--w 1920 --h 1080]
const fs = require("fs");
const path = require("path");
const puppeteer = require("puppeteer-core");
const nav = require("../navegador");
const args = process.argv.slice(2);
const carpeta = args.shift();
const opc = { w: 1920, h: 1080, q: "" };
const tiempos = [];
for (let i = 0; i < args.length; i++) {
  if (args[i] === "--w") opc.w = +args[++i]; else if (args[i] === "--h") opc.h = +args[++i];
  else if (args[i] === "--q") opc.q = "&" + args[++i]; else tiempos.push(+args[i]);
}
(async () => {
  fs.mkdirSync(carpeta, { recursive: true });
  const browser = await puppeteer.launch({ executablePath: nav.rutaNavegador(), headless: "new", protocolTimeout: 1800000,
    args: [...nav.ARGS_WEBGL] });
  const page = await browser.newPage();
  await page.setViewport({ width: opc.w, height: opc.h, deviceScaleFactor: 1 });
  page.on("pageerror", (e) => console.error("pageerror:", e.message));
  page.on("console", (m) => { if (["error", "warning"].includes(m.type())) console.error("consola:", m.text().slice(0, 300)); });
  let t0 = Date.now();
  await page.goto(require("url").pathToFileURL(path.join(__dirname, "escena.html")).href + `?w=${opc.w}&h=${opc.h}${opc.q}`, { waitUntil: "load", timeout: 600000 });
  await page.evaluate(() => window.__listo);
  console.log(`carga ${((Date.now() - t0) / 1000).toFixed(1)} s · fin ${await page.evaluate(() => window.__T_FIN.toFixed(2))} s`);
  for (const t of tiempos) {
    t0 = Date.now();
    await page.evaluate((x) => window.__cuadro(x), t);
    const t1 = Date.now();
    await page.screenshot({ path: path.join(carpeta, `t_${t.toFixed(2).padStart(7, "0")}.jpg`), type: "jpeg", quality: 85 });
    console.log(`t=${t}: render ${((t1 - t0) / 1000).toFixed(2)} s + captura ${((Date.now() - t1) / 1000).toFixed(2)} s`);
  }
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
