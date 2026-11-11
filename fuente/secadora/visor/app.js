// Visor 3D del secador SC-4 (entregable aparte de la secadora).
// Basado en la plantilla de la skill visor-3d-interactivo del kit (cámara orbital, capas, vistas,
// etiquetas, datos al hacer clic) con: despiece animado, montaje paso a paso, lista de piezas,
// corte del cerramiento y animación de las bandas. Se empaqueta con build.mjs en un solo HTML
// (three.js, el modelo GLB y los datos van adentro) para abrirlo con doble clic, sin internet.
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { CSS2DRenderer, CSS2DObject } from "three/addons/renderers/CSS2DRenderer.js";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";
import { RenderPass } from "three/addons/postprocessing/RenderPass.js";
import { GTAOPass } from "three/addons/postprocessing/GTAOPass.js";
import { OutputPass } from "three/addons/postprocessing/OutputPass.js";

const DATOS = window.__PIEZAS;          // piezas.json del modelo CadQuery
const PASOS = window.__PASOS;           // montaje paso a paso (manual de armado)

// ------------------------------------------------------------------ escena
const contenedor = document.getElementById("lienzo");
const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 0.92;
contenedor.appendChild(renderer.domElement);
const rotulos = new CSS2DRenderer();
rotulos.setSize(innerWidth, innerHeight);
Object.assign(rotulos.domElement.style, { position: "fixed", inset: "0", pointerEvents: "none" });
document.body.appendChild(rotulos.domElement);

const escena = new THREE.Scene();
escena.background = new THREE.Color(0xdde4ec);
escena.fog = new THREE.Fog(0xdde4ec, 60, 160);
const camara = new THREE.PerspectiveCamera(42, innerWidth / innerHeight, 0.05, 500);
const controles = new OrbitControls(camara, renderer.domElement);
controles.enableDamping = true;
escena.add(new THREE.HemisphereLight(0xffffff, 0x6d7a89, 0.55));
const sol = new THREE.DirectionalLight(0xfff6ea, 2.0);
sol.castShadow = true;
sol.shadow.mapSize.set(4096, 4096);
sol.shadow.bias = -0.0004;
sol.shadow.normalBias = 0.015;
sol.shadow.radius = 3;
escena.add(sol);
// entorno (reflejos de los metales: sin esto el acero inoxidable y el galvanizado se ven negros)
const pmrem = new THREE.PMREMGenerator(renderer);
escena.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
escena.environmentIntensity = 0.4;
const relleno = new THREE.DirectionalLight(0xdfe8ff, 0.35);
relleno.position.set(-20, 8, 15);
escena.add(relleno);

// calidad alta: oclusión ambiental (GTAO) y antialiasing multimuestra en la composición; en celulares y equipos
// chicos arranca en calidad normal (dibujo directo), y el botón «Calidad» la cambia
const compositor = new EffectComposer(renderer, new THREE.WebGLRenderTarget(innerWidth, innerHeight,
  { type: THREE.HalfFloatType, samples: 4 }));
compositor.setPixelRatio(Math.min(window.devicePixelRatio, 2));
compositor.addPass(new RenderPass(escena, camara));
const pasoAO = new GTAOPass(escena, camara, innerWidth, innerHeight);
pasoAO.updateGtaoMaterial({ radius: 0.6, distanceExponent: 1.4, thickness: 1.2, scale: 1.0, samples: 16 });
pasoAO.updatePdMaterial({ lumaPhi: 10, depthPhi: 2, normalPhi: 3, radius: 6, rings: 2, samples: 16 });
pasoAO.blendIntensity = 0.9;
compositor.addPass(pasoAO);
compositor.addPass(new OutputPass());
const esChico = matchMedia("(max-width: 820px), (pointer: coarse)").matches;
let calidadAlta = !esChico && !/calidad=normal/.test(location.search);
function dibujar() {
  if (calidadAlta) compositor.render(); else renderer.render(escena, camara);
}

