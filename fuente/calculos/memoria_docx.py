"""Arma la memoria de cálculo de la Rev. D en Word (memoria/Memoria_de_calculo_RevD.docx).

Usa los resultados de calculos_memoria.py (resultados.json), así los valores coinciden con los
planos. El PDF se arma desde el HTML equivalente con Chrome/Chromium (fuente/imprimir_pdf.js);
el índice del .docx se actualiza al abrirlo en Word (aceptar "actualizar campos").

    python calculos_memoria.py && python memoria_docx.py
"""
from __future__ import annotations

import html
import json
import os

from docx import Document
from docx.enum.section import WD_ORIENT  # noqa: F401
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_COLOR_INDEX
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
R = json.load(open(os.path.join(AQUI, "resultados.json"), encoding="utf-8"))
SALIDA = os.path.join(RAIZ, "memoria", "Memoria_de_calculo_RevD.docx")

ESCUELA = 'E.P.N.M. y S. N° 35 Técnica "Gral. Don José de San Martín"'
LUGAR = "Crespo, Entre Ríos"
INTEGRANTES = ["Belluzzo, B.", "Bernhardt, M.", "Goette, B.", "Hofstetter, P.", "Müller, G.", "Stegmann, F."]


def c(x, d=1):
    """Número con coma decimal y punto de miles."""
    s = f"{x:,.{d}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


# ---------------------------------------------------------------- utilidades de formato

def campo(parrafo, instruccion):
    r = parrafo.add_run()
    a = OxmlElement("w:fldChar"); a.set(qn("w:fldCharType"), "begin")
    b = OxmlElement("w:instrText"); b.set(qn("xml:space"), "preserve"); b.text = instruccion
    s = OxmlElement("w:fldChar"); s.set(qn("w:fldCharType"), "separate")
    tx = OxmlElement("w:t"); tx.text = "(actualizar campo)"
    e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), "end")
    for el in (a, b, s, tx, e):
        r._r.append(el)


def sombrear(celda, hexa):
    tc = celda._tc.get_or_add_tcPr()
    sh = OxmlElement("w:shd"); sh.set(qn("w:val"), "clear"); sh.set(qn("w:color"), "auto"); sh.set(qn("w:fill"), hexa)
    tc.append(sh)


def repetir_encabezado(fila):
    tr = fila._tr.get_or_add_trPr()
    el = OxmlElement("w:tblHeader"); el.set(qn("w:val"), "true")
    tr.append(el)


def esc(s):
    return html.escape(str(s))


class Memoria:
    """Escribe la memoria a la vez en Word (self.d) y en HTML (self.html) para el PDF."""

    def __init__(self):
        self.d = Document()
        self.html = []
        self.indice = []          # (nivel, id, texto) para el índice del PDF
        self.n_tabla = 0
        self.n_fig = 0
        self.n_ec = 0
        self.renumerar = {}       # {capítulo original: capítulo nuevo} para reutilizar capítulos en otro documento
        self._estilos()
        # que Word actualice el índice al abrir el archivo
        upd = OxmlElement("w:updateFields"); upd.set(qn("w:val"), "true")
        self.d.settings.element.append(upd)

    def _estilos(self):
        d = self.d
        sec = d.sections[0]
        sec.page_height, sec.page_width = Cm(29.7), Cm(21.0)
        for m in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
            setattr(sec, m, Cm(2.5))
        st = d.styles["Normal"]
        st.font.name = "Arial"
        st.element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")
        st.font.size = Pt(11)
        st.paragraph_format.space_after = Pt(6)
        st.paragraph_format.line_spacing = 1.15
        for i, tam in ((1, 15), (2, 12.5), (3, 11)):
            h = d.styles[f"Heading {i}"]
            h.font.name = "Arial"; h.element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")
            h.font.size = Pt(tam); h.font.bold = True; h.font.color.rgb = RGBColor(0x1F, 0x3A, 0x5F)
            h.paragraph_format.space_before = Pt(14 if i == 1 else 10); h.paragraph_format.space_after = Pt(6)
            h.paragraph_format.keep_with_next = True
        cap = d.styles["Caption"]
        cap.font.name = "Arial"; cap.font.size = Pt(9.5); cap.font.bold = False; cap.font.italic = False
        cap.font.color.rgb = RGBColor(0x33, 0x33, 0x33)

    # ---- bloques
    def h(self, texto, nivel=1, indice=True):
        import re
        mt = re.match(r"^(\d+)\.(.*)$", texto)
        if mt and int(mt.group(1)) in self.renumerar:
            texto = f"{self.renumerar[int(mt.group(1))]}.{mt.group(2)}"
        hid = f"h{len(self.indice) + 1}"
        if indice:
            self.indice.append((nivel, hid, texto))
        self.html.append(f'<h{nivel} id="{hid}">{esc(texto)}</h{nivel}>')
        return self.d.add_heading(texto, level=nivel)

    def p(self, texto="", negrita=False, cursiva=False, centrado=False, tam=None, resaltar=False):
        par = self.d.add_paragraph()
        if texto:
            r = par.add_run(texto); r.bold = negrita; r.italic = cursiva
            if tam:
                r.font.size = Pt(tam)
            if resaltar:
                r.font.highlight_color = WD_COLOR_INDEX.YELLOW
        if centrado:
            par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        else:
            par.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        estilo = []
        if tam:
            estilo.append(f"font-size:{tam}pt")
        if centrado:
            estilo.append("text-align:center")
        cont = esc(texto) if texto else "&nbsp;"
        if negrita:
            cont = f"<b>{cont}</b>"
        if cursiva:
            cont = f"<i>{cont}</i>"
        if resaltar:
            cont = f"<mark>{cont}</mark>"
        self.html.append(f'<p style="{";".join(estilo)}">{cont}</p>')
        return par

    def lista(self, items):
        for it in items:
            self.d.add_paragraph(it, style="List Bullet")
        self.html.append("<ul>" + "".join(f"<li>{esc(i)}</li>" for i in items) + "</ul>")

    def ec(self, formula, simbolos=None):
        """Ecuación numerada centrada y, debajo, el significado de cada símbolo."""
        self.n_ec += 1
        t = self.d.add_table(rows=1, cols=2)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        a, b = t.rows[0].cells
        a.width, b.width = Cm(14), Cm(2)
        pa = a.paragraphs[0]; pa.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = pa.add_run(formula); r.font.name = "Cambria Math"; r.font.size = Pt(11.5)
        pb = b.paragraphs[0]; pb.alignment = WD_ALIGN_PARAGRAPH.RIGHT; pb.add_run(f"({self.n_ec})")
        if simbolos:
            par = self.d.add_paragraph()
            par.paragraph_format.left_indent = Cm(1)
            r = par.add_run("donde " + "; ".join(simbolos) + ".")
            r.font.size = Pt(9.5)
        f_html = esc(formula).replace("        ", "&emsp;&emsp;&emsp;")
        self.html.append(f'<div class="ec"><span class="f">{f_html}</span><span class="n">({self.n_ec})</span></div>')
        if simbolos:
            self.html.append(f'<p class="simb">donde {esc("; ".join(simbolos))}.</p>')
        return self.n_ec

    def calculo(self, reemplazo, resultado):
        par = self.d.add_paragraph()
        par.paragraph_format.left_indent = Cm(1)
        par.add_run(reemplazo + "  →  ")
        r = par.add_run(resultado); r.bold = True
        self.html.append(f'<p class="calc">{esc(reemplazo)} &nbsp;→&nbsp; <b>{esc(resultado)}</b></p>')

    def tabla(self, titulo, filas, anchos=None, alin=None, total=False, resaltar=None):
        """Tabla numerada con título arriba; primera fila = encabezado."""
        self.n_tabla += 1
        cap = self.d.add_paragraph(f"Tabla {self.n_tabla} – {titulo}", style="Caption")
        cap.paragraph_format.keep_with_next = True
        t = self.d.add_table(rows=len(filas), cols=len(filas[0]))
        t.style = "Table Grid"
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        resaltar = set(resaltar or [])
        for i, fila in enumerate(filas):
            for j, val in enumerate(fila):
                cel = t.cell(i, j)
                cel.text = ""
                par = cel.paragraphs[0]
                par.paragraph_format.space_after = Pt(0)
                r = par.add_run(str(val)); r.font.size = Pt(9)
                if i == 0 or (total and i == len(filas) - 1):
                    r.bold = True
                if alin and i > 0:
                    par.alignment = {"L": WD_ALIGN_PARAGRAPH.LEFT, "C": WD_ALIGN_PARAGRAPH.CENTER,
                                     "R": WD_ALIGN_PARAGRAPH.RIGHT}[alin[j]]
                if i == 0:
                    sombrear(cel, "DCE3EA")
                elif i in resaltar:
                    sombrear(cel, "E2F0E4")
                if anchos:
                    cel.width = Cm(anchos[j])
        repetir_encabezado(t.rows[0])
        self.d.add_paragraph().paragraph_format.space_after = Pt(2)
        al = {"L": "left", "C": "center", "R": "right"}
        filas_html = []
        for i, fila in enumerate(filas):
            celdas = []
            for j, val in enumerate(fila):
                tag = "th" if i == 0 else "td"
                cls = []
                if i > 0 and alin:
                    cls.append(al[alin[j]])
                if total and i == len(filas) - 1:
                    cls.append("tot")
                if i in resaltar:
                    cls.append("res")
                ancho = f' style="width:{anchos[j]}cm"' if anchos and i == 0 else ""
                celdas.append(f'<{tag} class="{" ".join(cls)}"{ancho}>{esc(val)}</{tag}>')
            filas_html.append("<tr>" + "".join(celdas) + "</tr>")
        self.html.append(f'<p class="cap">Tabla {self.n_tabla} – {esc(titulo)}</p>'
                         f'<table><thead>{filas_html[0]}</thead><tbody>{"".join(filas_html[1:])}</tbody></table>')
        return self.n_tabla

    def figura(self, ruta, epigrafe, ancho_cm=16):
        self.n_fig += 1
        par = self.d.add_paragraph(); par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        par.add_run().add_picture(ruta, width=Cm(ancho_cm))
        par.paragraph_format.keep_with_next = True
        self.d.add_paragraph(f"Figura {self.n_fig} – {epigrafe}", style="Caption").alignment = WD_ALIGN_PARAGRAPH.CENTER
        import pathlib
        uri = pathlib.Path(ruta).resolve().as_uri()
        self.html.append(f'<figure><img src="{uri}" style="width:{ancho_cm}cm"><figcaption>Figura {self.n_fig} – '
                         f'{esc(epigrafe)}</figcaption></figure>')
        return self.n_fig

    def salto(self):
        self.d.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
        self.html.append('<div class="salto"></div>')

    def recuadro(self, titulo, texto):
        """Párrafo destacado en un recuadro sombreado (recomendaciones, advertencias)."""
        t = self.d.add_table(rows=1, cols=1)
        t.style = "Table Grid"
        cel = t.cell(0, 0)
        sombrear(cel, "EEF3F8")
        par = cel.paragraphs[0]
        par.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        r = par.add_run(titulo + ". "); r.bold = True
        par.add_run(texto)
        self.d.add_paragraph().paragraph_format.space_after = Pt(2)
        self.html.append(f'<div class="recuadro"><b>{esc(titulo)}.</b> {esc(texto)}</div>')


