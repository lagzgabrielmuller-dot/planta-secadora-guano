// Motor de la escena del video: three.js, mapa satelital en niveles, planta por bloques, secador SC-4 detallado,
// carteles con línea guía y placas de texto. Todo depende solo del tiempo t (cuadro por cuadro, sin reloj real).
// Ejes (los del visor): x al Este, y arriba, z al Sur, en metros; origen en el vértice SO de la nave.
import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";
import { mergeGeometries } from "three/addons/utils/BufferGeometryUtils.js";

export const PARAM = Object.fromEntries(new URLSearchParams(location.search));
const ANCHO = +(PARAM.w || 1920), ALTO = +(PARAM.h || 1080);
const DIS_W = 1920, DIS_H = 1080;      // la capa de textos se diseña siempre a 1920 × 1080 (se escala si el cuadro es otro)

// ------------------------------------------------------------------ utilidades de tiempo
export const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const suave = (x) => { x = clamp(x); return x * x * (3 - 2 * x); };
export const suave5 = (x) => { x = clamp(x); return x * x * x * (x * (x * 6 - 15) + 10); };
export const salida = (x) => 1 - Math.pow(1 - clamp(x), 3);
export const rebote = (x) => { x = clamp(x); const c1 = 1.4, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); };
export const tramo = (t, t0, t1) => clamp((t - t0) / (t1 - t0));
/** opacidad de algo visible entre t0 y t1, con entrada y salida de duración f */
export const ventana = (t, t0, t1, f = 0.4) => Math.min(suave(tramo(t, t0, t0 + f)), 1 - suave(tramo(t, t1 - f, t1)));

// ------------------------------------------------------------------ renderizador y escena
export const lienzo = document.getElementById("lienzo");
// sin profundidad logarítmica: con el plano cercano proporcional a la distancia alcanza la precisión, y el
// descarte temprano de fragmentos (early-z) acelera mucho el dibujo por procesador
export const renderer = new THREE.WebGLRenderer({ canvas: lienzo, antialias: PARAM.aa !== "0", logarithmicDepthBuffer: PARAM.logz === "1",
  preserveDrawingBuffer: true, powerPreference: "high-performance" });
renderer.setPixelRatio(1);
renderer.setSize(ANCHO, ALTO, false);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;
renderer.shadowMap.enabled = PARAM.sombras !== "0";
renderer.shadowMap.type = PARAM.sombraSuave === "1" ? THREE.PCFSoftShadowMap : THREE.PCFShadowMap;
export const escena = new THREE.Scene();
export const camara = new THREE.PerspectiveCamera(40, ANCHO / ALTO, 0.2, 400000);
const pmrem = new THREE.PMREMGenerator(renderer);
// el mapa de entorno (reflejos) es lo más caro de dibujar por procesador: por defecto no se usa y se compensa con
// materiales menos metálicos, más luz ambiente y una luz de relleno sin sombras (?env=1 lo activa)
export const CON_ENTORNO = PARAM.env === "1";
if (CON_ENTORNO) escena.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
const METAL = CON_ENTORNO ? 1 : 0.25;
escena.environmentIntensity = 0.45;

// cielo: degradé vertical como fondo de pantalla, y niebla del mismo color abajo
const cieloCanvas = document.createElement("canvas"); cieloCanvas.width = 4; cieloCanvas.height = 256;
const cieloTex = new THREE.CanvasTexture(cieloCanvas); cieloTex.colorSpace = THREE.SRGBColorSpace;
escena.background = cieloTex;
escena.fog = new THREE.Fog(0xcfd9e2, 1000, 20000);
function pintarCielo(arriba, abajo) {
  const g = cieloCanvas.getContext("2d"), gr = g.createLinearGradient(0, 0, 0, 256);
  gr.addColorStop(0, arriba); gr.addColorStop(1, abajo);
  g.fillStyle = gr; g.fillRect(0, 0, 4, 256); cieloTex.needsUpdate = true;
}

// luces
export const hemi = new THREE.HemisphereLight(0xdfeaf5, 0x6d6450, 0.9);
escena.add(hemi);
export const sol = new THREE.DirectionalLight(0xfff1dc, 2.6);
sol.castShadow = true;
sol.shadow.mapSize.set(+(PARAM.sombra || 2048), +(PARAM.sombra || 2048));
sol.shadow.bias = -0.0004; sol.shadow.normalBias = 0.04;
const sc = sol.shadow.camera; sc.left = -95; sc.right = 95; sc.top = 95; sc.bottom = -95; sc.near = 10; sc.far = 600;
escena.add(sol, sol.target);
export const relleno = new THREE.DirectionalLight(0xdfe8f5, CON_ENTORNO ? 0 : 0.9);
escena.add(relleno, relleno.target);
const CENTRO_PREDIO = new THREE.Vector3(38, 0, -2);