// piso de hormigón de la nave con juntas cada 3 m
const lienzoPiso = document.createElement("canvas");
lienzoPiso.width = lienzoPiso.height = 512;
{
  const g = lienzoPiso.getContext("2d");
  g.fillStyle = "#b9bcbd"; g.fillRect(0, 0, 512, 512);
  for (let i = 0; i < 4000; i++) {
    const v = 160 + Math.random() * 50;
    g.fillStyle = `rgba(${v},${v},${v - 4},0.35)`;
    g.fillRect(Math.random() * 512, Math.random() * 512, 2, 2);
  }
  g.strokeStyle = "rgba(90,90,90,0.55)"; g.lineWidth = 3; g.strokeRect(0, 0, 512, 512);
}
const texPiso = new THREE.CanvasTexture(lienzoPiso);
texPiso.wrapS = texPiso.wrapT = THREE.RepeatWrapping;
texPiso.repeat.set(20, 20);
texPiso.colorSpace = THREE.SRGBColorSpace;
const piso = new THREE.Mesh(new THREE.PlaneGeometry(60, 60), new THREE.MeshStandardMaterial({ map: texPiso, roughness: 0.92 }));
piso.rotation.x = -Math.PI / 2;
piso.position.set(6.5, -0.002, -1.3);
piso.receiveShadow = true;
escena.add(piso);

// ------------------------------------------------------------------ materiales por tipo
function texMalla() {
  const c = document.createElement("canvas"); c.width = c.height = 64;
  const g = c.getContext("2d");
  g.fillStyle = "#6d7378"; g.fillRect(0, 0, 64, 64);
  g.strokeStyle = "#b9c0c6"; g.lineWidth = 3;
  for (let i = -64; i < 128; i += 8) { g.beginPath(); g.moveTo(i, 0); g.lineTo(i + 64, 64); g.stroke(); }
  g.strokeStyle = "#9aa2a8"; g.lineWidth = 2;
  for (let i = 0; i < 64; i += 8) { g.beginPath(); g.moveTo(0, i); g.lineTo(64, i); g.stroke(); }
  const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(160, 30);
  t.colorSpace = THREE.SRGBColorSpace; return t;
}
const MALLA = texMalla();
MALLA.repeat.set(1, 1);
// panel sándwich: micronervado vertical cada 0,2 m y junta de módulo cada 1,0 m
function texPanel() {
  const c = document.createElement("canvas"); c.width = 256; c.height = 16;
  const g = c.getContext("2d");
  g.fillStyle = "#eef0ee"; g.fillRect(0, 0, 256, 16);
  for (let i = 0; i < 5; i++) {
    const x = i * 51.2;
    const gr = g.createLinearGradient(x + 18, 0, x + 34, 0);
    gr.addColorStop(0, "rgba(0,0,0,0)"); gr.addColorStop(0.5, "rgba(0,0,0,0.07)"); gr.addColorStop(1, "rgba(255,255,255,0.25)");
    g.fillStyle = gr; g.fillRect(x + 18, 0, 16, 16);
  }
  g.fillStyle = "rgba(60,64,70,0.55)"; g.fillRect(0, 0, 2, 16);
  const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 8; return t;
}
const PANEL = texPanel();
// coordenadas UV por proyección según la normal de cada cara (la malla del GLB no trae UV)
function uvCaja(geo, escala) {
  const g = geo.index ? geo.toNonIndexed() : geo;
  const p = g.attributes.position, uv = new Float32Array(p.count * 2);
  const a = new THREE.Vector3(), b = new THREE.Vector3(), c = new THREE.Vector3(), n = new THREE.Vector3();
  for (let i = 0; i < p.count; i += 3) {
    a.fromBufferAttribute(p, i); b.fromBufferAttribute(p, i + 1); c.fromBufferAttribute(p, i + 2);
    n.subVectors(c, b).cross(a.clone().sub(b)).normalize();
    const [ax, ay, az] = [Math.abs(n.x), Math.abs(n.y), Math.abs(n.z)];
    for (let k = 0; k < 3; k++) {
      const v = [a, b, c][k];
      let u, w;
      if (ay >= ax && ay >= az) { u = v.x; w = v.z; } else if (ax >= az) { u = v.z; w = v.y; } else { u = v.x; w = v.y; }
      uv[(i + k) * 2] = u / escala; uv[(i + k) * 2 + 1] = w / escala;
    }
  }
  g.setAttribute("uv", new THREE.BufferAttribute(uv, 2));
  g.computeVertexNormals();
  return g;
}
function materialPara(d) {
  const [r, g, b] = d.color;
  const col = new THREE.Color(r, g, b);
  const m = d.material;
  // acero pintado con epoxi: base mate con una capa de barniz (clearcoat) que da el brillo de la pintura
  const p = { color: col, roughness: 0.55, metalness: 0.25, clearcoat: 0.35, clearcoatRoughness: 0.45 };
  if (/AISI|inox/i.test(m)) Object.assign(p, { roughness: 0.32, metalness: 0.85 });
  if (/galv/i.test(m)) Object.assign(p, { roughness: 0.42, metalness: 0.7 });
  if (/lana/i.test(m)) Object.assign(p, { roughness: 0.75, metalness: 0.05 });
  if (/AISI|inox|galv|lana|UHMW|PTFE|goma/i.test(m)) p.clearcoat = 0;
  if (/UHMW/.test(m)) Object.assign(p, { roughness: 0.8, metalness: 0 });
  if (/PTFE/.test(m)) Object.assign(p, { roughness: 0.55, metalness: 0, color: new THREE.Color(0xf2f4f7), sheen: 0.3 });
  if (/goma/.test(m)) Object.assign(p, { roughness: 0.9, metalness: 0 });
  if (d.cod.startsWith("4.1-")) Object.assign(p, { map: MALLA, color: new THREE.Color(0xe8ecef), roughness: 0.4, metalness: 0.8 });
  if (/^4\.8[a-e]/.test(d.cod)) Object.assign(p, { map: PANEL, color: new THREE.Color(0xffffff), roughness: 0.5, metalness: 0.15 });
  if (d.cod.startsWith("M")) Object.assign(p, { roughness: 0.45, metalness: 0.35 });
  return new THREE.MeshPhysicalMaterial(p);
}