# ---------------------------------------------------------------- contenido

def portada(m):
    d = m.d
    for _ in range(2):
        m.p()
    m.p(ESCUELA, negrita=True, centrado=True, tam=14)
    m.p(LUGAR, centrado=True)
    m.p("Especialidad Electromecánica · 7.° año", centrado=True)
    m.p("Materia: [COMPLETAR]", centrado=True, resaltar=True)
    m.p("Docente: [COMPLETAR]", centrado=True, resaltar=True)
    for _ in range(3):
        m.p()
    m.p("PROYECTO FINAL", negrita=True, centrado=True, tam=13)
    m.p("Secadora de guano de gallina 8 t/día", negrita=True, centrado=True, tam=22)
    m.p("Memoria de cálculo – Revisión D", negrita=True, centrado=True, tam=16)
    m.p("Tablero TG2 y conductores · Ventilación de la nave · Biogás · Carga de fuego", centrado=True, tam=11)
    for _ in range(4):
        m.p()
    m.p("Integrantes", negrita=True, centrado=True)
    for n in INTEGRANTES:
        m.p(n, centrado=True)
    for _ in range(2):
        m.p()
    m.p(f"{LUGAR} – octubre de 2026", centrado=True)
    m.salto()
    m.h("Índice", 1, indice=False)
    campo(d.add_paragraph(), 'TOC \\o "1-3" \\h \\z \\u')
    m.html.append('<div id="indice">__INDICE__</div>')
    m.salto()


def encabezado_pie(m):
    sec = m.d.sections[0]
    sec.different_first_page_header_footer = True
    hp = sec.header.paragraphs[0]
    hp.text = "Secadora de guano 8 t/día – Memoria de cálculo Rev. D"
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    hp.runs[0].font.size = Pt(8.5); hp.runs[0].font.color.rgb = RGBColor(0x66, 0x66, 0x66)
    fp = sec.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fp.add_run("Página ").font.size = Pt(9)
    campo(fp, "PAGE")


def introduccion(m):
    m.h("1. Introducción", 1)
    m.h("1.1. Objeto y alcance", 2)
    m.p("Esta memoria reúne los cálculos de la Revisión D del proyecto de la secadora de guano de gallina de "
        "8 t/día: el tablero TG2 que alimenta las cargas nuevas (con los extractores de la nave agregados en "
        "esta revisión), la ventilación general de la nave, el sistema de biogás y el estudio de carga de "
        "fuego. Los cálculos del secador, del generador de aire caliente, de la cinta de alimentación y del "
        "tablero general TGF corresponden a la Revisión C y figuran en los planos 02 a 12, que no cambian.")
    m.p("Cada cálculo sigue el mismo orden: datos con su fuente, fórmula, reemplazo numérico, resultado, valor "
        "adoptado y verificación. Las cuentas se hicieron con el programa fuente/calculos/calculos_memoria.py; "
        "los resultados que genera (resultados.json) son los mismos que se usan en los planos, de modo que "
        "planos y memoria coinciden.")
    m.h("1.2. Documentos relacionados", 2)
    m.tabla("Planos de la Revisión D citados en esta memoria", [
        ["Plano", "Título", "Revisión"],
        ["05", "Esquema unifilar del tablero general (TGF)", "D"],
        ["13", "Implantación general ampliada (Sector Este)", "D"],
        ["15", "Protección contra incendios y medios de escape", "D"],
        ["16", "Estudio de carga de fuego (Dec. 351/79)", "D"],
        ["17", "Nave: seguridad, accesos y mantenimiento", "E"],
        ["20", "Sistema de biogás: planta, corte y balance", "D"],
        ["23", "Esquema unifilar TG2 (consumos Rev. D)", "E"],
        ["24", "Ventilación general de la nave: extractores y ventiladores", "E"],
    ], anchos=[1.6, 11.5, 2.0], alin=["C", "L", "C"])
    m.h("1.3. Criterios generales", 2)
    m.lista([
        "Unidades del Sistema Internacional; coma decimal y punto de miles.",
        "Red de 3 × 380/220 V, 50 Hz, esquema de conexión a tierra TT (plano 05).",
        "Instalación eléctrica según AEA 90364-7-771 (reglamentación de la Asociación Electrotécnica Argentina); "
        "corrientes admisibles de los cables según IEC 60364-5-52, que es la base de las tablas de la AEA.",
        "Higiene y seguridad según la Ley 19.587 y su Decreto 351/79 (capítulo 18 y Anexo VII para incendio).",
        "Coordenadas en metros con origen en el vértice Sudoeste de la nave, eje x al Este e y al Norte.",
    ])


