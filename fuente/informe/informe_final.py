"""Informe final del proyecto (Word definitivo y su PDF) y manual de armado y uso del secador SC-4.

    python informe_final.py            # informe/Informe_Final_Secadora_Guano.docx y .pdf
                                       # secadora/Manual_de_armado_SC4.docx y .pdf
Antes: calculos/calculos_memoria.py (resultados.json), calculos/presupuesto.py (presupuesto.json),
secadora/modelo_secador.py (piezas.json), secadora/visor/capturas.js (renders) y planos/juego.py.

Contenido:
  - capítulos de la Rev. C (fuente/informe/texto_revC.md, ya corregido con los valores vigentes);
  - capítulos nuevos de esta entrega: modelo 3D y despiece, verificación a fatiga, materiales y
    construcción, fijación al piso, montaje paso a paso, instalación y puesta en marcha, ubicación,
    ampliación Rev. D, pruebas de carga, resistencia y fatiga, presupuesto con LAR;
  - la memoria de cálculo de la Rev. D (TG2, iluminación, ventilación, biogás, fuego) con las mismas
    funciones de calculos/memoria_docx.py, renumeradas;
  - anexos: planos (juego general y juego del secador), memoria resumida, tareas, datos a confirmar
    y lista de archivos.
Todos los números salen de los .json: no hay valores copiados a mano.
"""
from __future__ import annotations

import json
import math
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
FUENTE = os.path.abspath(os.path.join(AQUI, ".."))
RAIZ = os.path.abspath(os.path.join(FUENTE, ".."))
sys.path.insert(0, os.path.join(FUENTE, "calculos"))
sys.path.insert(0, os.path.join(FUENTE, "planos"))

import memoria_docx as MD  # noqa: E402
from docx.enum.text import WD_ALIGN_PARAGRAPH  # noqa: E402
from docx.shared import Cm, Pt, RGBColor  # noqa: E402
from memoria_docx import Memoria, c, campo, esc  # noqa: E402

R = MD.R
FAT = R["fatiga"]
PRES = json.load(open(os.path.join(FUENTE, "calculos", "presupuesto.json"), encoding="utf-8"))
PIEZAS = json.load(open(os.path.join(RAIZ, "secadora", "modelo_3d", "piezas.json"), encoding="utf-8"))["piezas"]
PASOS = json.load(open(os.path.join(FUENTE, "secadora", "pasos_montaje.json"), encoding="utf-8"))

SALIDA = os.path.join(RAIZ, "informe", "Informe_Final_Secadora_Guano.docx")
SALIDA_MANUAL = os.path.join(RAIZ, "secadora", "Manual_de_armado_SC4.docx")
FIGURAS = os.path.join(RAIZ, "informe", "figuras")
RENDERS = os.path.join(RAIZ, "secadora", "renders")
PLANOS = os.path.join(RAIZ, "planos")
PLANOS_SC = os.path.join(RAIZ, "secadora", "planos")

INTEGRANTES = ["Gabriel Müller", "Pablo Hofstetter", "Baltazar Goette", "Facundo Stegmann", "Martín Bernhardt", "Bautista Belluzzo"]
ESCUELA = 'E.P.N.M. y S. N° 35 Técnica "Gral. Don José de San Martín"'


def miles(x):
    return c(x, 0)


SUP = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")


def pot(txt):
    """'7.78e+07' -> '7,78·10⁷' (textos con potencias de 10)."""
    mt = re.fullmatch(r"([\d.]+)e\+?(-?\d+)", str(txt).strip())
    if not mt:
        return str(txt)
    return f"{c(float(mt.group(1)), 2)}·10{str(int(mt.group(2))).translate(SUP)}"


# ================================================================ imágenes livianas para el Word
def liviana(ruta, ancho_px=1400, jpg=True):
    """Copia reducida de una imagen (JPEG para renders, PNG de 256 colores para planos) en informe/figuras."""
    from PIL import Image
    os.makedirs(FIGURAS, exist_ok=True)
    base = os.path.splitext(os.path.basename(ruta))[0]
    if os.path.basename(os.path.dirname(ruta)) == "montaje":
        base = "montaje_" + base
    destino = os.path.join(FIGURAS, base + (".jpg" if jpg else ".png"))
    if os.path.exists(destino) and os.path.getmtime(destino) >= os.path.getmtime(ruta):
        return destino
    with Image.open(ruta) as im:
        im = im.convert("RGB")
        if im.width > ancho_px:
            im = im.resize((ancho_px, round(im.height * ancho_px / im.width)), Image.LANCZOS)
        if jpg:
            im.save(destino, "JPEG", quality=82, optimize=True)
        else:
            im.quantize(colors=64, method=Image.Quantize.MEDIANCUT).save(destino, optimize=True)
    return destino


def plano(n, ancho_px=1650):
    return liviana(os.path.join(PLANOS, f"P{n:02d}.png"), ancho_px, jpg=False)


def plano_sc(n, ancho_px=1650):
    return liviana(os.path.join(PLANOS_SC, f"SC-{n:02d}.png"), ancho_px, jpg=False)


def render(nombre, ancho_px=1400):
    return liviana(os.path.join(RENDERS, nombre), ancho_px)


# ================================================================ gráficos (matplotlib)
def graficos():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.grid": True, "grid.alpha": 0.3,
                         "axes.spines.top": False, "axes.spines.right": False})
    os.makedirs(FIGURAS, exist_ok=True)
    em = FAT["eje_motriz"]
    sut, sy = em["Sut"], em["Sy"]
    rutas = {}
    # Goodman modificado
    fig, ax = plt.subplots(figsize=(6.4, 3.9), dpi=170)
    se = em["secciones"][0]["Se"]
    ax.plot([0, sut], [se, 0], color="#1f5fa8", lw=1.8, label=f"Goodman S1 (Se = {c(se, 0)} MPa)")
    ax.plot([0, sut / 1.5], [se / 1.5, 0], color="#1f5fa8", lw=1, ls="--", label="Goodman con n = 1,5")
    ax.plot([0, sy], [sy, 0], color="#c0392b", lw=1.4, label=f"fluencia de Langer (Sy = {sy} MPa)")
    for s in em["secciones"]:
        ax.plot(s["vm_m"], s["vm_a"], "s", color="#c0392b", ms=5)
        ax.annotate(f"{s['cod']}  n = {c(s['n_goodman'], 2)}", (s["vm_m"], s["vm_a"]), xytext=(6, 4),
                    textcoords="offset points", fontsize=8)
    for cso in FAT["eje_reenvio"]["casos"]:
        ax.plot(0, cso["sigma_a"], "o", mfc="white", mec="#333", ms=6)
        ax.annotate(f"reenvío Ø{cso['d']}  n = {c(cso['n'], 2)}", (0, cso["sigma_a"]), xytext=(8, -3),
                    textcoords="offset points", fontsize=8)
    ax.set_xlim(0, 600); ax.set_ylim(0, 340)
    ax.set_xlabel("tensión media de von Mises σm' (MPa)"); ax.set_ylabel("tensión alternante σa' (MPa)")
    ax.legend(loc="upper right", fontsize=7.5, frameon=False)
    fig.tight_layout(); rutas["goodman"] = os.path.join(FIGURAS, "fatiga_goodman.png"); fig.savefig(rutas["goodman"]); plt.close(fig)
    # Wöhler
    wo = FAT["wohler"]
    fig, ax = plt.subplots(figsize=(6.4, 3.9), dpi=170)
    import numpy as np
    n = np.logspace(3, 6, 60)
    ax.loglog(np.r_[n, 1e8], np.r_[wo["a"] * n ** wo["b"], wo["Se_prima"]], color="#1f5fa8", lw=1.8,
              label=f"probeta pulida SAE 1045 (Se' = {c(wo['Se_prima'], 0)} MPa)")
    a_c = (wo["f"] * sut) ** 2 / se
    b_c = -math.log10(wo["f"] * sut / se) / 3
    ax.loglog(np.r_[n, 1e8], np.r_[a_c * n ** b_c, se], color="#c0392b", lw=1.4, ls="--",
              label=f"eje motriz S1 con factores de Marin (Se = {c(se, 0)} MPa)")
    for niv in wo["niveles"]:
        try:
            ax.loglog(float(niv["N"]), niv["S"], "s", color="#333", ms=4)
        except ValueError:
            ax.loglog(1e7, niv["S"], "o", mfc="white", mec="#333", ms=5)
    ax.axvline(em["ciclos_vida"], color="#888", lw=1, ls=":")
    ax.text(em["ciclos_vida"] * 1.1, 620, "vida del eje\n(20 años)", fontsize=7.5)
    ax.set_xlim(1e3, 1e8); ax.set_ylim(100, 700)
    ax.set_xlabel("ciclos N"); ax.set_ylabel("amplitud de tensión S (MPa)")
    ax.legend(loc="lower left", fontsize=7.5, frameon=False)
    fig.tight_layout(); rutas["wohler"] = os.path.join(FIGURAS, "fatiga_wohler.png"); fig.savefig(rutas["wohler"]); plt.close(fig)
    # flujo de caja acumulado
    ev = PRES["evaluacion"]
    fig, ax = plt.subplots(figsize=(6.4, 3.6), dpi=170)
    colores = ["#1f5fa8", "#7fa7d6", "#c0392b", "#e59866"]
    anios = list(range(0, ev["anios"] + 1))
    for e, col in zip(ev["escenarios"], colores):
        ax.plot(anios, [(-e["inversion"] + e["neto"] * a) / 1000 for a in anios], color=col, lw=1.8,
                label=f"{e['nombre']} (TIR {c(e['TIR'], 1)} %)")
    ax.axhline(0, color="#333", lw=0.8)
    ax.set_xlabel("año"); ax.set_ylabel("flujo acumulado sin descontar (miles de USD)")
    ax.legend(fontsize=7, frameon=False, loc="lower right")
    fig.tight_layout(); rutas["flujo"] = os.path.join(FIGURAS, "flujo_de_caja.png"); fig.savefig(rutas["flujo"]); plt.close(fig)
    # inversión por rubro
    inv = PRES["inversion"]
    grupos = {"Planta Rev. C (A1-A9)": inv["sub_revC"], "Ampliación Rev. D/E (B1-B16)": inv["sub_revD"],
              "Ingeniería y habilitaciones": inv["sub_ing"], "Imprevistos": inv["imprevistos"]}
    fig, ax = plt.subplots(figsize=(6.4, 2.4), dpi=170)
    izq = 0
    for (k, v), col in zip(grupos.items(), ["#1f5fa8", "#7fa7d6", "#9aa5b1", "#d5dbe1"]):
        ax.barh([0], [v / 1000], left=izq, color=col, edgecolor="white")
        ax.text(izq + v / 2000, 0, f"{k}\n{miles(v / 1000)}", ha="center", va="center", fontsize=7.2,
                color="white" if col in ("#1f5fa8",) else "#111")
        izq += v / 1000
    ax.set_yticks([]); ax.set_xlabel("miles de USD"); ax.grid(axis="y", visible=False)
    ax.set_xlim(0, izq * 1.01)
    fig.tight_layout(); rutas["inversion"] = os.path.join(FIGURAS, "inversion.png"); fig.savefig(rutas["inversion"]); plt.close(fig)
    return rutas


# ================================================================ texto de la Rev. C (texto_revC.md)
RECUADROS = ("Configuración de la planta", "Balance ambiental del proyecto", "Recomendación económica")


def valores_md():
    ev = PRES["evaluacion"]["escenarios"]
    return {
        "n_planos": "24", "P_TG2": c(R["tg2"]["total_kW"], 1), "inv_total": miles(PRES["inversion"]["total"]),
        "inv_sin_biogas": miles(PRES["inversion"]["sin_biogas"]), "P_contratada": str(R["tg2"]["balance"]["adoptada_kW"]),
        "neto_1t": miles(ev[0]["neto"]), "neto_2t": miles(ev[2]["neto"]),
        "n_eje": c(FAT["eje_motriz"]["n_min"], 2), "n_reenvio": c(FAT["eje_reenvio"]["casos"][1]["n"], 2),
        "uso_anclaje": c(FAT["anclajes"]["secador"]["uso_V_pct"], 1),
    }