// ------------------------------------------------------------------ capas
const GRUPOS = [
  ["Estructura y anclajes", (c) => /^(4\.11|4\.20|4\.16-|4\.17)/.test(c)],
  ["Cerramiento y puertas", (c) => /^(4\.8|4\.9)/.test(c)],
  ["Bandas, tambores y guías", (c) => /^(4\.1-|4\.2|4\.3|4\.4|4\.6|4\.7|4\.14)/.test(c)],
  ["Accionamientos (motorreductores y cadenas)", (c) => /^(4\.5|M\d|4\.15|4\.16b)/.test(c)],
  ["Alimentación, descarga y aire", (c) => /^(4\.10|4\.12|4\.18|4\.19)/.test(c)],
  ["Pasarela y escalera", (c) => /^4\.13/.test(c)],
  ["Guano sobre las bandas", (c) => c === "guano"],
];
const capas = {};
const panelCapas = document.getElementById("capas");
GRUPOS.forEach(([nombre], i) => {
  const g = new THREE.Group(); g.name = nombre; escena.add(g); capas[nombre] = g;
  const fila = document.createElement("div"); fila.className = "fila";
  fila.innerHTML = `<input type="checkbox" id="c${i}" checked><label for="c${i}">${nombre}</label><button class="solo">solo</button>`;
  fila.querySelector("input").onchange = (e) => { g.visible = e.target.checked; };
  fila.querySelector(".solo").onclick = () => GRUPOS.forEach(([n], j) => {
    capas[n].visible = n === nombre; document.getElementById("c" + j).checked = n === nombre; });
  panelCapas.appendChild(fila);
});
const capaDe = (cod) => (GRUPOS.find(([, f]) => f(cod)) || GRUPOS[0])[0];

// ------------------------------------------------------------------ carga del modelo
const piezas = {};               // id -> { datos, objeto (Group), base (posición), explosion (Vector3) }
const mm = (v) => new THREE.Vector3(v[0] / 1000, v[2] / 1000, -v[1] / 1000);   // CAD (z arriba) -> three (y arriba)

function cargar() {
  const bin = Uint8Array.from(atob(window.__GLB_B64), (ch) => ch.charCodeAt(0)).buffer;
  new GLTFLoader().parse(bin, "", (gltf) => {
    const porId = {};
    gltf.scene.traverse((o) => {
      if (!o.isMesh) return;
      let n = o; while (n && !/^P\d{3}/.test(n.name)) n = n.parent;
      const id = n ? n.name.slice(0, 4) : null;
      if (!id) return;
      (porId[id] ||= []).push(o);
    });
    for (const d of DATOS.piezas) {
      const mallas = porId[d.id] || [];
      const grupo = new THREE.Group(); grupo.name = d.id;
      const mat = materialPara(d);
      for (const o of mallas) {
        o.updateWorldMatrix(true, false);
        let geo = o.geometry.clone().applyMatrix4(o.matrixWorld);
        if (d.cod.startsWith("4.1-")) geo = uvCaja(geo, 0.06);       // malla: un módulo de textura cada 6 cm
        if (/^4\.8[a-e]/.test(d.cod)) geo = uvCaja(geo, 1.0);       // paneles de 1,0 m
        const m = new THREE.Mesh(geo, mat);
        m.castShadow = m.receiveShadow = true;
        m.userData.pieza = d.id;
        grupo.add(m);
      }
      capas[capaDe(d.cod)].add(grupo);
      piezas[d.id] = { datos: d, objeto: grupo, explosion: mm(d.explosion_mm), mat };
    }
    prepararGiro();
    capaGuano();
    armarLista();
    etiquetas();
    vistaInicial();
    document.getElementById("cargando").style.display = "none";
  }, (e) => { document.getElementById("cargando").textContent = "Error al cargar el modelo: " + e; });
}

