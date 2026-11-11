// Copia el visor con ganchos que registran la geometría de cada pieza antes de que se fusionen
// las mallas, la carga en Chrome headless y guarda un JSON con primitivas por pieza.
//   node capturar_geometria.js <visor.html> <salida.json> [--resumen]
const fs = require("fs");
const path = require("path");
const puppeteer = require("puppeteer-core");
const [, , html, salida, modo] = process.argv;

const CAP = `<script>
window.__GEO = { partes: {} };
window.__promedioTextura = (function () {
  var cache = {};
  return function (tex) {
    if (cache[tex.uuid] !== undefined) return cache[tex.uuid];
    var r = null;
    try {
      var c = document.createElement("canvas"); c.width = c.height = 8;
      var g = c.getContext("2d"); g.drawImage(tex.image, 0, 0, 8, 8);
      var d = g.getImageData(0, 0, 8, 8).data, s = [0, 0, 0], k = 0;
      for (var i = 0; i < d.length; i += 4) { if (d[i + 3] < 20) continue; s[0] += d[i]; s[1] += d[i + 1]; s[2] += d[i + 2]; k++; }
      if (k) r = (Math.round(s[0] / k) << 16) | (Math.round(s[1] / k) << 8) | Math.round(s[2] / k);
    } catch (e) { r = null; }
    return (cache[tex.uuid] = r);
  };
})();
window.__CAP = function (grupos, filtro) {
  Object.keys(grupos).forEach(function (id) {
    if (filtro && !filtro(id)) return;
    var g = grupos[id];
    g.updateMatrixWorld(true);
    var lista = window.__GEO.partes[id] || (window.__GEO.partes[id] = []);
    g.traverse(function (o) {
      if (!o.isMesh || o.isSkinnedMesh) return;
      var geo = o.geometry, mat = Array.isArray(o.material) ? o.material[0] : o.material;
      var base = { t: geo.type, c: mat && mat.color ? mat.color.getHex() : 0x999999,
                   op: mat && mat.transparent ? mat.opacity : 1, mapa: !!(mat && mat.map) };
      // color promedio de la textura (para el video; el STEP no lo usa)
      if (mat && mat.map && mat.map.image) base.tex = window.__promedioTextura(mat.map);
      if (geo.parameters && /^(Box|Cylinder|Sphere|Torus|Cone|Plane|Circle|Ring)Geometry$/.test(geo.type)) {
        var p = {}; Object.keys(geo.parameters).forEach(function (k) { var v = geo.parameters[k]; if (typeof v === "number" || typeof v === "boolean") p[k] = v; });
        base.p = p;
        geo.computeBoundingBox(); var b = geo.boundingBox; base.bb = [b.min.x, b.min.y, b.min.z, b.max.x, b.max.y, b.max.z];
      }
      var pos = geo.attributes.position; if (!pos) return;
      var idx = geo.index, n = idx ? idx.count : pos.count, tri = new Array(n * 3);
      for (var i = 0; i < n; i++) { var k = idx ? idx.getX(i) : i; tri[i * 3] = +pos.getX(k).toFixed(5); tri[i * 3 + 1] = +pos.getY(k).toFixed(5); tri[i * 3 + 2] = +pos.getZ(k).toFixed(5); }
      base.tri = tri;
      var col = geo.attributes.color;
      if (col && mat && mat.vertexColors) {
        var vc = new Array(n * 3);
        for (var j2 = 0; j2 < n; j2++) { var k2 = idx ? idx.getX(j2) : j2; vc[j2 * 3] = +col.getX(k2).toFixed(3); vc[j2 * 3 + 1] = +col.getY(k2).toFixed(3); vc[j2 * 3 + 2] = +col.getZ(k2).toFixed(3); }
        base.vc = vc;
      }
      if (o.isInstancedMesh) {
        // una entrada por instancia, con la matriz de la instancia aplicada
        var M = o.matrixWorld, mi = new M.constructor();
        for (var j = 0; j < o.count; j++) {
          o.getMatrixAt(j, mi); var w = M.clone().multiply(mi); var extra = { m: w.elements.slice() };
          if (o.instanceColor) { var ic = new (o.material.color.constructor)(); o.getColorAt(j, ic); extra.c = ic.multiply(o.material.color).getHex(); }
          lista.push(Object.assign({}, base, extra));
        }
      } else lista.push(Object.assign({}, base, { m: o.matrixWorld.elements.slice() }));
    });
  });
};
</script>`;

let src = fs.readFileSync(html, "utf8");
const reemplazos = [
  // base (Rev. C): después de F1 y antes de agregar la Rev. D
  ["He=F1(Za,vs,{planta:ii,avisar:r=>yc(r)}),__revDBuild(Za,He,vs)",
   "He=F1(Za,vs,{planta:ii,avisar:r=>yc(r)}),window.__CAP(He.parts),__revDBuild(Za,He,vs)"],
  // Rev. D: antes de su fusión de mallas
  ["  Object.keys(__RD.grupos).forEach(function (id) { __rdMerge(__RD.grupos[id], R); });",
   "  window.__CAP(__RD.grupos);\n  Object.keys(__RD.grupos).forEach(function (id) { __rdMerge(__RD.grupos[id], R); });"],
  // nombres de todas las piezas (Rev. C + Rev. D) una vez armada la lista
  ["__revDSetup();\n/* ==== FIN REV. D ==== */",
   "__revDSetup();\nwindow.__GEO.nombres = Object.fromEntries(Object.entries(Bs).map(function (e) { return [e[0], e[1].nom]; }));\n/* ==== FIN REV. D ==== */"],
];
for (const [a, b] of reemplazos) {
  if (!src.includes(a)) { console.error("No encontré el punto de enganche:\n" + a); process.exit(1); }
  src = src.replace(a, b);
}
src = src.replace("<script>", CAP + "\n<script>");
const copia = path.join(path.dirname(salida), "_visor_captura.html");
fs.writeFileSync(copia, src);

(async () => {
  const browser = await puppeteer.launch({
    executablePath: require("./navegador").rutaNavegador(), headless: "new",
    args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--allow-file-access-from-files", ...require("./navegador").SIN_SANDBOX],
    protocolTimeout: 600000,
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 800, height: 600 });
  page.on("pageerror", (e) => console.error("pageerror:", e.message));
  await page.goto(require("url").pathToFileURL(path.resolve(copia)).href, { waitUntil: "load", timeout: 180000 });
  await page.waitForFunction(() => Object.keys(window.__GEO.partes).length > 50, { timeout: 180000 });
  await new Promise((r) => setTimeout(r, 2000));
  if (modo === "--resumen") {
    const r = await page.evaluate(() => Object.entries(window.__GEO.partes).map(([k, v]) => {
      const tipos = {}; let tri = 0;
      v.forEach((it) => { tipos[it.t] = (tipos[it.t] || 0) + 1; if (it.tri) tri += it.tri.length / 9; });
      return k + "\t" + v.length + "\ttri=" + Math.round(tri) + "\t" + JSON.stringify(tipos);
    }).join("\n"));
    console.log(r);
  } else {
    const json = await page.evaluate(() => JSON.stringify(window.__GEO));
    fs.writeFileSync(salida, json);
    console.log("guardado", salida, (json.length / 1e6).toFixed(1), "MB");
  }
  await browser.close();
})();