def leer_md():
    texto = open(os.path.join(AQUI, "texto_revC.md"), encoding="utf-8").read()
    for k, v in valores_md().items():
        texto = texto.replace("{{" + k + "}}", v)
    faltan = re.findall(r"\{\{[^}]+\}\}", texto)
    if faltan:
        raise ValueError(f"marcadores sin valor en texto_revC.md: {faltan}")
    caps, actual = {}, None
    for linea in texto.splitlines():
        if linea.startswith("<!--"):
            continue
        if linea.startswith("# "):
            titulo = linea[2:].strip()
            mt = re.match(r"(\d+)\. ", titulo)
            actual = int(mt.group(1)) if mt else titulo.split(".")[0]
            caps[actual] = [linea]
        elif actual is not None:
            caps[actual].append(linea)
    return caps


def figura_revC(numero, imagen):
    """Figuras del informe Rev. C: las que eran planos se reemplazan por las láminas vigentes."""
    reemplazo = {4: lambda: plano(6), 5: lambda: plano(2), 6: lambda: render("SC_interior.png"),
                 7: lambda: plano(3), 9: lambda: plano(7), 10: lambda: plano(5), 11: lambda: plano(4),
                 12: lambda: plano(1)}
    if numero in reemplazo:
        return reemplazo[numero]()
    return os.path.join(AQUI, "img_revC", imagen) if imagen else None


def es_formula(linea):
    return bool(re.match(r"^[^\s|#-]{1,12} = ", linea)) and len(linea) < 170


def emitir(m, lineas, nuevo=None, original=None, despues_de=None):
    """Escribe un capítulo del texto Rev. C. despues_de = {título de sección: función(m)} agrega contenido
    nuevo al final de esa sección (antes del título siguiente)."""
    m.renumerar = {original: nuevo} if original and nuevo else {}
    despues_de = despues_de or {}
    pendiente_img, pendiente_fn = None, None
    i = 0
    while i < len(lineas):
        ln = lineas[i]
        if ln.startswith("#"):
            if pendiente_fn:
                pendiente_fn(m)
                pendiente_fn = None
            nivel = len(ln) - len(ln.lstrip("#"))
            titulo = ln.lstrip("#").strip()
            m.h(titulo, nivel)
            for clave, fn in despues_de.items():
                if titulo.split(" ", 1)[-1].startswith(clave):
                    pendiente_fn = fn
        elif ln.startswith("[img:"):
            pendiente_img = ln[5:-1].strip()
        elif re.match(r"^Figura \d+\. ", ln):
            num = int(ln.split(".")[0].split()[1])
            ruta = figura_revC(num, pendiente_img)
            if ruta and os.path.exists(ruta):
                ancho = 16.5 if ruta.endswith(".png") and "P0" in os.path.basename(ruta) else 14
                m.figura(ruta, ln.split(". ", 1)[1], ancho)
            pendiente_img = None
        elif re.match(r"^Tabla \d+\. ", ln):
            titulo = ln.split(". ", 1)[1]
            filas = []
            i += 1
            while i < len(lineas) and lineas[i].startswith("|"):
                filas.append([x.strip() for x in lineas[i][1:].split(" | ")])
                i += 1
            ncol = max(len(f) for f in filas)
            filas = [f + [""] * (ncol - len(f)) for f in filas]
            m.tabla(titulo, filas)
            continue
        elif ln.startswith("| "):
            cuerpo = ln[2:].strip()
            tit = next((t for t in RECUADROS if cuerpo.startswith(t)), None)
            if tit:
                m.recuadro(tit, cuerpo[len(tit):].strip())
            else:
                m.p(cuerpo)
        elif ln.startswith("- "):
            items = []
            while i < len(lineas) and lineas[i].startswith("- "):
                items.append(lineas[i][2:].strip())
                i += 1
            m.lista(items)
            continue
        elif es_formula(ln):
            m.ec(ln)
        elif ln.strip():
            m.p(ln)
        i += 1
    if pendiente_fn:
        pendiente_fn(m)
    m.renumerar = {}


# ================================================================ portada y encabezado
def portada(m, titulo, subtitulo, temas, imagen):
    d = m.d
    m.p()
    m.p(ESCUELA, negrita=True, centrado=True, tam=14)
    m.p("Crespo, Entre Ríos · Especialidad Electromecánica · 7.° año", centrado=True)
    m.p("Materia: [COMPLETAR]", centrado=True, resaltar=True)
    m.p("Docente: [COMPLETAR]", centrado=True, resaltar=True)
    m.p()
    m.p("PROYECTO FINAL", negrita=True, centrado=True, tam=13)
    m.p(titulo, negrita=True, centrado=True, tam=21)
    m.p(subtitulo, negrita=True, centrado=True, tam=14)
    m.p(temas, centrado=True, tam=10.5)
    if imagen and os.path.exists(imagen):
        par = d.add_paragraph(); par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        par.add_run().add_picture(imagen, width=Cm(14.5))
        import pathlib
        m.html.append(f'<p style="text-align:center"><img src="{pathlib.Path(imagen).resolve().as_uri()}" '
                      f'style="width:14.5cm;border:0.5pt solid #999"></p>')
    m.p("Integrantes", negrita=True, centrado=True)
    m.p(" · ".join(INTEGRANTES[:3]), centrado=True)   # dos renglones de tres nombres
    m.p(" · ".join(INTEGRANTES[3:]), centrado=True)
    m.p("Crespo, Entre Ríos – octubre de 2026", centrado=True)
    m.salto()
    m.h("Índice", 1, indice=False)
    campo(d.add_paragraph(), 'TOC \\o "1-3" \\h \\z \\u')
    m.html.append('<div id="indice">__INDICE__</div>')
    m.salto()


def encabezado_pie(m, texto):
    sec = m.d.sections[0]
    sec.different_first_page_header_footer = True
    hp = sec.header.paragraphs[0]
    hp.text = texto
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    hp.runs[0].font.size = Pt(8.5)
    hp.runs[0].font.color.rgb = RGBColor(0x66, 0x66, 0x66)
    fp = sec.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fp.add_run("Página ").font.size = Pt(9)
    campo(fp, "PAGE")


# ================================================================ capítulos nuevos
def entrega_final(m):
    m.recuadro("Qué incluye esta entrega final",
               "Este informe reúne en un solo documento el proyecto completo: el informe de la Revisión C con sus "
               "valores actualizados, la ampliación de la Revisión D (seguridad, mantenimiento, Sector Este, biogás y "
               "ventilación de la nave) con su memoria de cálculo, y los capítulos nuevos de esta entrega: modelo 3D "
               "y despiece del secador, verificación a fatiga de los ejes y uniones según Shigley-Budynas, materiales "
               "y construcción, fijación al piso, manual de armado paso a paso, instalación y puesta en marcha, "
               "pruebas de carga, resistencia y fatiga, ubicación junto al Parque Industrial de Crespo y presupuesto "
               "con compras en la Cooperativa La Agrícola Regional (LAR).")


def grupos_piezas():
    g = {}
    for p in PIEZAS:
        base = re.sub(r"-\d$", "", p["cod"])
        base = "M5–M7" if re.fullmatch(r"M\d", base) else base
        nombre = re.sub(r"\s*–\s*piso \d$", "", p["nombre"])
        nombre = re.sub(r"Motor M\d", "Motores", nombre)
        x = g.setdefault(base, {"cod": base, "nombre": nombre, "cant": 0, "masa": 0.0, "material": p["material"]})
        x["cant"] += p["cantidad"]
        x["masa"] += p["masa_kg"]
    clave = lambda cod: [int(t) if t.isdigit() else ord(t[0]) for t in re.findall(r"\d+|[a-zA-Z]", cod)] \
        if not cod.startswith("M") else [4, 5, 0]
    return sorted(g.values(), key=lambda x: clave(x["cod"]))


def modelo_3d(m):
    total = sum(p["masa_kg"] for p in PIEZAS)
    m.h("7.7. Modelo 3D, despiece y lista de piezas del secador", 2)
    m.p("El secador se modeló pieza por pieza con CadQuery (Python sobre el núcleo OpenCASCADE, sólidos exactos) "
        "a partir de las cotas de los planos 02, 03, 09 y 22. El modelo tiene "
        f"{len(PIEZAS)} piezas con nombre, código, material y color, y se entrega en STEP (para abrir en SolidWorks "
        "o Fusion 360 como ensamble), en GLB (Blender y navegador) y en un visor interactivo que funciona sin "
        "internet (secadora/Visor_Secador_SC4.html): permite rotar, cortar el cerramiento, ver el despiece "
        "animado, recorrer los 13 pasos del montaje y consultar cada pieza con su masa y su plano.")
    m.figura(render("SC_general.png"), "Secador SC-4: vista general del modelo 3D (cara Sur, accionamientos y pasarela)", 15)
    m.figura(render("SC_accionamiento.png"), "Accionamiento de un piso: motor IEC de 0,75 kW, reductor doble "
             "sinfín-corona 1:300 sobre su consola con colisos y cárter cerrado de la cadena ASA 60", 13)
    m.figura(render("SC_despiece.png"), "Despiece del secador (plano SC-02): cerramiento, techo, tambores, ejes y "
             "accionamientos separados de la estructura", 15)
    filas = [["Cód.", "Pieza", "Cant.", "Material", "kg"]]
    for g in grupos_piezas():
        filas.append([g["cod"], g["nombre"], g["cant"], g["material"], miles(g["masa"])])
    filas.append(["", "Masa total del secador (sin producto)", "", "", miles(total)])
    m.tabla("Lista de piezas del secador SC-4 (las de los tres pisos agrupadas; masas del modelo 3D)", filas,
            anchos=[1.3, 8.2, 1.1, 4.0, 1.3], alin=["L", "L", "C", "L", "R"], total=True)
    ms = FAT["anclajes"]["masa"]
    m.p(f"La masa total del modelo ({miles(total)} kg) difiere en {c(ms.get('dif_cad_pct', 0), 1)} % de la estimación "
        f"por rubros de la memoria ({miles(sum(x[1] for x in ms['filas']))} kg); para la verificación de los anclajes "
        "se toma la mayor de las dos.")