// ------------------------------------------------------------------ despiece y montaje
let explotado = 0, objetivoExpl = 0;
function aplicarExplosion(k) {
  for (const p of Object.values(piezas)) {
    p.objeto.position.copy(p.explosion).multiplyScalar(k * k * (3 - 2 * k));
  }
}
document.getElementById("despiece").onclick = (e) => {
  objetivoExpl = objetivoExpl > 0.5 ? 0 : 1;
  e.target.textContent = objetivoExpl ? "Armar" : "Despiece";
  e.target.classList.toggle("activo", !!objetivoExpl);
};
let paso = -1;
function mostrarPaso(i, inmediato = false) {
  paso = i;
  const txt = document.getElementById("pasoTexto");
  if (i < 0) {
    for (const p of Object.values(piezas)) { p.objeto.visible = true; p.mat.emissive.setHex(0); }
    capas["Guano sobre las bandas"].visible = document.getElementById("c" + (GRUPOS.length - 1)).checked;
    replanteo.visible = false;
    txt.innerHTML = ""; document.getElementById("pasoN").textContent = "—"; return;
  }
  const P = PASOS[i];
  const hasta = new Set(PASOS.slice(0, i + 1).flatMap((s) => s.prefijos));
  const ahora = new Set(P.prefijos);
  for (const p of Object.values(piezas)) {
    const c = p.datos.cod;
    const vis = [...hasta].some((pre) => c.startsWith(pre));
    p.objeto.visible = vis;
    const nuevo = [...ahora].some((pre) => c.startsWith(pre));
    p.mat.emissive.setHex(nuevo ? 0x553300 : 0x000000);
  }
  capas["Guano sobre las bandas"].visible = false;     // durante el montaje no hay producto
  replanteo.visible = i <= 1;
  document.getElementById("pasoN").textContent = `${i + 1} / ${PASOS.length}`;
  txt.innerHTML = `<b>${P.titulo}</b><br>${P.texto}<br><span class="sub">Herramientas: ${P.herramientas}</span>`;
  if (P.camara) {
    if (inmediato) { viaje = null; camara.position.set(...P.camara[0]); controles.target.set(...P.camara[1]); controles.update(); }
    else volarA(P.camara[0], P.camara[1]);
  }
}
document.getElementById("pasoAnt").onclick = () => mostrarPaso(Math.max(-1, paso - 1));
document.getElementById("pasoSig").onclick = () => mostrarPaso(Math.min(PASOS.length - 1, paso + 1));
document.getElementById("pasoFin").onclick = () => {
  mostrarPaso(-1);
  for (const p of Object.values(piezas)) p.mat.emissive.setHex(0);
};

// corte: oculta el panel Sur, el techo y las puertas para ver el interior
let corte = false;
document.getElementById("corte").onclick = (e) => {
  corte = !corte; e.target.classList.toggle("activo", corte);
  for (const p of Object.values(piezas)) {
    if (/^(4\.8a|4\.8e|4\.9)/.test(p.datos.cod)) p.objeto.visible = !corte;
    if (/^4\.8b/.test(p.datos.cod)) { p.mat.transparent = corte; p.mat.opacity = corte ? 0.35 : 1; }
  }
};

