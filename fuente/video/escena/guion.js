// Guion del video de presentación de la secadora de guano. Todo es función del tiempo t (s) y está sincronizado
// con la música: B(n, p) = comienzo del compás n más p pulsos (datos/ritmo.json). Partes de la canción:
// intro 0-1 · estrofa 2-17 · estribillo 18-33 · valle 34-41 · subida 42-55 · corte 56-57 · estribillo 58-73 · final 74-83
import * as THREE from "three";
import { D, grupos, secador, cartel, trazo, rigCamara, ponerCamara, ambiente, iniciar, dibujar, escena,
  clamp, suave, suave5, salida, rebote, tramo, ventana, PARAM } from "./motor.js";

let B = () => 0, P = 0.6867;
const $ = (s) => document.querySelector(s);
const fmt = (x, dec = 0) => x.toLocaleString("es-AR", { minimumFractionDigits: dec, maximumFractionDigits: dec });

// ------------------------------------------------------------------ armado de la planta
// modo: crecer (escala desde el centro), subir (escala vertical desde el piso), caer (baja desde arriba), pop
const OBRA = [];
function obra(clave, t0, dur, modo = "caer", alto = 22) {
  if (grupos[clave]) OBRA.push({ g: grupos[clave], clave, t0, dur, modo, alto });
}
function aplicarObra(t) {
  for (const o of OBRA) {
    const u = (t - o.t0) / o.dur, obj = o.g.obj;
    obj.visible = u > 0;
    if (u <= 0) continue;
    const p = o.g.pivote || obj.position;
    obj.scale.set(1, 1, 1); obj.position.copy(p);
    if (o.modo === "crecer") { const k = salida(u); obj.scale.set(Math.max(0.001, k), 1, Math.max(0.001, k)); }
    else if (o.modo === "subir") obj.scale.y = Math.max(0.001, salida(u));
    else if (o.modo === "caer") obj.position.y = p.y + o.alto * (1 - rebote(u));
    else if (o.modo === "pop") { const k = rebote(u); obj.scale.setScalar(Math.max(0.001, k)); }
  }
}

// ------------------------------------------------------------------ secador: armado en el aire, bajada y despiece
const ORDEN_SECADOR = [["estructura", 0], ["anclaje", 0.5], ["piso", 1], ["cinta3", 2], ["cinta2", 2.5], ["cinta1", 3],
  ["trans3", 4], ["trans2", 4.5], ["trans1", 5], ["acces", 5.5], ["puertas", 6], ["panel_n", 6.5], ["panel_s", 7],
  ["panel_o", 7.25], ["panel_e", 7.5], ["techo", 8], ["pasarela", 9]];
function aplicarSecador(t) {
  const t0 = B(21), alto = 14;
  const bajada = suave5(tramo(t, B(24), B(25)));
  secador.raiz.position.y = alto * (1 - bajada) + (bajada > 0.98 ? 0 : 0);
  const k = suave(tramo(t, B(35), B(37))) * (1 - suave(tramo(t, B(39, 2), B(40, 2))));    // despiece
  for (const pz of Object.values(secador.piezas)) {
    const orden = ORDEN_SECADOR.find(([g]) => g === pz.grupo);
    const ta = t0 + (orden ? orden[1] : 9) * P;
    const u = tramo(t, ta, ta + 1.3 * P);
    pz.obj.visible = u > 0;
    const ent = 1 - salida(u);
    pz.obj.position.copy(pz.base)
      .addScaledVector(pz.expl, 2.2 * ent + 1.9 * k)
      .add(new THREE.Vector3(0, 9 * ent, 0));
  }
}

// ------------------------------------------------------------------ vehículos: el tráfico del visor (datos/trafico.json)
// Se reproducen los recorridos grabados del visor (camión que entra por el portón P1 y retrocede hasta la pila,
// pala entre la pila y la tolva, despacho, soplado de cáscara): así no atraviesan ningún equipo.
let TV = () => -1;                       // tiempo del visor para cada tiempo del video (-1: vehículos ocultos)
function poseVisor(clave, tv) {
  const P = D.trafico.pista[clave], n = P.length, f = ((tv % D.trafico.ciclo) + D.trafico.ciclo) % D.trafico.ciclo / D.trafico.paso;
  const i = Math.min(n - 1, Math.floor(f)), j = Math.min(n - 1, i + 1), u = f - i;
  const a = P[i], b = P[j];
  let dr = b[3] - a[3]; if (dr > Math.PI) dr -= 2 * Math.PI; if (dr < -Math.PI) dr += 2 * Math.PI;
  const salto = Math.hypot(b[0] - a[0], b[2] - a[2]) > 3;     // reaparece en otro lugar: sin interpolar
  return { x: salto ? a[0] : a[0] + (b[0] - a[0]) * u, y: a[1], z: salto ? a[2] : a[2] + (b[2] - a[2]) * u,
    r: a[3] + (salto ? 0 : dr * u), vis: a[4] && b[4] };
}
function aplicarVehiculos(t) {
  const tv = TV(t);
  for (const k of Object.keys(D.trafico.pista)) {
    const g = grupos[k]; if (!g) continue;
    const o = g.obj;
    if (tv < 0) { o.visible = false; continue; }
    const p = poseVisor(k, tv);
    o.visible = !!p.vis;
    if (!o.visible) continue;
    // la geometría está centrada en su pivote: se ubica el pivote con la pose del visor
    const c = Math.cos(p.r), s = Math.sin(p.r), px = g.pivote.x, pz = g.pivote.z;
    o.position.set(p.x + px * c + pz * s, p.y + g.pivote.y, p.z - px * s + pz * c);
    o.rotation.set(0, p.r, 0); o.scale.set(1, 1, 1);
  }
}