/** ambiente: k = 0 día, 1 atardecer, 2 noche (interpolado) */
const AMB = [
  { cielo: ["#7fa6cc", "#d9e3ea"], niebla: 0xd3dde5, sol: 0xfff1dc, solI: 2.6, hemi: 0.9, elev: 52, azim: 215, exp: 1.0, suelo: 1.0, env: 0.45 },
  { cielo: ["#3d5684", "#f0a868"], niebla: 0xe9a876, sol: 0xff9850, solI: 3.1, hemi: 0.42, elev: 11, azim: 292, exp: 1.05, suelo: 0.78, env: 0.3 },
  { cielo: ["#060b16", "#1b2a40"], niebla: 0x101a28, sol: 0x8aa6d8, solI: 0.25, hemi: 0.16, elev: 40, azim: 160, exp: 1.15, suelo: 0.22, env: 0.08 },
];
const colA = new THREE.Color(), colB = new THREE.Color();
const mezclaHex = (a, b, k) => colA.set(a).lerp(colB.set(b), k).getHex();
const mezclaCss = (a, b, k) => "#" + colA.set(a).lerp(colB.set(b), k).getHexString();
export const materialesSuelo = [];
export function ambiente(k) {
  const i = Math.min(1, Math.floor(k)), f = k - i, a = AMB[i], b = AMB[Math.min(2, i + 1)];
  const L = (x, y) => x + (y - x) * f;
  escena.fog.color.setHex(mezclaHex(a.niebla, b.niebla, f));
  pintarCielo(mezclaCss(a.cielo[0], b.cielo[0], f), "#" + escena.fog.color.getHexString());
  sol.color.setHex(mezclaHex(a.sol, b.sol, f));
  sol.intensity = L(a.solI, b.solI);
  hemi.intensity = L(a.hemi, b.hemi);
  renderer.toneMappingExposure = L(a.exp, b.exp);
  escena.environmentIntensity = L(a.env, b.env);
  const el = THREE.MathUtils.degToRad(L(a.elev, b.elev)), az = THREE.MathUtils.degToRad(L(a.azim, b.azim));
  sol.position.set(CENTRO_PREDIO.x + 300 * Math.cos(el) * Math.sin(az), 300 * Math.sin(el), CENTRO_PREDIO.z + 300 * Math.cos(el) * Math.cos(az));
  sol.target.position.copy(CENTRO_PREDIO);
  relleno.position.set(CENTRO_PREDIO.x - 300 * Math.sin(az), 160, CENTRO_PREDIO.z - 300 * Math.cos(az));
  relleno.target.position.copy(CENTRO_PREDIO);
  relleno.intensity = CON_ENTORNO ? 0 : 0.9 * L(a.hemi, b.hemi) / 0.9;
  if (!CON_ENTORNO) hemi.intensity *= 1.35;
  const s = L(a.suelo, b.suelo);
  const calido = Math.min(1, k) * (1 - clamp(k - 1));      // tinte cálido del suelo al atardecer
  for (const m of materialesSuelo) m.color.setRGB(s * (1 + 0.10 * calido), s * (1 - 0.02 * calido), s * (1 - 0.14 * calido));
  hemi.color.setHex(mezclaHex(0xdfeaf5, 0xffd0a0, calido));
  return { noche: clamp(k - 1) };
}

// ------------------------------------------------------------------ carga de datos
const cargador = new THREE.TextureLoader();
const textura = (url) => new Promise((ok, mal) => cargador.load(url, (t) => { t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = renderer.capabilities.getMaxAnisotropy(); ok(t); }, undefined, mal));
const json = (url) => fetch(url).then((r) => r.json());
const binario = (url) => fetch(url).then((r) => r.arrayBuffer());

export const D = {};      // datos: mapa, planta, piezas del secador, ritmo