// ------------------------------------------------------------------ animación de bandas y tambores
const giratorios = [];
function prepararGiro() {
  for (const p of Object.values(piezas)) {
    const c = p.datos.cod;
    if (!/^(4\.2-|4\.2\.1|4\.3-|4\.3\.1|4\.6|4\.18-|4\.18$)/.test(c)) continue;
    // eje de giro: paralelo al eje y del CAD (-z en three), por el centro de la caja de la pieza
    const caja = new THREE.Box3().setFromObject(p.objeto);
    const centro = caja.getCenter(new THREE.Vector3());
    const pivote = new THREE.Group(); pivote.position.copy(centro);
    for (const m of [...p.objeto.children]) { m.geometry.translate(-centro.x, -centro.y, -centro.z); pivote.add(m); }
    p.objeto.add(pivote);
    const r = c.startsWith("4.6") ? 0.0445 : c.startsWith("4.18") ? 0.12 : c.startsWith("4.3") ? 0.125 : 0.158;
    giratorios.push({ pivote, w: c.startsWith("4.6") ? 0 : 0.0062 / r, cod: c });
  }
}
let reloj = 0, pausado = false, factorVel = 60;
document.getElementById("pausa").onclick = (e) => { pausado = !pausado; e.target.textContent = pausado ? "Reanudar" : "Pausar"; };
document.getElementById("velocidad").onclick = (e) => {
  factorVel = { 60: 300, 300: 1, 1: 60 }[factorVel];
  e.target.textContent = factorVel === 1 ? "Velocidad real" : `Velocidad ×${factorVel}`;
};