// ------------------------------------------------------------------ resaltado (brillo que late) de piezas
function resaltar(claves, t, t0, t1, color = 0xf0b429) {
  const k = ventana(t, t0, t1, 0.5) * (0.55 + 0.45 * Math.sin((t - t0) * Math.PI * 2 / P));
  for (const c of claves) for (const m of grupos[c]?.mats || []) { m.emissive.setHex(color); m.emissiveIntensity = 0.55 * k; }
}

// ------------------------------------------------------------------ foco en el secador: se retira lo que tapa
const FOCO = ["CA", "CB", "CC", "L", "MC", "AU1", "AU2", "AU3", "22", "23", "24", "25", "29", "TGF", "D17", "D18", "D19",
  "D23", "E1", "E2", "E10", "30", "31", "34", "27", "pilar", "terreno:arboles"];
const VENTANAS_FOCO = [];
function foco(t) {
  for (const { claves, t0, t1 } of VENTANAS_FOCO) {
    const k = suave(tramo(t, t0, t0 + 1.5 * P)) * (1 - suave(tramo(t, t1 - 1.5 * P, t1)));
    if (k <= 0) continue;
    for (const c of claves) {
      const o = grupos[c]?.obj; if (!o || !o.visible) continue;
      if (k > 0.99) { o.visible = false; continue; }
      o.scale.multiplyScalar(1 - k);
    }
  }
}

// ------------------------------------------------------------------ corte de la nave (techo y paredes transparentes)
function corte(k, ocultar = 0) {
  for (const c of ["N:techo", "N:paredes", "AN:techo", "AN:paredes"]) {
    const g = grupos[c]; if (!g) continue;
    if (ocultar > 0.97) { g.obj.visible = false; continue; }
    for (const m of g.mats) {
      const op = (m.userData.opBase ?? 1) * (1 - 0.82 * k) * (1 - ocultar);
      m.opacity = op; m.transparent = op < 0.999; m.depthWrite = op > 0.5;
    }
  }
}

// ------------------------------------------------------------------ textos en pantalla
function titulo(t, t0, t1, sobre, h1, bajo) {
  const el = $("#titulo"), op = ventana(t, t0, t1, 0.8);
  el.style.opacity = op;
  if (op > 0) {
    el.querySelector(".sobre").textContent = sobre; el.querySelector("h1").textContent = h1;
    el.querySelector(".bajo").textContent = bajo;
    el.querySelector(".raya").style.width = `${Math.round(360 * salida(tramo(t, t0 + 0.3, t0 + 1.6)))}px`;
    el.style.transform = `translateY(${(1 - salida(tramo(t, t0, t0 + 1.2))) * 24}px)`;
  }
  return op;
}
let placaActiva = null;
function placa(t, t0, t1, tit, txt, paso = "") {
  const op = ventana(t, t0, t1, 0.45);
  if (op <= 0) return;
  placaActiva = { op, tit, txt, paso, x: (1 - salida(tramo(t, t0, t0 + 0.6))) * -60 };
}
function mostrarPlaca() {
  const el = $("#placa");
  if (!placaActiva) { el.style.opacity = 0; return; }
  const { op, tit, txt, paso, x } = placaActiva;
  el.style.opacity = op; el.style.transform = `translateX(${x}px)`;
  el.querySelector(".tit").textContent = tit; el.querySelector(".txt").textContent = txt;
  const ps = el.querySelector(".paso");
  ps.style.display = paso ? "" : "none";
  ps.innerHTML = paso ? `${paso.split("/")[0]}<small>DE ${paso.split("/")[1]}</small>` : "";
}

const CIFRAS = [];
function cifras(lista) {
  const cont = $("#cifras");
  for (const c of lista) {
    const el = document.createElement("div"); el.className = "cifra";
    el.innerHTML = `<b></b><span>${c.sub}</span>`; cont.appendChild(el);
    CIFRAS.push({ ...c, el, b: el.querySelector("b") });
  }
}
function mostrarCifras(t) {
  for (const c of CIFRAS) {
    const op = ventana(t, c.t0, c.t1, 0.4);
    c.el.style.opacity = op;
    c.el.style.display = op > 0 ? "" : "none";
    if (op <= 0) continue;
    c.el.style.transform = `translateX(${(1 - salida(tramo(t, c.t0, c.t0 + 0.6))) * 60}px)`;
    const k = salida(tramo(t, c.t0 + 0.1, c.t0 + 1.4));
    c.b.textContent = c.texto ? c.texto(k) : `${c.pre || ""}${fmt(c.valor * k, c.dec || 0)}${c.suf || ""}`;
  }
}