def tg2(m):
    t = R["tg2"]
    m.h("2. Tablero TG2 y conductores", 1)
    m.p("Todas las cargas nuevas de la Revisión D se alimentan desde un tablero nuevo, el TG2, ubicado en la "
        "sala de control (22) y conectado al pilar de acometida por una salida propia. El TGF y sus 15 circuitos "
        "no cambian. En esta revisión se suman al TG2 los dos extractores de la nave y los dos ventiladores "
        "móviles del ítem E10 (plano 24), que en la revisión anterior no figuraban en el unifilar.")
    m.h("2.1. Cargas del TG2", 2)
    filas = [["Tag", "Accionamiento", "kW", "In (A)", "Arranque", "Tablero"]]
    res = []
    for i, x in enumerate(t["motores"], start=1):
        filas.append([x["tag"], x["nom"], c(x["kW"], 2), c(x["In"], 1), x["arranque"], x["tablero"]])
        if x["tag"] in ("M36", "M37", "M38", "M39"):
            res.append(i)
    filas.append(["", "Total instalado (incluye bombas de incendio)", c(t["total_kW"], 2), "", "", ""])
    m.tabla("Motores y cargas del TG2 (sombreadas: agregadas en esta revisión)", filas,
            anchos=[1.2, 8.3, 1.4, 1.4, 1.7, 2.0], alin=["L", "L", "R", "R", "C", "L"], total=True, resaltar=res)
    m.p("Los extractores Campagnoni AirTEC 1215 tienen motor trifásico de 1,5 HP; se adopta el motor IEC "
        "normalizado inmediato, de 1,1 kW, con η = 84,1 % y cos φ = 0,77 (mismo motor que el M10 del plano 05). "
        "Los ventiladores móviles de 50\" son de 1 HP, monofásicos de 220 V con capacitor permanente; se adopta "
        "η = 0,72 y cos φ = 0,92. Con la potencia absorbida que indica el catálogo (735 W) la corriente resulta "
        "menor que la calculada, de modo que el valor adoptado queda del lado de la seguridad.")
    m.ec("I = P / (√3 · U · η · cos φ)        I = P / (U_f · η · cos φ)",
         ["I: corriente nominal (A)", "P: potencia útil del motor (W)", "U = 380 V: tensión de línea",
          "U_f = 220 V: tensión de fase", "η: rendimiento", "cos φ: factor de potencia"])
    m.calculo("I_EX = 1.100 / (√3 · 380 · 0,841 · 0,77)", f"{c(t['I_EX'], 2)} A")
    m.calculo("I_VM = 750 / (220 · 0,72 · 0,92)", f"{c(t['I_VM'], 2)} A")

    m.h("2.2. Potencia instalada y demanda", 2)
    m.p("Para la demanda se mantiene el criterio del plano 23: factor de simultaneidad 0,55 sobre la potencia "
        "instalada sin las bombas de incendio, que no funcionan junto con el proceso.")
    m.ec("P_d = f_s · Σ P_i", ["P_d: potencia de demanda (kW)", "f_s: factor de simultaneidad", "Σ P_i: potencia instalada sin incendio (kW)"])
    m.calculo(f"P_d = {c(t['fs'], 2)} · {c(t['base_fs_kW'], 2)} kW", f"{c(t['demanda_tg2_kW'])} kW "
              f"(antes de esta revisión: {c(t['demanda_tg2_anterior_kW'])} kW)")
    m.calculo(f"I_d = {c(t['demanda_tg2_kW'] * 1000, 0)} / (√3 · 380 · 0,85)", f"{c(t['I_demanda_A'])} A")
    m.p(f"Si arrancaran todas las cargas juntas (sin simultaneidad), la corriente sería {c(t['I_instalada_A'])} A.")

    m.h("2.3. Acometida del TG2", 2)
    ac = t["acometida"]
    m.p(f"El TG2 se alimenta desde el pilar con un cable de cobre IRAM 2178 de 4 × {ac['S']} mm², "
        f"{ac['L']} m enterrado en caño (método D1), protegido por fusibles NH00 de {ac['fusible']} A en el pilar y "
        f"por el interruptor general QG2 de {ac['In']} A. La coordinación entre carga, protección y cable exige:")
    m.ec("I_b ≤ I_n ≤ I_z", ["I_b: corriente de proyecto", "I_n: corriente asignada (o regulada) de la protección",
                              "I_z: corriente admisible del cable, ya corregida"])
    m.ec("I_z = I_z0 · k_t · k_a", ["I_z0: corriente admisible de tabla", "k_t: factor por temperatura",
                                     "k_a: factor por agrupamiento"])
    m.calculo("I_z = 98 A · 0,95 (suelo a 25 °C) · 1,0", f"{c(ac['Iz'])} A")
    m.p(f"Con I_b = {c(t['I_demanda_A'])} A ≤ I_n = {ac['In']} A ≤ I_z = {c(ac['Iz'])} A la coordinación verifica, "
        f"tanto para el QG2 como para los fusibles NH00 de {ac['fusible']} A del pilar. Además se cumple la "
        f"segunda condición de sobrecarga: I_2 = 1,6 · {ac['fusible']} = {c(ac['I2_fusible'], 0)} A ≤ 1,45 · I_z = "
        f"{c(ac['lim_I2'], 0)} A. En la Rev. D la acometida era de 4 × 25 mm² (I_z = 77,9 A), que no verificaba con "
        f"80 A; se pasó a 4 × 35 mm² y el térmico del QG2 se regula en I_r = {ac['Ir']} A para mantener la "
        f"selectividad con los fusibles del pilar (plano 23 Rev. F).")
    m.p(f"Caída de tensión en la acometida con la corriente de demanda: ΔU = {c(ac['dU_pct'], 2)} % (límite 3 %).")

    m.h("2.4. Circuitos de salida", 2)
    m.p("Para cada salida se calculó la corriente de proyecto, se eligió la protección (I_n ≥ 1,15 · I_b, "
        "valor normalizado inmediato superior) y se verificó el cable por corriente admisible y por caída de "
        "tensión. Los cables van en bandeja perforada dentro de la nave (método E, aire a 40 °C: k_t = 0,87; "
        "bandeja compartida: k_a = 0,80) o enterrados hacia el exterior (método D1, k_t = 0,95).")
    m.ec("ΔU = √3 · I · L · (r · cos φ + x · sen φ)        r = ρ_70 / S",
         ["ΔU: caída de tensión (V)", "L: largo del circuito (m)", "S: sección (mm²)",
          "ρ_70 = 0,0206 Ω·mm²/m: resistividad del cobre a 70 °C", "x = 0,08 mΩ/m: reactancia del cable",
          "cos φ = 0,85"])
    filas = [["Circ.", "Destino", "kW", "Ib (A)", "In (A)", "Cable", "L (m)", "Iz (A)", "ΔU (%)", "Verif."]]
    for x in t["circuitos"]:
        filas.append([x["Q"], x["destino"], c(x["kW"], 2), c(x["Ib"]), x["In"],
                      f"4 × {c(x['S'], 1).replace(',0', '')} mm² ({x['metodo']})", x["L"], c(x["Iz"]),
                      c(x["dU_pct"], 2), "Sí" if x["verifica"] else "No"])
    m.tabla("Verificación de los circuitos del TG2", filas,
            anchos=[1.1, 4.6, 1.2, 1.1, 1.0, 2.6, 1.0, 1.1, 1.1, 1.0], alin=["L", "L", "R", "R", "R", "L", "R", "R", "R", "C"],
            resaltar=[len(filas) - 1])
    q23 = next(x for x in t["circuitos"] if x["Q"] == "Q23")
    q27 = next(x for x in t["circuitos"] if x["Q"] == "Q27")
    m.p("Ejemplo 1 – Q27, TS-VEN (circuito nuevo).", negrita=True)
    m.p("Los extractores son trifásicos y los ventiladores móviles monofásicos, uno conectado entre L1 y N y "
        "el otro entre L2 y N, así la fase más cargada lleva los dos extractores y un ventilador:")
    m.calculo(f"I_b = 2 · {c(t['I_EX'], 2)} + {c(t['I_VM'], 2)}", f"{c(q27['Ib'])} A")
    m.calculo(f"I_n ≥ 1,15 · {c(q27['Ib'])} = {c(1.15 * q27['Ib'])} A", f"interruptor 4P {q27['In']} A curva C")
    m.calculo("I_z = 25 A · 0,87 · 0,80 (4 × 2,5 mm², método E)", f"{c(q27['Iz'])} A ≥ {q27['In']} A: verifica")
    m.calculo(f"ΔU = √3 · {c(q27['Ib'])} · {q27['L']} · (0,0206/2,5 · 0,85 + 0,00008 · 0,53)", f"{c(q27['dU_pct'], 2)} %")
    m.p("Ejemplo 2 – Q23, TS-BIO con la cogeneración.", negrita=True)
    m.p(f"{q23['nota'].capitalize()}. Se toma I_b = {c(q23['Ib'])} A y se elige un interruptor de "
        f"{q23['In']} A, que verifica con el cable de 4 × 16 mm² enterrado (I_z = {c(q23['Iz'])} A). "
        f"La caída de tensión en los 105 m es {c(q23['dU_pct'], 2)} %, dentro del 3 % para alimentadores.")
    il = R["iluminacion"]
    q25 = next(x for x in t["circuitos"] if x["Q"] == "Q25")
    m.p(f"Los circuitos Q25 (TL2, iluminación del Sector Este) y Q26 (central de incendio) se verifican con la "
        f"potencia que resulta del cálculo luminotécnico que sigue: {c(il['P_Q25_kW'], 2)} kW y "
        f"{c(il['P_Q26_kW'], 2)} kW. Los largos de Q22 ({next(x['L'] for x in t['circuitos'] if x['Q'] == 'Q22')} m) "
        f"y Q25 ({q25['L']} m) se midieron sobre el recorrido de las canalizaciones del plano 13.")
    m.h("2.4.1. Iluminación del depósito y del Sector Este", 3)
    m.p("Se aplica el método de los lúmenes (IRAM-AADL J 20-06) al depósito de expedición E7, de "
        f"{c(il['a'], 0)} × {c(il['b'], 0)} m, con campanas LED industriales de {c(il['p_lum'], 0)} W "
        f"({c(il['phi_lum'], 0)} lm) montadas a 5,6 m y plano de trabajo a 0,85 m.")
    m.ec("k = a · b / [h · (a + b)]        Φ_t = E · a · b / (CU · f_m)        n = Φ_t / Φ_lum", [
        "k: índice del local", "h: altura de montaje sobre el plano de trabajo (m)",
        "E: iluminancia media requerida (lx)", "CU: coeficiente de utilización", "f_m: factor de mantenimiento",
        "Φ_t: flujo total necesario (lm)", "Φ_lum: flujo de una luminaria (lm)"])
    m.calculo(f"k = {c(il['a'], 0)} · {c(il['b'], 0)} / [{c(il['h'], 2)} · ({c(il['a'], 0)} + {c(il['b'], 0)})]",
              f"{c(il['k'], 2)}")
    m.calculo(f"Φ_t = {c(il['E'], 0)} · {c(il['a'] * il['b'], 0)} / ({c(il['CU'], 2)} · {c(il['fm'], 2)})",
              f"{c(il['phi_t'], 0)} lm")
    m.calculo(f"n = {c(il['phi_t'], 0)} / {c(il['phi_lum'], 0)} = {c(il['n_calc'], 2)}",
              f"{il['n']} campanas (2 filas de 3) → E = {il['E_real']} lx")
    m.p(f"La separación entre luminarias (6,7 × 6 m) no supera 1,5 · h = {c(il['sep_max'], 1)} m, con lo que la "
        "iluminación es uniforme. La potencia del TL2 suma las cargas de la tabla siguiente.")
    filas = [["Carga del TL2 (Q25)", "Cant.", "W c/u", "kW"]]
    for nombre, cant, w in il["cargas"]:
        filas.append([nombre, cant, c(w, 0), c(cant * w / 1000, 2)])
    filas.append(["Total Q25", "", "", c(il["P_Q25_kW"], 2)])
    m.tabla("Potencia de iluminación del Sector Este", filas, anchos=[10, 1.5, 1.6, 1.6], alin=["L", "C", "R", "R"],
            total=True)

    m.h("2.5. Cortocircuito", 2)
    m.p("Con la corriente de cortocircuito presunta en el pilar (6 kA, plano 05) se calcula la impedancia de la "
        "red y se suma la de la acometida del TG2 (conductor a 20 °C, que da la corriente máxima):")
    m.ec("Z_red = U / (√3 · I_cc)        I_cc,TG2 = U / (√3 · |Z_red + Z_acometida|)", [
        "Z_red: impedancia de la red vista desde el pilar (Ω)", "Z_acometida: impedancia del cable al TG2 (Ω)"])
    m.calculo(f"Z_red = 380 / (√3 · 6.000) = 0,0366 Ω;  R_ac = 0,0172 · {ac['L']} / {ac['S']} = "
              f"{c(0.0172 * ac['L'] / ac['S'], 4)} Ω",
              f"I_cc,TG2 = {c(t['Icc_TG2_kA'], 2)} kA")
    m.p(f"El QG2 tiene I_cu = 10 kA ≥ {c(t['Icc_TG2_kA'], 2)} kA: verifica. Sección mínima por esfuerzo "
        f"térmico, con disparo magnético en 0,1 s y k = 115 (cobre en PVC):")
    m.ec("S ≥ I_cc · √t / k", ["S: sección (mm²)", "t: tiempo de disparo (s)", "k: constante del conductor"])
    m.calculo(f"S ≥ {c(t['Icc_TG2_kA'] * 1000, 0)} · √0,1 / 115", f"{c(t['S_min_cc_mm2'])} mm²")
    m.p("Las salidas de 2,5 y 4 mm² quedan por debajo de ese valor, por lo que sus interruptores deben limitar la "
        "energía (I²t) que dejan pasar: se especifican interruptores de clase de limitación 3 (IEC 60898-1), cuyo "
        "I²t máximo con 4,5 kA es del orden de 30.000 A²s, por debajo del k²·S² = 82.656 A²s del cable de 2,5 mm² "
        "(verificar con la curva I²t del modelo elegido).")

    m.h("2.6. Balance y potencia a contratar", 2)
    b = t["balance"]
    m.tabla("Balance de potencia de la planta", [
        ["Concepto", "kW"],
        ["Demanda del TGF existente (Rev. C, fs 0,8)", b["TGF_kW"]],
        [f"Demanda nueva del TG2 (fs {c(t['fs'], 2)} sobre {c(t['base_fs_kW'])} kW)", c(b["TG2_kW"])],
        ["Bomba de incendio (no simultánea, se suma igual por seguridad)", "7,5"],
        ["Total con la cogeneración parada", c(b["sin_G1_kW"])],
        ["Aporte de la cogeneración G1 (12,7 h/día)", "−25"],
        ["Total con la cogeneración en marcha", c(b["con_G1_kW"])],
        ["Potencia a contratar adoptada", str(b["adoptada_kW"])],
    ], anchos=[12, 3], alin=["L", "R"], total=True)
    m.p(f"Con la cogeneración parada (mantenimiento o falta de gas) la planta pide {c(b['sin_G1_kW'])} kW; los "
        f"{b['adoptada_kW']} kW del plano 23 siguen alcanzando, con un margen de {c(b['margen_sin_G1_pct'])} %, ya "
        f"con la iluminación del Sector Este y la central de incendio incluidas ({c(t['P_ilum_kW'], 2)} kW). La "
        "distribuidora LAR debe confirmar la potencia y la conexión en paralelo de la cogeneración G1.")