async function cargarMapa() {
  D.mapa = await json("datos/mapa.json");
  for (const [i, n] of D.mapa.niveles.entries()) {
    const tex = await textura(`datos/mapa_${n.nombre}.jpg`);
    const w = n.x1 - n.x0, d = n.zS - n.zN;
    const geo = new THREE.PlaneGeometry(w, d); geo.rotateX(-Math.PI / 2);
    // niveles opacos y escalonados: el más fino queda arriba y se dibuja primero, así tapa a los gruesos con el
    // descarte de profundidad (mucho más barato que mezclar cinco capas transparentes en toda la pantalla)
    const n_ = D.mapa.niveles.length;
    const mat = new THREE.MeshBasicMaterial({ map: tex });
    materialesSuelo.push(mat);
    const m = new THREE.Mesh(geo, mat);
    const y = [-12, -4, -1.2, -0.35, -0.02][i + (5 - n_)];
    m.position.set((n.x0 + n.x1) / 2, y, (n.zN + n.zS) / 2);
    m.renderOrder = -10 - i;
    escena.add(m);
  }
  // receptor de sombras alrededor del predio (el suelo satelital no recibe luz)
  const rec = new THREE.Mesh(new THREE.PlaneGeometry(420, 320).rotateX(-Math.PI / 2),
    new THREE.ShadowMaterial({ opacity: 0.38, depthWrite: false }));
  rec.position.set(CENTRO_PREDIO.x, 0.03, CENTRO_PREDIO.z); rec.receiveShadow = true; rec.renderOrder = -1;
  escena.add(rec);
}

function texturaRipio() {
  // ripio compactado: ruido de varias escalas sobre un gris pardo, con huellas suaves
  const N = 1024, c = document.createElement("canvas"); c.width = c.height = N;
  const g = c.getContext("2d"), img = g.createImageData(N, N);
  let sem = 7; const rnd = () => ((sem = (sem * 16807) % 2147483647) / 2147483647);
  const capa = (n) => { const a = new Float32Array(n * n); for (let i = 0; i < a.length; i++) a[i] = rnd(); return a; };
  const escalas = [[8, 0.35], [32, 0.25], [128, 0.2], [512, 0.2]].map(([n, w]) => [n, w, capa(n)]);
  for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) {
    let v = 0;
    for (const [n, w, a] of escalas) {
      const fx = x / N * n, fy = y / N * n, ix = Math.floor(fx) % n, iy = Math.floor(fy) % n, jx = (ix + 1) % n, jy = (iy + 1) % n;
      const u = fx - Math.floor(fx), t = fy - Math.floor(fy);
      v += w * ((a[iy * n + ix] * (1 - u) + a[iy * n + jx] * u) * (1 - t) + (a[jy * n + ix] * (1 - u) + a[jy * n + jx] * u) * t);
    }
    const k = 0.78 + 0.32 * v, i = (y * N + x) * 4;
    img.data[i] = 128 * k; img.data[i + 1] = 121 * k; img.data[i + 2] = 106 * k; img.data[i + 3] = 255;
  }
  g.putImageData(img, 0, 0);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.repeat.set(3, 2); t.anisotropy = 8;
  return t;
}

// ------------------------------------------------------------------ planta por bloques
export const grupos = {};   // clave "pieza" o "pieza:grupo" -> { obj, mats, caja, ... }
const metalico = (c) => { const r = (c >> 16) & 255, g = (c >> 8) & 255, b = c & 255;
  return Math.max(r, g, b) - Math.min(r, g, b) < 18 && r > 90 && r < 215; };

