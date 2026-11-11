// Arma la escena del video en un solo HTML (three.js + guion + fuentes adentro); los datos quedan en datos/.
//   cd fuente && node video/escena/build.mjs      -> fuente/video/escena.html
import { build } from "esbuild";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const AQUI = path.dirname(fileURLToPath(import.meta.url));
const VIDEO = path.resolve(AQUI, "..");
const FUENTE = path.resolve(VIDEO, "..");
const RAIZ = path.resolve(FUENTE, "..");
const NM = path.join(FUENTE, "node_modules");

const r = await build({
  entryPoints: [path.join(AQUI, "guion.js")], bundle: true, format: "iife", minify: true, write: false,
  nodePaths: [NM], alias: { "three/addons": path.join(NM, "three", "examples", "jsm") },
  legalComments: "none", target: "es2020",
});
const app = r.outputFiles[0].text.replace(/<\/script/gi, "<\\/script");
const fuentes = [["Barlow", "barlow", [400, 500, 600, 700]], ["Barlow Condensed", "barlow-condensed", [500, 600, 700]]]
  .flatMap(([fam, dir, pesos]) => pesos.map((w) => {
    const f = path.join(NM, "@fontsource", dir, "files", `${dir}-latin-${w}-normal.woff2`);
    return `@font-face { font-family:"${fam}"; font-weight:${w}; font-style:normal; src:url(data:font/woff2;base64,${fs.readFileSync(f).toString("base64")}) format("woff2"); }`;
  })).join("\n");
let html = fs.readFileSync(path.join(AQUI, "plantilla.html"), "utf8");
html = html.replace("__FUENTES__", () => fuentes).replace("__APP__", () => app);
fs.writeFileSync(path.join(VIDEO, "escena.html"), html);
// datos del secador detallado
const modelo = path.join(RAIZ, "secadora", "modelo_3d");
fs.copyFileSync(path.join(modelo, "Secador_SC4.glb"), path.join(VIDEO, "datos", "Secador_SC4.glb"));
fs.copyFileSync(path.join(modelo, "piezas.json"), path.join(VIDEO, "datos", "secador_piezas.json"));
console.log(`OK ${path.join(VIDEO, "escena.html")} (${(html.length / 1e6).toFixed(2)} MB)`);