def ventilacion(m):
    v = R["ventilacion"]
    m.h("3. Ventilación general de la nave", 1)
    m.p("La nave de proceso es de 33 × 18 m con 7,0 m de altura al alero y techo a dos aguas. Además de la "
        "campana de la recepción (E3), que capta el olor en el origen, se agregan dos extractores en el muro "
        "Este para sacar el calor que entrega el secador y el amoníaco y el polvo del ambiente (plano 24).")
    m.h("3.1. Volumen y caudal por renovaciones", 2)
    m.ec("V = L · A · H + ½ · A · f · L        Q = V · N", [
        "V: volumen de la nave (m³)", "L = 33 m, A = 18 m: largo y ancho", "H = 7,0 m: altura al alero",
        "f = 1,35 m: flecha del techo", "Q: caudal (m³/h)", "N: renovaciones por hora"])
    m.calculo(f"V = 33 · 18 · 7,0 + ½ · 18 · 1,35 · 33 = {c(v['V_nave'], 0)} + {c(v['V_techo'], 0)}", f"{c(v['V'], 0)} m³")
    m.calculo(f"Invierno (N = {v['n_inv']}): Q = {c(v['V'], 0)} · {v['n_inv']}", f"{c(v['Q_inv'], 0)} m³/h")
    m.calculo(f"Verano (N = {v['n_ver']}, calor, amoníaco y polvo): Q = {c(v['V'], 0)} · {v['n_ver']}", f"{c(v['Q_ver'], 0)} m³/h")
    m.h("3.2. Comprobación por balance térmico de verano", 2)
    filas = [["Aporte de calor", "kW"]] + [[k, c(x)] for k, x in v["cargas"].items()] + [["Total H", c(v["H_kW"])]]
    m.tabla("Cargas térmicas de la nave en verano (plano 24)", filas, anchos=[12, 3], alin=["L", "R"], total=True)
    m.p(f"Verificación del aporte del producto que se enfría: 329 kg/h · 1,5 kJ/kg·K · (60 − 35) K / 3.600 = "
        f"{c(v['q_prod_kW'])} kW, igual al de la tabla.")
    m.ec("Q = H / (ρ · c_p · ΔT)", ["H: calor a evacuar (kW)", "ρ = 1,15 kg/m³: densidad del aire a 35 °C",
                                     "c_p = 1,005 kJ/kg·K", "ΔT = 3 K: salto admitido entre interior y exterior"])
    m.calculo(f"Q = {c(v['H_kW'])} / (1,15 · 1,005 · 3) · 3.600", f"{c(v['Q_termico'], 0)} m³/h")
    m.p(f"El caudal por renovaciones ({c(v['Q_ver'], 0)} m³/h) es mayor que el térmico ({c(v['Q_termico'], 0)} m³/h): "
        f"manda el primero. Caudal de diseño adoptado: {c(v['Q_diseno'], 0)} m³/h.")
    m.h("3.3. Selección de los extractores", 2)
    m.p(f"Se eligieron extractores Campagnoni AirTEC 1215 (Ø 1.215 mm, 6 palas, 1,5 HP trifásico), fabricados en "
        f"el Parque Industrial de Crespo, con {c(v['Q_ex'], 0)} m³/h cada uno a presión libre según el catálogo "
        f"del fabricante.")
    m.calculo(f"n = {c(v['Q_diseno'], 0)} / {c(v['Q_ex'], 0)}", f"{v['n_ex']} extractores")
    pf = v["punto"]
    m.p(f"Los extractores axiales de pared trabajan con muy poca presión: la curva del catálogo cae a cero con "
        f"≈ {c(v['p_max'], 0)} Pa. El punto de funcionamiento se obtiene cruzando esa curva con la resistencia de las "
        f"tomas de aire (rejas y persianas fijas, K ≈ 2,5) y de la nave:")
    m.ec("p = p_max · [1 − (Q/Q_0)²]        Δp = K · ρ · v² / 2 + 1 Pa", [
        "p: presión del extractor (Pa)", "Q_0: caudal de catálogo a presión libre", "Δp: pérdida en tomas y nave (Pa)",
        "v: velocidad del aire en las tomas (m/s)"])
    m.calculo(f"iterando: Δp = {c(pf['dp_Pa'], 1)} Pa, v = {c(pf['v_toma'], 2)} m/s",
              f"Q = {c(pf['frac_calc'] * 100, 1)} % del caudal de catálogo")
    m.calculo(f"Caudal real adoptado (85 %, del lado de la seguridad): {v['n_ex']} · {c(v['Q_ex'], 0)} · 0,85",
              f"{c(v['Q_real'], 0)} m³/h = {c(v['ren_real'])} renovaciones por hora")
    m.p(f"En invierno o con un extractor fuera de servicio queda uno solo: {c(v['Q_un_extractor'], 0)} m³/h "
        f"({c(v['ren_un_extractor'])} renovaciones por hora), por encima de las 6 de invierno.")
    m.ec("A = Q / (3.600 · v)", ["A: sección libre de las tomas de aire (m²)", "v = 2 m/s: velocidad en las tomas"])
    m.calculo(f"A = {c(v['Q_real'], 0)} / (3.600 · 2)", f"{c(v['A_tomas'])} m² (se adoptan ≈ 15 m²: portón P1 y aberturas del Oeste)")
    m.p(f"Potencia eléctrica: 2 × 1,1 kW = {c(v['P_ex_kW'])} kW, alimentada desde el TS-VEN (circuito Q27 del TG2).")
    m.h("3.4. Biofiltro de la recepción (E3)", 2)
    bf = v["biofiltro"]
    m.ec("q = Q / A        t = h / q", ["q: carga superficial (m³/m²·h)", "A: superficie del lecho (m²)",
                                         "h: altura del lecho (m)", "t: tiempo de contacto (s)"])
    m.calculo(f"q = {c(bf['Q'], 0)} / (8,5 · 4,5 = {c(bf['A'])})", f"{c(bf['carga'], 0)} m³/m²·h")
    m.calculo(f"t = {c(bf['h'])} m / ({c(bf['carga'], 0)} / 3.600) m/s", f"{c(bf['t_contacto'])} s")
    m.p("El tiempo de contacto queda dentro del rango habitual de los biofiltros para olores y amoníaco "
        "(15 a 60 s de tiempo de residencia en el lecho vacío): verifica.")


