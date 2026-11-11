// Prueba funcional del sitio publicado, servido por HTTP como en GitHub Pages:
//   node tests/e2e/probar_sitio.js [carpeta_capturas]        (desde la raíz del repositorio)
//   SITIO_URL=https://.../ node tests/e2e/probar_sitio.js    (contra el sitio ya publicado)
// Controla: errores de página y de consola, que exista cada archivo enlazado, el video, la galería de planos,
// las páginas de equipos, la redirección de entrega.html, los visores 3D y el simulador, en computadora y celular.
const http = require("http");
const fs = require("fs");
const path = require("path");
const { chromium, devices } = require("playwright");

const RAIZ = path.resolve(__dirname, "..", "..");
const TIPOS = { ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".css": "text/css", ".json": "application/json",
  ".png": "image/png", ".jpg": "image/jpeg", ".svg": "image/svg+xml", ".pdf": "application/pdf", ".mp4": "video/mp4",
  ".glb": "model/gltf-binary", ".zip": "application/zip", ".dxf": "application/dxf", ".step": "application/step",
  ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" };

function servidor() {
  // servidor estático mínimo con soporte de Range (el video lo necesita), como GitHub Pages
  return http.createServer((req, res) => {
    const rel = decodeURIComponent(req.url.split("?")[0].split("#")[0]);
    let archivo = path.join(RAIZ, rel.endsWith("/") ? rel + "index.html" : rel);
    if (!archivo.startsWith(RAIZ) || !fs.existsSync(archivo) || fs.statSync(archivo).isDirectory()) {
      res.writeHead(404); return res.end("404");
    }
    const tam = fs.statSync(archivo).size;
    const tipo = TIPOS[path.extname(archivo).toLowerCase()] || "application/octet-stream";
    const rango = req.headers.range && /bytes=(\d*)-(\d*)/.exec(req.headers.range);
    if (rango) {
      const ini = rango[1] ? +rango[1] : 0, fin = rango[2] ? +rango[2] : tam - 1;
      res.writeHead(206, { "Content-Type": tipo, "Content-Range": `bytes ${ini}-${fin}/${tam}`, "Accept-Ranges": "bytes", "Content-Length": fin - ini + 1 });
      if (req.method === "HEAD") return res.end();
      return fs.createReadStream(archivo, { start: ini, end: fin }).pipe(res);
    }
    res.writeHead(200, { "Content-Type": tipo, "Content-Length": tam, "Accept-Ranges": "bytes" });
    if (req.method === "HEAD") return res.end();
    fs.createReadStream(archivo).pipe(res);
  });
}

const fallas = [];
const ok = (cond, msg) => { console.log((cond ? "  ✔ " : "  ✘ ") + msg); if (!cond) fallas.push(msg); };

async function vigilar(pagina, nombre) {
  const errores = [];
  pagina.on("pageerror", (e) => errores.push(`${nombre}: ${e.message.slice(0, 160)}`));
  pagina.on("console", (m) => { if (m.type() === "error" && !/favicon/.test(m.text())) errores.push(`${nombre} (consola): ${m.text().slice(0, 160)}`); });
  return errores;
}

(async () => {
  const capturas = process.argv[2];
  let base = process.env.SITIO_URL, srv = null;
  if (!base) {
    srv = servidor(); await new Promise((r) => srv.listen(0, "127.0.0.1", r));
    base = `http://127.0.0.1:${srv.address().port}/`;
  }
  console.log("Sitio:", base);
  const nav = await chromium.launch({ args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist",
    "--autoplay-policy=no-user-gesture-required"] });

  // ---------------- portada en computadora
  console.log("Portada (1366 × 860)");
  const ctx = await nav.newContext({ viewport: { width: 1366, height: 860 } });
  const p = await ctx.newPage();
  const err = await vigilar(p, "portada");
  const r = await p.goto(base + "index.html", { waitUntil: "load" });
  ok(r.status() === 200, "index.html responde 200");
  ok((await p.title()).length > 0, `título: «${await p.title()}»`);
  const refs = await p.evaluate(() => [...document.querySelectorAll("[href],[src]")]
    .map((e) => e.getAttribute("href") || e.getAttribute("src"))
    .concat(JSON.parse(document.getElementById("datos").textContent).planos.flatMap((x) => [x.src, x.pdf])));
  const relativos = [...new Set(refs.filter((x) => x && !/^(https?:|#|data:|mailto:|tel:)/.test(x)).map((x) => x.split("#")[0]))];
  let rotos = [];
  for (const rel of relativos) {
    const res = await p.request.fetch(new URL(rel, base).href, { method: "HEAD" });
    if (res.status() !== 200) rotos.push(`${rel} (${res.status()})`);
  }
  ok(rotos.length === 0, `${relativos.length} enlaces internos responden 200` + (rotos.length ? ": " + rotos.join(", ") : ""));
  const dur = await p.evaluate(() => new Promise((listo) => {
    const v = document.querySelector("#video video"); v.preload = "metadata";
    v.addEventListener("loadedmetadata", () => listo(v.duration), { once: true });
    v.addEventListener("error", () => listo(-1), { once: true }); v.load(); setTimeout(() => listo(-2), 30000);
  }));
  ok(dur > 225 && dur < 236, `el video carga y dura ${Math.round(dur)} s (3:51)`);
  await p.click("[data-planos] [data-next]");
  const pdf2 = await p.evaluate(() => document.querySelector("[data-p=pdf]").getAttribute("href"));
  ok(/P02\.pdf$/.test(pdf2), `la galería pasa a la lámina 2 (${pdf2})`);
  for (const id of ["secador", "biogas", "electrica"]) {
    await p.evaluate((id) => (location.hash = "#equipo-" + id), id); await p.waitForTimeout(700);
    const visible = await p.evaluate((id) => !document.getElementById("vista-" + id).hidden, id);
    ok(visible, `página del equipo «${id}» se abre con #equipo-${id}`);
  }
  await p.evaluate(() => (location.hash = "#inicio")); await p.waitForTimeout(500);
  // todas las imágenes llevan atributo alt; las visibles, con texto (la del visor ampliado recibe el suyo al abrirse)
  const sinTexto = await p.evaluate(() => [...document.querySelectorAll("img")].filter((i) =>
    !i.hasAttribute("alt") || (!i.getAttribute("alt") && i.offsetParent !== null)).length);
  ok(sinTexto === 0, "todas las imágenes tienen texto alternativo" + (sinTexto ? ` (faltan ${sinTexto})` : ""));
  await p.evaluate(() => document.querySelector("#planos").scrollIntoView());
  await p.click("[data-ampliar-plano]"); await p.waitForTimeout(600);
  const altLuz = await p.evaluate(() => { const l = document.querySelector(".luz"); return l && !l.hidden ? l.querySelector("img").alt : ""; });
  ok(altLuz.length > 5, `el visor ampliado se abre y describe la imagen («${altLuz.slice(0, 50)}»)`);
  await p.keyboard.press("Escape");
  if (capturas) await p.screenshot({ path: path.join(capturas, "portada_pc.png") });
  ok(err.length === 0, "portada sin errores" + (err.length ? ": " + err.join(" | ") : ""));

  // ---------------- portada en celular
  console.log("Portada en celular (iPhone 13)");
  const cel = await nav.newContext({ ...devices["iPhone 13"] });
  const pc = await cel.newPage();
  const errc = await vigilar(pc, "celular");
  await pc.goto(base + "index.html", { waitUntil: "load" });
  const ancho = await pc.evaluate(() => [document.documentElement.scrollWidth, window.innerWidth]);
  ok(ancho[0] <= ancho[1], `sin desplazamiento horizontal (${ancho[0]} ≤ ${ancho[1]} px)`);
  const menu = await pc.$("#menu-movil, [aria-controls='menu-movil'], .menu-boton");
  ok(!!menu, "hay botón o menú para celular");
  if (capturas) await pc.screenshot({ path: path.join(capturas, "portada_celular.png") });
  ok(errc.length === 0, "celular sin errores" + (errc.length ? ": " + errc.join(" | ") : ""));

  // ---------------- redirección de la dirección vieja
  const pr = await ctx.newPage();
  await pr.goto(base + "entrega.html", { waitUntil: "load" }); await pr.waitForTimeout(1500);
  ok(/index\.html$|\/$/.test(pr.url()), `entrega.html redirige a la portada (${pr.url().replace(base, "")})`);

  // ---------------- visores 3D y simulador
  for (const [rel, nombre] of [["visor.html", "visor de la planta"], ["secadora/Visor_Secador_SC4.html", "visor del secador"],
                               ["simulacion_termica/simulador.html", "simulador térmico"]]) {
    console.log(nombre);
    const pv = await ctx.newPage();
    const ev = await vigilar(pv, nombre);
    const rv = await pv.goto(base + rel, { waitUntil: "load", timeout: 180000 });
    await pv.waitForTimeout(8000);
    ok(rv.status() === 200, `${rel} responde 200`);
    const lienzo = await pv.evaluate(() => { const c = document.querySelector("canvas"); return c ? [c.width, c.height] : null; });
    ok(!!lienzo && lienzo[0] > 100, `${nombre}: dibuja en un lienzo WebGL (${lienzo})`);
    if (capturas) await pv.screenshot({ path: path.join(capturas, rel.split("/").pop().replace(".html", ".png")), timeout: 120000 });
    ok(ev.length === 0, `${nombre} sin errores` + (ev.length ? ": " + ev.join(" | ") : ""));
    await pv.close();
  }
  await nav.close();
  if (srv) srv.close();
  console.log(fallas.length ? `\n${fallas.length} prueba(s) fallaron` : "\nTodas las pruebas del sitio pasaron");
  process.exit(fallas.length ? 1 : 0);
})().catch((e) => { console.error(e); process.exit(2); });
