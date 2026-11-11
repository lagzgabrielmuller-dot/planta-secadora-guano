// Graba del visor (visor.html) los recorridos de los vehículos para reproducirlos en el video: así el camión
// entra por el portón P1 y retrocede hasta la pila, y la pala trabaja entre la pila y la tolva sin atravesar equipos.
//   node trafico.js            -> datos/trafico.json (un ciclo completo del visor, cada 0,1 s)
const fs = require("fs");
const path = require("path");
const puppeteer = require("puppeteer-core");
const nav = require("../navegador");

const VEH = { CA: "A", CB: "B", CC: "C", L: "L", MC: "MC" };     // pieza del video -> vehículo del visor (He.VH)
const PASO = 0.1;

(async () => {
  const b = await puppeteer.launch({ executablePath: nav.rutaNavegador(), headless: "new", args: nav.ARGS_WEBGL, protocolTimeout: 1800000 });
  const p = await b.newPage();
  await p.setViewport({ width: 640, height: 400 });
  p.on("pageerror", (e) => console.error("pageerror:", e.message));
  await p.goto(require("url").pathToFileURL(path.resolve(__dirname, "..", "..", "visor.html")).href, { waitUntil: "load", timeout: 300000 });
  await p.waitForFunction(() => window.__R && window.__setT, { timeout: 300000 });
  const datos = await p.evaluate((VEH, PASO) => {
    const He = window.__R, T = He.trafico;
    const g = Object.fromEntries(Object.entries(VEH).map(([k, v]) => [k, He.VH[v].g]));
    const pista = Object.fromEntries(Object.keys(VEH).map((k) => [k, []]));
    for (let t = 0; t < T.CICLO; t += PASO) {
      window.__setT(t);
      for (const [k, o] of Object.entries(g)) {
        o.updateMatrixWorld(true);
        const e = o.matrixWorld.elements;
        let vis = 1; for (let q = o; q; q = q.parent) if (!q.visible) { vis = 0; break; }
        pista[k].push([+e[12].toFixed(3), +e[13].toFixed(3), +e[14].toFixed(3), +Math.atan2(e[8], e[0]).toFixed(4), vis]);
      }
    }
    return { paso: PASO, ciclo: T.CICLO, marcas: { rev0: T.tA.rev0, desc0: T.tA.desc0, desc1: T.tA.desc1, libre0: T.libre0,
      c0: T.tB.c0, c1: T.tB.c1, s0: T.tC.s0, s1: T.tC.s1 }, pista };
  }, VEH, PASO);
  fs.writeFileSync(path.join(__dirname, "datos", "trafico.json"), JSON.stringify(datos));
  console.log("trafico.json:", Object.keys(datos.pista).length, "vehículos,", datos.pista.CA.length, "muestras; marcas", datos.marcas);
  await b.close();
})().catch((e) => { console.error(e); process.exit(1); });
