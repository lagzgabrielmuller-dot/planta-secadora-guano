/* Compara el modelo JavaScript con los casos de referencia calculados en Python.
 * Uso:  python exportar_web.py   y después   node web/probar_js.js
 */
const path = require("path");
const M = require(path.join(__dirname, "modelo.js"));
const D = require(path.join(__dirname, "datos.js"));
const ref = require(path.join(__dirname, "referencia.json"));

let peor = 0;
for (const c of ref.casos) {
  const cfg = Object.assign({}, D.defecto, { nx: ref.nx, nz: ref.nz, tol: 1e-4, maxit: 200, nbis: 48 }, c.cfg);
  const t0 = Date.now();
  const r = M.resolver(D, cfg, null);
  const ms = Date.now() - t0;
  const dh = 100 * (r.hum_out - c.hum_out);
  const dT = r.T_exh - c.T_exh;
  const dc = r.comb_kg_h - c.comb;
  const dt55 = (r.hig_peor[0] - c.t55_peor) / 60;
  const dq = Math.max(Math.abs(r.Q_util_kW - c.Q_util), Math.abs(r.Q_escape_kW - c.Q_escape));
  const dhr = 100 * Math.max(Math.abs(r.HR_exh - c.HR_exh), Math.abs(r.HR_mix - c.HR_mix));
  peor = Math.max(peor, Math.abs(dh), Math.abs(dT), Math.abs(dc) / 10, Math.abs(dt55), dq / 10, dhr);
  console.log(`${c.nombre.padEnd(28)} hum ${(100 * r.hum_out).toFixed(3)} (Δ ${dh.toExponential(1)} pts)  ` +
    `escape ${r.T_exh.toFixed(3)} (Δ ${dT.toExponential(1)} K)  cáscara Δ ${dc.toExponential(1)} kg/h  ` +
    `t55 Δ ${dt55.toExponential(1)} min  calor Δ ${dq.toExponential(1)} kW  HR Δ ${dhr.toExponential(1)} pts  ` +
    `${r.iteraciones} it.  ${ms} ms (Python ${(1000 * c.seg).toFixed(0)} ms)`);
}
// velocidad con la malla que usa la página
const cfg = Object.assign({}, D.defecto);
let t0 = Date.now();
let r = M.resolver(D, cfg, null);
console.log(`\npágina (nx ${cfg.nx}, nz ${cfg.nz}, nbis ${cfg.nbis}): ${Date.now() - t0} ms, ${r.iteraciones} it., ` +
  `hum ${(100 * r.hum_out).toFixed(2)} %`);
t0 = Date.now();
r = M.resolver(D, Object.assign({}, cfg, { T_aire: 130 }), r.estado);
console.log(`arranque en caliente: ${Date.now() - t0} ms, ${r.iteraciones} it.`);
console.log(peor < 0.05 ? "\nOK: JavaScript coincide con Python" : `\nDIFERENCIA máxima ${peor}`);
