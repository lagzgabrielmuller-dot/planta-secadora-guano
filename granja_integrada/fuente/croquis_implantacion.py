"""Croquis rápido de la implantación (PNG) para revisar la distribución antes de modelar.

    python croquis_implantacion.py   # -> ../docs/croquis_implantacion.png
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.patches as mp  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
D = json.loads((RAIZ / "datos" / "granja.json").read_text(encoding="utf-8"))

C_LIMPIO, C_SUCIO, C_GALPON, C_PLANTA = "#d8e6cf", "#ead9c4", "#9fb8cf", "#c9c2b6"


def rect(ax, x0, y0, x1, y1, **kw):
    ax.add_patch(mp.Rectangle((x0, y0), x1 - x0, y1 - y0, **kw))


def main():
    fig, ax = plt.subplots(figsize=(16, 7.2), dpi=150)
    pr = D["predio"]
    rect(ax, pr["x0"], pr["y0"], pr["x1"], pr["y1"], fill=False, ec="#2f5d2f", lw=1.6, ls="--")
    ax.text(pr["x0"] + 2, pr["y1"] - 4, "cerco perimetral", fontsize=7, color="#2f5d2f")
    c = D["calle"]
    rect(ax, pr["x0"] - 20, c["y0"], pr["x1"] + 20, c["y1"], color="#bdbdbd")
    ax.text(10, (c["y0"] + c["y1"]) / 2, c["nom"], fontsize=7, va="center")
    for cm in D["caminos"]:
        rect(ax, cm["x0"], cm["y0"], cm["x1"], cm["y1"], color=C_LIMPIO if cm["zona"] == "limpia" else C_SUCIO, ec="#8a8a8a", lw=0.4)
    for p in D["playones"]:
        rect(ax, p["x0"], p["y0"], p["x1"], p["y1"], color="#dcdcdc", ec="#8a8a8a", lw=0.4)
    for g in D["galpones"]:
        rect(ax, g["x0"], g["y0"], g["x1"], g["y1"], color=C_GALPON, ec="#2d4a63", lw=0.8)
        ax.text((g["x0"] + g["x1"]) / 2, g["y"], f"{g['id']} · {D['jaulas']['aves_por_galpon']:,} gallinas".replace(",", "."),
                ha="center", va="center", fontsize=7, color="#10263a", weight="bold")
    for a in D["ampliacion"]:
        rect(ax, a["x0"], a["y"] - 3, a["x1"], a["y"] + 3, fill=False, ec="#2d4a63", lw=0.7, ls=":")
        ax.text((a["x0"] + a["x1"]) / 2, a["y"], a["id"], ha="center", va="center", fontsize=6.5, color="#2d4a63")
    for dpo in D["depositos"]:
        rect(ax, dpo["x0"], dpo["y0"], dpo["x1"], dpo["y1"], color="#e9d79a", ec="#7a6420", lw=0.8)
        ax.text((dpo["x0"] + dpo["x1"]) / 2, (dpo["y0"] + dpo["y1"]) / 2, f"{dpo['id']}\nhuevos y\npalets", ha="center",
                va="center", fontsize=6)
    for s in D["silos_alimento"]:
        ax.add_patch(mp.Circle((s["x"], s["y"]), s["D"] / 2, color="#b0a68e", ec="#5d553f", lw=0.4))
    p = D["planta"]
    n = p["nave"]
    rect(ax, n["x0"], n["y0"], n["x0"] + n["L"], n["y0"] + n["A"], color=C_PLANTA, ec="#333", lw=0.9)
    an = p["anexo"]
    rect(ax, an["x0"], an["y0"], an["x1"], an["y1"], color="#b9aa98", ec="#333", lw=0.6)
    for k in ("silo", "ciclon", "scrubber"):
        e = p[k]
        ax.add_patch(mp.Circle((e["x"], e["y"]), e["D"] / 2, color="#9a9a9a", ec="#333", lw=0.4))
    ax.text(16.5, 9, "PLANTA DE SECADO\n(nave 33 × 18 m)", ha="center", va="center", fontsize=7, weight="bold")
    tp = D["tolva_pulmon"]
    rect(ax, tp["x0"], tp["y0"], tp["x1"], tp["y1"], color="#a0522d", ec="#4a2512", lw=0.6)
    for t in D["transporte"]:
        col = "#b33a1d" if t["tipo"] in ("principal", "interior", "exterior") else "#d9822b"
        ax.plot([t["p0"][0], t["p1"][0]], [t["p0"][1], t["p1"][1]], color=col, lw=1.6 if t["tipo"] != "transversal" else 1.0)
    for tt in D["torres"]:
        rect(ax, tt["x"] - tt["A"] / 2, tt["y"] - tt["B"] / 2, tt["x"] + tt["A"] / 2, tt["y"] + tt["B"] / 2,
             color="#6b6b6b", ec="#222", lw=0.5)
        ax.text(tt["x"], tt["y"] - 3.4, tt["id"], ha="center", fontsize=6)
    ac = D["acceso"]
    for k in ("garita", "bascula", "vado", "bioseguridad", "set"):
        e = ac[k]
        rect(ax, e["x0"], e["y0"], e["x1"], e["y1"], color="#cfcfe8", ec="#444", lw=0.4)
    ax.text(32, -80, "vestuarios\ny duchas", fontsize=5.5, ha="center", va="center")
    ax.text(-8, -84, "SET", fontsize=5.5, ha="center", va="center")
    ax.text(16.5, -42, "báscula", fontsize=5.5, ha="center", va="center", rotation=90)
    ax.text(16.5, -75.5, "vado", fontsize=5.5, ha="center", va="center")
    ax.annotate("cintas de guano a la planta", (-30, 9.3), (-95, -32), fontsize=7, color="#b33a1d",
                arrowprops=dict(arrowstyle="->", color="#b33a1d", lw=0.8))
    ax.annotate("zona limpia: huevos y alimento", (-160, 0), (-195, -30), fontsize=7, color="#2f5d2f",
                arrowprops=dict(arrowstyle="->", color="#2f5d2f", lw=0.8))
    ax.annotate("zona sucia: guano y planta", (16, 40), (60, 66), fontsize=7, color="#8a5a24",
                arrowprops=dict(arrowstyle="->", color="#8a5a24", lw=0.8))
    ax.set_aspect("equal")
    ax.set_xlim(pr["x0"] - 18, pr["x1"] + 18)
    ax.set_ylim(c["y0"] - 4, pr["y1"] + 6)
    ax.set_title("Granja avícola integrada con planta central de secado de guano — implantación (croquis, metros)", fontsize=10)
    ax.grid(True, lw=0.2, color="#cccccc")
    fig.tight_layout()
    out = RAIZ / "docs" / "croquis_implantacion.png"
    fig.savefig(out)
    print(out)


if __name__ == "__main__":
    main()
