// Extrae del visor el objeto de datos de la planta (vs: cálculos de proceso + geometría G en metros)
// y lo guarda como JSON para dibujar los planos con las mismas coordenadas que el modelo 3D.
//   node extraer_layout.js <visor.html> <salida.json>
// Coordenadas: x al Este, y al Norte, z arriba (m); origen en el vértice Sudoeste de la nave.
const fs = require("fs");
const vm = require("vm");
const [, , html, salida] = process.argv;
const src = fs.readFileSync(html, "utf8");
const ini = src.indexOf(" vs={") + 4;
// recorre llaves hasta cerrar el objeto (sin strings con llaves en este bloque)
let prof = 0, fin = ini, enStr = null;
for (let i = ini; i < src.length; i++) {
  const c = src[i];
  if (enStr) { if (c === "\\") { i++; continue; } if (c === enStr) enStr = null; continue; }
  if (c === '"' || c === "'" || c === "`") { enStr = c; continue; }
  if (c === "{") prof++;
  else if (c === "}") { prof--; if (prof === 0) { fin = i + 1; break; } }
}
const literal = src.slice(ini, fin);
let obj;
try { obj = vm.runInNewContext("(" + literal + ")", { Math }); }
catch (e) { console.error("No se pudo evaluar el objeto vs:", e.message, literal.slice(0, 200)); process.exit(1); }
// sacar rutas animadas largas (no sirven para los planos)
if (obj.G && obj.G.rutas) { for (const k of Object.keys(obj.G.rutas)) obj.G.rutas[k] = "(omitido)"; }
fs.writeFileSync(salida, JSON.stringify(obj, null, 1));
console.log("layout:", Object.keys(obj).join(", "), "| G:", Object.keys(obj.G || {}).length, "claves");
