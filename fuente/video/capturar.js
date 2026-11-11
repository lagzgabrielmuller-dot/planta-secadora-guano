// Captura cuadro por cuadro de la escena del video (Chrome sin ventana): cada cuadro pone el tiempo con
// window.__cuadro(t) y saca una captura. Los cuadros se numeran por su tiempo, así varias tandas en paralelo
// escriben en la misma carpeta sin pisarse.
//   node capturar.js <carpeta> [desde_s] [hasta_s] [fps] [ancho] [alto] [calidad_jpg] [cada_n]
// Ejemplo de vista previa rápida: node capturar.js _cuadros/prev 0 231 6 960 540 80
const fs = require("fs");
const path = require("path");
const puppeteer = require("puppeteer-core");
const nav = require("../navegador");

const [, , carpeta, desde = "0", hasta = "", fps = "30", ancho = "1920", alto = "1080", calidad = "92", cada = "1"] = process.argv;
const ESCENA = path.join(__dirname, "escena.html");

(async () => {
  fs.mkdirSync(carpeta, { recursive: true });
  const gpu = process.env.VIDEO_GPU === "1";
  const browser = await puppeteer.launch({
    executablePath: nav.rutaNavegador(), headless: "new", protocolTimeout: 1800000,
    args: [...(gpu ? ["--use-angle=d3d11", "--enable-gpu-rasterization", "--ignore-gpu-blocklist", "--enable-webgl",
      "--allow-file-access-from-files", ...nav.SIN_SANDBOX] : nav.ARGS_WEBGL), `--window-size=${ancho},${alto}`],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: +ancho, height: +alto, deviceScaleFactor: 1 });
  page.on("pageerror", (e) => console.error("pageerror:", e.message));
  page.on("console", (m) => { if (m.type() === "error") console.error("consola:", m.text()); });
  const q = `?w=${ancho}&h=${alto}`;
  await page.goto(require("url").pathToFileURL(ESCENA).href + q, { waitUntil: "load", timeout: 600000 });
  await page.evaluate(() => window.__listo);
  const fin = hasta ? +hasta : await page.evaluate(() => window.__T_FIN);
  // si el viewport no es 1920×1080, la capa HTML (diseñada a 1920) se escala
  if (+ancho !== 1920) await page.addStyleTag({ content: `body{transform:scale(${+ancho / 1920});transform-origin:0 0}` });
  const n0 = Math.ceil(+desde * +fps), n1 = Math.floor(fin * +fps);
  let hechos = 0; const t0 = Date.now();
  for (let n = n0; n <= n1; n += +cada) {
    const ruta = path.join(carpeta, `f_${String(n + 1).padStart(6, "0")}.jpg`);
    if (fs.existsSync(ruta)) continue;
    await page.evaluate((t) => window.__cuadro(t), n / +fps);
    await page.screenshot({ path: ruta + ".tmp", type: "jpeg", quality: +calidad, clip: { x: 0, y: 0, width: +ancho, height: +alto } });
    fs.renameSync(ruta + ".tmp", ruta);
    hechos++;
    if (hechos % 25 === 0 || n + (+cada) > n1) {
      const s = (Date.now() - t0) / 1000 / hechos;
      console.log(`${new Date().toISOString().slice(11, 19)} cuadro ${n + 1}/${n1 + 1} · ${s.toFixed(2)} s/cuadro · faltan ${(((n1 - n) / +cada) * s / 60).toFixed(0)} min`);
    }
  }
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