// ------------------------------------------------------------------ preparación (una vez cargados los datos)
let camaraEn, CARTELES = [], TRAZOS = [];
function puntoSuelo(c, y = 0) { return new THREE.Vector3(c[0], y, c[1]); }
function topeDe(clave, dy = 0.5) {
  const g = grupos[clave]; if (!g) return new THREE.Vector3();
  return new THREE.Vector3((g.lo.x + g.hi.x) / 2, g.hi.y + dy, (g.lo.z + g.hi.z) / 2);
}
/** cartel visible entre t0 y t1, anclado a un punto fijo o a una función del tiempo */
function C(t0, t1, ancla, tit, sub, opts) {
  const c = cartel("", tit, sub, opts);
  CARTELES.push({ c, t0, t1, ancla });
}
function Tz(t0, t1, puntos, opts, dibujo = 1.2) {
  const T = trazo(puntos, opts);
  TRAZOS.push({ T, t0, t1, dibujo });
  return T;
}

function preparar() {
  const R = D.ritmo; P = R.periodo;
  B = (n, p = 0) => R.compases[0] + (n + p / 4) * 4 * P;
  const M = D.mapa, L = M.lugares;
  const lote = M.lote_mundo, crespo = L["Crespo"].xz, parana = L["Paraná"].xz, pic = L["Parque Industrial Crespo"].xz;

  // ---- cámara
  const lx = 38, lz = -2;
  const st = (i) => B(42 + 1.75 * i);
  const claves = [
    { t: 0, o: [-9000, 0, -12500], d: 64000, az: 0, el: 88 },
    { t: B(2), o: [-8200, 0, -11500], d: 56000, az: -2, el: 86 },
    { t: B(4), o: [-3500, 0, -3500], d: 36000, az: -6, el: 78 },
    { t: B(6), o: [crespo[0], 0, crespo[1] - 700], d: 13500, az: -10, el: 66 },
    { t: B(9), o: [crespo[0], 0, crespo[1] - 900], d: 6800, az: -4, el: 56 },
    { t: B(12), o: [(pic[0] + lx) / 2, 0, (pic[1] + lz) / 2 + 150], d: 2400, az: 12, el: 48 },
    { t: B(15), o: [lx + 60, 0, lz], d: 820, az: 22, el: 42 },
    { t: B(17), o: [lx, 0, lz], d: 320, az: 16, el: 36 },
    { t: B(18), o: [lx, 0, lz], d: 168, az: 8, el: 31 },
    { t: B(20), o: [30, 0, -4], d: 124, az: -22, el: 30 },
    { t: B(21), o: [18, 7, -9], d: 66, az: -36, el: 22 },
    { t: B(23), o: [18, 11, -9], d: 52, az: -14, el: 16 },
    { t: B(25), o: [18, 3, -9], d: 50, az: 10, el: 22 },
    { t: B(27), o: [17, 2, -10], d: 78, az: 42, el: 32 },
    { t: B(29), o: [25, 2, -8], d: 98, az: 72, el: 34 },
    { t: B(31), o: [40, 0, -4], d: 152, az: 112, el: 32 },
    { t: B(33), o: [40, 0, -4], d: 178, az: 152, el: 30 },
    { t: B(34, 2), o: [18, 2.2, -9.3], d: 31, az: 248, el: 26 },
    { t: B(35, 2), o: [18, 2, -9.3], d: 27, az: 318, el: 21 },
    { t: B(37, 2), o: [18, 2.4, -9.3], d: 31, az: 340, el: 24 },
    { t: B(39, 2), o: [18, 2, -9.3], d: 29, az: 372, el: 19 },
    { t: B(41), o: [18, 2, -9.3], d: 25, az: 392, el: 15 },
    // recorrido del proceso: dos claves por parada (llega y se desliza un poco)
    { t: st(0) + 0.7, o: [-1, 1.5, -13.5], d: 22, az: 318, el: 40 }, { t: st(0) + 4.0, o: [0.5, 1.5, -13], d: 20, az: 330, el: 38 },
    { t: st(1) + 0.7, o: [7, 2.5, -9.2], d: 20, az: 330, el: 38 }, { t: st(1) + 4.0, o: [8, 2.5, -9.2], d: 19, az: 320, el: 36 },
    { t: st(2) + 0.7, o: [18, 2.2, -9.3], d: 19, az: 352, el: 23 }, { t: st(2) + 4.0, o: [18, 2.2, -9.3], d: 17.5, az: 342, el: 22 },
    { t: st(3) + 0.8, o: [26, 3.5, -21], d: 26, az: 505, el: 34 }, { t: st(3) + 4.0, o: [26, 3.5, -21], d: 24, az: 515, el: 32 },
    { t: st(4) + 0.7, o: [17, 4, -22], d: 26, az: 545, el: 28 }, { t: st(4) + 4.0, o: [17, 4.5, -22], d: 24, az: 555, el: 28 },
    { t: st(5) + 0.8, o: [28, 1.5, -5], d: 21, az: 430, el: 33 }, { t: st(5) + 4.0, o: [28, 1.5, -5], d: 19.5, az: 422, el: 32 },
    { t: st(6) + 0.8, o: [31, 2, -13], d: 22, az: 420, el: 36 }, { t: st(6) + 4.0, o: [62, 3, -7], d: 42, az: 440, el: 30 },
    { t: st(7) + 0.7, o: [24, 1.5, -2.5], d: 16, az: 335, el: 30 }, { t: st(7) + 3.6, o: [24, 1.5, -2.5], d: 15, az: 328, el: 29 },
    { t: B(56, 1), o: [40, 0, -4], d: 205, az: 380, el: 72 },
    { t: B(58), o: [36, 0, -6], d: 150, az: 390, el: 62 },
    { t: B(59), o: [20, 3, -12], d: 42, az: 392, el: 34 },
    { t: B(61, 3), o: [20, 3, -12], d: 40, az: 468, el: 32 },
    { t: B(63), o: [62, 2, -10], d: 92, az: 480, el: 30 },
    { t: B(65, 3), o: [66, 2, -12], d: 88, az: 532, el: 28 },
    { t: B(67), o: [38, 0, -2], d: 225, az: 545, el: 40 },
    { t: B(69, 3), o: [38, 0, -2], d: 215, az: 605, el: 36 },
    { t: B(71), o: [38, 4, -2], d: 128, az: 618, el: 20 },
    { t: B(73, 3), o: [38, 4, -2], d: 122, az: 672, el: 17 },
    { t: B(76), o: [38, 3, -2], d: 150, az: 700, el: 24 },
    { t: B(78), o: [38, 0, -190], d: 760, az: 712, el: 52 },
    { t: B(80), o: [-120, 0, -950], d: 3600, az: 716, el: 66 },
    { t: B(83, 2), o: [-300, 0, -2300], d: 9000, az: 718, el: 78 },
  ];
  camaraEn = rigCamara(claves);

  // ---- mapa: rutas, zonas y distancias
  const lotePol = [[-22, -40], [98, -40], [98, 36], [-22, 36]];
  const biogas = [[185, -150], [330, -150], [330, 150], [185, 150]];
  const rnMasCerca = M.rn12.flat().reduce((a, b) => (Math.hypot(b[0] - lx, b[1] - lz) < Math.hypot(a[0] - lx, a[1] - lz) ? b : a));
  for (const v of M.rn12) Tz(B(6), B(17, 2), v, { clase: "ruta-borde" }, 2.0);
  for (const v of M.rn12) Tz(B(6), B(17, 2), v, { clase: "ruta" }, 2.0);
  for (const v of M.pic) Tz(B(10), B(17), v, { clase: "pic", cerrado: true }, 0.01);
  Tz(B(2, 2), B(5, 2), [[parana[0], parana[1]], [lx, lz]], { clase: "dist" }, 2.0);
  Tz(B(13, 2), B(18, 1), lotePol, { clase: "lote", cerrado: true }, 0.01);
  Tz(B(14, 2), B(17, 2), biogas, { clase: "biogas", cerrado: true }, 0.01);
  Tz(B(15), B(17, 3), [[lx, lz], rnMasCerca], { clase: "dist" }, 0.8);
  Tz(B(15, 2), B(17, 3), [[lx, lz], crespo], { clase: "dist" }, 1.2);
  Tz(B(18), B(19, 2), lotePol, { clase: "replanteo", cerrado: true }, 0.01);
  Tz(B(78), B(83, 2), lotePol, { clase: "lote-borde", cerrado: true }, 0.01);
  C(B(78, 2), B(81), puntoSuelo([lx, lz]), "Secadora de guano", "lote propuesto junto al Parque Industrial", { dx: 90, dy: -70, clase: "grande" });

  // ---- carteles del mapa
  C(B(2), B(5, 3), puntoSuelo(parana), "Paraná", "capital de Entre Ríos", { dx: 80, dy: -60, clase: "azul" });
  C(B(2, 2), B(5, 3), () => puntoSuelo([(parana[0] + lx) / 2, (parana[1] + lz) / 2]), "36,6 km", "en línea recta (≈ 40 km por la RN 12)", { dx: 60, dy: 50, clase: "dist" });
  C(B(3), B(9), puntoSuelo(crespo), "Crespo", "Entre Ríos", { dx: -90, dy: 40, clase: "grande azul" });
  C(B(7), B(11), () => puntoSuelo(M.rn12[0][Math.floor(M.rn12[0].length / 2)]), "Ruta Nacional 12", "Paraná – Nogoyá", { dx: 90, dy: -50 });
  C(B(10), B(14, 2), puntoSuelo(pic), "Parque Industrial Crespo", "RN 12, km 40,6", { dx: -90, dy: 70, clase: "azul" });
  C(B(13, 2), B(17, 3), puntoSuelo([lx, lz]), "Lote propuesto", "120 × 76 m · 0,91 ha · frente al Parque Industrial", { dx: 90, dy: -80, clase: "grande" });
  C(B(14, 2), B(17, 2), puntoSuelo([258, 0]), "Planta de biogás vecina", "proyectada", { dx: 80, dy: 50, clase: "verde" });
  C(B(15), B(17, 3), () => puntoSuelo([(lx + rnMasCerca[0]) / 2, (lz + rnMasCerca[1]) / 2]), `${M.dist_rn12_m} m`, "a la RN 12", { dx: -70, dy: 60, clase: "dist" });
  C(B(15, 2), B(17, 3), () => puntoSuelo([(lx + crespo[0]) / 2, (lz + crespo[1]) / 2]), `${fmt(L["Crespo"].km, 1)} km`, "al centro de Crespo", { dx: 70, dy: 40, clase: "dist" });

  // ---- obra: la planta se arma
  obra("predio", B(18), 1.2 * P, "crecer");
  obra("terreno:solado", B(18, 1), P, "crecer"); obra("32", B(18, 1), 1.2 * P, "crecer"); obra("34", B(18, 2), P, "crecer");
  obra("33", B(18, 2), 2 * P, "subir"); obra("terreno:cerco", B(18, 2.5), 2 * P, "subir");
  obra("N:piso", B(19), 1.5 * P, "crecer"); obra("AN:piso", B(19, 1), 1.5 * P, "crecer"); obra("1", B(19, 2), P, "crecer");
  obra("N:estructura", B(20), 2 * P, "subir"); obra("AN:estructura", B(20, 1), 2 * P, "subir");
  const equipos = ["2", "3.8", "3.1", "3.2", "3.3", "3.4", "3.5", "3.6", "5", "6", "7", "8", "9", "10", "11", "12", "16",
    "14", "17", "18", "19", "21", "26", "22", "TGF", "29", "23", "24", "25", "28", "pilar", "30", "31"];
  equipos.forEach((c, i) => obra(c, B(25) + i * P / 3, 1.3 * P, "caer", 16));
  obra("N:paredes", B(28), 2 * P, "subir"); obra("AN:paredes", B(28, 1), 2 * P, "subir");
  obra("N:techo", B(29), 2 * P, "caer", 12); obra("AN:techo", B(29, 1), 2 * P, "caer", 12);
  ["13", "15", "20", "27"].forEach((c, i) => obra(c, B(30) + i * P / 2, 1.4 * P, "caer", 26));
  const dItems = Object.keys(grupos).filter((c) => /^D\d+$/.test(c));
  dItems.forEach((c, i) => obra(c, B(30, 2) + i * P / 6, P, "pop"));
  ["E9", "E7", "E8.1", "E8.2", "E8.3", "E8.4", "E8.5", "E8.6", "E1", "E2", "E3", "E4", "E5", "E6", "E10"]
    .forEach((c, i) => obra(c, B(31) + i * P / 3, 1.3 * P, "caer", 18));
  obra("terreno:arboles", B(32, 2), 2 * P, "subir");
  ["AU1", "AU2", "AU3"].forEach((c, i) => obra(c, B(32) + i * P / 2, P, "pop"));

  // ---- vehículos
  {
    // tiempo del visor: llegada a la báscula al final de la obra, maniobra de descarga acelerada en la parada
    // «Recepción» y después tiempo real (despacho, soplado de cáscara, pala cargando la tolva)
    const m = D.trafico.marcas, v0 = m.rev0 + 16, k = 2.2, v2 = v0 + k * (st(2) - st(0));
    TV = (t) => {
      if (t < B(32)) return -1;
      if (t < B(34)) return m.rev0 - 26 + (t - B(32));
      if (t < st(0)) return v0;
      if (t < st(2)) return v0 + k * (t - st(0));
      return v2 + (t - st(2));
    };
  }

  // ---- carteles de la obra
  C(B(20, 1), B(21, 3), topeDe("N:estructura", 1), "Nave industrial", "33 × 18 m · estructura metálica", { dx: 90, dy: -70 });
  C(B(23), B(25, 2), () => secador.raiz.position.clone().add(new THREE.Vector3(6.5, 4.6, -1.3)), "Secador de cinta SC-4",
    "3 pisos · 13,0 × 2,6 × 3,4 m · 9.538 kg", { dx: 90, dy: -80, clase: "grande" });
  C(B(25, 0.7), B(26, 3), topeDe("2", 0.3), "Tolva de recepción", "3,1 m³", { dx: -80, dy: -60 });
  C(B(27), B(28, 3), topeDe("9", 0.3), "Hogar a cáscara de arroz", "generador de aire caliente de 880 kW", { dx: 90, dy: -60 });
  C(B(30, 1), B(31, 3), topeDe("13", 0.3), "Silo de cáscara de arroz", "70 m³", { dx: 90, dy: -40 });
  C(B(30, 2), B(31, 3), topeDe("19", 0.3), "Lavador de gases", "y ciclón separador", { dx: -90, dy: -40 });
  C(B(31, 2), B(32, 3), topeDe("E8.2", 0.3), "Biogás con cogeneración", "25 kWe · ampliación Sector Este", { dx: 80, dy: -60, clase: "verde" });

  // ---- secador: despiece con carteles
  const pzs = secador.piezas;
  const anc = (id, dy = 0) => () => { const p = pzs[id]; return p ? p.obj.getWorldPosition(new THREE.Vector3()).add(new THREE.Vector3(0, dy, 0)) : new THREE.Vector3(); };
  const desp = [
    ["P000", "Estructura UPN 120 / IPN 140", "acero F-24 · 10 columnas", 70, -80, 1.6],
    ["P012", "Bandas de malla AISI 304", "3 pisos · 2,0 m de ancho", -90, -70, 0],
    ["P013", "Tambor motriz Ø300", "eje SAE 1045 verificado a fatiga", 90, -60, 0],
    ["P025", "Motorreductor 0,75 kW", "reductor sinfín-corona 1:300 · variador", 90, 50, 0],
    ["P023", "Transmisión ASA 60", "con cárter protector", -90, 60, 0],
    ["P005", "Paneles sándwich 80 mm", "aislación térmica", -100, 40, 0],
    ["P064", "Pasarela superior", "con baranda y escalera", 90, -60, 0.6],
    ["P060", "Campana de salida de aire", "800 × 800 mm", -90, -60, 0.3],
    ["P003", "Placas base y anclajes", "40 anclajes químicos M16", 80, 60, 0],
  ];
  desp.forEach(([id, a, b, dx, dy, ddy], i) => C(B(36) + i * P / 2, B(39, 2), anc(id, ddy), a, b, { dx, dy }));

  // ---- recorrido del proceso
  const PROCESO = [
    ["Recepción", "El camión descarga el guano húmedo (≈ 72 % de humedad) en la playa y la pala lo carga en la tolva.", [["2", "Tolva de recepción", -80, -50]]],
    ["Alimentación", "Una cinta con tacos sube el guano hasta el esparcidor, que lo reparte en una capa pareja sobre la banda.", [["3.1", "Cinta de alimentación", 80, -60]]],
    ["Secado en 3 pisos", "Tres bandas de malla de acero inoxidable lo llevan piso por piso mientras el aire caliente las atraviesa.", []],
    ["Aire caliente", "Un hogar a cáscara de arroz de 880 kW calienta el aire en un intercambiador: los humos no tocan el producto.", [["13", "Silo de cáscara", 80, -40], ["10", "Intercambiador humos-aire", -90, -60]]],
    ["Tratamiento de gases", "El aire húmedo pasa por un ciclón y por un lavador de gases antes de salir por la chimenea.", [["18", "Ciclón", 80, -60], ["19", "Lavador de gases", -80, -40]]],
    ["Descarga y acopio", "El producto seco (≈ 15 % de humedad) baja por un sinfín y sube por un elevador de cangilones al acopio.", [["6", "Sinfín de descarga", -90, -60], ["8", "Acopio de producto seco", 80, -40]]],
    ["Embolsado y expedición", "Una zaranda separa cáscaras y plumas; se embolsa en 25 kg y en bolsas chicas para viveros.", [["E5", "Ensacadora 25 kg", -80, -60], ["E7", "Depósito de expedición", 80, -60]]],
    ["Control", "Desde la sala de control se manejan los variadores, las temperaturas y las alarmas de toda la planta.", [["22", "Sala de control (TGF)", 80, -60]]],
  ];
  PROCESO.forEach(([tit, txt, cs], i) => {
    const t0 = st(i), t1 = st(i + 1) - 0.15;
    PLACAS.push([t0 + 0.2, t1, tit, txt, `${i + 1}/8`]);
    cs.forEach(([c, nom, dx, dy]) => C(t0 + 0.8, t1 - 0.2, topeDe(c, 0.3), nom, "", { dx, dy }));
  });
  C(st(2) + 0.8, st(3) - 0.35, () => secador.raiz.position.clone().add(new THREE.Vector3(6.5, 3.6, -1.3)), "Secador SC-4", "bandas a 6,2 mm/s (tambor a 0,37 rpm)", { dx: 90, dy: -70 });

  // ---- segundo estribillo: seguridad, ampliación e ingeniería
  PLACAS.push([B(58, 2), B(62), "Seguridad y mantenimiento", "Pasarelas y barandas, paradas de emergencia, protecciones de transmisiones, incendio y puesta a tierra.", ""]);
  C(B(59), B(61, 3), new THREE.Vector3(18, 4.7, -9.3), "Pasarelas y barandas", "acceso seguro al secador", { dx: 90, dy: -70 });
  C(B(59, 2), B(61, 3), new THREE.Vector3(14, 1.6, -7.2), "Paradas de emergencia", "tipo hongo", { dx: -90, dy: 50 });
  C(B(60), B(61, 3), topeDe("27", 0.3), "Agua contra incendio", "tanque de reserva y matafuegos", { dx: 80, dy: -50 });
  C(B(60, 2), B(61, 3), new THREE.Vector3(21.5, 12.8, -23.5), "Pararrayos y puesta a tierra", "anillo de Cu 50 mm² y jabalinas", { dx: -90, dy: -40 });
  PLACAS.push([B(62, 2), B(66), "Ampliación: Sector Este", "Lavado de vehículos, biofiltro en la recepción, embolsado, depósito de expedición y biogás con cogeneración.", ""]);
  C(B(63), B(65, 3), topeDe("E7", 0.3), "Depósito de expedición", "producto embolsado", { dx: -80, dy: -60 });
  C(B(63, 2), B(65, 3), topeDe("E8.2", 0.3), "Biodigestores y cogeneración", "25 kWe con el biogás del guano", { dx: 80, dy: -60, clase: "verde" });
  C(B(64), B(65, 3), topeDe("E1", 0.3), "Lavado y desinfección", "de camiones y personal", { dx: -80, dy: 50 });
  C(B(64, 2), B(65, 3), topeDe("E3", 0.3), "Biofiltro", "ventilación de la recepción", { dx: 80, dy: 50, clase: "verde" });
  cifras([
    { t0: B(66, 2), t1: B(70), valor: 880, suf: " kW", sub: "generador de aire caliente a cáscara de arroz (314 kg/h)" },
    { t0: B(67, 1), t1: B(70), valor: 117.0, dec: 1, suf: " kW", sub: "potencia instalada: TGF 66,9 kW + TG2 50,1 kW" },
    { t0: B(68), t1: B(70), texto: (k) => `n = ${fmt(1.59 * k, 2)}`, sub: "eje motriz del secador verificado a fatiga" },
    { t0: B(68, 3), t1: B(70), valor: 40, sub: "anclajes químicos M16 fijan el secador a la platea" },
  ]);
  PLACAS.push([B(70, 2), B(73, 3), "Planta de secado de guano · 8 t/día", "Crespo, Entre Ríos · Proyecto final 7.° año · Técnico Electromecánico · 2026", ""]);

  // ---- foco: se retira lo que tapa la cámara
  VENTANAS_FOCO.push({ claves: FOCO, t0: B(34), t1: B(42) });
  VENTANAS_FOCO.push({ claves: ["terreno:arboles"], t0: st(3) - 0.5, t1: st(5) + 0.5 });

  // ---- textos fijos
  $("#grandes").innerHTML = `<div class="g"><b>8 t/día</b><span>de guano húmedo (≈ 72 %)</span></div>
    <div class="flecha">→</div><div class="g"><b>2,6 t/día</b><span>de abono seco (≈ 15 %)</span></div>`;
  $("#creditos").innerHTML = `<div class="sobre">Proyecto final · 2026</div>
    <div class="nombres">Gabriel Müller · Pablo Hofstetter · Baltazar Goette<br>Facundo Stegmann · Martín Bernhardt · Bautista Belluzzo</div>
    <div class="esc">E.P.N.M. y S. N° 35 Técnica «Gral. Don José de San Martín»<br>Crespo, Entre Ríos · Técnico Electromecánico</div>`;
  $("#pie-izq").textContent = "Ubicación del lote y de la planta de biogás: orientativa, a confirmar con la Municipalidad de Crespo.";
  $("#pie-der").textContent = M.creditos;

  // ---- materiales de vidrio para el corte (quedan transparentes desde el principio para no cambiar de lista)
  // la nave se ve maciza al terminar la obra (en el visor es translúcida) y se vuelve transparente en los interiores
  for (const c of ["N:techo", "N:paredes", "AN:techo", "AN:paredes"]) for (const m of grupos[c]?.mats || []) m.userData.opBase = 1;
}
const PLACAS = [];