def biogas(m):
    b = R["biogas"]
    m.h("4. Sistema de biogás", 1)
    m.p("El guano que la secadora no procesa en fines de semana y feriados (≈ 920 t/año) se digiere en dos "
        "biodigestores mesofílicos. El biogás alimenta una cogeneración de 25 kWe y el quemador piloto del hogar "
        "(plano 20).")
    m.h("4.1. Alimentación", 2)
    m.ec("ST = m · (1 − w)        SV = ST · f_SV        Q_a = ST / (c_ST · ρ)", [
        "m: guano húmedo (kg/día)", "w = 0,72: humedad (plano 06)", "f_SV = 0,746: fracción volátil de los sólidos",
        "c_ST = 0,08: concentración de sólidos de la mezcla", "ρ ≈ 1.000 kg/m³", "Q_a: caudal de alimentación (m³/día)"])
    m.calculo(f"m = 920 t/año / 365 = {c(b['guano_t_dia'], 2)} t/día;  ST = 2.520 · 0,28", f"{c(b['ST_kg'], 0)} kg/día")
    m.calculo(f"SV = {c(b['ST_kg'], 0)} · 0,746", f"{c(b['SV_kg'], 0)} kg SV/día")
    m.calculo(f"Q_a = {c(b['ST_kg'], 0)} / (0,08 · 1.000)", f"{c(b['Q_alim_calc'], 2)} m³/día")
    m.p(f"El plano 20 adopta {c(b['Q_alim'], 2)} m³/día porque a la mezcla entran además los lixiviados y el agua "
        "de lavado (≈ 0,6 m³/día) con sus propios sólidos; se toma ese valor, que queda del lado de la seguridad "
        "para el volumen.")
    m.h("4.2. Volumen de los digestores y carga orgánica", 2)
    m.ec("V = Q_a · TRH        B_v = SV / V", ["V: volumen útil (m³)", "TRH = 30 días: tiempo de retención",
                                                "B_v: carga orgánica volumétrica (kg SV/m³·día)"])
    m.calculo(f"V = {c(b['Q_alim'], 2)} · {b['TRH']}", f"{c(b['V_util'], 0)} m³ → 2 digestores de {c(b['V_dig_c_u'], 0)} m³")
    m.calculo(f"Altura útil en Ø 6,5 m: {c(b['V_dig_c_u'], 0)} / {c(b['A_dig'])} m²", f"{c(b['h_util'], 2)} m (tanque de 5,0 m)")
    m.calculo(f"B_v = {c(b['SV_kg'], 0)} / {c(b['V_util'], 0)}", f"{c(b['carga'], 2)} kg SV/m³·día")
    m.p("La carga queda dentro del rango recomendado para digestión mesofílica de estiércol de aves (1,5 a 3 kg "
        "SV/m³·día) y con margen frente a la inhibición por amoníaco, que se controla por dilución y recirculación.")
    m.h("4.3. Producción de biogás y energía", 2)
    m.ec("V_b = SV · Y        E = V_b · PCI", ["V_b: biogás (m³/día)", "Y = 0,35 m³/kg SV: rendimiento adoptado",
                                                 "PCI = 20,8 MJ/m³ (58 % de metano)"])
    m.calculo(f"V_b = {c(b['SV_kg'], 0)} · 0,35", f"{c(b['biogas'], 0)} m³/día")
    m.calculo(f"E = {c(b['biogas'], 0)} · 20,8", f"{c(b['E_MJ'], 0)} MJ/día")
    m.ec("E_el = (V_b − V_p) · PCI / 3,6 · η_el        h = E_el / P_CHP", [
        "V_p = 12,1 m³/día: piloto del hogar", "η_el = 0,32: rendimiento eléctrico del motogenerador",
        "P_CHP = 25 kWe", "h: horas de marcha por día"])
    m.calculo(f"E_el = ({c(b['biogas'], 0)} − 12,1) · 20,8 / 3,6 · 0,32 = {c(b['E_chp_kWh'], 0)} · 0,32", f"{c(b['E_el'], 0)} kWh/día")
    m.calculo(f"h = {c(b['E_el'], 0)} / 25", f"{c(b['horas'])} h/día")
    m.calculo(f"Calor útil (η_th = 0,48): {c(b['E_chp_kWh'], 0)} · 0,48", f"{c(b['calor'], 0)} kWh/día")
    m.h("4.4. Calor que piden los digestores", 2)
    m.p("Se calcula el calor para llevar la alimentación hasta 38 °C más las pérdidas por la envolvente. Los "
        "coeficientes de transmisión se calcularon por capas según ISO 6946 (U = 1 / ΣR):")
    filas = [["Elemento", "Capas (resistencias en m²·K/W)", "U (W/m²·K)"]]
    for clave, nombre in (("paredes", "Paredes"), ("techo", "Techo (doble membrana)"), ("piso", "Piso")):
        capas = "; ".join(f"{n} {c(r, 3)}" for n, r in b["capas"][clave])
        filas.append([nombre, capas, c(b["U"][clave], 2)])
    m.tabla("Coeficientes de transmisión de los digestores (ISO 6946)", filas, anchos=[2.6, 11, 1.8], alin=["L", "L", "R"])
    m.p("La alimentación es una mezcla del guano y los líquidos fríos con 4,6 m³/día de líquido recirculado del "
        "tanque T3 a ≈ 30 °C, por lo que entra al digestor más tibia que el guano solo.")
    m.tabla("Calor de calefacción de los digestores", [
        ["Caso", "Mezcla (°C)", "Alimentación (kWh/día)", "Pérdidas (kWh/día)", "Total (kWh/día)", "Disponible (kWh/día)"],
        ["Medio anual (guano a 17 °C, aire a 18 °C)", c(b["calor_med"][0], 0), c(b["calor_med"][1], 0), c(b["calor_med"][2], 0), c(b["calor_med"][3], 0), c(b["calor"], 0)],
        ["Invierno (guano a 10 °C, aire a 8 °C)", c(b["calor_inv"][0], 0), c(b["calor_inv"][1], 0), c(b["calor_inv"][2], 0), c(b["calor_inv"][3], 0), c(b["calor"], 0)],
    ], anchos=[5.0, 1.6, 2.4, 2.2, 2.0, 2.4], alin=["L", "R", "R", "R", "R", "R"])
    m.p(f"El calor de la cogeneración alcanza en los dos casos, con un margen de "
        f"{c(b['calor'] - b['calor_med'][3], 0)} kWh/día en el caso medio y de {c(b['calor'] - b['calor_inv'][3], 0)} "
        f"kWh/día en invierno. Los valores del plano 20 (Rev. E) son estos mismos. Igual se recomienda prever un "
        f"aporte auxiliar (resistencia o quemador de biogás) para los días de helada.")
    m.h("4.5. Almacenamiento de gas y digestato", 2)
    m.calculo(f"Gas almacenado: 2 · 37 + 31 = {b['almacen']} m³ → {b['almacen']} / {c(b['biogas'], 0)} · 24", f"{c(b['h_almacen'])} h de producción")
    m.calculo(f"Digestato líquido: {c(b['Q_alim'], 2)} − 0,21 (gas) − {c(b['solido'])} (sólido) − {c(b['recirc'])} (recirculación)",
              f"{c(b['liquido'], 2)} m³/día")
    m.calculo(f"Tanque T3 Ø 8,0 × 4,0 m = {c(b['V_T3'], 0)} m³ → {c(b['V_T3'], 0)} / {c(b['liquido'], 2)}", f"{b['dias_T3']} días de almacenamiento")
    m.p("Los valores coinciden con el balance del plano 20 (Rev. E).")


