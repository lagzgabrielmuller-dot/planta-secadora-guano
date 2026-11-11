// Empaqueta el visor del secador en un solo HTML (three.js + modelo GLB + datos adentro).
//   cd fuente && node secadora/visor/build.mjs
// Requiere: npm install (three y esbuild en fuente/package.json) y haber corrido modelo_secador.py.
import { build } from "esbuild";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const AQUI = path.dirname(fileURLToPath(import.meta.url));
const RAIZ = path.resolve(AQUI, "..", "..", "..");
const MODELO = path.join(RAIZ, "secadora", "modelo_3d");
const SALIDA = path.join(RAIZ, "secadora", "Visor_Secador_SC4.html");

const r = await build({
  entryPoints: [path.join(AQUI, "app.js")], bundle: true, format: "iife", minify: true, write: false,
  nodePaths: [path.join(RAIZ, "fuente", "node_modules")],
  alias: { "three/addons": path.join(RAIZ, "fuente", "node_modules", "three", "examples", "jsm") },
  legalComments: "none", target: "es2020",
});
const app = r.outputFiles[0].text.replace(/<\/script/gi, "<\\/script");
const glb = fs.readFileSync(path.join(MODELO, "Secador_SC4.glb")).toString("base64");
const piezas = fs.readFileSync(path.join(MODELO, "piezas.json"), "utf8");
const pasos = fs.readFileSync(path.join(AQUI, "..", "pasos_montaje.json"), "utf8");
let html = fs.readFileSync(path.join(AQUI, "plantilla.html"), "utf8");
html = html.replace("__GLB__", () => glb).replace("__PIEZAS__", () => piezas).replace("__PASOS__", () => pasos)
  .replace("__APP__", () => app);
fs.mkdirSync(path.dirname(SALIDA), { recursive: true });
fs.writeFileSync(SALIDA, html);
console.log(`OK ${SALIDA} (${(html.length / 1e6).toFixed(2)} MB)`);