def fatiga(m, figs):
    em, re_, ch, ca, rod = FAT["eje_motriz"], FAT["eje_reenvio"], FAT["chaveta"], FAT["cadena"], FAT["rodamientos"]
    me, an, wo = FAT["mensula"], FAT["anclajes"], FAT["wohler"]
    sv, rc = FAT["servicio"], FAT["recepcion"]
    m.h("8. Verificación a fatiga y resistencia", 1)
    m.p("Las piezas del secador que giran o reciben cargas que cambian con el tiempo pueden romper por fatiga con "
        "tensiones muy por debajo de la resistencia estática. Los ejes de los tambores son el caso típico: cada "
        "vuelta invierte la flexión (flexión rotativa) mientras el par se mantiene casi constante. En este capítulo "
        "se verifican a fatiga, con el método de Budynas y Nisbett (Diseño en ingeniería mecánica de Shigley, "
        "8.ª edición, capítulos 6, 7, 8 y 11), los ejes motriz y de reenvío, la chaveta, la cadena, los "
        "rodamientos, la ménsula soldada y las uniones abulonadas, y se define el ensayo de "
        "Wöhler del material según el apunte de cátedra del INET (Ruiz, Fundamentos y ensayos en materiales "
        "metálicos), el libro de González Arias (Laboratorio de ensayos industriales, cap. IX) y las clases de "
        "Laboratorio de la escuela (tracción, flexión y dureza). Las cuentas están en fuente/calculos/fatiga.py.")
    m.h("8.1. Datos de servicio y materiales", 2)
    m.p(f"Servicio: {sv['horas_dia']:g} h por día (turno de 8 h más arranque y vaciado), {sv['dias_anio']} días por año "
        f"durante {sv['anios']} años; confiabilidad del {FAT['confiabilidad']} % y coeficiente de seguridad admisible "
        f"n = {c(FAT['n_adm'], 1)}. El tambor motriz gira a {c(em['rpm'], 3)} rpm, de modo que en 20 años el eje acumula "
        f"{c(em['ciclos_vida'] / 1e6, 2)} millones de ciclos de flexión: a partir de 10⁶ ciclos se diseña para vida "
        "infinita (límite de resistencia a la fatiga).")
    filas = [["Material", "Sut (MPa)", "Sy (MPa)", "Dureza HB", "Fuente"]]
    for k, v in FAT["materiales"].items():
        filas.append([k, v["Sut"], v["Sy"], v["HB"], v["fuente"]])
    m.tabla("Propiedades mínimas de los materiales", filas, anchos=[5, 2, 2, 2, 5], alin=["L", "R", "R", "R", "L"])
    m.h("8.2. Método de cálculo", 2)
    m.p("El límite de resistencia a la fatiga de la probeta pulida de flexión rotativa se corrige con los factores "
        "de Marin para llevarlo a la pieza real:")
    m.ec("S'e = 0,5 · Sut        Se = ka · kb · kc · kd · ke · kf · S'e", [
        "S'e: límite de la probeta (Sut ≤ 1.400 MPa)", "ka = a · Sut^b: superficie (rectificado, maquinado)",
        "kb: tamaño", "kc: tipo de carga", "kd: temperatura", f"ke = {c(em['secciones'][0]['marin']['ke'], 3)}: confiabilidad 99 %",
        "kf = 0,85: efectos varios (corrosión por amoníaco y humedad)"])
    m.p("Las entallas (escalones, chaveteros, asientos de cubos) concentran tensiones. El factor de fatiga se obtiene "
        "del teórico con la sensibilidad a la muesca de Neuber:")
    m.ec("Kf = 1 + q · (Kt − 1)        q = 1 / (1 + √a / √r)", [
        "Kt, Kts: factores teóricos en flexión y en torsión", "q: sensibilidad a la muesca", "r: radio de la entalla",
        "√a: constante de Neuber del acero"])
    m.p("Para ejes con flexión alternante y torsión media se usa el criterio DE-Goodman (ecuación 7-8): las tensiones "
        "se combinan con von Mises y se comparan con la recta de Goodman:")
    m.ec("σa' = √[(32·Kf·Ma/πd³)² + 3·(16·Kfs·Ta/πd³)²]        σm' = √[(32·Kf·Mm/πd³)² + 3·(16·Kfs·Tm/πd³)²]")
    m.ec("1/n = σa'/Se + σm'/Sut", ["n: coeficiente de seguridad a fatiga"])
    m.p("Se verifica también la fluencia en el primer ciclo (Langer): σmáx' = σa' + σm' ≤ Sy / n.")
    m.p("El diagrama de Smith que usa González Arias (cap. IX) es otra forma de dibujar el mismo criterio: en lugar "
        "de la tensión alternante en función de la media, representa las tensiones máxima y mínima del ciclo, con "
        "las rectas que van del límite de fatiga (tensión media nula) a la resistencia estática, cortadas por la "
        "fluencia. Con los mismos valores de Se, Sut y Sy da el mismo coeficiente que Goodman con el control de Langer.")
    m.h("8.3. Eje del tambor motriz", 2)
    m.p(f"Cargas: par de servicio T = {c(em['T'], 0)} N·m con una fluctuación de ±{int(em['fluct'] * 100)} % por la capa "
        f"irregular; en cada cubo actúan {c(em['P_H'], 0)} N horizontales (las dos ramas de la banda) y {c(em['P_V'], 0)} N "
        f"verticales (peso del tambor); en la corona, en voladizo, el tiro de la cadena de {c(em['Fc'], 0)} N. Con esas "
        "cargas se calculó el momento flector en las cuatro secciones críticas:")
    filas = [["Secc.", "Ubicación", "d (mm)", "M (N·m)", "Kt / Kts", "Kf / Kfs", "Se (MPa)", "σa' / σm'", "n Goodman", "n fluencia"]]
    for s in em["secciones"]:
        filas.append([s["cod"], s["seccion"], s["d"], c(s["M"], 0), f"{c(s['Kt'], 2)} / {c(s['Kts'], 2)}",
                      f"{c(s['Kf'], 2)} / {c(s['Kfs'], 2)}", c(s["Se"], 0), f"{c(s['vm_a'], 1)} / {c(s['vm_m'], 1)}",
                      c(s["n_goodman"], 2), c(s["n_fluencia"], 2)])
    m.tabla("Verificación a fatiga del eje motriz por sección", filas,
            anchos=[1.0, 4.2, 1.1, 1.3, 1.6, 1.6, 1.3, 1.9, 1.3, 1.3], alin=["C", "L", "R", "R", "C", "C", "R", "C", "R", "R"],
            resaltar=[1])
    s1 = em["secciones"][0]
    mk = s1["marin"]
    m.p(f"Cálculo detallado de la sección crítica S1 (asiento del cubo Sur, d = 60 mm, a {s1['temp']} °C):", negrita=True)
    m.calculo(f"S'e = 0,5 · {em['Sut']}", f"{c(em['Se_prima'], 1)} MPa")
    m.calculo(f"Se = {c(mk['ka'], 3)} · {c(mk['kb'], 3)} · {c(mk['kc'], 2)} · {c(mk['kd'], 2)} · {c(mk['ke'], 3)} · "
              f"{c(mk['kf'], 2)} · {c(em['Se_prima'], 1)}", f"{c(s1['Se'], 1)} MPa")
    m.calculo(f"Kf = 1 + {c(s1['q'], 3)} · ({c(s1['Kt'], 2)} − 1)", f"{c(s1['Kf'], 3)}")
    m.calculo(f"σa' = {c(s1['vm_a'], 1)} MPa;  σm' = {c(s1['vm_m'], 1)} MPa;  1/n = {c(s1['vm_a'], 1)}/{c(s1['Se'], 1)} + "
              f"{c(s1['vm_m'], 1)}/{em['Sut']}", f"n = {c(s1['n_goodman'], 2)} ≥ 1,5: verifica")
    m.p(f"Si el asiento del cubo quedara con terminación de torneado (ka menor), Se bajaría a "
        f"{c(em['S1_torneado']['Se'], 0)} MPa y n a {c(em['S1_torneado']['n_goodman'], 2)} < 1,5. Por eso el plano SC-03 "
        "pide rectificar los asientos de los cubos a Ra 0,8 µm: es la condición que hace verificar el eje.")
    at = em["atasco"]
    m.h("8.4. Par de atascamiento y límite de par del variador", 2)
    m.p("Si la banda se traba (un objeto extraño, un rodillo agarrotado), el motorreductor puede entregar en el eje "
        "un par muy superior al de servicio, porque la relación total es enorme:")
    m.calculo(f"T_atasco = 1,5 · T_motor · i · η = 1,5 · {c(at['T_motor'], 2)} · {at['i']} · {c(at['eta'], 2)}",
              f"{miles(at['T_atasco'])} N·m")
    m.calculo(f"τ = 16 · T / (π · d³) en el Ø50 = {c(at['tau'], 1)} MPa  frente a  Ssy = 0,577 · Sy = {c(at['Sys'], 1)} MPa",
              f"n = {c(at['n'], 2)}: el eje fluiría")
    m.p(f"Se resuelve programando en los variadores de M5, M6 y M7 un límite de par del 150 % del par de servicio "
        f"en el tambor ({at['T_limite_VFD']} N·m), con detención por sobrecarga y alarma en la HMI:")
    m.calculo(f"τ_lím = 16 · {at['T_limite_VFD']} / (π · 0,050³)", f"{c(at['tau_limite'], 1)} MPa → n = {c(at['n_limite'], 1)}")
    m.h("8.5. Eje del tambor de reenvío", 2)
    m.p(f"El reenvío no transmite par pero recibe la tensión de las dos ramas de la banda en la cola "
        f"({miles(re_['t_cola'])} N, incluida la fricción del retorno de {miles(re_['f_ret'])} N), con un momento de "
        f"{c(re_['M'], 0)} N·m en el asiento de los cubos.")
    filas = [["Ejecución", "d (mm)", "Kf", "Se (MPa)", "σa (MPa)", "n", "Vida"]]
    for cs in re_["casos"]:
        filas.append([cs["caso"], cs["d"], c(cs["Kf"], 2), c(cs["Se"], 0), c(cs["sigma_a"], 1), c(cs["n"], 2), cs["N_falla"]])
    m.tabla("Eje de reenvío: diseño anterior y Rev. E", filas, anchos=[6, 1.3, 1.3, 1.6, 1.6, 1.2, 2],
            alin=["L", "R", "R", "R", "R", "R", "C"], resaltar=[2])
    m.p(f"Con Ø50 en todo el largo el coeficiente queda en {c(re_['casos'][0]['n'], 2)}, por debajo del 1,5 exigido. La "
        f"Rev. E adopta Ø60 entre los cubos (n = {c(re_['casos'][1]['n'], 2)}) y deja muñones de Ø50 para las unidades "
        f"UCT 210, donde el momento es pequeño (n = {c(re_['n_munon'], 1)}). El cambio cuesta unos USD 2.600 para los "
        "tres ejes y quedó incorporado en los planos 03 y SC-03.")
    m.h("8.6. Chaveta, cadena, rodamientos, sinfín, ménsula y uniones abulonadas", 2)
    filas = [["Elemento", "Solicitación", "Resultado", "n"],
             ["Chaveta 14 × 9 × 63 DIN 6885 A", f"F = {miles(ch['F'])} N; τm = {c(ch['tau_m'], 1)} MPa; σaplast = {c(ch['sigma_ap'], 1)} MPa",
              "fatiga en corte / aplastamiento", f"{c(ch['n_fatiga'], 1)} / {c(ch['n_aplast'], 1)}"],
             ["Cadena ASA 60 simple", f"tiro {miles(ca['Fc'])} N × {c(ca['k'], 1)} (choques) = {miles(ca['F_servicio'])} N",
              f"admisible a fatiga {miles(ca['F_adm_fatiga'])} N; rotura {miles(ca['F_rotura_min'])} N",
              f"{c(ca['n_fatiga'], 2)}"],
             ["Ménsula PL 12, 2 filetes 6 × 370", f"R = {miles(me['R'])} N con ±15 %; σ = {c(me['sigma'], 2)} MPa",
              f"Kfs = {c(me['Kfs'], 1)} (pie de filete); Sse = {c(me['Sse'], 0)} MPa", c(me["n"], 1)],
             ["Bulones M16 8.8 del ventilador M1/M2", f"desbalanceo G 6,3 × 10 (polvo): {miles(an['ventilador']['F_falla_N'])} N",
              f"precarga {c(an['ventilador']['Fi_kN'], 1)} kN; Goodman de bulones (ec. 8-38)", c(an["ventilador"]["n_f"], 0)]]
    m.tabla("Otros elementos verificados a fatiga", filas, anchos=[4.2, 5.4, 4.6, 1.6], alin=["L", "L", "L", "R"])
    filas = [["Rodamiento", "C / C0 (kN)", "P (kN)", "rpm", "L10 (millones de rev.)", "L10 (h)", "s0 = C0/P"]]
    for r_ in rod["filas"]:
        filas.append([r_["rodamiento"], f"{c(r_['C'], 1)} / {c(r_['C0'], 1)}", c(r_["P"], 2), c(r_["rpm"], 3),
                      miles(r_["L10_Mrev"]), pot(r_["L10_h"]), c(r_["s0"], 1)])
    m.tabla("Vida de los rodamientos (L10 = (C/P)³, Shigley cap. 11)", filas, anchos=[5.2, 2, 1.4, 1.2, 2.4, 1.8, 1.6],
            alin=["L", "C", "R", "R", "R", "R", "R"])
    m.p(rod["nota"].capitalize())
    m.figura(figs["goodman"], "Diagrama de Goodman modificado del eje motriz (secciones S1 a S4) y del eje de reenvío "
             "(plano SC-04)", 14.5)
    m.h("8.7. Curva de Wöhler y ensayo de fatiga del material", 2)
    m.p("La curva S-N (de Wöhler) relaciona la amplitud de tensión con el número de ciclos hasta la rotura. Para "
        "aceros, a partir de unos 10⁶ ciclos la curva se hace horizontal: ese valor es el límite de resistencia a la "
        "fatiga. Entre 10³ y 10⁶ ciclos se usa la recta de Basquin en escala logarítmica:")
    m.ec("S = a · N^b        a = (f · Sut)² / S'e        b = −⅓ · log(f · Sut / S'e)", [
        f"f = {c(wo['f'], 3)}: fracción de Sut a 10³ ciclos (fig. 6-18)", f"a = {c(wo['a'], 1)} MPa", f"b = {c(wo['b'], 4)}"])
    m.figura(figs["wohler"], "Curva S-N del SAE 1045 (probeta y eje S1 con factores de Marin) y niveles del ensayo propuesto", 14.5)
    m.p("Como los valores de tabla son mínimos y el acero comercial varía de una colada a otra, se propone ensayar el "
        "material de los ejes según el apunte del INET: máquina de flexión rotativa (tipo Moore, ciclo alternado "
        f"R = −1), {wo['probetas']} probetas pulidas de 7,5 mm sacadas de la misma barra, una por nivel de tensión (González "
        f"Arias pide no menos de {rc['probetas_wohler_min']} probetas y hasta {rc['probetas_wohler_rigurosa']} en "
        "determinaciones rigurosas según ASTM); las "
        "que superan 10⁷ ciclos sin romper se cuentan como «no rompe» y definen el límite real. Si el S'e medido "
        f"resultara menor que {c(wo['Se_prima'], 0)} MPa, se recalculan los coeficientes con el valor del ensayo.")
    filas = [["Nivel", "S (MPa)", "S / Sut", "Vida esperada N"]]
    for i, nv in enumerate(wo["niveles"], 1):
        filas.append([i, nv["S"], c(nv["frac"], 2), pot(nv["N"])])
    m.tabla("Plan del ensayo de Wöhler (flexión rotativa, SAE 1045 laminado en caliente)", filas,
            anchos=[1.4, 2, 2, 4], alin=["C", "R", "R", "L"])
    m.h("8.8. Material de los ejes y control de recepción", 2)
    m.p("Toda la verificación supone SAE 1045 laminado en caliente. Según el catálogo de Acindar, las barras redondas "
        "laminadas se fabrican de stock en los grados 1008 a 1020 y el 1045 se entrega solo a pedido: si el "
        f"proveedor entregara la barra común ({rc['stock']}), los ejes no verificarían. Por eso el SAE 1045 se compra "
        "con certificado de colada y se controla por dureza al recibirlo.")
    m.tabla("Efecto del material sobre los ejes", [
        ["Material de la barra", "Sut (MPa)", "n eje motriz (S1)", "n eje de reenvío Ø60", "Resultado"],
        ["SAE 1045 HR (de proyecto)", FAT["materiales"]["SAE 1045 HR"]["Sut"], c(em["n_min"], 2),
         c(re_["casos"][1]["n"], 2), "Verifica"],
        [f"{rc['stock']} (barra de stock)", FAT["materiales"][rc["stock"]]["Sut"], c(rc["n_motriz_stock"], 2),
         c(rc["n_reenvio_stock"], 2), "No verifica (n < 1,5)"],
        [f"SAE 1045 con {rc['hb_min']} HB (mínimo)", rc["sut_hb_min"], c(rc["n_hb_min"], 2), "≥ 1,5", "Límite"],
    ], anchos=[4.6, 2, 2.6, 2.8, 3.2], alin=["L", "R", "R", "R", "L"], resaltar=[2])
    m.p("La dureza Brinell permite estimar la resistencia a la tracción del acero sin romper la barra (clase de "
        "dureza Brinell): Sut ≈ 3,45 · HB (MPa). La dureza más baja con la que los dos ejes siguen verificando con "
        f"n ≥ 1,5 es {rc['hb_min']} HB; se adopta como criterio de recepción HB ≥ {rc['hb_adop']}.")
    b = rc["brinell"]
    m.lista([
        f"Ensayo {b['designacion']}: bolilla de {b['D']} mm, carga de {miles(b['P'])} kgf (constante C = {b['C']} para "
        f"aceros), permanencia de {b['t']}; el diámetro de la impronta d es el promedio de dos medidas a 90°.",
        f"Validez: d/D entre {b['d_D']}; centro de la impronta a más de {b['borde']} del borde y a más de "
        f"{b['entre_centros']} de otra impronta; espesor de la pieza mayor que {b['espesor']} (h = profundidad).",
        f"Aceptación: d ≤ {c(rc['d_max'], 2)} mm (HB ≥ {rc['hb_adop']}) y d ≥ {c(rc['d_min'], 2)} mm (HB ≤ {rc['hb_max']}). "
        "Tres improntas en cada extremo de cada barra, en la zona que después se mecaniza.",
        "Si la dureza no cumple, la barra se rechaza o se hace el ensayo de tracción (probeta IRAM-IAS U 500-102) "
        "para decidir con la resistencia real.",
    ])
    m.h("8.9. Conclusiones de la verificación", 2)
    m.lista([
        f"El eje motriz verifica a fatiga con n = {c(em['n_min'], 2)} en la sección crítica (asiento del cubo) siempre que "
        "ese asiento se rectifique; el escalón Ø60/Ø50 con radio de 2 mm y el chavetero tienen márgenes amplios.",
        f"El par de atascamiento ({miles(at['T_atasco'])} N·m) haría fluir el eje: es obligatorio programar el límite de "
        f"par del 150 % en los variadores ({at['T_limite_VFD']} N·m en el eje).",
        f"El eje de reenvío de Ø50 no verificaba (n = {c(re_['casos'][0]['n'], 2)}); con Ø60 entre cubos queda en "
        f"n = {c(re_['casos'][1]['n'], 2)} (Rev. E).",
        "Chaveta, cadena, rodamientos, sinfín, ménsula y bulones tienen vida infinita con coeficientes holgados.",
        f"Los ejes deben hacerse con SAE 1045 pedido con certificado (Acindar lo lamina a pedido): con la barra común "
        f"{rc['stock']} el eje motriz quedaría en n = {c(rc['n_motriz_stock'], 2)}. Recepción por dureza: HB ≥ {rc['hb_adop']}.",
        "Se recomienda ensayar el material de los ejes (tracción, dureza y Wöhler) y controlar los escalones y "
        "chaveteros por partículas magnéticas antes del montaje y cada 2 años (capítulo de pruebas).",
    ])