def fuego(m):
    f = R["fuego"]
    m.h("5. Carga de fuego", 1)
    m.p("Se aplica el Decreto 351/79, capítulo 18 y Anexo VII. La carga de fuego se expresa en kilogramos de "
        "madera equivalente por metro cuadrado de cada sector de incendio (plano 16).")
    m.ec("q = Σ (m_i · PCI_i) / (PCI_madera · S)", ["q: carga de fuego (kg/m²)", "m_i: masa de cada material (kg)",
                                                     "PCI_i: poder calorífico (MJ/kg)", "PCI_madera = 18,41 MJ/kg", "S: superficie del sector (m²)"])
    filas = [["Material (sector S1, nave de proceso, 594 m²)", "kg", "PCI (MJ/kg)", "Energía (MJ)"]]
    for x in f["S1"]:
        filas.append([x["material"], c(x["kg"], 0), c(x["PCI"]), c(x["MJ"], 0)])
    filas.append(["Total S1", "", "", c(f["E_S1"], 0)])
    m.tabla("Carga de fuego del sector S1", filas, anchos=[9.5, 1.8, 2.0, 2.3], alin=["L", "R", "R", "R"], total=True)
    m.calculo(f"q_S1 = {c(f['E_S1'], 0)} / (18,41 · 594) = {c(f['madera_S1'], 0)} kg / 594 m²",
              f"{c(f['sectores'][0]['q'])} kg/m² (rango 16 a 30)")
    filas = [["Sector", "S (m²)", "Energía (MJ)", "q (kg/m²)", "Rango", "Riesgo", "Resist.", "Pot. A", "Pot. B"]]
    for s in f["sectores"]:
        filas.append([s["sector"], c(s["sup"], 0), c(s["E"], 0), c(s["q"]), s["rango"], s["riesgo"], s["F"], s["A"], s["B"]])
    m.tabla("Resistencia al fuego y potencial extintor por sector (Anexo VII)", filas,
            anchos=[4.6, 1.2, 1.9, 1.4, 1.6, 1.2, 1.4, 1.2, 1.2], alin=["L", "R", "R", "R", "C", "C", "C", "C", "C"])
    m.p("Los resultados coinciden con el plano 16. El silo (S3) supera los 60 kg/m² por la cáscara acumulada: "
        "como está al aire libre y es de chapa, se protege con rociadores con válvula de diluvio comandada por el "
        "cable de temperatura TS-01 en lugar de exigirle resistencia al fuego. En S1 la estructura metálica "
        "existente necesita F 60: pintura intumescente en columnas y cabriadas del sector del acopio y la zaranda.")
    m.h("5.1. Servicio de agua contra incendio", 2)
    m.ec("P = ρ · g · Q · H / η", ["P: potencia en el eje de la bomba (kW)", "Q = 24 m³/h", "H = 45 m c.a.", "η = 0,60"])
    m.calculo("P = 1.000 · 9,81 · (24/3.600) · 45 / 0,60", f"{c(f['bomba_kW_eje'])} kW → motor de 7,5 kW (M25)")
    m.calculo(f"Reserva: máx. (10 m³; 10 l/m² · 901 m²) = {c(f['reserva_m3'])} m³; 2 hidrantes × 200 l/min × 30 min",
              f"{c(f['hidrantes_m3'])} m³ ≤ tanque existente de {f['tanque_m3']} m³: verifica")


