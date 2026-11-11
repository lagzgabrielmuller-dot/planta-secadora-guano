/* Vista 3D del secador SC-4 para el simulador (three.js r128, sin internet).
 *
 * Medidas del visor 3D del proyecto (Rev. D, "Solo secadora"): cámara de 13,0 × 2,6 m con paneles de
 * 80 mm, techo a 3,4 m sobre patas de 0,4 m, bandas de 2,0 m con la cara de arriba a 2,70, 1,85 y
 * 1,00 m, tambores de 158 y 125 mm de radio, guías de UHMW-PE, entrada de aire por la cara norte y
 * campana de escape en x = 3 m.
 *
 * Uso:  const v = Vista3D.crear(contenedor, { fmt, colorGuano, tip });
 *       if (v) v.actualizar(resultado, filas, extra);
 * Devuelve null si el navegador no tiene WebGL (la página usa entonces el esquema plano).
 */
(function (root) {
  "use strict";
  const THREE = root.THREE;

  const G = {
    L: 13.0, A: 2.6, z0: 0.4, H: 3.4, e: 0.08,
    columnas: [0.06, 3.25, 6.5, 9.75, 12.94],
    banda: 2.0,
    // el guano entra por la cola y sale por la cabeza (motriz)
    pisos: [
      { zc: 2.70, cola: 0.55, cabeza: 12.45 },
      { zc: 1.85, cola: 12.70, cabeza: 0.55 },
      { zc: 1.00, cola: 0.30, cabeza: 12.45 },
    ],
    rMotriz: 0.158, rReenvio: 0.125,
    retorno: [2.5, 4.5, 6.5, 8.5, 10.5],
    guias: [0.55, 0.9, 1.3, 1.7, 2.05],
    alimentacion: 0.9, esparcidor: 1.35, campana: 3.0,
    entrada: { x0: 10.4, x1: 11.6, z0: 0.48, z1: 0.88 },
    descarga: [12.6, 12.9],
  };
  const EXAG = 6;                 // el espesor del lecho se dibuja 6 veces más grueso
  const Y0 = 0.32, Y1 = 2.28;     // bordes del lecho sobre la banda (2,0 m de banda)

  // coordenadas de planta (x a lo largo, y de sur a norte, z altura) → escena (y arriba, sur hacia +z)
  const V = (x, z, y) => new THREE.Vector3(x - G.L / 2, z, G.A / 2 - y);

  function std(color, rough, metal, extra) {
    return new THREE.MeshStandardMaterial(Object.assign({ color, roughness: rough, metalness: metal }, extra || {}));
  }

  function lienzo(w, h, dibujar) {
    const c = document.createElement("canvas");
    c.width = w; c.height = h;
    dibujar(c.getContext("2d"), w, h);
    const t = new THREE.CanvasTexture(c);
    t.wrapS = t.wrapT = THREE.RepeatWrapping;
    return t;
  }

  // ruido fijo (no parpadea al recalcular)
  const RUIDO = new Float32Array(4096);
  (function () { let s = 12345; for (let i = 0; i < RUIDO.length; i++) { s = (s * 16807) % 2147483647; RUIDO[i] = s / 2147483647 - 0.5; } })();

  // rampa de temperatura del aire: azul (frío) → ámbar → rojo (caliente)
  const RAMPA_T = [[20, [0.23, 0.47, 0.80]], [45, [0.27, 0.66, 0.74]], [70, [0.93, 0.76, 0.30]],
    [100, [0.95, 0.52, 0.19]], [135, [0.84, 0.21, 0.17]]];
  function colorT(T, out) {
    const p = RAMPA_T;
    if (T <= p[0][0]) { out[0] = p[0][1][0]; out[1] = p[0][1][1]; out[2] = p[0][1][2]; return out; }
    for (let i = 1; i < p.length; i++) if (T <= p[i][0]) {
      const u = (T - p[i - 1][0]) / (p[i][0] - p[i - 1][0]), a = p[i - 1][1], b = p[i][1];
      out[0] = a[0] + u * (b[0] - a[0]); out[1] = a[1] + u * (b[1] - a[1]); out[2] = a[2] + u * (b[2] - a[2]);
      return out;
    }
    const z = p[p.length - 1][1]; out[0] = z[0]; out[1] = z[1]; out[2] = z[2];
    return out;
  }
  function cssT(T) { const c = colorT(T, [0, 0, 0]); return `rgb(${c.map((v) => Math.round(255 * v)).join(",")})`; }

  function crear(cont, opc) {
    if (!THREE || !opc) return null;
    let renderer;
    try {
      const prueba = document.createElement("canvas");
      if (!(prueba.getContext("webgl") || prueba.getContext("experimental-webgl"))) return null;
      renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: false });
    } catch (e) { return null; }
    const fmt = opc.fmt, colorGuano = opc.colorGuano;
    const reducido = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.setClearColor(0x000000, 0);
    const lienzo3d = renderer.domElement;
    lienzo3d.className = "v3d-lienzo";
    lienzo3d.setAttribute("role", "img");
    cont.appendChild(lienzo3d);
    const capaEtq = document.createElement("div");
    capaEtq.className = "v3d-etiquetas";
    capaEtq.setAttribute("aria-hidden", "true");
    cont.appendChild(capaEtq);

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(32, 2, 0.1, 200);
    const OBJETIVO = new THREE.Vector3(0.9, 1.55, 0.2);
    const POS0 = new THREE.Vector3(-6.4, 6.9, 15.6);
    camera.position.copy(POS0);
    const DIR0 = POS0.clone().sub(OBJETIVO).normalize(), D0 = POS0.distanceTo(OBJETIVO);
    const controls = new THREE.OrbitControls(camera, lienzo3d);
    controls.target.copy(OBJETIVO);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.minDistance = 5;
    controls.maxDistance = 34;
    controls.maxPolarAngle = Math.PI * 0.49;
    controls.screenSpacePanning = true;
    controls.update();

    // ---------------------------------------------------------------- luces y piso
    scene.add(new THREE.HemisphereLight(0xf6f7fb, 0x8a867e, 0.85));
    const sol = new THREE.DirectionalLight(0xffffff, 0.85);
    sol.position.set(-9, 15, 11);
    sol.castShadow = true;
    sol.shadow.mapSize.set(2048, 2048);
    Object.assign(sol.shadow.camera, { left: -12, right: 12, top: 9, bottom: -9, near: 1, far: 50 });
    sol.shadow.bias = -0.0005;
    scene.add(sol);
    const relleno = new THREE.DirectionalLight(0xffffff, 0.28);
    relleno.position.set(8, 6, -9);
    scene.add(relleno);
    const piso = new THREE.Mesh(new THREE.PlaneGeometry(80, 80), new THREE.ShadowMaterial({ opacity: 0.17 }));
    piso.rotation.x = -Math.PI / 2;
    piso.receiveShadow = true;
    scene.add(piso);
    const losa = new THREE.Mesh(new THREE.BoxGeometry(G.L + 3.2, 0.06, G.A + 4.2), std(0xd3d6d6, 0.95, 0.0));
    losa.position.set(0, -0.03, -0.2);
    losa.receiveShadow = true;
    scene.add(losa);

    // ---------------------------------------------------------------- materiales
    const malla = lienzo(64, 64, (c, w, h) => {
      c.fillStyle = "#5f676f"; c.fillRect(0, 0, w, h);
      c.strokeStyle = "#a5adb4"; c.lineWidth = 2;
      for (let i = 0; i <= w; i += 8) { c.beginPath(); c.moveTo(i, 0); c.lineTo(i, h); c.stroke(); c.beginPath(); c.moveTo(0, i); c.lineTo(w, i); c.stroke(); }
    });
    malla.repeat.set(G.L / 0.12, G.banda / 0.12);
    const grano = lienzo(128, 128, (c, w, h) => {
      const img = c.createImageData(w, h);
      for (let i = 0; i < w * h; i++) {
        const v = 128 + 110 * RUIDO[(i * 7) % RUIDO.length] + 40 * RUIDO[(i * 13 + 5) % RUIDO.length];
        img.data[4 * i] = img.data[4 * i + 1] = img.data[4 * i + 2] = Math.max(0, Math.min(255, v)); img.data[4 * i + 3] = 255;
      }
      c.putImageData(img, 0, 0);
    });
    const rejilla = lienzo(64, 64, (c, w, h) => {
      c.fillStyle = "#8d949a"; c.fillRect(0, 0, w, h);
      c.fillStyle = "#4b5157";
      for (let i = 0; i < w; i += 8) for (let j = 0; j < h; j += 16) c.fillRect(i + 2, j + 2, 4, 12);
    });
    rejilla.repeat.set(G.L / 0.5, 2);
    const chorro = lienzo(64, 256, (c, w, h) => {
      c.clearRect(0, 0, w, h);
      for (let i = 0; i < 70; i++) {
        const x = (i * 37) % w, y = (i * 91) % h, l = 30 + (i * 53) % 90;
        c.fillStyle = `rgba(255,255,255,${0.35 + 0.6 * ((i * 17) % 10) / 10})`;
        c.fillRect(x, y, 2 + (i % 3), l);
        c.fillRect(x, y - h, 2 + (i % 3), l);
      }
    });
    const M = {
      panel: std(0xe9e7e0, 0.82, 0.05),
      interior: std(0xaeb3b7, 0.75, 0.15),
      corte: std(0xcfb878, 1.0, 0.0),
      azul: std(0x263646, 0.62, 0.3),
      acero: std(0x9aa3ab, 0.42, 0.55),
      banda: std(0xffffff, 0.6, 0.45, { map: malla }),
      galv: std(0xbac1c7, 0.48, 0.45),
      amarillo: std(0xf0b92a, 0.55, 0.1),
      motor: std(0x2f5f8f, 0.5, 0.35),
      oscuro: std(0x2b3036, 0.85, 0.2),
      rejilla: std(0xffffff, 0.7, 0.4, { map: rejilla }),
      hueco: new THREE.MeshBasicMaterial({ color: 0x15191d }),
    };
    const mGuia = [0, 1, 2].map(() => std(0xefefea, 0.6, 0.0, { emissive: 0x000000 }));
    const mLecho = [0, 1, 2].map(() => std(0xffffff, 0.96, 0.0, { vertexColors: true, bumpMap: grano, bumpScale: 0.025 }));
    const mChorro = [0, 1, 2, 3].map(() => new THREE.MeshBasicMaterial({ map: chorro.clone(), color: 0x6b4a2c, transparent: true, depthWrite: false, side: THREE.DoubleSide, opacity: 0.95 }));
    mChorro.forEach((m) => { m.map.needsUpdate = true; m.map.wrapS = m.map.wrapT = THREE.RepeatWrapping; });

    const grupo = new THREE.Group();
    scene.add(grupo);
    function caja(x0, x1, z0, z1, y0, y1, mat, sombra) {
      const m = new THREE.Mesh(new THREE.BoxGeometry(x1 - x0, z1 - z0, y1 - y0), mat);
      m.position.copy(V((x0 + x1) / 2, (z0 + z1) / 2, (y0 + y1) / 2));
      if (sombra) { m.castShadow = true; m.receiveShadow = true; }
      grupo.add(m);
      return m;
    }
    function cilindroX(x0, x1, z, y, r, mat) {     // eje a lo largo de x
      const m = new THREE.Mesh(new THREE.CylinderGeometry(r, r, x1 - x0, 24), mat);
      m.rotation.z = Math.PI / 2; m.position.copy(V((x0 + x1) / 2, z, y)); grupo.add(m); return m;
    }
    function cilindroY(x, z, y0, y1, r, mat) {     // eje de sur a norte
      const m = new THREE.Mesh(new THREE.CylinderGeometry(r, r, y1 - y0, 28), mat);
      m.rotation.x = Math.PI / 2; m.position.copy(V(x, z, (y0 + y1) / 2)); grupo.add(m); return m;
    }
    function cilindroZ(x, y, z0, z1, r, mat, seg) {  // vertical
      const m = new THREE.Mesh(new THREE.CylinderGeometry(r, r, z1 - z0, seg || 28), mat);
      m.position.copy(V(x, (z0 + z1) / 2, y)); grupo.add(m); return m;
    }

    // ---------------------------------------------------------------- estructura y cámara
    const { L, A, z0, H, e } = G;
    G.columnas.forEach((x) => {
      caja(x - 0.05, x + 0.05, 0, z0, 0.0, 0.1, M.azul, true);
      caja(x - 0.05, x + 0.05, 0, z0, A - 0.1, A, M.azul, true);
    });
    caja(0, L, z0 - 0.12, z0, 0, 0.1, M.azul, true);
    caja(0, L, z0 - 0.12, z0, A - 0.1, A, M.azul, true);
    const conCorte = (base) => [base, base, base, base, M.corte, base];   // cara sur (+z) cortada
    function panel(x0, x1, za, zb, ya, yb, cara) {
      const m = new THREE.Mesh(new THREE.BoxGeometry(x1 - x0, zb - za, yb - ya), cara);
      m.position.copy(V((x0 + x1) / 2, (za + zb) / 2, (ya + yb) / 2));
      m.receiveShadow = true;
      grupo.add(m);
      return m;
    }
    const piso0 = panel(0, L, z0, z0 + e, 0, A, [M.interior, M.interior, M.interior, M.interior, M.corte, M.interior]); piso0.castShadow = true;
    panel(0, L, z0, H, A - e, A, [M.panel, M.panel, M.panel, M.panel, M.interior, M.panel]).castShadow = true;  // pared norte
    panel(0, e, z0, H, 0, A, [M.interior, M.panel, M.panel, M.panel, M.corte, M.panel]).castShadow = true;  // testero oeste
    panel(L - e, L, z0, H, 0, A, [M.panel, M.interior, M.panel, M.panel, M.corte, M.panel]).castShadow = true;  // testero este
    const techo = panel(0, L, H - e, H, 0, A, [M.panel, M.panel, M.panel, M.interior, M.corte, M.panel]);
    // juntas de los paneles en la pared norte (cara interior)
    for (let x = 1.0; x < L - 0.5; x += 1.0833) caja(x - 0.008, x + 0.008, z0 + e, H - e, A - e - 0.005, A - e, M.oscuro, false);
    // frente sur: abierto (solo columnas y largueros) o cerrado
    const frente = new THREE.Group();
    G.columnas.forEach((x) => {
      const c = new THREE.Mesh(new THREE.BoxGeometry(0.07, H - z0, 0.07), M.azul);
      c.position.copy(V(Math.min(Math.max(x, 0.04), L - 0.04), (z0 + H) / 2, 0.04)); frente.add(c);
    });
    const largTop = new THREE.Mesh(new THREE.BoxGeometry(L, 0.08, 0.08), M.azul);
    largTop.position.copy(V(L / 2, H - 0.04, 0.04)); frente.add(largTop);
    grupo.add(frente);
    const paredSur = new THREE.Mesh(new THREE.BoxGeometry(L, H - z0, e), M.panel);
    paredSur.position.copy(V(L / 2, (z0 + H) / 2, e / 2));
    paredSur.castShadow = true; paredSur.visible = false;
    grupo.add(paredSur);
    // hueco de la entrada de aire en la pared norte
    const hueco = new THREE.Mesh(new THREE.PlaneGeometry(G.entrada.x1 - G.entrada.x0, G.entrada.z1 - G.entrada.z0), M.hueco);
    hueco.position.copy(V((G.entrada.x0 + G.entrada.x1) / 2, (G.entrada.z0 + G.entrada.z1) / 2, A - e - 0.003));
    grupo.add(hueco);

    // pasarela del techo con baranda (como el visor)
    caja(0.2, L - 0.2, H, H + 0.03, 0.15, 1.15, M.rejilla, false);
    for (let x = 0.25; x <= L - 0.2; x += 1.6) {
      caja(x - 0.02, x + 0.02, H, H + 1.0, 0.08, 0.12, M.amarillo, true);
      caja(x - 0.02, x + 0.02, H, H + 1.0, 1.18, 1.22, M.amarillo, true);
    }
    [0.55, 1.0].forEach((dz) => {
      caja(0.2, L - 0.2, H + dz - 0.02, H + dz + 0.02, 0.08, 0.12, M.amarillo, true);
      caja(0.2, L - 0.2, H + dz - 0.02, H + dz + 0.02, 1.18, 1.22, M.amarillo, true);
    });
    caja(L - 0.24, L - 0.2, H + 0.98, H + 1.02, 0.08, 1.22, M.amarillo, true);
    // escalera marinera en el testero oeste
    [0.25, 0.75].forEach((y) => caja(-0.12, -0.07, 0, H + 1.0, y - 0.025, y + 0.025, M.amarillo, true));
    for (let z = 0.3; z < H + 0.9; z += 0.3) caja(-0.11, -0.08, z - 0.015, z + 0.015, 0.25, 0.75, M.amarillo, false);

    // campana y ducto de escape Ø800
    const campana = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 1.0, 0.45, 4, 1), M.galv);
    campana.rotation.y = Math.PI / 4; campana.position.copy(V(G.campana, H + 0.225, 1.75)); campana.castShadow = true; grupo.add(campana);
    cilindroZ(G.campana, 1.75, H + 0.45, H + 1.7, 0.4, M.galv).castShadow = true;
    const codo = new THREE.Mesh(new THREE.TorusGeometry(0.55, 0.4, 16, 24, Math.PI / 2), M.galv);
    codo.rotation.y = Math.PI / 2; codo.position.copy(V(G.campana, H + 1.7, 2.3)); codo.castShadow = true; grupo.add(codo);
    cilindroY(G.campana, H + 2.25, 2.3, 3.6, 0.4, M.galv).castShadow = true;

    // entrada de aire caliente (cara norte, bajo el piso 3) y ducto desde el generador
    caja(G.entrada.x0, G.entrada.x1, G.entrada.z0, G.entrada.z1, A, A + 0.9, M.galv, true);
    caja(G.entrada.x0, G.entrada.x1, G.entrada.z0, 2.2, A + 0.9, A + 1.3, M.galv, true);

    // tolva de alimentación y esparcidor en el techo
    caja(G.alimentacion - 0.3, G.alimentacion + 0.3, H, H + 0.55, 0.9, 1.7, M.galv, true);
    const tolva = new THREE.Mesh(new THREE.CylinderGeometry(0.62, 0.36, 0.5, 4, 1), M.galv);
    tolva.rotation.y = Math.PI / 4; tolva.position.copy(V(G.alimentacion, H + 0.8, 1.3)); tolva.castShadow = true; grupo.add(tolva);
    const esparcidor = cilindroY(G.esparcidor, G.pisos[0].zc + 0.32, 0.4, 2.2, 0.05, M.acero);
    const paletas = new THREE.Group();
    for (let i = 0; i < 4; i++) {
      const p = new THREE.Mesh(new THREE.BoxGeometry(0.015, 0.11, 1.7), M.acero);
      p.rotation.z = i * Math.PI / 4; paletas.add(p);
    }
    paletas.position.copy(V(G.esparcidor, G.pisos[0].zc + 0.32, 1.3));
    grupo.add(paletas);

    // descarga: tolva bajo el piso de la cámara y sinfín hacia el sur (MT-01, TT-05)
    const tolvaD = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 0.12, 0.25, 4, 1), M.galv);
    tolvaD.rotation.y = Math.PI / 4; tolvaD.position.copy(V(12.75, z0 - 0.13, 1.3)); grupo.add(tolvaD);
    cilindroY(12.75, 0.17, -0.8, 1.45, 0.11, M.galv).castShadow = true;
    cilindroY(12.75, 0.17, -0.95, -0.8, 0.13, M.motor);

    // ---------------------------------------------------------------- pisos: banda, tambores, guías, lecho
    const lechos = [], hitPisos = [];
    G.pisos.forEach((p, k) => {
      const xa = Math.min(p.cola, p.cabeza), xb = Math.max(p.cola, p.cabeza);
      const rC = G.rMotriz, rR = G.rReenvio;
      const zr = p.zc - 2 * Math.max(rC, rR) + 0.01;
      // banda superior y retorno
      const sup = caja(xa, xb, p.zc - 0.012, p.zc, 0.3, 2.3, M.banda, false);
      sup.receiveShadow = true;
      caja(xa + 0.1, xb - 0.1, zr - 0.012, zr, 0.3, 2.3, M.banda, false);
      // tambores (motriz en la cabeza, reenvío en la cola)
      cilindroY(p.cabeza, p.zc - rC, 0.22, 2.38, rC, M.acero);
      cilindroY(p.cola, p.zc - rR, 0.22, 2.38, rR, M.acero);
      // largueros de la banda
      caja(xa, xb, p.zc - 0.11, p.zc - 0.04, 0.2, 0.24, M.acero, false);
      caja(xa, xb, p.zc - 0.11, p.zc - 0.04, 2.36, 2.4, M.acero, false);
      // rodillos de retorno
      G.retorno.forEach((x) => cilindroY(x, zr - 0.055, 0.26, 2.34, 0.045, M.acero));
      // guías de UHMW-PE bajo el tramo de arriba
      G.guias.forEach((y) => caja(xa + 0.25, xb - 0.25, p.zc - 0.04, p.zc - 0.012, y - 0.02, y + 0.02, mGuia[k], false));
      // motorreductor en la cara norte, en la cabeza
      cilindroY(p.cabeza, p.zc - rC, A, A + 0.18, 0.07, M.acero);
      caja(p.cabeza - 0.17, p.cabeza + 0.17, p.zc - rC - 0.17, p.zc - rC + 0.17, A + 0.18, A + 0.42, M.motor, true);
      cilindroY(p.cabeza, p.zc - rC, A + 0.42, A + 0.8, 0.13, M.motor);
      caja(p.cabeza - 0.24, p.cabeza + 0.24, p.zc - rC - 0.24, p.zc - rC + 0.24, A + 0.02, A + 0.16, M.amarillo, true);
      // lecho (se arma en actualizar)
      const geo = new THREE.BufferGeometry();
      const mesh = new THREE.Mesh(geo, mLecho[k]);
      mesh.userData.piso = k;
      grupo.add(mesh);
      lechos.push(mesh);
      hitPisos.push(mesh);
    });

    // caídas de producto entre pisos y alimentación (chorros animados)
    function cortina(x, zA, zB, ya, yb, mat) {
      const m = new THREE.Mesh(new THREE.PlaneGeometry(yb - ya, zA - zB), mat);
      m.rotation.y = Math.PI / 2;
      m.position.copy(V(x, (zA + zB) / 2, (ya + yb) / 2));
      m.renderOrder = 2;
      grupo.add(m);
      return m;
    }
    const chorros = [
      cortina(G.esparcidor + 0.06, G.H - 0.1, G.pisos[0].zc + 0.12, 0.45, 2.15, mChorro[0]),     // tolva → piso 1
      cortina(12.56, G.pisos[0].zc - 0.02, G.pisos[1].zc + 0.12, 0.4, 2.2, mChorro[1]),           // piso 1 → piso 2
      cortina(0.44, G.pisos[1].zc - 0.02, G.pisos[2].zc + 0.1, 0.4, 2.2, mChorro[2]),             // piso 2 → piso 3
      cortina(12.62, G.pisos[2].zc - 0.02, z0 + e, 0.5, 2.1, mChorro[3]),                         // piso 3 → descarga
    ];
    chorros.forEach((c, i) => { c.material.map.repeat.set(1, (i === 0 ? 0.55 : 0.85)); });

    // ---------------------------------------------------------------- aire: partículas
    const ancho = cont.clientWidth || 800;
    const N = ancho < 600 ? 650 : 1150;
    const pos = new Float32Array(3 * N), col = new Float32Array(3 * N);
    const part = [];
    const puntoTex = lienzo(64, 64, (c, w, h) => {
      const g = c.createRadialGradient(w / 2, h / 2, 0, w / 2, h / 2, w / 2);
      g.addColorStop(0, "rgba(255,255,255,1)"); g.addColorStop(0.45, "rgba(255,255,255,0.9)"); g.addColorStop(1, "rgba(255,255,255,0)");
      c.fillStyle = g; c.fillRect(0, 0, w, h);
    });
    const geoP = new THREE.BufferGeometry();
    geoP.setAttribute("position", new THREE.BufferAttribute(pos, 3));
    geoP.setAttribute("color", new THREE.BufferAttribute(col, 3));
    const mP = new THREE.PointsMaterial({ size: 0.42, map: puntoTex, vertexColors: true, transparent: true, depthWrite: false, opacity: 0.95, sizeAttenuation: true, alphaTest: 0.02 });
    const puntos = new THREE.Points(geoP, mP);
    puntos.renderOrder = 3;
    scene.add(puntos);
    let semilla = 987654;
    const azar = () => { semilla = (semilla * 16807) % 2147483647; return semilla / 2147483647; };

    // ---------------------------------------------------------------- estado de los datos
    let R = null, FILAS = null, X_ANCHO = [], gDist = null, borde = 0, bypPiso = 0.05;
    const perfilT = [null, null, null];     // aire que sale de cada piso a lo largo de x de planta
    function sAx(k, s) { const p = G.pisos[k]; return p.cola + (p.cabeza - p.cola) * s / 12; }
    function interpX(k, x, arr) {            // valor de un perfil (por posición de banda) en la x de planta
      if (!arr) return 0;
      const p = G.pisos[k], n = arr.length;
      let s = (x - p.cola) / (p.cabeza - p.cola) * 12;
      s = Math.max(0, Math.min(12, s));
      const f = s / 12 * n - 0.5, i = Math.max(0, Math.min(n - 1, Math.floor(f))), j = Math.min(n - 1, i + 1), u = Math.max(0, Math.min(1, f - i));
      return arr[i] + u * (arr[j] - arr[i]);
    }
    function nuevaParticula(i, inicio) {
      const q = part[i] || (part[i] = {});
      const lateral = azar() < 0.06 + 0.9 * borde;
      q.borde = lateral;
      q.y = lateral ? (azar() < 0.5 ? 0.1 + 0.18 * azar() : A - 0.28 + 0.16 * azar()) : 0.35 + 1.9 * azar();
      if (inicio) {
        q.fase = 1; q.x = 0.3 + 12.4 * azar(); q.z = z0 + 0.1 + (H - z0 - 0.3) * azar();
      } else {
        q.fase = 0; q.x = G.entrada.x0 + (G.entrada.x1 - G.entrada.x0) * azar(); q.z = G.entrada.z0 + 0.05 + 0.3 * azar();
        q.tx = 0.3 + 12.4 * azar(); q.yv = A - e;
      }
      q.v = 0.75 + 0.5 * azar();
      return q;
    }
    for (let i = 0; i < N; i++) nuevaParticula(i, true);
    const tmp = [0, 0, 0];
    function tempAire(q) {
      const z = q.z, Tin = R.Tin, P = G.pisos;
      if (q.borde && borde > 0) return Tin[2];                 // sube por los bordes sin tocar el guano
      if (z < P[2].zc) return Tin[2];
      const zonas = [[P[2].zc, P[1].zc, 2, Tin[1]], [P[1].zc, P[0].zc, 1, Tin[0]], [P[0].zc, H, 0, R.T_exh]];
      for (const [za, zb, k, Tm] of zonas) if (z < zb || k === 0) {
        if (q.borde) return Tm;
        const Tl = interpX(k, q.x, perfilT[k]);
        const u = Math.max(0, Math.min(1, (z - za) / (zb - za)));
        return Tl + (Tm - Tl) * (u * u * (3 - 2 * u));
      }
      return R.T_exh;
    }
    function velocidad(q) {
      if (!gDist || q.borde) return 1;
      const P = G.pisos;
      const k = q.z < P[2].zc ? 2 : q.z < P[1].zc ? 1 : q.z < P[0].zc ? 0 : -1;
      return k < 0 ? 1 : Math.max(0.35, Math.min(2.2, interpX(k, q.x, gDist[k])));
    }
    function moverParticulas(dt) {
      for (let i = 0; i < N; i++) {
        const q = part[i];
        if (q.fase === 0) {                 // chorro que entra por la cara norte y se reparte en el plenum
          const d = q.tx - q.x;
          q.x += Math.sign(d) * Math.min(Math.abs(d), 2.6 * q.v * dt);
          q.yv += ((q.y) - q.yv) * Math.min(1, 1.5 * dt);
          if (Math.abs(d) < 0.05) { q.fase = 1; }
        } else if (q.fase === 1) {          // sube atravesando los pisos
          q.z += 0.42 * q.v * velocidad(q) * dt;
          if (q.z > H - 0.2) { q.fase = 2; }
        } else {                            // campana → ducto de escape
          const dx = G.campana - q.x, dy = 1.75 - q.y;
          const d = Math.hypot(dx, dy);
          if (d > 0.25) { q.x += dx / d * 1.6 * dt; q.y += dy / d * 1.6 * dt; q.z = Math.min(H - 0.08, q.z + 0.05 * dt); }
          else { q.z += 1.4 * dt; if (q.z > H + 1.6) nuevaParticula(i, false); }
        }
      }
    }
    function escribirParticulas() {
      if (!R) return;
      for (let i = 0; i < N; i++) {
        const q = part[i];
        const y = q.fase === 0 ? q.yv : q.y;
        const v = V(q.x, q.z, y);
        pos[3 * i] = v.x; pos[3 * i + 1] = v.y; pos[3 * i + 2] = v.z;
        colorT(tempAire(q), tmp);
        col[3 * i] = tmp[0]; col[3 * i + 1] = tmp[1]; col[3 * i + 2] = tmp[2];
      }
      geoP.attributes.position.needsUpdate = true;
      geoP.attributes.color.needsUpdate = true;
    }

    // ---------------------------------------------------------------- lecho de guano
    function rgb(h) { const m = colorGuano(h).match(/\d+/g); return [m[0] / 255, m[1] / 255, m[2] / 255]; }
    function armarLecho(k, filas, nz) {
      const p = G.pisos[k];
      const f = filas.filter((q) => q.piso === k);
      if (!f.length) return;
      const pts = f.map((q, i) => ({
        x: sAx(k, q.x - 12 * k), Hm: Math.max(0.004, (q.H || (f[i + 1] && f[i + 1].H) || 0.02)) * EXAG,
        capas: q.capas ? Array.from(q.capas, (X) => rgb(X / (1 + X))) : null, c: rgb(q.h),
      }));
      pts.forEach((q) => { if (!q.capas) q.capas = Array.from({ length: nz }, () => q.c); });
      const nY = 9;
      const P = [], C = [], U = [];
      const zTop = (i, j) => p.zc + pts[i].Hm * (1 + 0.16 * RUIDO[(i * 31 + j * 7 + k * 101) % RUIDO.length]);
      const yj = (j) => Y0 + (Y1 - Y0) * j / (nY - 1);
      function tri(a, b, c2, ca, cb, cc, ua, ub, uc) {
        P.push(...a, ...b, ...c2); C.push(...ca, ...cb, ...cc); U.push(...ua, ...ub, ...uc);
      }
      const vv = (x, z, y) => { const t = V(x, z, y); return [t.x, t.y, t.z]; };
      for (let i = 0; i < pts.length - 1; i++) {
        const a = pts[i], b = pts[i + 1];
        const ca = a.capas[nz - 1], cb = b.capas[nz - 1];
        // cara de arriba (la capa de arriba es la que se ve)
        for (let j = 0; j < nY - 1; j++) {
          const p00 = vv(a.x, zTop(i, j), yj(j)), p01 = vv(a.x, zTop(i, j + 1), yj(j + 1));
          const p10 = vv(b.x, zTop(i + 1, j), yj(j)), p11 = vv(b.x, zTop(i + 1, j + 1), yj(j + 1));
          const u0 = [a.x * 2, yj(j) * 2], u1 = [a.x * 2, yj(j + 1) * 2], u2 = [b.x * 2, yj(j) * 2], u3 = [b.x * 2, yj(j + 1) * 2];
          tri(p00, p10, p11, ca, cb, cb, u0, u2, u3);
          tri(p00, p11, p01, ca, cb, ca, u0, u3, u1);
        }
        // cara del frente (sur): las capas, de abajo (seca) a arriba (húmeda)
        for (let l = 0; l < nz; l++) {
          const za0 = p.zc + (zTop(i, 0) - p.zc) * l / nz, za1 = p.zc + (zTop(i, 0) - p.zc) * (l + 1) / nz;
          const zb0 = p.zc + (zTop(i + 1, 0) - p.zc) * l / nz, zb1 = p.zc + (zTop(i + 1, 0) - p.zc) * (l + 1) / nz;
          const q00 = vv(a.x, za0, Y0), q01 = vv(a.x, za1, Y0), q10 = vv(b.x, zb0, Y0), q11 = vv(b.x, zb1, Y0);
          const c1 = a.capas[l], c2 = b.capas[l];
          const ua = [a.x * 2, za0 * 8], ub = [b.x * 2, zb0 * 8], uc = [b.x * 2, zb1 * 8], ud = [a.x * 2, za1 * 8];
          tri(q00, q11, q10, c1, c2, c2, ua, uc, ub);
          tri(q00, q01, q11, c1, c1, c2, ua, ud, uc);
        }
        // cara de atrás (norte)
        const r00 = vv(a.x, p.zc, Y1), r01 = vv(a.x, zTop(i, nY - 1), Y1), r10 = vv(b.x, p.zc, Y1), r11 = vv(b.x, zTop(i + 1, nY - 1), Y1);
        tri(r00, r10, r11, a.capas[0], b.capas[0], cb, [0, 0], [1, 0], [1, 1]);
        tri(r00, r11, r01, a.capas[0], cb, ca, [0, 0], [1, 1], [0, 1]);
      }
      // tapas en los extremos
      [0, pts.length - 1].forEach((i) => {
        const q = pts[i];
        for (let l = 0; l < nz; l++) {
          const z0l = p.zc + q.Hm * l / nz, z1l = p.zc + q.Hm * (l + 1) / nz;
          const a1 = vv(q.x, z0l, Y0), a2 = vv(q.x, z0l, Y1), a3 = vv(q.x, z1l, Y1), a4 = vv(q.x, z1l, Y0);
          const c = q.capas[l];
          tri(a1, a2, a3, c, c, c, [0, 0], [1, 0], [1, 1]);
          tri(a1, a3, a4, c, c, c, [0, 0], [1, 1], [0, 1]);
        }
      });
      const geo = new THREE.BufferGeometry();
      geo.setAttribute("position", new THREE.Float32BufferAttribute(P, 3));
      geo.setAttribute("color", new THREE.Float32BufferAttribute(C, 3));
      geo.setAttribute("uv", new THREE.Float32BufferAttribute(U, 2));
      geo.computeVertexNormals();
      lechos[k].geometry.dispose();
      lechos[k].geometry = geo;
      lechos[k].userData.pts = f;
    }

    // ---------------------------------------------------------------- etiquetas
    const etq = {};
    function etiqueta(id, clase, ancla) {
      const d = document.createElement("div");
      d.className = "v3d-etq " + (clase || "");
      capaEtq.appendChild(d);
      etq[id] = { el: d, p: new THREE.Vector3(), ancla: ancla || "arriba" };
      return etq[id];
    }
    etiqueta("alim").p.copy(V(G.alimentacion, H + 1.15, 1.3));
    etiqueta("tt02").p.copy(V(G.campana, H + 2.7, 2.3));
    etiqueta("tt01").p.copy(V(11.0, (G.entrada.z0 + G.entrada.z1) / 2, A - e - 0.06));
    etiqueta("desc").p.copy(V(12.75, 0.05, -0.9));
    [0, 1, 2].forEach((k) => etiqueta("p" + k, "piso", "derecha").p.copy(V(L + 0.05, G.pisos[k].zc - 0.05, -0.12)));
    const proy = new THREE.Vector3(), dirEtq = new THREE.Vector3(), rayEtq = new THREE.Raycaster();
    const tapan = grupo.children.filter((m) => m.isMesh && m.geometry && m.geometry.type === "BoxGeometry" &&
      m.geometry.parameters && Math.max(m.geometry.parameters.width, m.geometry.parameters.height, m.geometry.parameters.depth) > 2.5 &&
      Math.min(m.geometry.parameters.width, m.geometry.parameters.height, m.geometry.parameters.depth) >= G.e - 1e-6);
    function tapada(o) {
      dirEtq.copy(o.p).sub(camera.position);
      const d = dirEtq.length();
      rayEtq.set(camera.position, dirEtq.normalize());
      rayEtq.far = d - 0.05;
      return rayEtq.intersectObjects(tapan.filter((m) => m.visible), false).length > 0;
    }
    // orden de prioridad: si dos etiquetas se pisan, se oculta la de menos prioridad
    const PRIORIDAD = ["desc", "tt02", "p0", "p1", "p2", "alim", "tt01"];
    function posicionarEtiquetas() {
      const w = lienzo3d.clientWidth, h = lienzo3d.clientHeight;
      const puestas = [];
      PRIORIDAD.map((id) => etq[id]).forEach((o) => {
        proy.copy(o.p).project(camera);
        const fuera = proy.z > 1 || Math.abs(proy.x) > 1.05 || Math.abs(proy.y) > 1.05 || tapada(o);
        o.el.style.visibility = fuera || !o.el.textContent ? "hidden" : "visible";
        if (fuera) return;
        // que la etiqueta no se salga del dibujo
        const ew = o.ew || (o.ew = o.el.offsetWidth), eh = o.eh || (o.eh = o.el.offsetHeight);
        const px = (proy.x + 1) / 2 * w, py = (1 - proy.y) / 2 * h;
        let x = o.ancla === "derecha" ? px + 6 : px - ew / 2, y = o.ancla === "derecha" ? py - eh / 2 : py - eh - 6;
        x = Math.max(4, Math.min(w - ew - 4, x)); y = Math.max(4, Math.min(h - eh - 4, y));
        if (puestas.some((q) => x < q[0] + q[2] + 3 && q[0] < x + ew + 3 && y < q[1] + q[3] + 2 && q[1] < y + eh + 2)) {
          o.el.style.visibility = "hidden";
          return;
        }
        puestas.push([x, y, ew, eh]);
        o.el.style.transform = `translate(${x.toFixed(1)}px, ${y.toFixed(1)}px)`;
      });
    }

    // ---------------------------------------------------------------- tamaño y bucle
    let W = 0, Hh = 0, sucio = true, animar = !reducido, visible = true;
    // distancia de la vista inicial para que entre todo el largo del secador (pantallas angostas)
    function distanciaEncuadre() {
      const t = Math.tan(THREE.MathUtils.degToRad(camera.fov / 2));
      return Math.max(D0, (G.L / 2 + 1.4) / (t * camera.aspect));
    }
    let tocada = false;
    controls.addEventListener("start", () => { tocada = true; });
    function medir() {
      const w = cont.clientWidth;
      const h = Math.round(Math.max(300, Math.min(560, w < 640 ? w * 1.0 : w * 0.56)));
      if (w === W && h === Hh) return;
      W = w; Hh = h;
      Object.values(etq).forEach((o) => { o.ew = 0; o.eh = 0; });
      renderer.setSize(w, h, false);
      lienzo3d.style.width = w + "px"; lienzo3d.style.height = h + "px";
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      if (!tocada) volver();
      sucio = true;
    }
    new ResizeObserver(medir).observe(cont);
    medir();
    if ("IntersectionObserver" in window) new IntersectionObserver((en) => { visible = en[0].isIntersecting; }).observe(cont);
    controls.addEventListener("change", () => { sucio = true; });
    let tPrev = performance.now();
    function bucle(t) {
      requestAnimationFrame(bucle);
      const dt = Math.min(0.05, (t - tPrev) / 1000);
      tPrev = t;
      if (!visible || document.hidden) return;
      controls.update();
      if (animar && R) {
        moverParticulas(dt);
        chorros.forEach((c) => { c.material.map.offset.y += 0.55 * dt; });
        paletas.rotation.z -= 2.2 * dt;
        sucio = true;
      }
      if (sucio) {
        escribirParticulas();
        renderer.render(scene, camera);
        posicionarEtiquetas();
        sucio = false;
      }
    }
    requestAnimationFrame(bucle);

    // ---------------------------------------------------------------- puntero: valores sobre el lecho
    const ray = new THREE.Raycaster(), mouse = new THREE.Vector2();
    const tip = opc.tip;
    lienzo3d.addEventListener("pointermove", (ev) => {
      if (!R || ev.buttons) { if (tip) tip.hidden = true; return; }
      const b = lienzo3d.getBoundingClientRect();
      mouse.set((ev.clientX - b.left) / b.width * 2 - 1, -(ev.clientY - b.top) / b.height * 2 + 1);
      ray.setFromCamera(mouse, camera);
      const hit = ray.intersectObjects(hitPisos, false)[0];
      if (!hit || !tip) { if (tip) tip.hidden = true; return; }
      const k = hit.object.userData.piso, pts = hit.object.userData.pts;
      const x = hit.point.x + G.L / 2, pz = G.pisos[k];
      const s = Math.max(0, Math.min(12, (x - pz.cola) / (pz.cabeza - pz.cola) * 12));
      let f = pts[0];
      pts.forEach((q) => { if (Math.abs(q.x - 12 * k - s) < Math.abs(f.x - 12 * k - s)) f = q; });
      tip.innerHTML = `<b>Piso ${k + 1} · ${fmt(s, 1)} m de banda</b>` +
        `<div class="fila"><span>tiempo desde la entrada</span><span>${fmt(f.t)} min</span></div>` +
        `<div class="fila"><span>humedad media</span><span>${fmt(100 * f.h, 1)} %</span></div>` +
        `<div class="fila"><span>capas: de / a</span><span>${fmt(100 * f.hmin, 1)} – ${fmt(100 * f.hmax, 1)} %</span></div>` +
        `<div class="fila"><span>guano</span><span>${fmt(f.T)} °C</span></div>` +
        `<div class="fila"><span>aire bajo la banda</span><span>${fmt(f.Tin)} °C</span></div>` +
        `<div class="fila"><span>aire que sale arriba</span><span>${fmt(f.Ta)} °C</span></div>`;
      tip.hidden = false;
      const caja = cont.getBoundingClientRect();
      let left = ev.clientX - caja.left + 14;
      if (left + 250 > caja.width) left = ev.clientX - caja.left - 260;
      tip.style.left = left + "px"; tip.style.top = (ev.clientY - caja.top + 14) + "px";
    });
    lienzo3d.addEventListener("pointerleave", () => { if (tip) tip.hidden = true; });
    lienzo3d.addEventListener("dblclick", () => volver());

    function volver() {
      controls.target.copy(OBJETIVO);
      camera.position.copy(OBJETIVO).addScaledVector(DIR0, distanciaEncuadre());
      controls.update(); sucio = true;
    }

    // ---------------------------------------------------------------- API
    function actualizar(r, filas, extra) {
      R = r; FILAS = filas;
      const nz = (r.perfiles[0].capas ? r.perfiles[0].capas.length / r.perfiles[0].x.length : 5) | 0;
      for (let k = 0; k < 3; k++) {
        armarLecho(k, filas, nz);
        const pf = r.perfiles[k];
        perfilT[k] = Array.from(pf.Taout);
      }
      gDist = r.estado && r.estado.g ? r.estado.g.map((g) => Array.from(g)) : null;
      borde = (extra && extra.borde) || 0;
      // reparto de partículas por los bordes según el aire que se escapa
      for (let i = 0; i < N; i++) if (part[i].fase === 1 && azar() < 0.15) nuevaParticula(i, true);
      // guías: color según el aire que tienen debajo
      r.Tin.forEach((T, k) => {
        const m = mGuia[k];
        if (T >= extra.uhmwFusion) { m.color.setHex(0xd03b3b); m.emissive.setHex(0x5c1010); }
        else if (T >= extra.uhmwContinuo) { m.color.setHex(0xf08a24); m.emissive.setHex(0x4a2300); }
        else { m.color.setHex(0xefefea); m.emissive.setHex(0x000000); }
      });
      // color de los chorros: humedad al caer
      const hEnt = r.X_feed / (1 + r.X_feed);
      const hk = [0, 1, 2].map((k) => { const f = filas.filter((q) => q.piso === k && !q.borde); return f.length ? f[f.length - 1].h : hEnt; });
      [hEnt, hk[0], hk[1], hk[2]].forEach((h, i) => { const c = rgb(h); mChorro[i].color.setRGB(c[0], c[1], c[2]); });
      // etiquetas
      const sat = (hrx, niebla) => niebla > 1e-5 ? "saturado, con niebla" : `HR ${fmt(100 * hrx)} %`;
      etq.alim.el.innerHTML = `<b>Guano</b> ${fmt(extra.alimentacion)} kg/h · ${fmt(100 * hEnt)} %`;
      etq.tt02.el.innerHTML = `<b>TT-02</b> escape ${fmt(r.T_exh)} °C · ${sat(r.HR_exh, r.niebla_exh)}`;
      etq.tt01.el.innerHTML = `<b>TT-01</b> aire ${fmt(extra.T_aire)} °C`;
      etq.desc.el.innerHTML = `<b>MT-01</b> ${r.hum_out < 0.02 ? "< 2" : fmt(100 * r.hum_out, 1)} % · <b>TT-05</b> ${fmt(r.T_prod_out)} °C`;
      [0, 1, 2].forEach((k) => {
        const T = r.Tin[k], cl = T >= extra.uhmwFusion ? "critico" : T >= extra.uhmwContinuo ? "serio" : "";
        const e2 = etq["p" + k].el;
        e2.className = "v3d-etq piso " + cl;
        e2.innerHTML = `<b>Piso ${k + 1}</b> aire ${fmt(T)} °C`;
      });
      Object.values(etq).forEach((o) => { o.ew = 0; o.eh = 0; });
      lienzo3d.setAttribute("aria-label", `Secador SC-4 en 3D: el guano entra al ${fmt(100 * hEnt)} % y sale al ${r.hum_out < 0.02 ? "menos de 2" : fmt(100 * r.hum_out, 1)} %; ` +
        `aire de entrada ${fmt(extra.T_aire)} °C, escape ${fmt(r.T_exh)} °C.`);
      sucio = true;
    }
    return {
      actualizar,
      volver,
      frente: (cerrado) => { paredSur.visible = cerrado; sucio = true; },
      animar: (si) => { animar = si && !reducido; sucio = true; },
      animando: () => animar,
      reducido,
      colorT: cssT,
    };
  }

  root.Vista3D = { crear, colorT: cssT, RAMPA_T };
})(typeof self !== "undefined" ? self : this);
