"""Extrae el informe de la Rev. C (Proyecto_Final_Secadora_Guano.docx, en la raíz del repositorio) a un
texto fuente editable: fuente/informe/texto_revC.md y las imágenes a fuente/informe/img_revC/.

Se corrió una sola vez; después texto_revC.md se corrigió a mano (valores de la Rev. D/E, plano y
distribuidora) y es la fuente de los capítulos de la Rev. C dentro del informe final. No volver a
correrlo salvo que se quiera empezar de nuevo desde el Word original (pisa las correcciones).

Formato de texto_revC.md:
  # / ## / ###            títulos de nivel 1, 2 y 3
  Tabla N. título         seguido de renglones "| a | b | c" (el primero es el encabezado)
  Figura N. epígrafe      [img: archivo.png] en el renglón anterior si la figura tiene imagen
  - texto                 ítem de lista
  texto                   párrafo
"""
import os
import sys

from docx import Document
from docx.oxml.ns import qn

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ_REPO = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))


def main(origen):
    doc = Document(origen)
    carpeta_img = os.path.join(AQUI, "img_revC")
    os.makedirs(carpeta_img, exist_ok=True)
    rels = doc.part.rels
    salida, n_img = [], 0
    cuerpo = doc.element.body
    for el in cuerpo.iterchildren():
        if el.tag == qn("w:p"):
            from docx.text.paragraph import Paragraph
            p = Paragraph(el, doc)
            for blip in el.iter(qn("a:blip")):
                rid = blip.get(qn("r:embed"))
                if rid in rels:
                    n_img += 1
                    nombre = f"revC_{n_img:02d}.png"
                    with open(os.path.join(carpeta_img, nombre), "wb") as f:
                        f.write(rels[rid].target_part.blob)
                    salida.append(f"[img: {nombre}]")
            txt = p.text.strip()
            if not txt:
                continue
            try:
                estilo = (p.style.name or "").lower()
            except AttributeError:
                estilo = ""
            ppr = el.find(qn("w:pPr"))
            if not estilo and ppr is not None and ppr.find(qn("w:pStyle")) is not None:
                estilo = ppr.find(qn("w:pStyle")).get(qn("w:val")).lower()
            if ppr is not None and ppr.find(qn("w:numPr")) is not None and "heading" not in estilo:
                estilo = "lista"
            if estilo.startswith("heading") or estilo.startswith("título"):
                nivel = int("".join(ch for ch in estilo if ch.isdigit()) or 1)
                salida.append("#" * nivel + " " + txt)
            elif "list" in estilo or "lista" in estilo:
                salida.append("- " + txt)
            else:
                salida.append(txt)
        elif el.tag == qn("w:tbl"):
            from docx.table import Table
            tb = Table(el, doc)
            for fila in tb.rows:
                celdas = []
                for c in fila.cells:
                    v = " ".join(c.text.split())
                    if not celdas or celdas[-1] is not c:
                        celdas.append(v)
                salida.append("| " + " | ".join(celdas))
    with open(os.path.join(AQUI, "texto_revC.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(salida) + "\n")
    print(f"{len(salida)} renglones, {n_img} imágenes")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(RAIZ_REPO, "Proyecto_Final_Secadora_Guano.docx"))