def resumen(m):
    t, v, b, f = R["tg2"], R["ventilacion"], R["biogas"], R["fuego"]
    m.h("6. Resumen de resultados", 1)
    m.tabla("Resultados principales y valores adoptados", [
        ["Magnitud", "Resultado", "Adoptado / verificación", "Plano"],
        ["Potencia instalada TG2 (con incendio)", f"{c(t['total_kW'], 2)} kW", f"+{c(t['agregado_kW'], 2)} kW por E10", "23"],
        ["Demanda TG2 (fs 0,55)", f"{c(t['demanda_tg2_kW'])} kW · {c(t['I_demanda_A'])} A", f"QG2 {t['acometida']['In']} A (Ir {t['acometida']['Ir']} A)", "23"],
        [f"Acometida TG2 4 × {t['acometida']['S']} mm² enterrada", f"Iz = {c(t['acometida']['Iz'])} A", f"verifica con {t['acometida']['In']} A", "23"],
        ["Iluminación del depósito E7", f"{R['iluminacion']['n']} × 150 W LED", f"E = {R['iluminacion']['E_real']} lx ≥ 200 lx", "23"],
        ["Circuito nuevo Q27 TS-VEN", f"Ib = {c(next(x['Ib'] for x in t['circuitos'] if x['Q'] == 'Q27'))} A", "4P 13 A · 4 × 2,5 mm²", "23"],
        ["Icc en barras del TG2", f"{c(t['Icc_TG2_kA'], 2)} kA", "Icu 10 kA: verifica", "23"],
        ["Potencia a contratar (G1 parada)", f"{c(t['balance']['sin_G1_kW'])} kW", f"{t['balance']['adoptada_kW']} kW", "23"],
        ["Caudal de ventilación de diseño", f"{c(v['Q_diseno'], 0)} m³/h", f"2 extractores · {c(v['Q_real'], 0)} m³/h reales", "24"],
        ["Renovaciones reales", f"{c(v['ren_real'])} /h", "≥ 12 /h: verifica", "24"],
        ["Biogás", f"{c(b['biogas'], 0)} m³/día", f"CHP 25 kWe · {c(b['horas'])} h/día", "20"],
        ["Volumen útil de digestores", f"{c(b['V_util'], 0)} m³", f"2 × Ø 6,5 m · B_v = {c(b['carga'], 2)}", "20"],
        ["Calor de digestores en invierno", f"{c(b['calor_inv'][3], 0)} kWh/día", f"≤ {c(b['calor'], 0)} disponibles", "20"],
        ["Carga de fuego S1", f"{c(f['sectores'][0]['q'])} kg/m²", "R3 · F 60 · 2 A / 6 B", "16"],
        ["Bomba de incendio", f"{c(f['bomba_kW_eje'])} kW en el eje", "motor 7,5 kW", "16"],
    ], anchos=[5.8, 3.6, 4.8, 1.3], alin=["L", "R", "L", "C"])


def conclusiones(m):
    t = R["tg2"]
    m.h("7. Conclusiones y observaciones", 1)
    m.lista([
        f"Los extractores y ventiladores del ítem E10 se suman al TG2 con un circuito propio (Q27, TS-VEN). La "
        f"potencia instalada del TG2 queda en {c(t['total_kW'], 2)} kW y los {t['balance']['adoptada_kW']} kW a contratar "
        f"siguen alcanzando con la cogeneración parada (margen {c(t['balance']['margen_sin_G1_pct'])} %).",
        f"La acometida del TG2 pasa a 4 × {t['acometida']['S']} mm² enterrada: verifica con los fusibles NH00 y el QG2 "
        f"de {t['acometida']['In']} A (en la Rev. D, con 25 mm², no verificaba).",
        "Los largos de Q22 y Q25 se tomaron sobre el recorrido de las canalizaciones del plano 13 y la iluminación "
        "del Sector Este quedó calculada por el método de los lúmenes, con lo que el balance eléctrico está cerrado.",
        "El caudal real de los extractores se justificó con el punto de funcionamiento sobre la curva del catálogo; "
        "se mantiene el 85 % del caudal libre del lado de la seguridad.",
        "El calor de la cogeneración cubre la calefacción de los digestores con los coeficientes U calculados por "
        "capas (ISO 6946); conviene prever un aporte auxiliar para las heladas.",
        "Quedan para confirmar con terceros: la potencia y la conexión en paralelo de G1 con la distribuidora LAR, "
        "los retiros del lote con el reglamento del Parque Industrial y la rosa de vientos del SMN.",
        "La carga de fuego y los medios de extinción del plano 16 verifican sin cambios.",
    ])


def bibliografia(m):
    m.h("Bibliografía y normas", 1)
    for x in [
        "Asociación Electrotécnica Argentina. (2006). AEA 90364-7-771: Reglamentación para la ejecución de instalaciones eléctricas en inmuebles. Buenos Aires: AEA.",
        "International Electrotechnical Commission. (2009). IEC 60364-5-52: Low-voltage electrical installations – Selection and erection of electrical equipment – Wiring systems. Ginebra: IEC.",
        "IRAM. IRAM 2178: Cables de energía aislados con dieléctricos sólidos extruidos para tensiones nominales de 1,1 kV.",
        "IRAM. IRAM 2281: Puesta a tierra de sistemas eléctricos. IRAM 2184: Protección de las estructuras contra las descargas eléctricas atmosféricas.",
        "República Argentina. (1972). Ley 19.587 de Higiene y Seguridad en el Trabajo, y Decreto Reglamentario 351/79, capítulo 18 y Anexo VII.",
        "KTBL. (2013). Faustzahlen Biogas (3.ª ed.). Darmstadt: Kuratorium für Technik und Bauwesen in der Landwirtschaft.",
        "Campagnoni. Catálogo de extractores AirTEC. Crespo, Entre Ríos (dato a confirmar con la ficha técnica vigente).",
    ]:
        par = m.d.add_paragraph(x)
        par.paragraph_format.left_indent = Cm(0.8)
        par.paragraph_format.first_line_indent = Cm(-0.8)
        m.html.append(f'<p class="biblio">{esc(x)}</p>')
    m.h("Anexo – Programa de cálculo", 1)
    m.p("Los cálculos de esta memoria se hicieron con fuente/calculos/calculos_memoria.py (Python 3). El programa "
        "guarda todos los resultados en fuente/calculos/resultados.json, que también usa el script del plano 23. "
        "Para recalcular después de cambiar un dato: python calculos_memoria.py y luego python memoria_docx.py.")