async function cargarPlanta() {
  D.planta = await json("datos/planta.json");
  const buf = new Float32Array(await binario("datos/planta.bin"));
  const bufCol = new Uint8Array(await binario("datos/planta_col.bin"));
  const porClave = {};
  for (const b of D.planta.bloques) {
    const clave = ["N", "AN", "terreno"].includes(b.pieza) ? `${b.pieza}:${b.grupo}` : b.pieza;
    (porClave[clave] ||= []).push(b);
  }
  for (const [clave, bloques] of Object.entries(porClave)) {
    const lo = new THREE.Vector3(1e9, 1e9, 1e9), hi = new THREE.Vector3(-1e9, -1e9, -1e9);
    for (const b of bloques) { lo.min(new THREE.Vector3(...b.min)); hi.max(new THREE.Vector3(...b.max)); }
    const pivote = new THREE.Vector3((lo.x + hi.x) / 2, lo.y, (lo.z + hi.z) / 2);
    const obj = new THREE.Group(); obj.position.copy(pivote); obj.name = clave;
    const mats = [];
    for (const b of bloques) {
      const geo = new THREE.BufferGeometry();
      const pos = buf.slice(b.ofs, b.ofs + b.n);
      for (let i = 0; i < pos.length; i += 3) { pos[i] -= pivote.x; pos[i + 1] -= pivote.y; pos[i + 2] -= pivote.z; }
      geo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
      const vc = b.vc_ofs !== undefined;
      if (vc) geo.setAttribute("color", new THREE.BufferAttribute(bufCol.slice(b.vc_ofs, b.vc_ofs + b.n), 3, true));
      geo.computeVertexNormals();
      const veh = b.grupo === "vehiculo";
      const met = !vc && metalico(b.c);
      const mat = new THREE.MeshStandardMaterial({ color: b.c, vertexColors: vc, roughness: met ? 0.45 : 0.78,
        metalness: (met ? 0.55 : 0.05) * METAL, transparent: b.op < 1, opacity: b.op, side: THREE.DoubleSide,
        emissive: 0x000000 });
      mat.userData.opBase = b.op;
      const m = new THREE.Mesh(geo, mat);
      m.castShadow = b.op >= 0.99 && !(b.grupo === "solado"); m.receiveShadow = true;
      if (veh) m.castShadow = true;
      obj.add(m); mats.push(mat);
    }
    escena.add(obj);
    grupos[clave] = { obj, mats, lo, hi, pivote, alto: hi.y - lo.y, centro: new THREE.Vector3().addVectors(lo, hi).multiplyScalar(0.5) };
  }
  // placa del predio nivelado (aparece al empezar la obra)
  const pl = new THREE.Mesh(new THREE.PlaneGeometry(120, 76).rotateX(-Math.PI / 2),
    new THREE.MeshStandardMaterial({ map: texturaRipio(), color: 0xffffff, roughness: 0.97, metalness: 0 }));
  pl.receiveShadow = true;
  const predio = new THREE.Group(); predio.position.set(38, 0.04, -2); predio.add(pl); escena.add(predio);
  grupos.predio = { obj: predio, mats: [pl.material], alto: 0.1, centro: new THREE.Vector3(38, 0, -2) };
}

// ------------------------------------------------------------------ secador SC-4 detallado (CadQuery)
export const secador = { raiz: new THREE.Group(), piezas: {} };
const OFFSET_SECADOR = new THREE.Vector3(11.5, 0, -8.0);
const mmV = (v) => new THREE.Vector3(v[0] / 1000, v[2] / 1000, -v[1] / 1000);

function materialSecador(d) {
  const c = new THREE.Color(...d.color);
  const inox = /AISI|inox|malla|Banda/i.test(d.nombre + d.material);
  const panel = /^4\.8/.test(d.cod);
  return new THREE.MeshStandardMaterial({ color: c, roughness: inox ? 0.35 : panel ? 0.6 : 0.5,
    metalness: (inox ? 0.75 : panel ? 0.1 : 0.45) * METAL, side: THREE.DoubleSide, transparent: false });
}

async function cargarSecador() {
  D.piezas = (await json("datos/secador_piezas.json")).piezas;
  const gltf = await new Promise((ok, mal) => new GLTFLoader().load("datos/Secador_SC4.glb", ok, undefined, mal));
  const porId = {};
  gltf.scene.updateMatrixWorld(true);
  gltf.scene.traverse((o) => {
    if (!o.isMesh) return;
    let n = o; while (n && !/^P\d{3}/.test(n.name)) n = n.parent;
    if (!n) return;
    const g = o.geometry.clone().applyMatrix4(o.matrixWorld);
    for (const k of Object.keys(g.attributes)) if (k !== "position" && k !== "normal") g.deleteAttribute(k);
    (porId[n.name.slice(0, 4)] ||= []).push(g.index ? g.toNonIndexed() : g);
  });
  secador.raiz.position.copy(OFFSET_SECADOR);
  escena.add(secador.raiz);
  for (const d of D.piezas) {
    const lista = porId[d.id]; if (!lista) continue;
    const geo = mergeGeometries(lista, false);
    geo.computeBoundingBox();
    const c = geo.boundingBox.getCenter(new THREE.Vector3());
    geo.translate(-c.x, -c.y, -c.z);
    const mat = materialSecador(d);
    const m = new THREE.Mesh(geo, mat); m.castShadow = m.receiveShadow = true;
    const obj = new THREE.Group(); obj.add(m); obj.position.copy(c);
    secador.raiz.add(obj);
    secador.piezas[d.id] = { d, obj, mat, base: c.clone(), expl: mmV(d.explosion_mm), grupo: d.grupo };
  }
}