def materiales(m):
    m.h("9. Materiales y construcción del secador", 1)
    m.p("Este capítulo describe cómo se fabrica y cómo queda armado el secador: qué se hace en el taller, qué se "
        "arma en obra, con qué uniones y con qué protección. La lista completa de piezas con sus masas está en el "
        "capítulo 7 y en el plano SC-02.")
    m.h("9.1. Especificación de materiales", 2)
    m.tabla("Materiales del secador SC-4", [
        ["Pieza", "Material y norma", "Por qué"],
        ["Columnas, vigas, travesaños, placas base, ménsulas, consolas", "Acero F-24 (IRAM-IAS U 500-503): UPN 120, IPN 140, L 50×50×5, PL 12", "Estructural, soldable, de stock en Crespo"],
        ["Ejes de tambores", "SAE 1045 laminado en caliente (IRAM-IAS U 500-600), barra Ø65", "Resistencia a fatiga; asientos rectificados"],
        ["Tambores", "Tubo SAE 1020 Ø300 × 4 y discos PL 12; engomado romboidal 8 mm (motriz)", "Rigidez y adherencia de la malla"],
        ["Bandas", "Malla trenzada AISI 304, alambre Ø2, paso 5, 2.000 mm", "Corrosión por amoníaco y 135 °C"],
        ["Guías de deslizamiento", "PTFE 40 × 20 mm en los pisos 2 y 3; UHMW-PE 40 × 20 mm en el piso 1 (Rev. F)", "Bajo rozamiento; el PTFE aguanta el aire de entrada a cada piso (hasta 135 °C; UHMW-PE: 80 °C)"],
        ["Faldones de sellado de bordes", "Chapa AISI 304 de 1,5 mm con labio de goma siliconada apta 200 °C (Rev. F)", "Que el aire no suba por los bordes sin tocar el guano"],
        ["Paneles", "Sándwich 80 mm lana de roca 100 kg/m³; cara interior AISI 304 0,6 mm; exterior galvanizada prepintada", "Aislación incombustible"],
        ["Tolvas, chapas deflectoras, esparcidor", "AISI 304 de 2 a 5 mm", "Contacto con guano húmedo"],
        ["Rodamientos", "UCF 212 con brida (motriz) y UCT 210 tensoras (reenvío), con sello y graseras", "Autoalineantes"],
        ["Transmisión", "Cadena ASA 60 simple, piñón Z15 y corona Z75 en C45 con dientes templados", "Relación 1:5"],
        ["Bulonería", "Clase 8.8 zincada; A2 (inoxidable) dentro de la cámara", "Corrosión"],
        ["Anclajes", "Varilla M16 clase 5.8 zincada + resina epoxi para anclajes", "Fijación a la platea existente"],
        ["Pintura", "Arenado Sa 2½, epoxi rico en zinc 75 µm + esmalte poliuretánico 50 µm", "Ambiente agresivo (C4)"],
        ["Pasarela y escalera", "Rejilla electrosoldada 30 × 30 galvanizada; barandas de caño Ø42", "EN ISO 14122"],
    ], anchos=[4.6, 7.2, 4.0], alin=["L", "L", "L"])
    m.h("9.2. Cómo va armado: subconjuntos y uniones", 2)
    m.p("Para que el secador se pueda fabricar en un taller metalúrgico de Crespo, transportar en un semirremolque "
        "común y armar con una grúa chica, se divide en subconjuntos que llegan terminados a la obra:")
    m.tabla("Subconjuntos de fabricación y montaje", [
        ["Subconjunto", "Se hace en taller", "Se une en obra con"],
        ["Columnas (10)", "UPN 120 cortada a 3.388 mm, placa base soldada (filete 6 mm), cartelas de unión, arenado y pintura", "Anclajes químicos M16 a la platea"],
        ["Vigas longitudinales (4)", "IPN 140 de 13,0 m en dos tramos (9,75 + 3,25 m, de barras comerciales de 12 m) con agujeros para cartelas y cubrejuntas", "Bulones M16 8.8 a las cartelas; empalme con cubrejuntas abulonadas sobre la columna D"],
        ["Travesaños (39)", "L 50×50×5 cortados a medida", "Soldadura E7018 en obra a las vigas"],
        ["Ménsulas y consolas", "PL 12 con cartelas y colisos", "Soldadura a la estructura (ménsulas) y bulones M16 (consolas)"],
        ["Tambores motrices (3)", "Tambor engomado + eje SAE 1045 rectificado + bujes cónicos, balanceado estático", "UCF 212 sobre las ménsulas"],
        ["Tambores de reenvío (3)", "Tambor + eje Ø60/Ø50", "UCT 210 con tornillo M20"],
        ["Bandas (3)", "Rollos de 25 m del fabricante, con varilla de empalme", "Empalme en obra"],
        ["Accionamientos (3)", "Motorreductor armado y probado en banco (sentido de giro y límite de par)", "Consola con colisos; cadena"],
        ["Cerramiento", "Paneles sándwich a medida, puertas con marco y microinterruptor", "Tornillos autoperforantes con arandela de neopreno y silicona de alta temperatura"],
        ["Pasarela y escalera", "Tramos de 3,25 m galvanizados", "Bulones a las columnas"],
    ], anchos=[3.4, 7.6, 4.8], alin=["L", "L", "L"])
    m.p("Las uniones principales de la estructura son abulonadas para poder desarmar el equipo: solo los travesaños y "
        "las ménsulas se sueldan en obra. Todas las soldaduras se hacen con electrodo básico E7018, con soldador "
        "calificado, y se controlan visualmente al 100 % y con líquidos penetrantes las de las ménsulas (capítulo de "
        "pruebas). Después de soldar se retoca la pintura con epoxi rico en zinc.")
    m.h("9.3. Tolerancias de fabricación y montaje", 2)
    m.lista([
        "Planta: diagonales de los ejes de columnas iguales con ± 3 mm (13,13 m).",
        "Columnas a plomo con ± 2 mm en 3,4 m; placas base niveladas con ± 1 mm.",
        "Travesaños de un mismo piso en un plano con ± 1 mm (asiento de las guías).",
        "Ejes de tambores a escuadra con el eje de la cámara: ≤ 1 mm por metro; paralelismo motriz-reenvío ≤ 1 mm.",
        "Ruedas de la cadena en el mismo plano con ≤ 1 mm; flecha de la cadena ≈ 2 % de la distancia entre centros.",
        "Asientos de cubos de los ejes rectificados Ra 0,8 µm; rectitud del eje ≤ 0,1 mm/m.",
    ])