def main():
    m = Memoria()
    portada(m)
    encabezado_pie(m)
    introduccion(m)
    tg2(m)
    p23 = os.path.join(RAIZ, "planos", "P23.png")
    if os.path.exists(p23):
        m.figura(p23, "Esquema unifilar del TG2, plano 23 Rev. E", 16)
    figuras = {"24": "Ventilación general de la nave, plano 24 Rev. E",
               "20": "Sistema de biogás: planta, corte y balance, plano 20 Rev. D",
               "16": "Estudio de carga de fuego, plano 16 Rev. D"}

    def fig(n):
        ruta = os.path.join(RAIZ, "planos", f"P{n}.png")
        if os.path.exists(ruta):
            m.figura(ruta, figuras[n], 16)

    ventilacion(m)
    fig("24")
    biogas(m)
    fig("20")
    fuego(m)
    fig("16")
    resumen(m)
    conclusiones(m)
    bibliografia(m)
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    m.d.save(SALIDA)
    print("guardado", SALIDA, "| tablas", m.n_tabla, "| ecuaciones", m.n_ec, "| figuras", m.n_fig)
    pdf_desde_html(m)


# ---------------------------------------------------------------- PDF (Chrome headless)

CSS = """
@page { size: A4; margin: 2.5cm 2.5cm 2.3cm 2.5cm; }
body { font-family: Arial, Helvetica, sans-serif; font-size: 11pt; line-height: 1.38; color: #111; }
p { margin: 0 0 6pt; text-align: justify; }
h1 { font-size: 15pt; color: #1F3A5F; margin: 16pt 0 7pt; break-after: avoid; }
h2 { font-size: 12.5pt; color: #1F3A5F; margin: 12pt 0 6pt; break-after: avoid; }
h3 { font-size: 11pt; color: #1F3A5F; break-after: avoid; }
ul { margin: 0 0 8pt 0; padding-left: 18pt; } li { margin-bottom: 3pt; text-align: justify; }
mark { background: #ffff00; }
.salto { break-after: page; }
.ec { display: flex; justify-content: center; position: relative; margin: 8pt 0 3pt; font-family: 'Cambria Math', Cambria, serif; font-size: 11.5pt; }
.ec .n { position: absolute; right: 0; font-family: Arial; }
.simb { margin-left: 1cm; font-size: 9.5pt; text-align: left; }
.calc { margin-left: 1cm; text-align: left; }
.cap { font-size: 9.5pt; color: #333; margin: 10pt 0 3pt; break-after: avoid; text-align: left; }
table { border-collapse: collapse; width: auto; margin: 0 auto 10pt; font-size: 9pt; }
th, td { border: 0.6pt solid #555; padding: 1.6pt 4pt; vertical-align: top; }
th { background: #DCE3EA; text-align: left; } tr { break-inside: avoid; }
td.right { text-align: right; } td.center { text-align: center; } td.tot { font-weight: bold; } td.res { background: #E2F0E4; }
figure { margin: 10pt 0; text-align: center; break-inside: avoid; } figure img { max-width: 100%; border: 0.5pt solid #999; }
figcaption { font-size: 9.5pt; color: #333; margin-top: 4pt; }
.biblio { padding-left: 0.8cm; text-indent: -0.8cm; text-align: left; }
.recuadro { border: 0.6pt solid #7a8ea5; background: #EEF3F8; padding: 6pt 8pt; margin: 6pt 0 10pt; text-align: justify; break-inside: avoid; }
#indice .l { display: flex; align-items: baseline; margin: 3pt 0; }
#indice .l span.t { white-space: nowrap; } #indice .l span.d { flex: 1; border-bottom: 1pt dotted #888; margin: 0 4pt; }
#indice .n2 { padding-left: 14pt; font-size: 10.5pt; } #indice .n1 { font-weight: bold; margin-top: 7pt; }
#indice .n3 { padding-left: 28pt; font-size: 10pt; }
"""


def _html(m, paginas=None, titulo=None):
    lineas = []
    for nivel, hid, texto in m.indice:
        pg = str(paginas.get(hid, "")) if paginas else "00"
        lineas.append(f'<div class="l n{nivel}"><span class="t">{esc(texto)}</span><span class="d"></span><span>{pg}</span></div>')
    cuerpo = "\n".join(m.html).replace("__INDICE__", "\n".join(lineas))
    return f'<!doctype html><html lang="es"><head><meta charset="utf-8"><title>{esc(titulo or "Memoria de cálculo Rev. D")}</title><style>{CSS}</style></head><body>{cuerpo}</body></html>'


def fuente_arial():
    """Arial en Windows; en Linux, la Liberation Sans (métrica igual a Arial)."""
    for r in (r"C:\Windows\Fonts\arial.ttf", os.path.expanduser("~/.fonts/arial.ttf"),
              "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
              "/usr/share/fonts/liberation/LiberationSans-Regular.ttf"):
        if os.path.exists(r):
            return r
    return None


def pdf_desde_html(m, salida=None, encabezado="Secadora de guano 8 t/día – Memoria de cálculo Rev. D", titulo=None):
    import subprocess

    import pymupdf
    pdf = os.path.splitext(salida or SALIDA)[0] + ".pdf"
    tmp_html = os.path.join(AQUI, "_memoria.html")
    script = os.path.join(RAIZ, "fuente", "imprimir_pdf.js")

    def imprimir(paginas):
        with open(tmp_html, "w", encoding="utf-8") as f:
            f.write(_html(m, paginas, titulo))
        subprocess.run(["node", script, tmp_html, pdf], check=True)

    imprimir(None)
    # primera pasada: en qué página cae cada título
    paginas = {}
    with pymupdf.open(pdf) as d:
        textos = [d[i].get_text() for i in range(d.page_count)]
    desde = 2
    for _nivel, hid, texto in m.indice:
        for i in range(desde, len(textos)):
            if texto in textos[i].replace("\n", " ") or texto in textos[i]:
                paginas[hid] = i + 1
                desde = i
                break
    imprimir(paginas)
    # encabezado y número de página (no en la portada)
    fuente = fuente_arial()
    letra = {"fontname": "arial", "fontfile": fuente} if fuente else {"fontname": "helv"}
    with pymupdf.open(pdf) as d:
        for i in range(1, d.page_count):
            pg = d[i]
            w, h = pg.rect.width, pg.rect.height
            ancho = pymupdf.get_text_length(encabezado, fontsize=8.5, fontname="helv")
            pg.insert_text((w - 71 - ancho, 42), encabezado, fontsize=8.5, color=(0.4, 0.4, 0.4), **letra)
            pg.draw_line((71, 48), (w - 71, 48), color=(0.7, 0.7, 0.7), width=0.5)
            txt = f"Página {i + 1} de {d.page_count}"
            pg.insert_text((w / 2 - 30, h - 30), txt, fontsize=9, **letra)
        d.save(pdf + ".tmp", garbage=3, deflate=True)
    os.replace(pdf + ".tmp", pdf)
    os.remove(tmp_html)
    print("PDF", pdf, "| páginas del índice:", paginas)


if __name__ == "__main__":
    main()