// ------------------------------------------------------------------ lista de piezas e información
function armarLista() {
  const tb = document.querySelector("#lista tbody");
  const filas = [...DATOS.piezas].sort((a, b) => a.cod.localeCompare(b.cod, "es", { numeric: true }));
  let total = 0;
  for (const d of filas) {
    total += d.masa_kg;
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${d.cod}</td><td>${d.nombre}</td><td class="n">${d.cantidad}</td><td class="n">${d.masa_kg.toLocaleString("es-AR")}</td>`;
    tr.onclick = () => { seleccionar(d.id); const c = new THREE.Box3().setFromObject(piezas[d.id].objeto);
      const cen = c.getCenter(new THREE.Vector3()), r = Math.max(1.2, c.getSize(new THREE.Vector3()).length());
      volarA([cen.x + r * 0.9, cen.y + r * 0.6, cen.z + r * 1.1], [cen.x, cen.y, cen.z]); };
    tb.appendChild(tr);
  }
  document.getElementById("masaTotal").textContent = Math.round(total).toLocaleString("es-AR") + " kg";
}
let elegido = null;
function seleccionar(id) {
  if (elegido) piezas[elegido].mat.emissive.setHex(0);
  elegido = id;
  const info = document.getElementById("info");
  if (!id) { info.style.display = "none"; return; }
  const d = piezas[id].datos;
  piezas[id].mat.emissive.setHex(0x1d4f86);
  info.innerHTML = `<b>${d.cod} · ${d.nombre}</b><br>Material: ${d.material}<br>Cantidad: ${d.cantidad} · Masa: ${d.masa_kg.toLocaleString("es-AR")} kg`
    + (d.nota ? `<br>${d.nota}` : "") + `<br><span class="sub">Plano: ${planoDe(d.cod)}</span>`;
  info.style.display = "block";
}
function planoDe(c) {
  if (/^(4\.2|4\.15|4\.5|M)/.test(c)) return "SC-03 (tambor motriz y transmisión) · P03";
  if (/^(4\.3|4\.14)/.test(c)) return "SC-04 (tambor de reenvío y tensor)";
  if (/^(4\.11|4\.17|4\.20|4\.16)/.test(c)) return "SC-05 (bastidor y fijación al piso)";
  return "SC-01 / SC-02 (conjunto y despiece)";
}
const rayo = new THREE.Raycaster(), puntero = new THREE.Vector2();
let abajo = null;
renderer.domElement.addEventListener("pointerdown", (e) => { abajo = [e.clientX, e.clientY]; });
renderer.domElement.addEventListener("pointerup", (e) => {
  if (!abajo || Math.hypot(e.clientX - abajo[0], e.clientY - abajo[1]) > 4) return;
  puntero.set((e.clientX / innerWidth) * 2 - 1, -(e.clientY / innerHeight) * 2 + 1);
  rayo.setFromCamera(puntero, camara);
  const t = rayo.intersectObjects(Object.values(capas).filter((g) => g.visible), true).find((i) => i.object.visible);
  seleccionar(t ? t.object.userData.pieza : null);
});

// ------------------------------------------------------------------ etiquetas
// cada etiqueta cuelga de su pieza: se mueve con el despiece, se oculta con la pieza y se atenúa si
// otra pieza la tapa (prueba de rayo cada 12 cuadros)
const listaEtiquetas = [];
const porCod = (cod) => Object.values(piezas).find((p) => p.datos.cod === cod);
function etiqueta(texto, pos, cod) {
  const div = document.createElement("div"); div.className = "etiqueta"; div.textContent = texto;
  const e = new CSS2DObject(div);
  const p = cod ? porCod(cod) : null;
  e.position.copy(pos);
  (p ? p.objeto : escena).add(e);
  listaEtiquetas.push({ e, p, div });
  return e;
}
function etiquetas() {
  etiqueta("SC-4 · secador de cinta de 3 pisos · 13,0 × 2,6 × 3,4 m", mm([6500, 1300, 4300]), "4.8e");
  etiqueta("M5 · piso 1", mm([12100, -420, 2216]), "M5");
  etiqueta("M6 · piso 2", mm([900, -420, 1366]), "M6");
  etiqueta("M7 · piso 3", mm([12100, -420, 516]), "M7");
  etiqueta("Transmisión ASA 60 (cárter)", mm([12450, -260, 2810]), "4.15c-1");
  etiqueta("Entrada de aire caliente (plenum)", mm([11000, 2900, 900]), "4.19b");
  etiqueta("Campana de salida 800 × 800", mm([3000, 1300, 4150]), "4.12");
  etiqueta("Alimentación (cinta)", mm([900, 1300, 3900]), "4.19c");
  etiqueta("Descarga al sinfín", mm([12750, 1300, -100]), "4.19a");
  etiqueta("Escalera marinera con jaula", mm([-500, 300, 2600]), "4.13");
}
// rótulos que se pisan en pantalla: el de más abajo baja lo justo para quedar libre (cada cuadro, después de
// ubicarlos; CSS2DRenderer maneja la posición con transform, así que el corrimiento va como margen superior)
function separarEtiquetas() {
  if (rotulos.domElement.style.display === "none") return;
  for (const it of listaEtiquetas) it.div.style.marginTop = "0px";
  const cajas = [];
  for (const it of listaEtiquetas) {
    if (!it.e.visible || it.div.style.display === "none") continue;
    const r = it.div.getBoundingClientRect();
    if (r.width) cajas.push({ div: it.div, l: r.left, r: r.right, t: r.top, b: r.bottom });
  }
  cajas.sort((a, b) => a.t - b.t);
  const puestas = [];
  for (const c of cajas) {
    let dy = 0, choca = true;
    while (choca) {
      choca = false;
      for (const p of puestas) {
        if (c.l < p.r + 4 && c.r > p.l - 4 && c.t + dy < p.b + 2 && c.b + dy > p.t - 2) { dy = p.b + 2 - c.t; choca = true; }
      }
    }
    if (dy) c.div.style.marginTop = `${Math.round(dy)}px`;
    puestas.push({ l: c.l, r: c.r, t: c.t + dy, b: c.b + dy });
  }
}
const rayoEt = new THREE.Raycaster();
let cuadro = 0;
function actualizarEtiquetas() {
  if (++cuadro % 12) return;
  const todos = Object.values(capas).filter((g) => g.visible);
  const w = new THREE.Vector3();
  for (const it of listaEtiquetas) {
    const vis = !it.p || (it.p.objeto.visible && it.p.objeto.parent.visible);
    it.e.visible = vis;
    if (!vis) continue;
    it.e.getWorldPosition(w);
    const dir = w.clone().sub(camara.position), dist = dir.length();
    rayoEt.set(camara.position, dir.normalize()); rayoEt.far = dist - 0.25;
    const tapa = rayoEt.intersectObjects(todos, true).some((x) => x.object.visible && x.object.material && !x.object.material.transparent);
    it.div.style.opacity = tapa ? "0.28" : "1";
  }
}

// replanteo sobre la platea (pasos 1 y 2): contorno del secador, ejes de columnas y cotas
const replanteo = new THREE.Group(); replanteo.visible = false; escena.add(replanteo);
{
  const mat = new THREE.LineDashedMaterial({ color: 0xc0392b, dashSize: 0.25, gapSize: 0.12 });
  const pts = [[0, 0], [13000, 0], [13000, 2600], [0, 2600], [0, 0]].map(([x, y]) => mm([x, y, 3]));
  const l = new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), mat); l.computeLineDistances(); replanteo.add(l);
  const ejes = new THREE.LineBasicMaterial({ color: 0x1f5fa8 });
  for (const x of [0, 3250, 6500, 9750, 13000]) {
    replanteo.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([mm([x, -600, 3]), mm([x, 3200, 3])]), ejes));
  }
  for (const y of [0, 2600]) {
    replanteo.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([mm([-600, y, 3]), mm([13600, y, 3])]), ejes));
  }
  const div = document.createElement("div"); div.className = "etiqueta";
  div.textContent = "Replanteo: 13,00 × 2,60 m · ejes de columnas cada 3,25 m · diagonales iguales ±3 mm";
  const e = new CSS2DObject(div); e.position.copy(mm([6500, -900, 0])); replanteo.add(e);
}

// ------------------------------------------------------------------ guano sobre las bandas
// capa de 30 mm (compuerta niveladora) que avanza con la banda: húmedo y oscuro arriba (≈ 60 % de
// humedad), seco y claro en el piso 3 (≈ 15 %). La textura se desplaza a la velocidad de la banda.
const capasGuano = [];
function texGuano(base) {
  const c = document.createElement("canvas"); c.width = c.height = 256;
  const g = c.getContext("2d");
  g.fillStyle = base; g.fillRect(0, 0, 256, 256);
  for (let i = 0; i < 2600; i++) {
    const r = 1 + Math.random() * 4, v = Math.random();
    g.fillStyle = v < 0.5 ? `rgba(0,0,0,${0.1 + v * 0.3})` : `rgba(255,240,210,${(v - 0.5) * 0.35})`;
    g.beginPath(); g.arc(Math.random() * 256, Math.random() * 256, r, 0, 7); g.fill();
  }
  const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.colorSpace = THREE.SRGBColorSpace;
  return t;
}
function capaGuano() {
  const colores = { 1: "#3f3020", 2: "#5d4a31", 3: "#8a7553" };
  const capa = capas["Guano sobre las bandas"];
  for (const n of [1, 2, 3]) {
    const banda = porCod(`4.1-${n}`), motriz = porCod(`4.2-${n}`), reenvio = porCod(`4.3-${n}`);
    if (!banda || !motriz || !reenvio) continue;
    const [, , , , , zt] = banda.datos.caja_mm;
    const xm = motriz.datos.centro_mm[0], xr = reenvio.datos.centro_mm[0];
    const sentido = Math.sign(xm - xr);
    // el piso 1 recibe el producto después del esparcidor (x ≈ 1,6 m)
    let x0 = Math.min(xm, xr) + 120, x1 = Math.max(xm, xr) - 120;
    if (n === 1) x0 = 1750;
    const largo = (x1 - x0) / 1000, ancho = 1.86, esp = 0.03;
    const tex = texGuano(colores[n]); tex.repeat.set(largo / 0.5, ancho / 0.5);
    const geo = new THREE.BoxGeometry(largo, esp, ancho);
    const m = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ map: tex, roughness: 0.95, metalness: 0 }));
    m.position.copy(mm([(x0 + x1) / 2, 1300, zt + esp * 500]));
    m.castShadow = m.receiveShadow = true;
    capa.add(m);
    capasGuano.push({ tex, sentido, rep: tex.repeat.x / largo });
  }
}
document.getElementById("etiquetas").onclick = (e) => {
  const ver = rotulos.domElement.style.display === "none";
  rotulos.domElement.style.display = ver ? "" : "none"; e.target.classList.toggle("activo", ver);
};

// ------------------------------------------------------------------ vistas
let viaje = null;
function volarA(pos, obj) {
  viaje = { t: 0, p0: camara.position.clone(), o0: controles.target.clone(), p1: new THREE.Vector3(...pos), o1: new THREE.Vector3(...obj) };
}
const VISTAS = {
  "General": [[20, 9, 9], [6.5, 1.6, -1.3]],
  "Accionamientos (Sur)": [[11.5, 2.6, 6.5], [11.5, 1.6, -0.5]],
  "Interior (corte)": [[5.5, 3.8, 5.5], [6.5, 1.7, -1.3]],
  "Despiece": [[25, 15, 14], [6.5, 2.5, -1.3]],
  "Planta": [[6.5, 30, -1.29], [6.5, 0, -1.3]],
  "Frente Oeste": [[-12, 2.5, -1.3], [6.5, 1.7, -1.3]],
};
const contVistas = document.getElementById("vistas");
for (const [n, [p, o]] of Object.entries(VISTAS)) {
  const b = document.createElement("button"); b.textContent = n;
  b.onclick = () => {
    volarA(p, o);
    if (n === "Despiece" && objetivoExpl === 0) document.getElementById("despiece").click();
    if (n === "Interior (corte)" && !corte) document.getElementById("corte").click();
  };
  contVistas.appendChild(b);
}
function vistaInicial() {
  camara.position.set(20, 9, 9); controles.target.set(6.5, 1.6, -1.3);
  sol.position.set(26, 30, 18); sol.target.position.set(6.5, 0, -1.3); escena.add(sol.target);
  const s = sol.shadow.camera; s.left = s.bottom = -16; s.right = s.top = 16; s.near = 1; s.far = 90; s.updateProjectionMatrix();
}

// ------------------------------------------------------------------ herramientas
document.getElementById("captura").onclick = () => {
  dibujar();
  const a = document.createElement("a"); a.href = renderer.domElement.toDataURL("image/png");
  a.download = "secador_SC4.png"; a.click();
};
document.getElementById("completa").onclick = () => {
  if (document.fullscreenElement) document.exitFullscreen(); else document.documentElement.requestFullscreen?.();
};
const panel = document.getElementById("panel"), abrir = document.getElementById("abrir");
document.getElementById("ocultar").onclick = () => { panel.style.display = "none"; abrir.style.display = "block"; };
abrir.onclick = () => { panel.style.display = ""; abrir.style.display = "none"; };
document.getElementById("verLista").onclick = () => {
  const l = document.getElementById("lista"); l.style.display = l.style.display === "block" ? "none" : "block";
};
addEventListener("resize", () => {
  camara.aspect = innerWidth / innerHeight; camara.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight); rotulos.setSize(innerWidth, innerHeight);
  compositor.setSize(innerWidth, innerHeight); pasoAO.setSize(innerWidth, innerHeight);
});
const botonCalidad = document.getElementById("calidad");
const rotularCalidad = () => { botonCalidad.textContent = calidadAlta ? "Calidad alta" : "Calidad normal";
  botonCalidad.classList.toggle("activo", calidadAlta); };
botonCalidad.onclick = () => { calidadAlta = !calidadAlta; rotularCalidad(); };
rotularCalidad();

// API para capturas automáticas (planos y manual)
window.__visor = {
  vista: (p, o) => { camara.position.set(...p); controles.target.set(...o); controles.update(); },
  explosion: (k) => { objetivoExpl = explotado = k; aplicarExplosion(k); },
  paso: (i) => mostrarPaso(i, true),
  corte: (v) => { if (v !== corte) document.getElementById("corte").click(); },
  ocultarUI: () => { for (const id of ["panel", "info", "abrir", "lista"]) document.getElementById(id).style.display = "none"; },
  etiquetas: (v) => { rotulos.domElement.style.display = v ? "" : "none"; },
  proyectar: (pts) => pts.map((v) => { const p = mm(v).project(camara);
    return [(p.x + 1) / 2 * innerWidth, (1 - p.y) / 2 * innerHeight]; }),
  listo: () => Object.keys(piezas).length > 0,
  calidad: (alta) => { calidadAlta = !!alta; rotularCalidad(); },
};

let anterior = performance.now();
renderer.setAnimationLoop((ahora) => {
  const dtReal = Math.min((ahora - anterior) / 1000, 0.1); anterior = ahora;
  const dt = dtReal * factorVel;
  if (!pausado) {
    reloj += dt;
    for (const g of giratorios) g.pivote.rotation.z -= g.w * dt;
    for (const c of capasGuano) c.tex.offset.x -= c.sentido * 0.0062 * dt * c.rep;   // 6,2 mm/s
  }
  actualizarEtiquetas();
  if (Math.abs(explotado - objetivoExpl) > 1e-3) {
    explotado += Math.sign(objetivoExpl - explotado) * Math.min(Math.abs(objetivoExpl - explotado), dtReal / 1.6);
    aplicarExplosion(explotado);
  }
  if (viaje) {
    viaje.t = Math.min(viaje.t + dtReal / 0.9, 1);
    const k = viaje.t * viaje.t * (3 - 2 * viaje.t);
    camara.position.lerpVectors(viaje.p0, viaje.p1, k); controles.target.lerpVectors(viaje.o0, viaje.o1, k);
    if (viaje.t >= 1) viaje = null;
  }
  controles.update(); dibujar(); rotulos.render(escena, camara); separarEtiquetas();
});
cargar();