// ------------------------------------------------------------------ capa de textos (HTML) y carteles 3D
export const capa = document.getElementById("capa");
const svg = document.getElementById("guias");
const carteles = [];
/** cartel anclado a un punto 3D, con línea guía. dx, dy: desplazamiento de la caja en px */
export function cartel(id, titulo, sub = "", { dx = 70, dy = -70, clase = "" } = {}) {
  const el = document.createElement("div"); el.className = "cartel " + clase;
  el.innerHTML = `<b>${titulo}</b>${sub ? `<span>${sub}</span>` : ""}`;
  capa.appendChild(el);
  const ln = document.createElementNS("http://www.w3.org/2000/svg", "polyline"); svg.appendChild(ln);
  const pt = document.createElementNS("http://www.w3.org/2000/svg", "circle"); pt.setAttribute("r", 4); svg.appendChild(pt);
  const c = { id, el, ln, pt, dx, dy, op: 0, pos: new THREE.Vector3() };
  carteles.push(c);
  return c;
}
const vtmp = new THREE.Vector3();
function ubicarCarteles() {
  const vis = [];
  for (const c of carteles) {
    const v = c.op > 0.01;
    c.el.style.display = v ? "" : "none"; c.ln.style.display = c.pt.style.display = v ? "" : "none";
    if (!v) continue;
    vtmp.copy(c.pos).project(camara);
    if (vtmp.z > 1) { c.el.style.display = "none"; c.ln.style.display = c.pt.style.display = "none"; continue; }
    c.x = (vtmp.x * 0.5 + 0.5) * DIS_W; c.y = (-vtmp.y * 0.5 + 0.5) * DIS_H;
    c.w = c.el.offsetWidth; c.h = c.el.offsetHeight;
    c.bx = c.x + c.dx; c.by = c.y + c.dy;
    c.izq = c.dx < 0 ? c.bx - c.w : c.bx;
    vis.push(c);
  }
  // que no se pisen: de arriba hacia abajo, cada caja baja lo necesario para no tocar a las de arriba
  vis.sort((a, b) => a.by - b.by);
  for (let i = 0; i < vis.length; i++) {
    const a = vis[i];
    for (let k = 0; k < 3; k++) for (let j = 0; j < i; j++) {
      const b = vis[j];
      const solapX = a.izq < b.izq + b.w + 10 && b.izq < a.izq + a.w + 10;
      const solapY = Math.abs(a.by - b.by) < (a.h + b.h) / 2 + 8;
      if (solapX && solapY) a.by = b.by + (a.h + b.h) / 2 + 8;
    }
    a.by = Math.min(DIS_H - a.h / 2 - 20, Math.max(a.h / 2 + 20, a.by));
  }
  for (const c of vis) {
    c.el.style.opacity = c.op; c.ln.style.opacity = c.pt.style.opacity = c.op;
    c.el.style.transform = `translate(${c.bx.toFixed(1)}px, ${c.by.toFixed(1)}px) translate(${c.dx < 0 ? "-100%" : "0"}, -50%)`;
    const codo = c.bx - Math.sign(c.dx) * 12;
    c.ln.setAttribute("points", `${c.x.toFixed(1)},${c.y.toFixed(1)} ${codo.toFixed(1)},${c.by.toFixed(1)} ${c.bx.toFixed(1)},${c.by.toFixed(1)}`);
    c.pt.setAttribute("cx", c.x.toFixed(1)); c.pt.setAttribute("cy", c.y.toFixed(1));
  }
}