def fijacion(m):
    an, ms = FAT["anclajes"]["secador"], FAT["anclajes"]["masa"]
    m.h("10. Fijación al piso", 1)
    m.p("El secador apoya en diez placas base, una por columna, fijadas a la platea con anclajes químicos. Se eligió "
        "anclaje químico (varilla roscada pegada con resina) porque se coloca sobre el hormigón ya hecho, sin "
        "insertos previos, admite corregir la ubicación al replantear y no expande el hormigón cerca de los bordes.")
    m.h("10.1. Fundación", 2)
    m.p("El piso general de la nave es de 15 cm de hormigón armado. Debajo del secador se hace una platea de 20 cm "
        "de espesor y 14,0 × 3,6 m, de hormigón H-21 con malla Q188 arriba y abajo, integrada al piso: los anclajes de "
        "125 mm de profundidad efectiva piden un espesor mínimo del orden de h_ef + 2·d0 ≈ 165 mm y una distancia al "
        "borde de al menos 150 mm. La presión de contacto es muy baja (ver tabla), por lo que no hacen falta bases "
        "aisladas.")
    m.h("10.2. Verificación de los anclajes", 2)
    m.p(f"Cargas: peso propio {miles(ms['total_kg'])} kg más {miles(an['m_kg'] - ms['total_kg'])} kg de guano en proceso, "
        f"repartidos en {an['placas']} placas; esfuerzo horizontal por el tiro de las cadenas y el arranque de las "
        f"bandas de {miles(an['H_total_N'])} N en total. Crespo está en zona sísmica 0 (INPRES-CIRSOC 103) y dentro de "
        "la nave no hay viento, de modo que no se consideran esas acciones.")
    m.tabla("Verificación de la fijación al piso", [
        ["Magnitud", "Valor"],
        ["Compresión por placa", f"{c(an['V_placa_kN'], 1)} kN → σ = {c(an['sigma_apoyo_MPa'], 2)} MPa sobre el grout"],
        ["Corte por varilla", f"{miles(an['H_var_N'])} N → τ = {c(an['tau_MPa'], 1)} MPa"],
        ["Resistencia de cálculo por varilla (catálogo, H-21 no fisurado)", f"N_Rd = {c(an['N_Rd'], 0)} kN; V_Rd = {c(an['V_Rd'], 0)} kN"],
        ["Uso al corte", f"{c(an['uso_V_pct'], 1)} %"],
        ["Par de instalación y precarga", f"{c(an['T_inst'], 0)} N·m → F ≈ {c(an['F_pre_kN'], 0)} kN (T = K·F·d, K = 0,2)"],
    ], anchos=[8.5, 7.3], alin=["L", "L"])
    m.p("Los anclajes trabajan muy por debajo de su capacidad: lo que manda es la buena ejecución (limpieza del "
        "agujero, curado) y no la resistencia. Los valores de N_Rd y V_Rd son típicos de catálogo y se deben "
        "confirmar con la ficha del producto que se compre.")
    m.figura(plano_sc(5), "Plano SC-05: estructura, plantilla de replanteo y detalle de la placa base con el anclaje químico", 16.5)
    m.h("10.3. Procedimiento de colocación", 2)
    m.lista([
        "Replantear los ejes A a E y 1 a 2 con tiza de línea y nivel láser; controlar las diagonales.",
        "Marcar los 4 agujeros de cada placa con la plantilla (cuadrado de 140 mm).",
        "Perforar Ø18 × 135 mm con taladro percutor, sin ovalizar.",
        "Limpiar: 2 soplados, 2 cepillados con cepillo de Ø18 y 2 soplados más. El polvo que queda reduce mucho la adherencia.",
        "Inyectar la resina desde el fondo hasta llenar 2/3 del agujero y colocar la varilla girándola hasta el fondo.",
        "Respetar el tiempo de curado del fabricante antes de cargar (≈ 24 h a 20 °C; el doble con menos de 10 °C).",
        "Presentar la columna con su placa sobre cuñas, nivelar y aplomar, llenar debajo con grout de 20 mm.",
        "Con el grout fraguado, apretar las tuercas con llave dinamométrica a 80 N·m.",
    ])


def montaje(m):
    m.h("11. Manual de armado paso a paso", 1)
    m.p("El montaje del secador lo hace un equipo de dos técnicos y dos ayudantes con una grúa o autoelevador de "
        "3 t, en unos 15 días hábiles. Cada paso tiene su imagen del modelo 3D (las piezas que se montan en ese paso "
        "aparecen resaltadas), las herramientas y los controles. Los mismos pasos se pueden recorrer en el visor "
        "3D (botón «Montaje paso a paso») y están resumidos en el plano SC-06.")
    m.recuadro("Seguridad durante el montaje",
               "Casco, calzado de seguridad, guantes y anteojos en todo momento. Arnés con línea de vida para trabajar a "
               "más de 2 m hasta que la pasarela tenga su baranda. Izajes con equipo habilitado y eslingas revisadas, "
               "sin personas debajo de la carga. Soldadura con permiso de trabajo en caliente y matafuego ABC al lado. "
               "No energizar ningún motor hasta que los cárteres estén colocados.")
    for i, p in enumerate(PASOS, 1):
        m.h(f"11.{i}. Paso {i}: {p['titulo'].split('. ', 1)[1]}", 2)
        m.figura(render(os.path.join("montaje", f"paso_{i:02d}.png"), 1400), f"Paso {i}: {p['titulo'].split('. ', 1)[1]}", 12.5)
        m.p(p["texto"])
        m.p(f"Herramientas: {p['herramientas']}.", cursiva=True)
    m.h(f"11.{len(PASOS) + 1}. Controles al terminar el armado", 2)
    m.tabla("Lista de control del montaje", [
        ["Control", "Tolerancia / valor", "Cómo se mide"],
        ["Diagonales de la planta", "± 3 mm", "Cinta métrica entre ejes A1-E2 y A2-E1"],
        ["Plomo de columnas", "± 2 mm en 3,4 m", "Plomada o nivel láser"],
        ["Nivel de los travesaños de cada piso", "± 1 mm", "Nivel láser y regla"],
        ["Escuadra de los ejes de tambores", "≤ 1 mm/m", "Diagonales desde el eje al bastidor"],
        ["Alineación de piñón y corona", "< 1 mm", "Regla de acero apoyada en las dos ruedas"],
        ["Flecha de la cadena", "≈ 2 % de la distancia entre centros", "Regla y cinta en el ramal flojo"],
        ["Tensión de banda", "T2 ≈ 2.000 N (flecha ≈ 15 mm entre rodillos)", "Dinamómetro de mano en el ramal de retorno"],
        ["Capa de producto", "30 mm", "Galgas en la compuerta niveladora"],
        ["Par de los anclajes", "80 N·m", "Llave dinamométrica"],
        ["Microinterruptores de puertas", "Detienen la banda al abrir", "Prueba con la banda en marcha lenta"],
    ], anchos=[5.2, 5.0, 5.6], alin=["L", "L", "L"])


SIM = os.path.join(RAIZ, "simulacion_termica", "figuras")


def modelo_termico(m):
    """Rev. F: láminas del estudio térmico del secador (simulacion_termica/figuras)."""
    m.figura(os.path.join(SIM, "01_perfiles_diseno.png"),
             "Modelo térmico: humedad del guano y temperatura del aire a lo largo de los tres pisos (a 135 °C el producto "
             "queda seco al final del piso 2)", 16)
    m.figura(os.path.join(SIM, "14_balance_de_energia.png"),
             "Modelo térmico: destino del calor del generador en el punto de diseño, con el aire ajustado al 15 % y a la "
             "capacidad máxima", 16)


def lazo_humedad(m):
    """Rev. F: respuesta del lazo de humedad en cascada (simulacion_termica/figuras/12)."""
    m.figura(os.path.join(SIM, "12_control_dinamico.png"),
             "Modelo térmico: respuesta a un cambio del guano de 72 a 76 % con el lazo anterior (bandas) y con MIC-01 en "
             "cascada sobre TIC-01, con y sin ajuste anticipado", 16)


def instalacion(m):
    m.h("12. Instalación y puesta en marcha", 1)
    m.h("12.1. Aplicación del equipo y límites de uso", 2)
    m.p("El secador SC-4 está pensado para guano de gallina ponedora con 60 a 78 % de humedad, en capa de 20 a 40 mm, "
        "con aire de entrada de 90 a 150 °C, cuya consigna fija el lazo de humedad (apartado 14.5.2). Con esos valores "
        "procesa 8 t/día de guano húmedo en un turno de 8 h (1.000 kg/h, con aire a unos 100 °C) y entrega producto al "
        "12 a 17 % de humedad. A 135 °C el mismo equipo seca unos 1.440 kg/h al 15 % (apartado 6.7): las 16 t de dos "
        "turnos entran en unas 11,1 h de marcha, con la cinta de alimentación a unos 5,6 cm/s (variador al 56 %). Puede secar también cama de "
        "pollo o estiércoles pastosos de características parecidas, ajustando la temperatura del aire y la velocidad "
        "de las bandas. No debe usarse con materiales que se peguen a la malla en forma permanente, con piedras o "
        "metales (dañan la malla y los tambores) ni con aire por encima de 150 °C (se pierde nitrógeno y aumenta el "
        "riesgo de incendio del producto seco).")
    m.h("12.2. Requisitos del lugar", 2)
    m.lista([
        "Platea de 20 cm bajo el secador (capítulo 10) y espacio libre de 1,0 m alrededor para mantenimiento; 2,5 m del "
        "lado Sur para sacar ejes y motorreductores.",
        "Altura libre mínima de 4,8 m sobre el piso (secador, campana y pasarela).",
        "Ducto de aire caliente desde el generador hasta la boca 1.200 × 400 de la cara Norte, aislado.",
        "Ducto Ø800 desde la campana hasta el ciclón; cinta de alimentación hasta la boca de alimentación del extremo Oeste; "
        "sinfín de descarga bajo la tolva del extremo Este.",
        "Alimentación eléctrica desde el TGF (variadores de M5, M6 y M7) y tablero local TS-1 junto al secador.",
        "Anillo de puesta a tierra de la nave (plano 17, ítem D16) para conectar el bastidor.",
    ])
    m.h("12.3. Conexiones", 2)
    m.tabla("Conexiones del secador", [
        ["Conexión", "Desde → hasta", "Detalle"],
        ["Aire caliente", "Ducto del generador → plenum Norte", "Brida con junta de fibra cerámica; compensador de dilatación"],
        ["Aire agotado", "Campana 800 × 800 → ciclón", "Ducto Ø800 con compuerta y tomas de presión y temperatura (D6)"],
        ["Producto húmedo", "Cinta de alimentación M8 → boca de alimentación", "Manga de lona para absorber vibraciones"],
        ["Producto seco", "Tolva de descarga → sinfín M10", "Brida abulonada con junta de goma"],
        ["Fuerza motriz", "VFD en el TGF → motores M5, M6, M7", "Cable apantallado 4 × 1,5 mm², pantalla a tierra en los dos extremos"],
        ["Seguridad", "Puertas ZS-01..06, hongos, sensores de giro SS-01..03", "Al relé de seguridad categoría 3 y al PLC"],
        ["Instrumentos", "PT100 TT-02/03/04, sensores de borde ZS-10/11", "Cable apantallado en bandeja separada de la fuerza"],
        ["Puesta a tierra", "Bastidor → anillo de Cu 50 mm²", "Cable verde-amarillo 16 mm² y terminal a una placa base"],
    ], anchos=[3.0, 5.4, 7.4], alin=["L", "L", "L"])
    m.h("12.4. Ajuste de los variadores de las cintas", 2)
    at = FAT["eje_motriz"]["atasco"]
    m.lista([
        "Datos de placa del motor (0,75 kW, 380 V, corriente, 1.400 rpm) y autoajuste del variador.",
        "Frecuencia mínima 12 Hz y máxima 50 Hz (bandas de 0,2 a 0,9 m/min); consigna inicial ≈ 20 Hz.",
        "Rampas de aceleración y desaceleración de 10 s (arranque suave de la banda cargada).",
        f"Límite de corriente o de par del 150 % del nominal ({at['T_limite_VFD']} N·m en el eje del tambor) con detención "
        "por sobrecarga: protege el eje si la banda se traba (capítulo 8).",
        "Protección térmica del motor por modelo I²t y entrada de habilitación desde el relé de seguridad.",
        "Comunicación Profinet con el PLC para la consigna de velocidad y el estado.",
    ])
    m.h("12.5. Puesta en marcha", 2)
    m.tabla("Etapas de la puesta en marcha", [
        ["Etapa", "Qué se hace", "Criterio de aceptación"],
        ["1. Inspección previa", "Lista de control del montaje, limpieza interior, retiro de herramientas", "Lista completa y firmada"],
        ["2. Prueba eléctrica", "Aislación de motores (megóhmetro 500 V), continuidad de tierra, sentido de giro en vacío", "> 1 MΩ; R tierra < 5 Ω"],
        ["3. Marcha en vacío y en frío", "Cada banda 4 h a 20 y a 50 Hz; centrado; ruido; temperatura de reductores", "Banda centrada ± 10 mm; reductor < 70 °C"],
        ["4. Calentamiento sin carga", "Generador en marcha, aire a 135 °C, bandas en vacío 4 h", "Sin fugas de aire; dilataciones libres; paneles afuera < 45 °C"],
        ["5. Carga progresiva", "25, 50, 75 y 100 % del caudal de guano, 2 h cada escalón", "Humedad de salida 12 a 17 %; corriente < nominal"],
        ["6. Marcha continua", "3 turnos completos a capacidad nominal", "8 t/día al 15 % de humedad; sin paradas por falla"],
        ["7. Entrega", "Acta de recepción, capacitación de operadores, entrega de manuales y planos", "Acta firmada"],
    ], anchos=[3.4, 7.2, 5.2], alin=["L", "L", "L"])


