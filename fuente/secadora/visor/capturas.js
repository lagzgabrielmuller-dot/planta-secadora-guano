// Imágenes del secador SC-4 sacadas del visor (para los planos SC, el manual de armado y el informe).
//   cd fuente && node secadora/visor/capturas.js            # todo
//   cd fuente && node secadora/visor/capturas.js vistas     # solo las 5 vistas (sin los 13 pasos)
//   cd fuente && node secadora/visor/capturas.js paso 1 9   # solo esos pasos del montaje
// Salida: secadora/renders/*.png, SC_despiece_globos.json (posición en la imagen del centro de cada
// pieza despiezada, para los globos del plano SC-02) y secadora/renders/montaje/paso_01.png … paso_13.png
const puppeteer = require("puppeteer-core");
const path = require("path");
const fs = require("fs");
const { rutaNavegador, ARGS_WEBGL } = require("../../navegador");

const RAIZ = path.resolve(__dirname, "..", "..", "..");
const VISOR = path.join(RAIZ, "secadora", "Visor_Secador_SC4.html");
const SALIDA = path.join(RAIZ, "secadora", "renders");
const espera = (ms) => new Promise((r) => setTimeout(r, ms));

(async () => {
  fs.mkdirSync(path.join(SALIDA, "montaje"), { recursive: true });
  const nav = await puppeteer.launch({ executablePath: rutaNavegador(), headless: "new", args: ARGS_WEBGL, protocolTimeout: 600000 });
  const p = await nav.newPage();
  await p.setViewport({ width: 2000, height: 1250 });
  await p.goto(require("url").pathToFileURL(VISOR).href, { waitUntil: "load", timeout: 180000 });
  await p.waitForFunction(() => window.__visor && window.__visor.listo(), { timeout: 240000 });
  await espera(3000);
  await p.evaluate(() => window.__visor.ocultarUI());
  const foto = async (archivo, accion, ms = 4500) => {
    await p.evaluate(accion);
    await espera(ms);
    await p.screenshot({ path: path.join(SALIDA, archivo) });
    console.log(archivo);
  };
  if (process.argv[2] === "paso") {          // node capturas.js paso 1 3 …: solo esos pasos
    await p.evaluate(() => window.__visor.etiquetas(false));
    for (const n of process.argv.slice(3).map(Number))
      await foto(path.join("montaje", `paso_${String(n).padStart(2, "0")}.png`), `__visor.paso(${n - 1})`);
    await nav.close(); return;
  }
  await foto("SC_general.png", "__visor.vista([16.0,6.6,8.2],[6.6,1.3,-1.3])");
  await foto("SC_accionamiento.png", "__visor.vista([13.9,2.3,3.4],[12.35,1.5,0.1])");
  await foto("SC_interior.png", "__visor.corte(true); __visor.vista([9.5,4.6,6.2],[6.0,1.6,-1.3])");
  await foto("SC_despiece.png", "__visor.corte(false); __visor.etiquetas(false); __visor.explosion(1); __visor.vista([19.5,11.5,12.0],[6.6,1.8,-1.3])", 6000);
  // centro de cada pieza ya despiezada, proyectado a píxeles de la captura (para los globos del SC-02)
  const globos = await p.evaluate(() => {
    const ps = window.__PIEZAS.piezas;
    const pts = ps.map((d) => d.centro_mm.map((c, i) => c + d.explosion_mm[i]));
    const xy = window.__visor.proyectar(pts);
    return { ancho: innerWidth, alto: innerHeight, piezas: ps.map((d, i) => ({ id: d.id, cod: d.cod, px: xy[i] })) };
  });
  fs.writeFileSync(path.join(SALIDA, "SC_despiece_globos.json"), JSON.stringify(globos));
  await foto("SC_oeste.png", "__visor.explosion(0); __visor.etiquetas(true); __visor.vista([-6.5,4.2,6.5],[3.0,1.6,-1.3])");
  if (process.argv[2] === "vistas") { await nav.close(); return; }
  await p.evaluate(() => window.__visor.etiquetas(false));
  const pasos = await p.evaluate(() => window.__PASOS.length);
  for (let i = 0; i < pasos; i++) await foto(path.join("montaje", `paso_${String(i + 1).padStart(2, "0")}.png`), `__visor.paso(${i})`);
  await nav.close();
})();