// ------------------------------------------------------------------ luces de noche
let lucesNoche = [];
function prepararNoche() {
  // las luces se agregan a la escena recién al anochecer: aun apagadas encarecen cada píxel
  for (const [x, y, z] of [[10, 6, -9], [26, 6, -9], [70, 6, -6], [6, 6, 20]]) {
    const l = new THREE.PointLight(0xffd29a, 0, 70, 1.6); l.position.set(x, y, z); lucesNoche.push(l);
  }
}

// ------------------------------------------------------------------ cuadro
export function cuadro(t) {
  // ambiente: día -> atardecer -> noche
  const kAmb = 1 * suave(tramo(t, B(69), B(72))) + 1 * suave(tramo(t, B(74), B(76)));
  const amb = ambiente(kAmb);
  for (const l of lucesNoche) {
    l.intensity = 900 * amb.noche;
    if (amb.noche > 0.01 && !l.parent) escena.add(l); else if (amb.noche <= 0.01 && l.parent) escena.remove(l);
  }
  for (const c of ["D17"]) for (const m of grupos[c]?.mats || []) { m.emissive.setHex(0xffe0a8); m.emissiveIntensity = 2.2 * amb.noche; }

  ponerCamara(camaraEn(t));
  aplicarObra(t);
  aplicarSecador(t);
  aplicarVehiculos(t);
  foco(t);
  corte(suave(tramo(t, B(34), B(34, 2))) * (1 - suave(tramo(t, B(61, 2), B(62, 2)))),
    suave(tramo(t, B(34), B(34, 2))) * (1 - suave(tramo(t, B(41, 2), B(42)))));
  for (const g of Object.values(grupos)) for (const m of g.mats) if (m.emissive && !g.obj.name.startsWith("D17")) m.emissiveIntensity = 0;
  resaltar(["D3"], t, B(59), B(61, 3)); resaltar(["D4"], t, B(59, 2), B(61, 3)); resaltar(["27", "D19"], t, B(60), B(61, 3));
  resaltar(["D16"], t, B(60, 2), B(61, 3)); resaltar(["E8.2", "E8.3"], t, B(63, 2), B(65, 3), 0x6cc28a);
  resaltar(["E3"], t, B(64, 2), B(65, 3), 0x6cc28a);

  // trazos y carteles
  for (const { T, t0, t1, dibujo } of TRAZOS) { T.op = ventana(t, t0, t1, 0.5); T.prog = salida(tramo(t, t0, t0 + dibujo)); }
  for (const { c, t0, t1, ancla } of CARTELES) {
    c.op = ventana(t, t0, t1, 0.35);
    if (c.op > 0) c.pos.copy(typeof ancla === "function" ? ancla() : ancla);
  }

  // textos
  titulo(t, 0.7, B(2, 2), "Proyecto final · E.P.N.M. y S. N° 35 · Crespo", "Secadora de guano de gallina",
    "Planta de secado de 8 t/día con energía de cáscara de arroz");
  if (t > B(18) - 1 && t < B(20)) titulo(t, B(18), B(19, 3), "La obra", "Así se arma la planta", "120 × 76 m junto al Parque Industrial de Crespo");
  if (t > B(80)) titulo(t, B(81), B(83, 2), "Crespo · Entre Ríos", "Secadora de guano de gallina", "Proyecto final 2026 · Técnico Electromecánico");
  placaActiva = null;
  for (const [t0, t1, a, b, p] of PLACAS) placa(t, t0, t1, a, b, p);
  placa(t, B(40, 2), B(41, 3), "Secador de cinta SC-4", "13,0 × 2,6 × 3,4 m · 9.538 kg · 3 bandas de 2,0 m · motorreductores de 0,75 kW", "");
  mostrarPlaca();
  mostrarCifras(t);
  $("#grandes").style.opacity = ventana(t, B(56), B(57, 3), 0.35);
  $("#grandes").style.transform = `scale(${1 + 0.04 * tramo(t, B(56), B(58))})`;
  $("#creditos").style.opacity = ventana(t, B(76), B(80, 2), 0.8);
  $("#pie").style.opacity = Math.max(ventana(t, B(2), B(17, 3), 0.6), ventana(t, B(77), B(83), 0.6));
  $("#pie-izq").style.visibility = t < B(30) ? "visible" : "hidden";
  $("#marca").style.opacity = ventana(t, B(18, 2), B(74), 0.8);
  $("#blanco").style.opacity = 0.85 * (1 - salida(tramo(t, B(18), B(18) + 0.45))) * (t >= B(18) ? 1 : 0)
    + 0.9 * (1 - salida(tramo(t, B(58), B(58) + 0.5))) * (t >= B(58) ? 1 : 0);
  $("#negro").style.opacity = Math.max(1 - suave(tramo(t, 0, 1.4)), suave(tramo(t, B(83, 1), B(83, 3.2))));

  dibujar();
}

// ------------------------------------------------------------------ arranque
// vista libre para revisar encuadres: __vista(t, [ox, oy, oz], distancia, azimut, elevación)
window.__vista = (t, o, d, az, el) => {
  const rig = rigCamara([{ t: 0, o, d, az, el }, { t: 1, o, d, az, el }]);
  const orig = camaraEn; camaraEn = () => rig(0); cuadro(t); camaraEn = orig;
};
window.__listo = (async () => {
  await iniciar();
  preparar();
  prepararNoche();
  window.__T_FIN = B(83, 3.4);
  window.__cuadro = (t) => cuadro(t);
  cuadro(+(PARAM.t || 0));
  return true;
})().catch((e) => { document.body.dataset.error = String(e && e.stack || e); console.error(e); throw e; });