def operacion_extra(m):
    m.h("13.6. Advertencias para el operador", 2)
    m.lista([
        "No abrir las puertas de inspección con las bandas en marcha: el microinterruptor detiene la banda, pero el "
        "aire caliente sigue circulando.",
        "No meter las manos ni herramientas entre la banda y los tambores ni en las cadenas, aun con el equipo detenido, "
        "sin bloquear y etiquetar el seccionador (LOTO).",
        "No subir a la pasarela con el equipo en marcha salvo para inspección visual, por los pasillos y con casco.",
        "No subir la temperatura del aire por encima de 150 °C ni dejar producto seco acumulado dentro de la cámara: es "
        "combustible.",
        "Ante un ruido anormal, olor a quemado o una alarma de banda detenida: pulsar parada, avisar a mantenimiento y "
        "no rearmar sin conocer la causa.",
    ])
    m.h("13.7. Limpieza al final del turno", 2)
    m.p("Con el dosificador detenido, dejar que las bandas descarguen el producto (≈ 97 min), bajar la temperatura a "
        "60 °C, rasquetear los restos adheridos a la malla desde las puertas de inspección (equipo bloqueado), limpiar "
        "la tolva de descarga y las guías, y registrar las novedades en el parte diario.")


def ubicacion(m):
    m.h("16.3. Ubicación en Crespo, junto al Parque Industrial", 2)
    m.p("La planta se ubica en un lote de 120 × 76 m (9.120 m²) junto al Parque Industrial de Crespo, con acceso por la "
        "Ruta Nacional N.° 12 (km 40,6) y acceso secundario por la calle Democracia (continuación de Santiago Besler), "
        "al lado del predio donde se proyecta la planta de biogás «Ñande Zukunft I» de Bioenergía Virch S.A. (32,76 ha, "
        "24 biodigestores; en septiembre de 2026 estaba en etapa de estudios). La "
        "energía eléctrica la provee la Cooperativa La Agrícola Regional (LAR), que puso en servicio una subestación "
        "nueva en mayo de 2026.")
    m.lista([
        "El guano que la secadora no alcanza a procesar (fines de semana y feriados, ≈ 920 t/año) tiene un destino cercano.",
        "Los camiones de guano llegan desde las granjas por la ruta sin entrar a la planta urbana.",
        "El parque ofrece servicios industriales, acceso a la red de la LAR y una zonificación compatible con la actividad.",
        "La distancia a las viviendas reduce los conflictos por olores (con el lavador de gases y el biofiltro).",
    ])
    m.figura(plano(14), "Plano 14: croquis de ubicación en Crespo (sin escala) e implantación del lote a 1:1000", 16.5)
    crespo = os.path.join(RAIZ, "modelo_3d", "renders", "P10_C_crespo.png")
    if os.path.exists(crespo):
        m.figura(liviana(crespo), "Vista «Ubicación en Crespo» del visor 3D: el lote junto al Parque Industrial, la "
                 "planta de biogás vecina y la Ruta Nacional 12 (esquemático, sin escala)", 15)
    m.p("Los retiros del lote (frente 10 m, laterales y fondo 5 m) se adoptaron hasta confirmarlos con el reglamento "
        "del Parque Industrial; la parcela exacta, la orientación y los datos catastrales se deben verificar en la "
        "Municipalidad de Crespo antes del proyecto ejecutivo.")
    m.figura(plano(13), "Plano 13: implantación general ampliada (predio de la Rev. C y Sector Este de la Rev. D)", 16.5)
    p10 = os.path.join(RAIZ, "modelo_3d", "renders", "P10_A2_predio.png")
    if os.path.exists(p10):
        m.figura(liviana(p10), "Modelo 3D del predio completo (visor.html)", 15)


def ampliacion(m):
    from P10 import AGREGADOS
    m.h("17. Ampliación de la Revisión D", 1)
    m.p("La Revisión D agregó al proyecto los ítems de seguridad y mantenimiento que pidieron la revisión de los planos "
        "y la visita a plantas de la zona (D1 a D24) y una ampliación del predio hacia el Este (E1 a E10): limpieza de "
        "vehículos, ventilación de la recepción con biofiltro, zaranda, ensacado, depósito de expedición, biogás con "
        "cogeneración y ventilación general de la nave. Todas las cargas eléctricas nuevas van a un tablero nuevo, el "
        "TG2; el tablero general TGF de la Rev. C no cambia. Los capítulos 18 a 21 son la memoria de cálculo de estas "
        "ampliaciones.")
    filas = [["Ítem", "Descripción", "Plano"]] + [[a, b, cc] for a, b, cc in AGREGADOS]
    m.tabla("Agregados de la Revisión D (lista de partes del plano 10)", filas, anchos=[1.4, 12, 1.6], alin=["L", "L", "C"])
    m.figura(plano(17), "Plano 17: nave y equipos, seguridad, accesos y mantenimiento (Rev. E)", 16.5)


def pruebas(m):
    an = FAT["anclajes"]["secador"]
    wo = FAT["wohler"]
    m.h("25. Pruebas de carga, resistencia y fatiga", 1)
    m.p("Este capítulo define las pruebas que confirman que los materiales y el equipo armado tienen la resistencia "
        "calculada. Se dividen en ensayos de recepción de materiales (destructivos, sobre probetas), ensayos no "
        "destructivos de piezas terminadas, pruebas de carga del equipo montado y controles en servicio. Los ensayos "
        "de materiales siguen el apunte de cátedra del INET y las normas citadas; los puede hacer el laboratorio de la "
        "escuela o uno externo (INTI, universidades).")
    m.h("25.1. Ensayos de recepción de materiales", 2)
    m.tabla("Ensayos destructivos sobre probetas", [
        ["Ensayo", "Norma", "Material / pieza", "Criterio de aceptación"],
        ["Tracción", "ISO 6892-1 (IRAM-IAS U 500-102)", "Barra SAE 1045 de los ejes; perfil F-24", "Sut ≥ 570 / 370 MPa; Sy ≥ 310 / 240 MPa; alargamiento ≥ 16 / 22 %"],
        ["Dureza Brinell HB 10/3000/15", "ISO 6506-1", "Barra SAE 1045 (3 improntas por extremo)",
         f"{FAT['recepcion']['hb_adop']} a {FAT['recepcion']['hb_max']} HB: impronta de {c(FAT['recepcion']['d_min'], 2)} a "
         f"{c(FAT['recepcion']['d_max'], 2)} mm (Sut ≈ 3,45·HB; capítulo 8.8)"],
        ["Impacto Charpy V", "ISO 148-1", "Chapa PL 12 de ménsulas y placas", "≥ 27 J a 0 °C"],
        ["Fatiga por flexión rotativa (Wöhler)", "ISO 1143", f"{wo['probetas']} probetas Ø7,5 de la barra de los ejes", f"S'e ≥ {c(wo['Se_prima'], 0)} MPa (si no, recalcular)"],
        ["Plegado de soldadura", "ISO 5173", "Probeta de calificación del soldador (E7018)", "Sin fisuras > 3 mm"],
    ], anchos=[3.0, 3.6, 4.4, 4.8], alin=["L", "L", "L", "L"])
    m.h("25.2. Ensayo de fatiga de Wöhler", 2)
    m.p("Procedimiento (apunte INET, ensayos dinámicos): se mecanizan las probetas de la misma barra que los ejes, con "
        "sección de ensayo de 7,5 mm pulida a espejo en sentido longitudinal. En la máquina de flexión rotativa cada "
        "probeta gira cargada con un peso que fija la tensión máxima de flexión; un contador registra las vueltas hasta "
        "la rotura. Se empieza por el nivel más alto (85 % de Sut) y se baja hasta encontrar dos niveles seguidos sin "
        "rotura a 10⁷ ciclos. Con los puntos se traza la curva S-N en escala logarítmica, se ajusta la recta de Basquin "
        "y se toma como límite de fatiga el nivel más alto sin rotura. El plan de niveles y la vida esperada están en "
        "el capítulo 8 y en el plano SC-04. Se observa además la superficie de fractura: zona lisa de propagación con "
        "marcas de playa y zona rugosa de rotura final, típicas de la falla por fatiga.")
    m.h("25.3. Ensayos no destructivos", 2)
    m.tabla("Ensayos no destructivos", [
        ["Ensayo", "Norma", "Dónde", "Cuándo"],
        ["Partículas magnéticas", "ISO 9934-1", "Escalones, chaveteros y asientos de los 6 ejes", "Antes del montaje y cada 2 años"],
        ["Líquidos penetrantes", "ISO 3452-1", "Soldaduras de ménsulas, cartelas y consolas", "Después de soldar"],
        ["Ultrasonido", "ISO 16810", "Barras Ø65 de los ejes (defectos internos)", "Recepción del material"],
        ["Inspección visual de soldaduras", "ISO 17637", "Todas las soldaduras", "100 %"],
        ["Espesor de pintura", "ISO 2808", "Estructura", "Recepción: ≥ 125 µm de película seca"],
    ], anchos=[3.6, 2.6, 5.8, 3.8], alin=["L", "L", "L", "L"])
    m.h("25.4. Pruebas de carga del equipo montado", 2)
    m.tabla("Pruebas de carga", [
        ["Prueba", "Cómo se hace", "Aceptación"],
        ["Pasarela y escalera (EN ISO 14122-2/3)", "Carga uniforme de 3 kN/m² (1,5 × 2 kN/m²) con bolsas de arena 30 min; "
         "carga horizontal de 500 N/m en la baranda", "Flecha ≤ L/200 sin deformación permanente; baranda sin deformación"],
        ["Bandas (sobrecarga)", "Piso 1 cargado con guano o arena húmeda hasta 30 kg/m² (125 % de la carga de diseño) "
         "durante 2 h a velocidad nominal", "Corriente < In; sin patinamiento en el tambor; malla centrada"],
        ["Límite de par (atasco simulado)", "En banco, el motorreductor con brazo de reacción y dinamómetro; se frena la "
         "salida hasta que el variador detiene", f"Par en el tambor ≤ {FAT['eje_motriz']['atasco']['T_limite_VFD']} N·m equivalente; detención < 2 s"],
        ["Anclajes químicos", f"Tracción de prueba de 15 kN con gato hueco en 1 de cada 10 anclajes (N_Rd = {c(an['N_Rd'], 0)} kN)",
         "Desplazamiento < 0,5 mm; sin fisuras en el hormigón"],
        ["Tensores y ejes", "Tensado al 120 % de T2 durante 1 h; luego medición de rectitud de los ejes", "Sin deformación permanente"],
    ], anchos=[3.8, 7.4, 4.6], alin=["L", "L", "L"])
    m.h("25.5. Controles en servicio", 2)
    m.tabla("Controles periódicos relacionados con la fatiga y la resistencia", [
        ["Control", "Norma / método", "Frecuencia", "Límite"],
        ["Vibraciones de motorreductores y ventiladores", "ISO 20816-3", "Trimestral", "Zona A/B (< 2,8 mm/s en reductores)"],
        ["Termografía de rodamientos, motores y tablero", "Cámara termográfica", "Semestral", "ΔT < 30 K sobre el ambiente en rodamientos"],
        ["Partículas magnéticas de ejes", "ISO 9934-1", "Cada 2 años", "Sin indicaciones lineales"],
        ["Reapriete de anclajes", "Llave dinamométrica", "Anual", "80 N·m"],
        ["Registro de horas y detenciones por sobrecarga", "HMI", "Continuo", "Analizar cada detención por límite de par"],
    ], anchos=[5.4, 3.4, 2.6, 4.4], alin=["L", "L", "L", "L"])


