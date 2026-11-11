/* Modelo del secador de guano SC-4 — versión JavaScript del paquete Python `secado`.
 * Mismas ecuaciones que secado/psicrometria.py, guano.py, nucleo.py y secador.py.
 * Se usa en el simulador web; validar_js.py compara sus resultados con los de Python.
 */
(function (root) {
  "use strict";
  const CPA = 1006.0, CPV = 1860.0, CPW = 4186.0, LAMBDA0 = 2.501e6, MW = 0.621945;
  const RGAS = 8.314, RHO_W = 1000.0;

  // ------------------------------------------------------------------ psicrometría
  function psat(T) {
    let Tk = T + 273.15;
    if (Tk < 273.16) Tk = 273.16;
    const ln = -5.8002206e3 / Tk + 1.3914993 - 4.8640239e-2 * Tk + 4.1764768e-5 * Tk * Tk
      - 1.4452093e-8 * Tk * Tk * Tk + 6.5459673 * Math.log(Tk);
    return Math.exp(ln);
  }
  function YdePv(pv, P) { if (pv >= 0.999 * P) pv = 0.999 * P; return MW * pv / (P - pv); }
  function pvdeY(Y, P) { return P * Y / (MW + Y); }
  function Ysat(T, P) { return YdePv(psat(T), P); }
  function hr(T, Y, P) { return pvdeY(Y, P) / psat(T); }
  function entalpia(T, Y) { return CPA * T + Y * (LAMBDA0 + CPV * T); }
  function tempDeEntalpia(h, Y) { return (h - LAMBDA0 * Y) / (CPA + CPV * Y); }
  function hfg(T) { return LAMBDA0 + (CPV - CPW) * T; }
  function bulboHumedo(T, Y, P) {
    const h = entalpia(T, Y); let lo = -10, hi = Math.min(T, 99);
    for (let i = 0; i < 60; i++) {
      const tw = 0.5 * (lo + hi), ys = Ysat(tw, P);
      const g = entalpia(tw, ys) - (ys - Y) * CPW * tw - h;
      if (g > 0) hi = tw; else lo = tw;
    }
    return 0.5 * (lo + hi);
  }
  // estado real de un aire con más agua que la de saturación: el exceso es niebla (misma entalpía)
  function saturar(T, Y, P) {
    if (Y <= Ysat(T, P)) return [T, Y, 0];
    const h = entalpia(T, Y);
    let lo = T, hi = T + 40;
    for (let i = 0; i < 60; i++) {
      const t = 0.5 * (lo + hi), ys = Ysat(t, P);
      if (entalpia(t, ys) + (Y - ys) * CPW * t - h > 0) hi = t; else lo = t;
    }
    const t = 0.5 * (lo + hi), ys = Ysat(t, P);
    return [t, ys, Y - ys];
  }
  function puntoRocio(Y, P) {
    const pv = pvdeY(Y, P); let lo = 0.01, hi = 150;
    for (let i = 0; i < 60; i++) { const t = 0.5 * (lo + hi); if (psat(t) > pv) hi = t; else lo = t; }
    return 0.5 * (lo + hi);
  }
  function rhoAire(T, Y, P) { return P / (287.055 * (T + 273.15)) * (1 + Y) / (1 + 1.6078 * Y); }
  function muAire(T) { const Tk = T + 273.15; return 1.716e-5 * Math.pow(Tk / 273.15, 1.5) * (273.15 + 110.4) / (Tk + 110.4); }
  function kAire(T) { return 0.0241 * Math.pow((T + 273.15) / 273.15, 0.81); }
  function difVapor(T, P) { const Tk = T + 273.15; return 1.87e-10 * Math.pow(Tk, 2.072) / (P / 101325.0); }

  // ------------------------------------------------------------------ guano
  function gab(T, p) {
    const Xm = p.xm25 * Math.exp(p.xmdt * (T - 25));
    const C = p.c25 * Math.exp(p.ch * (1 / (T + 273.15) - 1 / 298.15));
    return [Xm, C, p.k];
  }
  function humedadEquilibrio(aw, T, p) {
    const [Xm, C, K] = gab(T, p); if (aw > 0.999) aw = 0.999; const u = K * aw;
    return Xm * C * u / ((1 - u) * (1 - u + C * u));
  }
  function actividadAgua(X, T, p) {
    if (X <= 0) return 0;
    const [Xm, C, K] = gab(T, p);
    const a = X * (C - 1), b = X * (C - 2) - Xm * C;
    const u = (b + Math.sqrt(b * b + 4 * a * X)) / (2 * a);
    const aw = u / K; return aw > 1 ? 1 : aw;
  }
  function factorSorcion(X, p) { if (X < 0) X = 0; return 1 + p.sa * Math.exp(-p.sb * X); }
  function difusividad(T, X, p) {
    if (X < 0) X = 0;
    return p.dref * Math.exp(p.db * (X - p.xdref)) * Math.exp(-p.ea / RGAS * (1 / (T + 273.15) - 1 / (p.tref + 273.15)));
  }
  function volParticula(X, p) {
    const vp0 = (1 + p.x0) / p.rhop0;
    let vp = vp0 - p.betap * (p.x0 - X) / RHO_W;
    const vmin = 1 / 1500 + Math.max(X, 0) / RHO_W;
    return vp < vmin ? vmin : vp;
  }
  function volLecho(X, p) {
    const vb0 = (1 + p.x0) / p.rhob0, vbf = (1 + p.xf_ref) / p.rhobf;
    const beta = (vb0 - vbf) / (p.x0 - p.xf_ref);
    let vb = vb0 - beta * (p.x0 - X);
    const vp = volParticula(X, p);
    if (vb < vp / 0.85) vb = vp / 0.85;
    return vb;
  }
  function diametro(X, p) { const vp0 = (1 + p.x0) / p.rhop0; return p.d0 * Math.cbrt(volParticula(X, p) / vp0); }
  function porosidad(X, p) {
    let e = 1 - volParticula(X, p) / volLecho(X, p);
    if (e < 0.15) e = 0.15; if (e > 0.6) e = 0.6; return e;
  }

  // ------------------------------------------------------------------ capa (igual a nucleo.capa)
  const R_ = new Float64Array(11);
  function capa(Xj, Tj, m, Ta, Ya, G, p, P, nbis) {
    const vp = volParticula(Xj, p), d = diametro(Xj, p), eps = porosidad(Xj, p), vb = volLecho(Xj, p);
    const As = 6 * vp / d, Acapa = m * As, H = m * vb;
    const rho = rhoAire(Ta, Ya, P), mu = muAire(Ta), ka = kAire(Ta), Dva = difVapor(Ta, P);
    const u = G * (1 + Ya) / rho, Re = rho * u * d / mu, Pr = 1006 * mu / ka, Sc = mu / (rho * Dva);
    const f06 = 1.1 * Math.pow(Re, 0.6);
    const Nu = 2 + f06 * Math.cbrt(Pr), Sh = 2 + f06 * Math.cbrt(Sc);
    const h = Nu * ka / d, ky = Sh * Dva / d * rho / (1 + Ya), cs = 1006 + 1860 * Ya;
    const NTUh = h * Acapa / (G * cs), NTUm = ky * Acapa / G;
    const phih = 1 - Math.exp(-NTUh), phim = 1 - Math.exp(-NTUm);
    const R = 0.5 * d, kL = 15 * difusividad(Tj, Xj, p) / (R * R);
    const ps = psat(Tj), pvmax = 0.95 * P, ysat_s = YdePv(Math.min(ps, pvmax), P);
    let E, Xs;
    if (ysat_s <= Ya) { E = G * phim * (ysat_s - Ya); Xs = Xj; }
    else {
      let lo = 0, hi = Xj + 50;
      for (let i = 0; i < nbis; i++) {
        const mid = 0.5 * (lo + hi), aw = actividadAgua(mid, Tj, p);
        const ys = YdePv(Math.min(aw * ps, pvmax), P);
        const f = m * kL * (Xj - mid) - G * phim * (ys - Ya);
        if (f > 0) lo = mid; else hi = mid;
      }
      Xs = 0.5 * (lo + hi); E = m * kL * (Xj - Xs);
    }
    const Tout = Tj + (Ta - Tj) * Math.exp(-NTUh);
    let Yout = Ya + E / G;
    const ylim = Ysat(Tout, P);
    if (Yout > ylim && E > 0) { Yout = Math.max(ylim, Ya); E = G * (Yout - Ya); }
    if (Yout < 0) Yout = 0;
    const Qconv = G * (entalpia(Ta, Ya) - entalpia(Tout, Yout)) + E * (LAMBDA0 + CPV * Tj);
    const cap = m * (p.cps + CPW * Xj);
    const lat = ysat_s > Ya ? hfg(Tj) * factorSorcion(Xs, p) : hfg(Tj);
    const S = E * (lat - hfg(Tj));
    const dTdt = (Qconv - E * lat) / cap;
    const dlnps = hfg(Tj) / (461.5 * (Tj + 273.15) * (Tj + 273.15));
    const awm = actividadAgua(Xs, Tj, p), pvs = awm * ps;
    let dYdT = 0, dYdX = 0;
    if (pvs < pvmax) {
      const fac = 0.621945 * P / ((P - pvs) * (P - pvs));
      dYdT = fac * pvs * dlnps;
      const dX = 1e-3 + 1e-3 * Xs;
      dYdX = fac * ps * (actividadAgua(Xs + dX, Tj, p) - awm) / dX;
    }
    const ext = G * phim;
    const dEdT = m * kL * ext * dYdT / (m * kL + ext * dYdX + 1e-30);
    const tau = cap / (G * cs * phih + hfg(Tj) * dEdT + 1e-12);
    const e3 = eps * eps * eps;
    const A = H * 150 * mu * (1 - eps) * (1 - eps) / (e3 * d * d);
    const B = H * 1.75 * rho * (1 - eps) / (e3 * d);
    R_[0] = E; R_[1] = Tout; R_[2] = Yout; R_[3] = Qconv; R_[4] = dTdt; R_[5] = Xs; R_[6] = tau;
    R_[7] = A; R_[8] = B; R_[9] = H; R_[10] = S;
    return R_;
  }

  // ------------------------------------------------------------------ un piso
  function avanzarPiso(X, Tp, hig, TaIn, YaIn, g, wdm, Gmed, L, v, nx, p, out, opt) {
    const nz = X.length, P = p.P, byp = p.byp, d70 = p.d70, zs = p.z;
    const dt = L / (v * nx), dx = L / nx, m = wdm / nz, hIn = entalpia(TaIn, YaIn);
    const nbis = opt.nbis;
    let sumG = 0, sumGh = 0, sumGY = 0, sumE = 0, sumQ = 0, sumS = 0, nsub = 25, t = 0;
    for (let i = 0; i < nx; i++) {
      const Gloc = Gmed * g[i], G = (1 - byp) * Gloc, dts = dt / nsub;
      let accH = 0, accY = 0, accE = 0, accQ = 0, accS = 0, tauMin = 1e30, Aerg = 0, Berg = 0, Htot = 0;
      for (let s = 0; s < nsub; s++) {
        let Ta = TaIn, Ya = YaIn, Ecol = 0, Qcol = 0, Scol = 0;
        for (let j = 0; j < nz; j++) {
          const r = capa(X[j], Tp[j], m, Ta, Ya, G, p, P, nbis);
          const E = r[0];
          X[j] -= E * dts / m; if (X[j] < 0) X[j] = 0;
          Tp[j] += r[4] * dts;
          const Tj = Tp[j];
          if (hig) {
            const o = j * 4;
            if (Tj >= 55) hig[o] += dts;
            if (Tj >= 70) hig[o + 1] += dts;
            hig[o + 2] += dts / 60 * Math.pow(10, (Tj - 70) / 10);
            if (Tj >= 50) hig[o + 3] += dts / 60 / (d70 * Math.pow(10, (70 - Tj) / zs));
          }
          if (r[6] < tauMin) tauMin = r[6];
          if (s === 0) { Aerg += r[7]; Berg += r[8]; Htot += r[9]; }
          Ecol += E; Qcol += r[3]; Scol += r[10];
          Ta = r[1]; Ya = r[2];
        }
        accH += entalpia(Ta, Ya); accY += Ya; accE += Ecol; accQ += Qcol; accS += Scol;
      }
      t += dt;
      const hTr = accH / nsub, YTr = accY / nsub;
      const hMix = (1 - byp) * hTr + byp * hIn, YMix = (1 - byp) * YTr + byp * YaIn;
      sumG += Gloc; sumGh += Gloc * hMix; sumGY += Gloc * YMix;
      sumE += accE / nsub; sumQ += accQ / nsub; sumS += accS / nsub;
      if (out) {
        let xm = 0, tm = 0, xmn = 1e9, xmx = -1e9, tmn = 1e9, tmx = -1e9;
        for (let j = 0; j < nz; j++) {
          xm += X[j]; tm += Tp[j];
          if (X[j] < xmn) xmn = X[j]; if (X[j] > xmx) xmx = X[j];
          if (Tp[j] < tmn) tmn = Tp[j]; if (Tp[j] > tmx) tmx = Tp[j];
        }
        out.x[i] = (i + 1) * dx; out.t[i] = t;
        out.Xmed[i] = xm / nz; out.Xmin[i] = xmn; out.Xmax[i] = xmx;
        out.Tmed[i] = tm / nz; out.Tmin[i] = tmn; out.Tmax[i] = tmx;
        out.Taout[i] = (hTr - LAMBDA0 * YTr) / (1006 + 1860 * YTr); out.Yaout[i] = YTr;
        out.A[i] = Aerg; out.B[i] = Berg; out.H[i] = Htot;
        if (out.capas) for (let j = 0; j < nz; j++) out.capas[i * nz + j] = X[j];
      }
      let ns = Math.ceil(dt / (0.3 * tauMin)); if (ns < 1) ns = 1; if (ns > 400) ns = 400; nsub = ns;
    }
    return [sumGh / sumG, sumGY / sumG, sumQ / nx, sumE / nx, sumS / nx];
  }

  function distribucion(A, B, uMed) {
    const n = A.length; const u = new Float64Array(n);
    let hi = 1;
    for (let i = 0; i < n; i++) { const a = Math.max(A[i], 1e-9), b = Math.max(B[i], 1e-12); hi = Math.max(hi, (a * uMed + b * uMed * uMed) * 4 + 1); }
    let lo = 0;
    const uDe = (dp) => { let s = 0; for (let i = 0; i < n; i++) { const a = Math.max(A[i], 1e-9), b = Math.max(B[i], 1e-12); u[i] = (-a + Math.sqrt(a * a + 4 * b * dp)) / (2 * b); s += u[i]; } return s / n; };
    for (let k = 0; k < 60; k++) { const mid = 0.5 * (lo + hi); if (uDe(mid) > uMed) hi = mid; else lo = mid; }
    const dp = 0.5 * (lo + hi); const media = uDe(dp);
    const g = new Float64Array(n); for (let i = 0; i < n; i++) g[i] = u[i] / media;
    return [g, dp];
  }

  /* Aceleración de Anderson (Walker y Ni 2011) para el punto fijo del circuito de aire:
   * no cambia la solución, solo llega antes. Con historial m y resguardo si el residuo crece. */
  function nuevoAnderson(m) {
    let dF = [], dG = [], fPrev = null, gPrev = null, normPrev = Infinity;
    return {
      paso(x, g, w) {
        const n = x.length, f = g.map((gi, i) => gi - x[i]);
        const norm = Math.sqrt(f.reduce((s, v) => s + v * v, 0));
        if (fPrev && norm > 10 * normPrev) { dF = []; dG = []; }
        if (fPrev) {
          dF.push(f.map((v, i) => v - fPrev[i])); dG.push(g.map((v, i) => v - gPrev[i]));
          if (dF.length > m) { dF.shift(); dG.shift(); }
        }
        fPrev = f; gPrev = g; normPrev = norm;
        const k = dF.length;
        if (k === 0) return x.map((xi, i) => xi + w * f[i]);
        // mínimos cuadrados min ||f − ΔF·γ|| por ecuaciones normales con regularización
        const A = [], b = [];
        for (let a = 0; a < k; a++) {
          A.push([]);
          for (let c = 0; c < k; c++) { let s = 0; for (let i = 0; i < n; i++) s += dF[a][i] * dF[c][i]; A[a].push(s); }
          let s = 0; for (let i = 0; i < n; i++) s += dF[a][i] * f[i]; b.push(s);
        }
        let tr = 0; for (let a = 0; a < k; a++) tr += A[a][a];
        for (let a = 0; a < k; a++) A[a][a] += 1e-10 * tr + 1e-14;
        const gam = resolverLineal(A, b);
        if (!gam) { dF = []; dG = []; return x.map((xi, i) => xi + w * f[i]); }
        const out = new Array(n);
        for (let i = 0; i < n; i++) {
          let sx = x[i] + w * f[i];
          for (let a = 0; a < k; a++) sx -= gam[a] * ((dG[a][i] - dF[a][i]) + w * dF[a][i]);
          out[i] = sx;
        }
        return out;
      },
    };
  }
  function resolverLineal(A, b) {
    const n = b.length, M = A.map((r, i) => r.concat([b[i]]));
    for (let c = 0; c < n; c++) {
      let p = c; for (let r = c + 1; r < n; r++) if (Math.abs(M[r][c]) > Math.abs(M[p][c])) p = r;
      if (Math.abs(M[p][c]) < 1e-300) return null;
      [M[c], M[p]] = [M[p], M[c]];
      for (let r = 0; r < n; r++) if (r !== c) { const f = M[r][c] / M[c][c]; for (let q = c; q <= n; q++) M[r][q] -= f * M[c][q]; }
    }
    return M.map((r, i) => r[n] / r[i]);
  }

  function nuevoPerfil(nx, nz, capas) {
    const f = () => new Float64Array(nx);
    const o = { x: f(), t: f(), Xmed: f(), Xmin: f(), Xmax: f(), Tmed: f(), Tmin: f(), Tmax: f(), Taout: f(), Yaout: f(), A: f(), B: f(), H: f() };
    if (capas) o.capas = new Float64Array(nx * nz);
    return o;
  }

  // ------------------------------------------------------------------ secador completo
  /* D: datos geométricos y de planta (exportados desde Python), cfg: condiciones de operación.
   * Si cfg.controlar es true, la velocidad de banda se ajusta dentro de la misma iteración para
   * llegar a la humedad objetivo (lazo MIC-01 en régimen). */
  function resolver(D, cfg, inicial) {
    const p = Object.assign({}, D.prm, cfg.prm || {});
    const P = p.P, nx = cfg.nx, nz = cfg.nz;
    const Tamb = cfg.T_amb, Tnave = Tamb + D.dt_nave;
    const Yamb = YdePv(cfg.HR_amb * psat(Tamb), P), hamb = entalpia(Tamb, Yamb);
    const Tg = Tnave;
    const hum = cfg.humedad_entrada, Xfeed = hum / (1 - hum);
    const mdm = cfg.alimentacion * (1 - hum) / 3600;
    const mair = cfg.aire_seco / 3600;
    const areaPiso = D.ancho * D.largo;
    const paralelo = cfg.modo_aire === "paralelo";
    const fp = cfg.bypass_pila || 0, mpila = (1 - fp) * mair;   // aire que atraviesa los pisos
    const Gp = mpila / areaPiso / (paralelo ? 3 : 1);
    const r = cfg.recirc;
    const UA = D.area_zonas.map(a => a * cfg.U_panel);
    const Xobj = cfg.humedad_objetivo / (1 - cfg.humedad_objetivo);
    const dY = Math.max(mdm * (Xfeed - Xobj), 1e-6) / mair;
    let st = inicial ? JSON.parse(JSON.stringify(inicial)) : null;
    if (!st) st = { T_exh: 70, Y_exh: Yamb + dY / (1 - r), Tin: [75, 100, cfg.T_aire], Yin: [Yamb + dY, Yamb + 0.5 * dY, Yamb], g: null, lnv: Math.log(cfg.vel) };
    if (!st.g || st.g[0].length !== nx) st.g = [0, 1, 2].map(() => Array.from({ length: nx }, () => 1));
    let lnv = cfg.controlar ? (st.lnv || Math.log(cfg.vel)) : Math.log(cfg.vel);
    const outs = [0, 1, 2].map(() => nuevoPerfil(nx, nz, cfg.capas));
    const vmin = D.vel_min, vmax = D.vel_max;
    let conv = false, it = 0, err = 0, Xp, Tp, higC, higM, salida, qpl, qz, Ymix, hmix, Tmix, csmix, vel, T3;
    let secante = null;   // (lnv, error) anteriores para el control
    const anderson = nuevoAnderson(cfg.profundidad_aa || 3);
    for (it = 0; it < cfg.maxit; it++) {
      vel = [0, 1, 2].map(k => Math.exp(lnv) * cfg.factores_vel[k]);
      const wdm = vel.map(v => mdm / (D.ancho * v));
      const hexh = entalpia(st.T_exh, st.Y_exh);
      Ymix = (1 - r) * Yamb + r * st.Y_exh; hmix = (1 - r) * hamb + r * hexh;
      Tmix = tempDeEntalpia(hmix, Ymix); csmix = 1006 + 1860 * Ymix;
      qpl = UA[0] * (cfg.T_aire - Tnave);
      T3 = cfg.T_aire - qpl / (mair * csmix);
      if (paralelo) { st.Tin = [T3, T3, T3]; st.Yin = [Ymix, Ymix, Ymix]; } else { st.Tin[2] = T3; st.Yin[2] = Ymix; }
      Xp = new Float64Array(nz).fill(Xfeed); Tp = new Float64Array(nz).fill(Tg);
      higC = new Float64Array(nz * 4); higM = new Float64Array(nz * 4);
      salida = [];
      for (let k = 0; k < 3; k++) {
        const inc = new Float64Array(nz * 4);
        const g = Float64Array.from(st.g[k]);
        const s = avanzarPiso(Xp, Tp, inc, st.Tin[k], st.Yin[k], g, wdm[k], Gp, D.largo, vel[k], nx, p, outs[k], cfg);
        salida.push(s);
        for (let q = 0; q < nz * 4; q++) { higC[q] += inc[q]; higM[q] += inc[q]; }
        if (k < 2) {
          if (cfg.transferencia === "inversion") {
            Xp.reverse(); Tp.reverse();
            const rev = (a) => { const b = new Float64Array(a.length); for (let j = 0; j < nz; j++) for (let c = 0; c < 4; c++) b[j * 4 + c] = a[(nz - 1 - j) * 4 + c]; return b; };
            higC = rev(higC); higM = rev(higM);
          } else {
            let sc = 0, sct = 0, sx = 0;
            for (let j = 0; j < nz; j++) { const cp = p.cps + 4186 * Xp[j]; sc += cp; sct += cp * Tp[j]; sx += Xp[j]; }
            Xp.fill(sx / nz); Tp.fill(sct / sc);
            for (let c = 0; c < 4; c++) {
              let mn = 1e30, me = 0;
              for (let j = 0; j < nz; j++) { mn = Math.min(mn, higC[j * 4 + c]); me += higM[j * 4 + c]; }
              for (let j = 0; j < nz; j++) { higC[j * 4 + c] = mn; higM[j * 4 + c] = me / nz; }
            }
          }
        }
      }
      const Tout = salida.map(s => tempDeEntalpia(s[0], s[1])), Yout = salida.map(s => s[1]);
      let TexhN, YexhN, nuevos = null;
      const hByp = entalpia(T3, Ymix);
      if (paralelo) {
        const Yx = (1 - fp) * (Yout[0] + Yout[1] + Yout[2]) / 3 + fp * Ymix;
        const hx = (1 - fp) * (salida[0][0] + salida[1][0] + salida[2][0]) / 3 + fp * hByp;
        const Tx = tempDeEntalpia(hx, Yx);
        qz = [UA[1] * (Tout[2] - Tnave), UA[2] * (Tout[1] - Tnave), UA[3] * (Tout[0] - Tnave)];
        TexhN = Tx - (qz[0] + qz[1] + qz[2]) / (mair * (1006 + 1860 * Yx)); YexhN = Yx;
      } else {
        const q32 = UA[1] * (Tout[2] - Tnave), Tin2 = Tout[2] - q32 / (mpila * (1006 + 1860 * Yout[2]));
        const q21 = UA[2] * (Tout[1] - Tnave), Tin1 = Tout[1] - q21 / (mpila * (1006 + 1860 * Yout[1]));
        // campana: el aire del piso 1 se junta con el que subió por los bordes
        const Yc = (1 - fp) * Yout[0] + fp * Ymix, Tc = tempDeEntalpia((1 - fp) * salida[0][0] + fp * hByp, Yc);
        const q1 = UA[3] * (Tc - Tnave);
        TexhN = Tc - q1 / (mair * (1006 + 1860 * Yc)); YexhN = Yc;
        qz = [q32, q21, q1]; nuevos = [Tin1, Yout[1], Tin2, Yout[2]];
      }
      const w = cfg.relajacion;
      err = Math.abs(TexhN - st.T_exh) + 1e4 * Math.abs(YexhN - st.Y_exh);
      if (nuevos) {
        const [Tin1, Yin1, Tin2, Yin2] = nuevos;
        err += Math.abs(Tin1 - st.Tin[0]) + Math.abs(Tin2 - st.Tin[1]) + 1e4 * (Math.abs(Yin1 - st.Yin[0]) + Math.abs(Yin2 - st.Yin[1]));
      }
      // vector de estado del aire (escalado) y su imagen por un barrido completo
      const xv = nuevos ? [st.T_exh, 1e3 * st.Y_exh, st.Tin[0], 1e3 * st.Yin[0], st.Tin[1], 1e3 * st.Yin[1]]
                        : [st.T_exh, 1e3 * st.Y_exh];
      const gv = nuevos ? [TexhN, 1e3 * YexhN, nuevos[0], 1e3 * nuevos[1], nuevos[2], 1e3 * nuevos[3]]
                        : [TexhN, 1e3 * YexhN];
      let xn;
      if (cfg.acelerar) xn = anderson.paso(xv, gv, w);
      else xn = xv.map((x, i) => (1 - w) * x + w * gv[i]);
      st.T_exh = xn[0]; st.Y_exh = xn[1] / 1e3;
      if (nuevos) { st.Tin[0] = xn[2]; st.Yin[0] = Math.max(xn[3] / 1e3, 1e-5); st.Tin[1] = xn[4]; st.Yin[1] = Math.max(xn[5] / 1e3, 1e-5); }
      for (let k = 0; k < 3; k++) {
        const rho = rhoAire(st.Tin[k], st.Yin[k], P);
        const uMed = (1 - p.byp) * Gp * (1 + st.Yin[k]) / rho;
        const [gk] = distribucion(outs[k].A, outs[k].B, uMed);
        if (cfg.distribuir) for (let i = 0; i < nx; i++) st.g[k][i] = (1 - w) * st.g[k][i] + w * gk[i];
      }
      // control de velocidad simultáneo (secante en log v sobre la humedad de salida)
      let errCtrl = 0;
      if (cfg.controlar) {
        let xm = 0; for (let j = 0; j < nz; j++) xm += Xp[j]; xm /= nz;
        const e = xm / (1 + xm) - cfg.humedad_objetivo;
        errCtrl = Math.abs(e);
        let nl;
        if (secante && Math.abs(e - secante[1]) > 1e-7 && Math.abs(lnv - secante[0]) > 1e-6) {
          nl = lnv - e * (lnv - secante[0]) / (e - secante[1]);
        } else {
          nl = lnv - 4.0 * e;     // primer paso: sensibilidad típica
        }
        nl = Math.max(Math.log(vmin), Math.min(Math.log(vmax), nl));
        nl = lnv + Math.max(-0.25, Math.min(0.25, nl - lnv));
        secante = [lnv, e];
        lnv = nl;
        st.lnv = lnv;
        err += 50 * errCtrl;
      }
      if (err < cfg.tol && it > 2) { conv = true; break; }
    }
    // resultados
    let xm = 0; for (let j = 0; j < nz; j++) xm += Xp[j]; const Xout = xm / nz;
    let sc = 0, sct = 0; for (let j = 0; j < nz; j++) { const cp = p.cps + 4186 * Xp[j]; sc += cp; sct += cp * Tp[j]; }
    const Tout = sct / sc;
    const W = mdm * (Xfeed - Xout);
    const hin = entalpia(cfg.T_aire, Ymix);
    const Qgen = mair * (hin - hmix) + D.q_ducto;
    const comb = Qgen / (D.pci * D.rend_gen);
    const Qparedes = qpl + qz[0] + qz[1] + qz[2];
    const aguaAire = mair * (st.Y_exh - Ymix);
    const Hin = mair * hin, Hout = mair * entalpia(st.T_exh, st.Y_exh);
    const Hpin = mdm * (p.cps + 4186 * Xfeed) * Tg, Hpout = mdm * (p.cps + 4186 * Xout) * Tout;
    const Ssorc = (salida[0][4] + salida[1][4] + salida[2][4]) * areaPiso;
    const resid = Hin + Hpin - Hout - Hpout - Qparedes - Ssorc;
    // destino del calor: evaporar + calentar el producto + sorción + paredes y ducto + escape
    const Qevap = W * hfg(Tg), Qprod = mdm * (p.cps + 4186 * Xout) * (Tout - Tg), Qutil = Qevap + Qprod;
    const Qescape = (1 - r) * mair * (CPA + CPV * Yamb) * (st.T_exh - Tamb) + W * CPV * (st.T_exh - Tg);
    const dTp = Tout - Tg;
    const QutilMem = W * (4186 * dTp + 2.36e6) + mdm * p.cps * dTp + mdm * Xout * 4186 * dTp;
    const [TmR, YmV, nieblaMix] = saturar(Tmix, Ymix, P), [TeR, YeV, nieblaExh] = saturar(st.T_exh, st.Y_exh, P);
    const dpPisos = [0, 1, 2].map(k => {
      const rho = rhoAire(st.Tin[k], st.Yin[k], P);
      const u0 = (1 - p.byp) * Gp * (1 + st.Yin[k]) / rho;
      let s = 0; for (let i = 0; i < nx; i++) { const u = u0 * st.g[k][i]; s += outs[k].A[i] * u + outs[k].B[i] * u * u; }
      return s / nx;
    });
    const Vvent = mair * (1 + Ymix) / rhoAire(TmR, YmV, P) * 3600;
    const higPeor = [0, 1, 2, 3].map(c => { let mn = 1e30; for (let j = 0; j < nz; j++) mn = Math.min(mn, higC[j * 4 + c]); return mn; });
    const higMed = [0, 1, 2, 3].map(c => { let s = 0; for (let j = 0; j < nz; j++) s += higM[j * 4 + c]; return s / nz; });
    const capa0 = mdm / (D.ancho * vel[0]) * volLecho(Xfeed, p) * 1000;
    return {
      convergio: conv, iteraciones: it + 1, X_feed: Xfeed, X_out: Xout, hum_out: Xout / (1 + Xout),
      T_prod_out: Tout, T_nave: Tnave, T_mix: TmR, Y_mix: Ymix, HR_mix: hr(TmR, YmV, P), niebla_mix: nieblaMix,
      T_exh: TeR, Y_exh: st.Y_exh, HR_exh: hr(TeR, YeV, P), niebla_exh: nieblaExh, T_rocio_exh: puntoRocio(YeV, P),
      T_bh_entrada: bulboHumedo(cfg.T_aire, Ymix, P),
      Tin: st.Tin.slice(), Yin: st.Yin.slice(), Tout: salida.map(s => tempDeEntalpia(s[0], s[1])), Yout: salida.map(s => s[1]),
      W_kg_h: W * 3600, prod_kg_h: mdm * (1 + Xout) * 3600,
      Q_gen_kW: Qgen / 1e3, comb_kg_h: comb * 3600, cenizas_kg_h: comb * D.cenizas * 3600,
      Q_paredes_kW: Qparedes / 1e3, Q_util_kW: Qutil / 1e3, rendimiento: Qutil / Qgen,
      Q_evap_kW: Qevap / 1e3, Q_producto_kW: Qprod / 1e3, Q_escape_kW: Qescape / 1e3, Q_sorcion_kW: Ssorc / 1e3,
      Q_util_memoria_kW: QutilMem / 1e3, rendimiento_memoria: QutilMem / Qgen,
      consumo_MJ_kg: Qgen / Math.max(W, 1e-9) / 1e6,
      err_masa: (aguaAire - W) / Math.max(W, 1e-9), err_energia: resid / Math.max(Qgen, 1),
      dp_pisos: dpPisos, V_vent_m3h: Vvent, P_vent_kW: Vvent / 3600 * D.vent_presion / D.vent_rend / 1e3,
      hig_peor: higPeor, hig_med: higMed, capa_mm: capa0, t_res_min: vel.map(v => D.largo / v / 60),
      vel: vel, perfiles: outs, estado: st, sat_control: cfg.controlar ? (Math.abs(lnv - Math.log(vmin)) < 1e-9 ? "min" : Math.abs(lnv - Math.log(vmax)) < 1e-9 ? "max" : "ok") : "manual",
      Xe_salida: humedadEquilibrio(hr(TeR, YeV, P), TeR, p),
    };
  }

  const api = { psat, YdePv, pvdeY, Ysat, hr, entalpia, tempDeEntalpia, bulboHumedo, puntoRocio, rhoAire, saturar,
    humedadEquilibrio, actividadAgua, difusividad, volLecho, resolver, capa, avanzarPiso, distribucion };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  root.ModeloSecador = api;
})(typeof self !== "undefined" ? self : this);