// ------------------------------------------------------------------ trazos del mapa en pantalla (SVG): rutas, distancias, zonas
const NS = "http://www.w3.org/2000/svg";
const svgTrazos = document.getElementById("trazos");
const trazos = [];
/** puntos [[x, z], ...] sobre el suelo; prog (0-1) recorta el trazo para dibujarlo de a poco */
export function trazo(puntos, { clase = "ruta", cerrado = false, y = 0.5 } = {}) {
  const el = document.createElementNS(NS, cerrado ? "polygon" : "polyline");
  el.setAttribute("class", clase); svgTrazos.appendChild(el);
  const p3 = puntos.map(([x, z]) => new THREE.Vector3(x, y, z));
  const acum = [0];
  for (let i = 1; i < p3.length; i++) acum.push(acum[i - 1] + p3[i].distanceTo(p3[i - 1]));
  const T = { el, p3, acum, total: acum[acum.length - 1], prog: 1, op: 0, cerrado };
  trazos.push(T);
  return T;
}
function ubicarTrazos() {
  for (const T of trazos) {
    if (T.op <= 0.01) { T.el.style.display = "none"; continue; }
    T.el.style.display = ""; T.el.style.opacity = T.op;
    const lim = T.total * clamp(T.prog);
    const pts = [];
    for (let i = 0; i < T.p3.length; i++) {
      let q = T.p3[i];
      if (!T.cerrado && T.acum[i] > lim) {
        const a = T.p3[i - 1], f = (lim - T.acum[i - 1]) / (T.acum[i] - T.acum[i - 1]);
        q = a.clone().lerp(q, f);
      }
      vtmp.copy(q).project(camara);
      if (vtmp.z > 1) continue;
      pts.push(`${((vtmp.x * 0.5 + 0.5) * DIS_W).toFixed(1)},${((-vtmp.y * 0.5 + 0.5) * DIS_H).toFixed(1)}`);
      if (!T.cerrado && T.acum[i] > lim) break;
    }
    T.el.setAttribute("points", pts.join(" "));
  }
}

// ------------------------------------------------------------------ cámara: rig esférico con claves en el tiempo
// clave: { t, o: [x,y,z] objetivo, d: distancia, az: azimut (°, 0 = cámara al Sur mirando al Norte), el: elevación (°), fov }
function hermite(ts, vs, t) {
  const n = ts.length;
  if (t <= ts[0]) return vs[0];
  if (t >= ts[n - 1]) return vs[n - 1];
  let i = 0; while (ts[i + 1] < t) i++;
  const t0 = ts[i], t1 = ts[i + 1], h = t1 - t0, u = (t - t0) / h;
  const m = (k) => {
    if (k === 0 || k === n - 1) return 0;          // arranca y frena en las claves de los extremos
    return (vs[k + 1] - vs[k - 1]) / (ts[k + 1] - ts[k - 1]);
  };
  const m0 = m(i) * h, m1 = m(i + 1) * h;
  const u2 = u * u, u3 = u2 * u;
  return (2 * u3 - 3 * u2 + 1) * vs[i] + (u3 - 2 * u2 + u) * m0 + (-2 * u3 + 3 * u2) * vs[i + 1] + (u3 - u2) * m1;
}
export function rigCamara(claves) {
  const ts = claves.map((c) => c.t);
  const canal = (f) => claves.map(f);
  const ox = canal((c) => c.o[0]), oy = canal((c) => c.o[1]), oz = canal((c) => c.o[2]);
  const ld = canal((c) => Math.log(c.d)), az = canal((c) => c.az), el = canal((c) => c.el), fov = canal((c) => c.fov ?? 40);
  return (t) => {
    const o = new THREE.Vector3(hermite(ts, ox, t), hermite(ts, oy, t), hermite(ts, oz, t));
    const d = Math.exp(hermite(ts, ld, t)), a = THREE.MathUtils.degToRad(hermite(ts, az, t));
    const e = THREE.MathUtils.degToRad(hermite(ts, el, t));
    const p = new THREE.Vector3(o.x + d * Math.cos(e) * Math.sin(a), o.y + d * Math.sin(e), o.z + d * Math.cos(e) * Math.cos(a));
    return { o, p, d, fov: hermite(ts, fov, t) };
  };
}
export function ponerCamara({ o, p, d, fov }) {
  camara.position.copy(p); camara.lookAt(o);
  camara.fov = fov;
  camara.near = Math.max(0.15, d * 0.004); camara.far = Math.max(60000, d * 40);
  camara.updateProjectionMatrix();
  camara.updateMatrixWorld(true);          // los carteles y trazos se proyectan antes de dibujar
  const alt = Math.max(5, p.y);
  escena.fog.near = Math.max(600, alt * 2.5 + d * 1.2);
  escena.fog.far = escena.fog.near + Math.max(9000, alt * 10);
  sol.castShadow = renderer.shadowMap.enabled && d < 900;
}

// ------------------------------------------------------------------ arranque y cuadro
export async function iniciar() {
  D.ritmo = await json("datos/ritmo.json");
  D.trafico = await json("datos/trafico.json");
  await Promise.all([cargarMapa(), cargarPlanta(), cargarSecador()]);
  await document.fonts.ready;
}
export function dibujar() {
  ubicarTrazos();
  ubicarCarteles();
  renderer.render(escena, camara);
}