def presupuesto(m, figs):
    inv, lar, en, ev = PRES["inversion"], PRES["lar"], PRES["energia"], PRES["evaluacion"]
    sec = PRES["secador"]
    m.h("26. Presupuesto con compras en LAR y evaluación económica", 1)
    m.p(f"El presupuesto se armó a valores de octubre de 2026, en dólares (BNA vendedor ${miles(PRES['dolar'])} por dólar, "
        f"{PRES['fecha']}) y en pesos para los materiales que se compran en la zona. Los materiales de obra, de "
        "ferretería y eléctricos se piden a la Cooperativa La Agrícola Regional (LAR) de Crespo, que además es la "
        "distribuidora de energía. Es una estimación de anteproyecto (± 25 %). La planilla completa, con las fuentes de "
        "cada precio, es presupuesto/Presupuesto_Secadora_Guano.xlsx (fuente: fuente/calculos/presupuesto.py).")
    m.h("26.1. Inversión", 2)
    filas = [["Ítem", "Rubro", "Descripción", "USD"]]
    for f in inv["filas"]:
        filas.append([f[0], f[1], f[2], miles(f[6])])
    filas += [["", "", "Subtotal planta Rev. C", miles(inv["sub_revC"])],
              ["", "", "Subtotal ampliación Rev. D/E", miles(inv["sub_revD"])],
              ["", "", "Ingeniería y habilitaciones", miles(inv["sub_ing"])],
              ["", "", "Imprevistos", miles(inv["imprevistos"])],
              ["", "", "TOTAL", miles(inv["total"])]]
    m.tabla("Presupuesto de inversión", filas, anchos=[1.1, 2.8, 10.0, 1.9], alin=["L", "L", "L", "R"], total=True)
    m.figura(figs["inversion"], "Composición de la inversión", 15)
    m.h("26.2. Costo del secador SC-4", 2)
    filas = [["Componente", "Cant.", "Unid.", "USD unit.", "USD", "Proveedor"]]
    for f in sec["filas"]:
        filas.append([f[0], miles(f[1]), f[2], c(f[3], 2) if f[3] < 10 else miles(f[3]), miles(f[4]), f[5]])
    filas.append(["Total del secador", "", "", "", miles(sec["total"]), ""])
    m.tabla("Costo del secador por componentes", filas, anchos=[6.6, 1.2, 1.0, 1.5, 1.5, 4.0],
            alin=["L", "R", "C", "R", "R", "L"], total=True)
    m.h("26.3. Pedido a la Cooperativa La Agrícola Regional", 2)
    filas = [["Material", "Detalle", "Cant.", "Unid.", "$ unit.", "$ total"]]
    for f in lar["filas"]:
        filas.append([f[0], f[1], miles(f[2]), f[3], miles(f[4]), miles(f[5])])
    filas.append(["Total del pedido", "", "", "", "", f"$ {miles(lar['total_ARS'])} (USD {miles(lar['total_USD'])})"])
    m.tabla("Pedido de materiales a LAR (corralón, ferretería y electricidad)", filas,
            anchos=[3.2, 6.4, 1.2, 1.0, 1.7, 2.3], alin=["L", "L", "R", "C", "R", "R"], total=True)
    m.h("26.4. Energía eléctrica con LAR", 2)
    t = en["tarifa"]
    m.p(f"Con la tarifa T3 de grandes demandas en baja tensión (valores de referencia del cuadro tarifario del EPRE a "
        f"confirmar con LAR: cargo fijo ${miles(t['cargo_fijo_mes'])}/mes, potencia ${miles(t['potencia_kw_mes'])}/kW·mes, "
        f"energía ${miles(t['energia_kwh'])}/kWh) y {en['potencia_kW']} kW contratados:")
    m.tabla("Consumo y costo de la energía eléctrica", [
        ["Concepto", "Valor"],
        ["Consumo anual TGF (proceso Rev. C)", f"{miles(en['E_TGF_kWh'])} kWh"],
        ["Consumo anual TG2 (ampliación)", f"{miles(en['E_TG2_kWh'])} kWh"],
        ["Generación de la cogeneración G1", f"{miles(en['E_G1_kWh'])} kWh (autoconsumo {miles(en['autoconsumo_kWh'])}; inyección {miles(en['inyectada_kWh'])})"],
        ["Costo anual sin G1", f"$ {miles(en['costo_sin_G1_ARS'])} (USD {miles(en['costo_sin_G1_USD'])})"],
        ["Costo anual con G1", f"$ {miles(en['costo_con_G1_ARS'])} (USD {miles(en['costo_con_G1_USD'])})"],
        ["Ahorro por la cogeneración", f"USD {miles(en['ahorro_G1_USD'])} por año"],
    ], anchos=[7, 8.8], alin=["L", "L"])
    m.h("26.5. Costos operativos, ingresos y evaluación", 2)
    filas = [["Costo operativo anual (escenario A)", "USD"]] + [[k, miles(v)] for k, v in ev["costos"].items()]
    filas.append(["Total", miles(ev["costo"])])
    m.tabla("Costos operativos anuales", filas, anchos=[12.5, 3.3], alin=["L", "R"], total=True)
    mix = ev["mix"]
    filas = [["Ingreso anual (escenario A)", "USD"]]
    filas.append([f"Venta de guano seco ({', '.join(f'{k} {int(v[0] * 100)} % a USD {miles(v[1])}/t' for k, v in mix.items())})", miles(ev["ventas"])])
    filas += [["Digestato (biofertilizante)", miles(ev["digestato"])], ["Sulfato de amonio del lavador", miles(ev["sulfato"])],
              ["Ahorro en la gestión del guano fresco", miles(ev["ahorro_gestion"])], ["Total", miles(ev["ingresos"])]]
    m.tabla("Ingresos y ahorros anuales", filas, anchos=[12.5, 3.3], alin=["L", "R"], total=True)
    filas = [["Escenario", "Inversión", "Neto anual", "Repago", "VAN 10 %", "TIR"]]
    for e in ev["escenarios"]:
        filas.append([e["nombre"], miles(e["inversion"]), miles(e["neto"]), f"{c(e['repago'], 1)} años", miles(e["VAN"]),
                      f"{c(e['TIR'], 1)} %"])
    m.tabla(f"Indicadores por escenario (USD, {ev['anios']} años, tasa {int(ev['tasa'] * 100)} %)", filas,
            anchos=[6.2, 1.9, 1.9, 1.7, 2.1, 1.4], alin=["L", "R", "R", "R", "R", "R"], resaltar=[3, 4])
    m.figura(figs["flujo"], "Flujo de caja acumulado de los cuatro escenarios", 15)
    a, b_, cc, d = ev["escenarios"]
    m.recuadro("Recomendación económica",
               f"Con un solo turno la planta completa recupera la inversión en {c(a['repago'], 1)} años (TIR {c(a['TIR'], 1)} %): "
               "se justifica por sus beneficios ambientales y sanitarios más que como negocio. Operando en dos turnos "
               f"(16 t/día, guano de dos granjas) el repago baja a {c(cc['repago'], 1)} años con una TIR de {c(cc['TIR'], 1)} %, "
               f"y sin la planta de biogás a {c(d['repago'], 1)} años (TIR {c(d['TIR'], 1)} %). Se recomienda construir el "
               "secador y la nave en la primera etapa, planificar desde el inicio la operación en dos turnos y dejar el "
               "biogás como segunda etapa, cuando el volumen de guano sobrante lo justifique.")


def conclusiones(m):
    em = FAT["eje_motriz"]
    ev = PRES["evaluacion"]["escenarios"]
    m.h("28. Conclusiones", 1)
    m.p("El proyecto demuestra que es técnicamente factible resolver el problema del guano de gallina de una granja de "
        "60.000 ponedoras con un secador de cinta de tres pisos alimentado con aire caliente de cáscara de arroz. El "
        "equipo, de 13 m de largo y 72 m² de superficie de secado, procesa 1.000 kg/h de guano al 72 % y entrega "
        "329 kg/h de fertilizante al 15 % de humedad. El generador de 880 kW quema 314 kg/h de cáscara a la "
        "temperatura máxima de diseño (135 °C); con el aire ajustado al 15 %, unos 219 kg/h (apartado 6.7).")
    m.p("En esta entrega final el secador quedó definido hasta el nivel de fabricación: modelo 3D pieza por pieza con "
        "su despiece y lista de materiales, planos de conjunto, despiece, ejes, bastidor y anclajes, y un manual de "
        f"armado de 13 pasos. La verificación a fatiga mostró que el eje motriz verifica (n = {c(em['n_min'], 2)}) solo "
        "si se rectifican los asientos de los cubos y se limita el par en los variadores, y que el eje de reenvío de "
        "50 mm no alcanzaba: se cambió a 60 mm. Son mejoras baratas que evitan roturas en servicio.")
    m.p("La ampliación de la Rev. D (seguridad, mantenimiento, limpieza de vehículos, ventilación, zaranda, ensacado, "
        "depósito y biogás) completa la planta como establecimiento habilitable. Su instalación eléctrica quedó "
        f"verificada con el TG2 y {R['tg2']['balance']['adoptada_kW']} kW contratados a la LAR, y la planta se ubica "
        "junto al Parque Industrial de Crespo, al lado del predio de la planta de biogás proyectada.")
    m.p("La Rev. F incorpora el estudio térmico del secador (apartado 6.7 y carpeta simulacion_termica/): el equipo "
        "tiene más capacidad de la necesaria y la humedad del producto se controla con la temperatura del aire, en "
        "cascada sobre el lazo de temperatura. Por eso se cambiaron el lazo de humedad, las guías de los pisos 2 y 3 "
        "(PTFE), el sello de los bordes de las bandas, la aislación y la purga de condensado del escape, la regla de la "
        "recirculación CD-03 y la descarga, que suma una tolva de retención de una hora y un enfriador.")
    m.p(f"En lo económico, con un turno la planta completa se justifica por sus beneficios ambientales (repago "
        f"{c(ev[0]['repago'], 1)} años); en dos turnos es un buen negocio (repago {c(ev[2]['repago'], 1)} años, TIR "
        f"{c(ev[2]['TIR'], 1)} %). Para el grupo, el proyecto integró termodinámica, máquinas eléctricas, instalaciones, "
        "elementos de máquinas, ensayos de materiales, organización industrial, seguridad e higiene, gestión ambiental "
        "y evaluación de proyectos, además del dibujo técnico y el modelado 3D. Proponemos como continuación la "
        "construcción de un módulo piloto de una sola cinta y el ensayo de Wöhler del acero de los ejes. El módulo "
        "piloto debe medir el tamaño de grumo que deja el esparcidor, la curva de secado del guano de Crespo, la "
        "humedad del aire de escape y cuánto aire pasa por los bordes, y con eso ajustar el modelo térmico antes de "
        "construir el SC-4.")


BIBLIO_EXTRA = [
    "Budynas, R. G. y Nisbett, J. K. (2008). Diseño en ingeniería mecánica de Shigley (8.ª ed.). McGraw-Hill. Caps. 6 (fatiga), 7 (ejes), 8 (uniones abulonadas), 9 (soldaduras) y 11 (rodamientos).",
    "Ruiz, D. H. (2006). Fundamentos y ensayos en materiales metálicos. Instituto Nacional de Educación Tecnológica (INET). Apunte de cátedra: ensayos de tracción, dureza, impacto, fatiga y no destructivos.",
    "González Arias, A. y González Arias, C. E. (1999). Laboratorio de ensayos industriales. Metales (14.ª ed.). Ediciones Litenia. Cap. IX: fatiga (curva de Wöhler, diagrama de Smith, efectos que modifican la resistencia a la fatiga, máquinas de flexión rotativa).",
    "E.P.N.M. y S. N° 35. Laboratorio de ensayos: clases 2 (clasificación de los ensayos y normas), 3 (tracción), 5 (flexión), 6 (dureza Brinell), 8 (Rockwell) y 9 (Vickers y Shore).",
    "Acindar (Grupo ArcelorMittal). Tablas y equivalencias: perfiles laminados (IRAM-IAS U 500-503, grado F-24), barras y planchuelas (IRAM-IAS U 500-600), electrodos.",
    "ISO 6892-1, ISO 6506-1, ISO 148-1, ISO 1143 (ensayo de fatiga por flexión rotativa), ISO 9934-1, ISO 3452-1, ISO 16810, ISO 17637.",
    "ISO 20816-3: Vibraciones mecánicas – Medición y evaluación de la vibración de máquinas. EN ISO 14122-2/3: Medios de acceso permanentes a máquinas.",
    "IRAM-AADL J 20-06: Iluminación en ambientes de trabajo. ISO 6946: Resistencia térmica y transmitancia de elementos de construcción.",
    "INPRES-CIRSOC 103: Reglamento argentino para construcciones sismorresistentes (zonificación sísmica).",
    "Catálogos: NTN y SKF (unidades UCF y UCT), Tsubaki (cadenas RS60), WEG (motores W22 y variadores CFW500), Campagnoni (extractores AirTEC), Hilti y Fischer (anclajes químicos).",
    "Cooperativa La Agrícola Regional (LAR), Crespo: corralón, ferretería, electricidad y distribución de energía. EPRE Entre Ríos: cuadro tarifario 10/2026.",
]


def bibliografia(m, lineas):
    m.h("Bibliografía", 1)
    items = [ln[2:].strip() for ln in lineas if ln.startswith("- ")] + BIBLIO_EXTRA
    for x in items:
        par = m.d.add_paragraph(x)
        par.paragraph_format.left_indent = Cm(0.8)
        par.paragraph_format.first_line_indent = Cm(-0.8)
        m.html.append(f'<p class="biblio">{esc(x)}</p>')


def titulos_planos():
    filas = []
    for n in range(1, 25):
        ruta = os.path.join(FUENTE, "planos", f"P{n:02d}.py")
        primera = open(ruta, encoding="utf-8").readline().strip().strip('"').strip()
        tit = re.sub(r"^P\d+\s*-\s*", "", primera).rstrip(".")
        filas.append((f"{n:02d}", tit))
    return filas


TITULOS_SC = ["Secador de cinta SC-4: conjunto general (1:75)", "Despiece y lista de piezas",
              "Ejes motriz y de reenvío: fabricación (Rev. E)", "Verificación a fatiga (Shigley-Budynas)",
              "Bastidor, replanteo y fijación al piso", "Montaje paso a paso (manual de armado)"]


def anexo_planos(m):
    m.h("Anexo A. Planos", 1)
    m.p("Los planos se entregan en PDF A3 (vectoriales), en DXF para AutoCAD y como imágenes. El juego general tiene "
        "24 láminas (planos/pdf/Planos_Secadora_RevD.pdf) y el juego aparte del secador 6 láminas propias más las 4 del "
        "juego general que son del secador (secadora/planos/pdf/Planos_Secador_SC4.pdf). Se reproducen a continuación "
        "en tamaño reducido.")
    filas = [["N.°", "Plano"]] + [[n, t] for n, t in titulos_planos()] + [[f"SC-{i:02d}", t] for i, t in enumerate(TITULOS_SC, 1)]
    m.tabla("Lista de planos", filas, anchos=[1.6, 14.2], alin=["C", "L"])
    for n, t in titulos_planos():
        m.figura(plano(int(n)), f"Plano {n}: {t}", 16.5)
    for i, t in enumerate(TITULOS_SC, 1):
        m.figura(plano_sc(i), f"Plano SC-{i:02d}: {t}", 16.5)


def anexo_datos(m):
    m.h("Anexo D. Datos confirmados y pendientes de confirmar", 1)
    m.tabla("Datos que se cerraron en esta entrega", [
        ["Dato", "Cómo se resolvió"],
        ["Largos de Q22 y Q25", "Medidos sobre el recorrido de canalizaciones del plano 13"],
        ["Potencia de Q25 (TL2) y Q26 (central de incendio)", "Cálculo luminotécnico (método de los lúmenes) y potencia de la central"],
        ["Caudal real de los extractores (85 %)", "Punto de funcionamiento sobre la curva de catálogo (87,7 %)"],
        ["η y cos φ de los ventiladores móviles", "Corriente adoptada mayor que la de la potencia de catálogo (del lado de la seguridad)"],
        ["Coeficientes U de los digestores", "Calculados por capas según ISO 6946"],
        ["Fusible y QG2 de 80 A con cable de 25 mm²", "Acometida de 4 × 35 mm² (verifica In ≤ Iz)"],
        ["Clase de limitación de los interruptores", "Clase 3 especificada en el plano 23"],
        ["Distribuidora", "LAR (Crespo) en todos los planos y en la memoria"],
        ["Ejes de los tambores", "Verificados a fatiga; reenvío Ø60 (Rev. E)"],
    ], anchos=[6.4, 9.4], alin=["L", "L"])
    m.tabla("Datos que dependen de terceros", [
        ["Dato", "A quién consultar"],
        ["Materia y docente de la portada", "Grupo / escuela [COMPLETAR]"],
        ["Potencia contratada y conexión en paralelo de la cogeneración G1", "Cooperativa La Agrícola Regional (LAR)"],
        ["Tarifa T3 vigente (cargo fijo, potencia, energía, inyección)", "LAR / EPRE Entre Ríos"],
        ["Retiros del lote y reglamento del Parque Industrial", "Municipalidad de Crespo (Dirección del PIC)"],
        ["Rosa de vientos", "Servicio Meteorológico Nacional (estación Paraná)"],
        ["Precios de equipos y materiales", "Proveedores (cotización formal antes de comprar)"],
        ["Resistencia de los anclajes químicos (N_Rd, V_Rd)", "Ficha técnica del producto que se compre"],
        ["Límite de fatiga real del acero de los ejes", "Ensayo de Wöhler (capítulo de pruebas)"],
    ], anchos=[8.4, 7.4], alin=["L", "L"])


def anexo_archivos(m):
    m.h("Anexo E. Archivos de la entrega", 1)
    m.tabla("Contenido de la carpeta de entrega", [
        ["Archivo o carpeta", "Contenido"],
        ["index.html", "Portada de la entrega: abre todo lo de esta lista desde el navegador"],
        ["informe/Informe_Final_Secadora_Guano.docx y .pdf", "Este informe (Word definitivo)"],
        ["memoria/Memoria_de_calculo_RevD.docx y .pdf", "Memoria de cálculo de la ampliación (TG2, ventilación, biogás, fuego)"],
        ["planos/pdf/Planos_Secadora_RevD.pdf", "Juego general de 24 planos A3 (y cada lámina en PDF, DXF y PNG)"],
        ["visor.html", "Visor 3D de la planta completa (sin internet)"],
        ["secadora/Visor_Secador_SC4.html", "Visor 3D del secador: despiece, corte, montaje paso a paso"],
        ["secadora/planos/pdf/Planos_Secador_SC4.pdf", "Juego del secador (SC-01 a SC-06 + P02, P03, P09, P22)"],
        ["secadora/Manual_de_armado_SC4.pdf", "Manual de armado, instalación y uso del secador"],
        ["secadora/modelo_3d/Secador_SC4.step", "Modelo 3D del secador para SolidWorks / Fusion 360"],
        ["modelo_3d/", "STEP de la planta completa y renders"],
        ["presupuesto/Presupuesto_Secadora_Guano.xlsx", "Presupuesto, pedido a LAR, energía y evaluación económica"],
        ["video/", "Video de presentación de 3:51 (1080p a 60 cuadros por segundo y 720p)"],
        ["simulacion_termica/", "Modelo térmico del secador SC-4 (Python), resultados, láminas y simulador interactivo"],
        ["fuente/", "Programas que generan todo lo anterior (Python y Node.js) y sus datos"],
    ], anchos=[6.6, 9.2], alin=["L", "L"])


# ================================================================ documentos
def informe():
    figs = graficos()
    caps = leer_md()
    m = Memoria()
    portada(m, "Planta de secado de guano de gallina 8 t/día",
            "Informe final – entrega definitiva",
            "Secador de cinta SC-4 · Generador a cáscara de arroz · Ampliación Rev. D · Fatiga · Montaje · Presupuesto LAR",
            render("SC_general.png"))
    encabezado_pie(m, "Secadora de guano 8 t/día – Informe final del proyecto")
    emitir(m, caps[1], despues_de={"Resumen ejecutivo": entrega_final})
    for k in (2, 3, 4, 5):
        emitir(m, caps[k])
    emitir(m, caps[6], despues_de={"Verificación con el modelo térmico": modelo_termico})
    emitir(m, caps[7], despues_de={"Lista de materiales principales": modelo_3d})
    fatiga(m, figs)
    materiales(m)
    fijacion(m)
    montaje(m)
    instalacion(m)
    emitir(m, caps[8], nuevo=13, original=8, despues_de={"Registros": operacion_extra})
    emitir(m, caps[9], nuevo=14, original=9, despues_de={"Lazos de regulación": lazo_humedad})
    emitir(m, caps[10], nuevo=15, original=10)
    emitir(m, caps[11], nuevo=16, original=11, despues_de={"Distribución adoptada": ubicacion})
    ampliacion(m)
    for fn, orig, nuevo, fig in ((MD.tg2, 2, 18, 23), (MD.ventilacion, 3, 19, 24), (MD.biogas, 4, 20, 20), (MD.fuego, 5, 21, 16)):
        m.renumerar = {orig: nuevo}
        fn(m)
        m.renumerar = {}
        m.figura(plano(fig), f"Plano {fig}: {dict(titulos_planos())[f'{fig:02d}']}", 16.5)
    emitir(m, caps[12], nuevo=22, original=12)
    emitir(m, caps[13], nuevo=23, original=13)
    emitir(m, caps[14], nuevo=24, original=14)
    pruebas(m)
    presupuesto(m, figs)
    emitir(m, caps[16], nuevo=27, original=16)
    conclusiones(m)
    bibliografia(m, caps["Bibliografía"])
    anexo_planos(m)
    emitir(m, caps["Anexo B"])
    emitir(m, caps["Anexo C"])
    anexo_datos(m)
    anexo_archivos(m)
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    m.d.save(SALIDA)
    print("guardado", SALIDA, "| tablas", m.n_tabla, "| ecuaciones", m.n_ec, "| figuras", m.n_fig)
    MD.pdf_desde_html(m, SALIDA, "Secadora de guano 8 t/día – Informe final del proyecto", "Informe final – Secadora de guano")


def manual():
    """Manual de armado, instalación y uso del secador (separata del informe, mismos capítulos)."""
    caps = leer_md()
    m = Memoria()
    portada(m, "Secador de cinta SC-4", "Manual de armado, instalación y uso",
            "Materiales · Fijación al piso · Montaje paso a paso · Puesta en marcha · Operación · Mantenimiento · Pruebas",
            render("SC_despiece.png"))
    encabezado_pie(m, "Secador SC-4 – Manual de armado, instalación y uso")
    m.h("Presentación", 1)
    m.p("Este manual reúne lo necesario para fabricar, armar, instalar, poner en marcha, operar y mantener el secador "
        "de cinta SC-4 de la planta de secado de guano de 8 t/día. Acompaña a los planos SC-01 a SC-06 y al visor 3D "
        "(secadora/Visor_Secador_SC4.html), donde cada paso del montaje se puede ver en tres dimensiones. Los capítulos "
        "conservan la numeración del informe final del proyecto.")
    m.figura(render("SC_general.png"), "Secador SC-4 armado", 15)
    materiales(m)
    fijacion(m)
    montaje(m)
    instalacion(m)
    emitir(m, caps[8], nuevo=13, original=8, despues_de={"Registros": operacion_extra})
    emitir(m, caps[14], nuevo=24, original=14)
    pruebas(m)
    os.makedirs(os.path.dirname(SALIDA_MANUAL), exist_ok=True)
    m.d.save(SALIDA_MANUAL)
    print("guardado", SALIDA_MANUAL, "| figuras", m.n_fig)
    MD.pdf_desde_html(m, SALIDA_MANUAL, "Secador SC-4 – Manual de armado, instalación y uso", "Manual de armado SC-4")


if __name__ == "__main__":
    informe()
    manual()
