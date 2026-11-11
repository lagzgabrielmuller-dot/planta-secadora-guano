"""Arma simulador.html (en la carpeta del estudio, al lado de figuras/, para que se vean las láminas):
la plantilla + three.js (web/vendor, licencia MIT) + la vista 3D (vista3d.js) + el modelo JavaScript + los
datos de planta + los textos del estudio con los números de resultados/*.json + el punto de diseño ya calculado.

Uso:  python web/construir.py      (antes: python correr_todo.py y python exportar_web.py)
"""
import json
import os
import subprocess

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
RES = os.path.join(RAIZ, "resultados")


def cargar(n):
    with open(os.path.join(RES, f"{n}.json"), encoding="utf-8") as f:
        return json.load(f)


def num(x, d=0):
    s = f"{abs(x):,.{d}f}".replace(",", "§").replace(".", ",").replace("§", ".")
    return ("−" if x < 0 and float(f"{abs(x):.{d}f}") != 0 else "") + s


def lamina(archivo, alt, pie=None):
    pie = f"<figcaption>{pie}</figcaption>" if pie else ""
    return (f'<figure class="lamina"><img src="figuras/{archivo}" alt="{alt}">{pie}</figure>')


def hallazgo(titulo, cifra, cifra_pie, parrafos, laminas):
    ps = "".join(f"<p>{p}</p>" for p in parrafos)
    return (f'<article class="hallazgo"><div class="texto"><h3>{titulo}</h3>'
            f'<div class="cifra">{cifra}<small>{cifra_pie}</small></div>{ps}</div>'
            f'<div class="laminas">{"".join(laminas)}</div></article>')


def textos():
    P = cargar("perfiles")
    C = cargar("capacidad")
    TN = cargar("temperatura")
    R = cargar("recirculacion")
    S = cargar("sensibilidad")
    CL = cargar("clima")
    E = cargar("energia")
    DY = cargar("dinamica")
    VA = cargar("validacion")
    B = cargar("bordes")
    HG = cargar("higiene")
    d, a, _c = P["diseno"]["resumen"], P["ajustado"]["resumen"], P["capacidad"]["resumen"]
    T15 = P["T15"]
    cap135 = [r for r in C["vel_fija"] if r["T_aire"] == 135.0][0]["alimentacion"]
    cerrados = [r for r in C["vel_fija"] if r.get("cd03") in ("cerrada", "cicla")]
    pend_cap = (cerrados[-1]["alimentacion"] - cerrados[0]["alimentacion"]) / (cerrados[-1]["T_aire"] - cerrados[0]["T_aire"])
    ph = TN["por_humedad"]
    T65, T78 = ph[0]["T_aire"], ph[-1]["T_aire"]
    tot15 = sum(m["a15"]["cascara_t_mes"] for m in CL["meses"])
    tot135 = sum(m["a135"]["cascara_t_mes"] for m in CL["meses"])
    [m["nombre"] for m in CL["meses"] if m["a15"].get("cd03") in ("cerrada", "cicla")]
    # recirculación con la CD-03 fija al 25 %, al 15 % y a 135 °C
    i25 = R["recirc"].index(0.25)
    ah = lambda clave, caso: 100 * (1 - R[clave][i25][caso]["comb"] / R[clave][0][caso]["comb"])
    # aire por los bordes
    bc = {round(x["bypass_pila"], 2): x for x in B["casos"]}
    T05, T10 = bc[0.05]["a15"]["T_aire"], bc[0.10]["a15"]["T_aire"]
    cap10 = bc[0.10]["capacidad"]["alimentacion"]
    e10 = bc[0.10]["a15"]
    ahorro10 = B["anual"]["0.10"]["t135"] - B["anual"]["0.10"]["t15"]
    extra05 = B["anual"]["0.05"]["t15"] - tot15
    # higiene según el espesor de capa
    h3 = next(f for f in HG["filas"] if f["nz"] == 3)
    hfina = max(HG["filas"], key=lambda f: f["nz"])
    next(f for f in HG["filas"] if f["nz"] == 8)
    gr_ = {g["d0_mm"]: g["hum135"] for g in S["grumos"]}
    fila_grumo = [f for f in S["filas"] if f["nombre"].startswith("Tamaño")][0]
    fila_D = [f for f in S["filas"] if f["nombre"].startswith("Difusividad")][0]
    fila_borde = [f for f in S["filas"] if f["nombre"].startswith("Aire que sube")][0]
    casos = {c_["nombre"]: c_ for c_ in DY["casos"]}
    import numpy as np

    def met(c_):
        t = np.array(c_["t"])
        h = 100 * np.array(c_["hum_real"])
        m = t >= 1.0
        llega = float(t[np.argmax(m & (h > 16.0))])
        fuera = np.where(m & (np.abs(h - 15.0) > 1.0))[0]
        vuelve = float(t[fuera[-1]]) if len(fuera) else 1.0
        return dict(max=h[m].max(), min=h[m].min(), fin=h[-30:].mean(), llega=llega, vuelve=vuelve,
                    s20=float(((h > 20.0) & m).sum() * (t[1] - t[0]) * 60.0), alarma=max(c_["alarma"]))
    sin = met([v for k, v in casos.items() if k.startswith("sin")][0])
    mi = met([v for k, v in casos.items() if k.startswith("informe")][0])
    mp = met([v for k, v in casos.items() if k.startswith("propuesto:")][0])
    mf = met([v for k, v in casos.items() if k.startswith("propuesto +")][0])
    r_mod = [100 * E[k]["rendimiento"] for k in ("diseno", "ajustado", "capacidad")]
    r_mem = 100 * E["informe"]["rendimiento"]
    # enfriamiento del producto antes del acopio
    X15 = 0.15 / 0.85
    ss = 280.0 / 3600.0
    q_enfr = ss * (1500.0 + 4186.0 * X15) * (a["T_prod"] - 40.0) / 1e3          # kW
    aire_enfr = q_enfr / (1.006 * 22.0) / 1.18 * 3600.0                         # m³/h con 22 K de salto
    prod = a["prod"]

    H = []
    H.append(hallazgo(
        "A 135 °C el SC-4 seca de más",
        "< 2 %", "humedad de salida en el punto de diseño de la Rev. E",
        [f"Con 1.000 kg/h al 72 %, aire a 135 °C, bandas a 0,37 m/min y 25 % de recirculación, el guano ya está "
         f"seco al terminar el piso 2 y sale a {num(d['T_prod'])} °C. El piso 3 solo lo calienta.",
         f"La memoria supone que el aire sale a 65 °C y que el {num(r_mem)} % del calor va al guano. En un lecho "
         f"atravesado pasa otra cosa: mientras el guano tiene agua, el aire sale casi saturado y se aprovecha "
         f"{num(min(r_mod))}-{num(max(r_mod))} % del calor. Para dejarlo al 15 % alcanza con aire a {num(T15)} °C, con "
         f"{num(a['comb'])} kg/h de cáscara en vez de {num(d['comb'])}; si entre 5 y 10 % del aire sube por los bordes "
         f"sin tocar el guano, con {num(T05)} a {num(T10)} °C."],
        [lamina("01_perfiles_diseno.png", "Humedad y temperaturas a lo largo del secador a 135 y a 102 °C"),
         lamina("14_balance_de_energia.png", "Destino del calor del generador: memoria contra modelo")]))
    H.append(hallazgo(
        "Sobra capacidad",
        f"{num(round(cap135, -1))} kg/h", "de guano al 72 % que el SC-4 lleva al 15 % con aire a 135 °C",
        [f"A 135 °C el escape pasa de 45 g/kg y la CD-03 se cierra por su regla. Así el secador procesa "
         f"{num(100 * (cap135 / 1000 - 1))} % más que lo pedido, y cada grado de aire suma unos {num(pend_cap)} kg/h: "
         f"las 8 t del día en {num(8000 / cap135, 1)} h, o las 16 t de dos turnos en {num(16000 / cap135, 1)} h de marcha. "
         f"Si un 10 % del aire sube por los bordes, la capacidad baja a {num(round(cap10, -1))} kg/h.",
         f"Para eso la cinta de alimentación (M8) tiene que pasar de 3,9 a unos {num(3.9 * cap135 / 1000, 1)} cm/s. Si el guano viene "
         f"con 65 % alcanza con aire a {num(T65)} °C; con 78 %, {num(T78)} °C (el informe prevé 120 a 150 °C)."],
        [lamina("06_capacidad.png", "Capacidad al 15 % según la temperatura del aire"),
         lamina("05_temperatura_necesaria.png", "Temperatura de aire necesaria según la humedad y el caudal de guano")]))
    H.append(hallazgo(
        "La humedad se controla con el aire, no con las bandas",
        "−1,8 puntos/°C", "cambio de la humedad de salida por grado de aire cerca del 15 %",
        ["Cerca del 15 % el secador está limitado por el calor: todo el calor que trae el aire se gasta en evaporar. "
         "Mover las bandas cambia poco la humedad, y la cambia tarde y al revés: si se frenan, primero sale menos "
         "producto con el mismo calor (más seco) y una hora y media después llega la capa más gruesa (más húmeda).",
         f"Si el guano pasa de 72 a 76 %, el húmedo tarda {num(mp['llega'] - 1.0, 1)} h en llegar a la salida y "
         f"ningún lazo que mida ahí evita el primer pico ({num(sin['max'])} %). Después, el lazo MIC-01 del informe "
         f"(bandas) hace oscilar el producto entre {num(mi['min'])} y {num(mi['max'])} % y no vuelve al 15 % en 8 h. Si "
         f"el MIC-01 corrige la consigna de TIC-01, vuelve al 15 % (±1 punto) {num(mp['vuelve'] - mp['llega'], 1)} h "
         f"después de que llega el guano húmedo. Midiendo la humedad del guano fresco, el pico baja a "
         f"{num(mf['max'])} % y queda {num(mf['s20'])} min sobre 20 %, menos que los 15 min de la alarma."],
        [lamina("03_ventana_de_operacion.png", "Humedad de salida según la temperatura del aire y la velocidad de las bandas"),
         lamina("04_que_controla_la_humedad.png", "Humedad de salida según la velocidad de las bandas y según la temperatura del aire"),
         lamina("12_control_dinamico.png", "Respuesta en el tiempo de las tres estrategias de control")]))
    H.append(hallazgo(
        "El escape sale casi saturado",
        f"{num(100 * a['HR_exh'])} %", f"humedad relativa del aire de escape al 15 % ({num(a['T_exh'])} °C)",
        ["El apartado 4.1.3 del informe dice que no hay riesgo de condensación porque el aire sale a 65 °C con 33 g/kg. "
         f"Operando al 15 % sale a {num(a['T_exh'])} °C con {num(1000 * a['Y_exh'])} g/kg: condensa en el ducto "
         f"Ø800 y en el ciclón, y el polvo mojado tiende a pegarse. Si un 10 % del aire sube por los bordes, sale a "
         f"{num(e10['T_exh'])} °C y {num(100 * e10['HR_exh'])} %: condensa más adelante, igual.",
         f"Por lo mismo, al 15 % la recirculación casi no ahorra: con la CD-03 al 25 % se ahorra "
         f"{num(ah('diseno', 'a15'), 1)} % de cáscara a 18 °C, {num(ah('invierno', 'a15'), 1)} % en julio (con la "
         f"cámara de mezcla saturada) y en enero se gasta {num(-ah('verano', 'a15'), 1)} % más. Solo rinde a 135 °C, con "
         f"el escape caliente ({num(ah('diseno', 'a135'))} %). La regla de la CD-03 (cerrar sobre 45 g/kg) cae justo en "
         "el punto de trabajo: en verano la cerraría y, cerrada, el escape baja de 45 g/kg y la volvería a abrir."],
        [lamina("07_recirculacion.png", "Efecto de la recirculación en la cáscara y en la cámara de mezcla")]))
    H.append(hallazgo(
        "Las guías de UHMW-PE quedan en el aire más caliente",
        f"{num(a['Tin'][2])} a {num(d['Tin'][2])} °C", "aire bajo la banda del piso 3, donde van las guías",
        ["El informe (7.2.5) dice que la guía queda bajo la malla, en la zona de aire más frío. Con el aire subiendo "
         "desde el plenum pasa lo contrario: bajo cada banda va el aire que entra a ese piso, y bajo el piso 3 es el "
         "aire del generador.",
         f"El UHMW-PE aguanta 80 °C en uso continuo y funde a 130-135 °C. A 135 °C también el piso 2 queda a "
         f"{num(d['Tin'][1])} °C. Conviene cambiar las guías de los pisos 2 y 3 por PTFE, que trabaja hasta 260 °C."],
        [lamina("10_guias_uhmw.png", "Temperatura del aire bajo cada banda")]))
    H.append(hallazgo(
        "La higienización hay que pensarla de nuevo",
        f"{num(a['t55_med'])} min", "sobre 55 °C en promedio cuando el guano sale al 15 %",
        [f"El aire seca y calienta primero la capa de abajo. Al 15 % el guano pasa en promedio {num(a['t55_med'])} min "
         f"sobre 55 °C y los grumos de arriba del piso 3 llegan como mucho a {num(hfina['Tmax_arriba'][2])}-"
         f"{num(h3['Tmax_arriba'][2])} °C, según el espesor de capa que se tome: el criterio del informe (más de 55 °C "
         f"durante 1 h) solo se cumple sobresecando, a 135 °C. Además, el 15 % es un promedio: arriba salen grumos "
         f"con {num(100 * h3['hum_arriba'])}-{num(100 * hfina['hum_arriba'])} % de humedad y abajo con "
         f"{num(100 * hfina['hum_abajo'], 1)}-{num(100 * h3['hum_abajo'], 1)} %.",
         f"El TT-05 de la descarga mide la mezcla, que sale a {num(a['T_prod'])} °C, y no ve los grumos fríos. Una "
         f"tolva aislada de retención de 1 h ({num(prod / 500, 1)} m³ útiles) a la salida podría tener todo el "
         f"producto 1 h sobre 70 °C, que es lo que pide la Unión Europea para el estiércol procesado, pero con solo "
         f"{num(a['T_prod'] - 70)} K de margen: hay que aislarla bien y comprobarlo con el TT-05 adentro. Después hay "
         f"que enfriarlo antes del acopio: unos {num(q_enfr)} kW."],
        [lamina("11_higiene.png", "Temperatura de la capa de arriba, de la de abajo y del promedio dentro del secador"),
         lamina("02_capas_del_lecho.png", "Humedad y temperatura de cada capa del lecho a lo largo del secador")]))
    H.append(hallazgo(
        "El grumo y el sellado de los bordes pesan más que la cinética",
        f"+{num(fila_grumo['a']['T15'] - S['base']['T15'])} °C", "más de aire si los grumos son de 20 mm en vez de 10",
        [f"Duplicar o dividir por dos la difusividad del agua en el grumo mueve la temperatura necesaria apenas "
         f"{num(abs(fila_D['a']['T15'] - S['base']['T15']), 1)} K, porque el secador está limitado por el calor. Lo "
         f"que sí pesa son los caudales (±8 K por ±10 %), cómo deja el guano el esparcidor y el aire que sube por los "
         f"bordes de las bandas sin tocar el guano: con un 10 %, hacen falta "
         f"{num(fila_borde['a']['T15'] - S['base']['T15'], 1)} K más.",
         f"Con grumos de hasta 20 mm el diseño a 135 °C sobreseca igual; con 25 mm sale al {num(100 * gr_[25.0], 1)} % "
         f"y con 30 mm ya no llega ({num(100 * gr_[30.0], 1)} %). Conviene medir el grumo en el módulo piloto y "
         f"asegurar el sello entre las bandas y las paredes."],
        [lamina("08_sensibilidad.png", "Sensibilidad de la temperatura necesaria y efecto del tamaño de grumo")]))
    H.append(hallazgo(
        "Cáscara por año",
        f"−{num(tot135 - tot15)} t", f"de cáscara por año ajustando el aire al 15 % ({num(100 * (1 - tot15 / tot135))} % menos)",
        [f"Con el clima del turno de Crespo mes a mes: {num(tot15)} t/año al 15 % contra {num(tot135)} t a 135 °C, con "
         f"la CD-03 siguiendo su regla (el informe estima 575 t con recirculación). A USD 25/t son unos "
         f"USD {num(round((tot135 - tot15) * 25, -2))} por año. Si un 10 % del aire sube por los bordes, el ahorro baja "
         f"a {num(ahorro10)} t.",
         "La temperatura de aire que deja 15 % casi no cambia en el año; lo que cambia es cuánto calor hace falta para "
         "llegar a ella desde el aire de la nave."],
        [lamina("09_clima_anual.png", "Cámara de mezcla y cáscara mes a mes")]))
    hallazgos_html = "\n".join(H)

    cambios = [
        ("Lazo de humedad", "14.5.2 · MIC-01 → TIC-01",
         "Que el MIC-01 corrija la consigna de temperatura del aire (cascada sobre TIC-01, entre 90 y 150 °C) y que "
         "las bandas sigan al caudal del dosificador para mantener la capa en 30 mm. Sintonía de partida: 0,8 K por "
         "punto de humedad y 45 min de tiempo integral, sin integrar mientras la consigna está limitada por la rampa o "
         "por los topes."),
        ("Humedad del guano fresco", "opcional · ajuste anticipado",
         "Un sensor de humedad sobre la cinta de alimentación permite adelantar la corrección: 1,25 K por punto de humedad, "
         f"aplicados 40 min después. Ante un cambio de 72 a 76 % el pico baja de {num(mp['max'])} a {num(mf['max'])} % "
         f"y no llega a saltar la alarma; a cambio, antes de que llegue el guano húmedo el producto sale un rato al "
         f"{num(mf['min'])} %."),
        ("Guías de las bandas", "7.2.5",
         "Cambiar las guías de UHMW-PE de los pisos 2 y 3 por PTFE (uso continuo hasta 260 °C) o por guías de acero "
         "inoxidable con patín de PTFE."),
        ("Sello de los bordes", "bandas · cámara",
         "Asegurar un sello entre los bordes de las bandas y las paredes (faldón de goma o chapa). Cada 5 % del aire que "
         f"sube por la rendija sin tocar el guano pide unos {num(T05 - T15)} K más de aire y unas {num(extra05)} t más "
         "de cáscara por año."),
        ("Escape y ciclón", "4.1.3 · 23.4",
         f"Aislar el ducto Ø800 y el ciclón y prever purga de condensado. Corregir el 4.1.3: al 15 % el escape sale a "
         f"unos {num(a['T_exh'])} °C casi saturado."),
        ("Recirculación", "CD-03 · plano 18",
         "Con el aire ajustado al 15 % la recirculación casi no ahorra y en verano gasta más: dejar la CD-03 cerrada, "
         "o regularla por la humedad relativa de la cámara de mezcla (cerrar sobre 90 %). La regla de 45 g/kg cae justo "
         "en el punto de trabajo y haría abrir y cerrar la compuerta."),
        ("Higienización y enfriamiento", "TT-05 · descarga",
         f"Tolva aislada de retención de 1 h a la salida (≈ {num(prod / 500, 1)} m³) con el TT-05 adentro, y después "
         f"enfriar el producto a menos de 40 °C antes del acopio: unos {num(q_enfr)} kW, con unos {num(round(aire_enfr, -2))} "
         "m³/h de aire de la nave."),
        ("Capacidad", "12.1",
         f"A 135 °C el mismo equipo seca {num(round(cap135, -1))} kg/h: las 16 t de dos turnos entran en unas "
         f"{num(16000 / cap135, 1)} h de marcha. Hay que llevar la cinta de alimentación a unos {num(3.9 * cap135 / 1000, 1)} cm/s."),
        ("Módulo piloto", "cap. 28",
         "Usarlo para medir el tamaño de grumo que deja el esparcidor, la curva de secado, la humedad del escape y "
         "cuánto aire pasa por los bordes, y ajustar con eso el modelo antes de construir el SC-4."),
    ]
    cambios_html = "\n".join(
        f'<div class="cambio"><span class="tag">{t}</span><h3>{n}</h3><p>{p}</p></div>' for n, t, p in cambios)

    cin = VA["cinetica"]
    bal = VA["balances"]
    em = max(abs(b_["err_masa"]) for b_ in bal)
    ee = max(abs(b_["err_energia"]) for b_ in bal)
    metodo = [
        "El secador se resuelve en régimen. El guano avanza con la banda y el aire lo atraviesa de abajo hacia arriba. "
        "Cada piso se divide en posiciones a lo largo de la banda y en capas en el espesor; en cada capa se calcula el "
        "intercambio de calor y de agua entre el aire y los grumos (correlación de Wakao y Kaguei para lechos), la "
        "difusión del agua dentro del grumo con una difusividad que depende de la temperatura y de la humedad, la "
        "isoterma de equilibrio (GAB) y el calor de sorción.",
        "Entre pisos el guano se mezcla. El aire pasa en serie por los pisos 3, 2 y 1, pierde calor por las paredes y se "
        "reparte a lo largo de cada banda según la pérdida de carga del lecho (Ergun). Un 5 % esquiva cada banda y se "
        "mezcla antes del piso siguiente; aparte se estudia el aire que sube por los bordes de los tres pisos sin tocar "
        "ninguno. El circuito de aire (generador, recirculación del plano 18 con su regla, plenum) se itera hasta que "
        f"cierran los balances: masa al {num(100 * em, 3)} % y energía al {num(100 * ee, 3)} % del calor del generador. "
        "Si al mezclar dos corrientes el aire queda sobresaturado, el exceso se cuenta como niebla.",
        f"La difusividad se ajustó a 9 ensayos de estufa de Ghaly y MacDonald (2012) y a los de Liška y Kic (2011). El "
        f"ajuste sigue el tiempo de secado con un error típico de {num(100 * cin['rms_log_tiempo'])} % y la velocidad "
        f"inicial con {num(100 * cin['rms_log_vel0'])} %, pero son los mismos ensayos del ajuste, no una prueba "
        f"independiente, y la velocidad inicial a 70 °C sale más baja que la medida "
        f"({num(cin['liska_vel0_70']['modelo'], 2)} contra 0,85-1,00 kg/kg·h). Otra combinación de parámetros con el "
        "mismo error cambia la temperatura necesaria en menos de 1 K. La malla (120 × 8) difiere de una de 320 × 20 en "
        "menos de 0,1 punto de humedad.",
        "La simulación en el tiempo divide cada piso en 96 celdas que avanzan con la banda y agrega el sensor MT-01 "
        "(retardo de 2 min), el PLC cada 30 s y el generador, que sigue a su consigna con 5 min de constante de tiempo. "
        "El lazo de bandas del informe se simuló sin el ajuste anticipado por TT-04, porque con él fue peor (las pruebas "
        "están en resultados/sintonia_pruebas.json).",
        "Límites: el tamaño de grumo (10 mm) y el aire que no toca el guano son supuestos; el lecho tiene pocos grumos "
        "de espesor y el modelo lo trata como continuo, así que la temperatura de la capa de arriba depende de en cuántas "
        "capas se lo divida; no hay ensayos de guano de Crespo; la humedad de equilibrio a más de 100 °C sale de "
        "extrapolar la isoterma; el generador se representa por su rendimiento (75 %).",
    ]
    metodo_html = "".join(f"<p>{p}</p>" for p in metodo)
    datos = [
        ("Guano", "1.000 kg/h al 72 % · 15 % a la salida", "tabla 6"),
        ("Aire", "26.600 kg/h a 135 °C", "6.4"),
        ("Recirculación", "CD-03 al 25 %; cierra si el escape pasa de 45 g/kg", "plano 18"),
        ("Bandas", "3 × 2,0 × 12 m · 0,37 m/min · capa 30 mm", "6.6, 12.1"),
        ("Cámara", "13,0 × 2,6 × 3,0 m · panel 80 mm · U 0,5 W/m²·K", "7.1.2, 19.2"),
        ("Generador", "cáscara 13,5 MJ/kg · rendimiento 75 %", "cap. 15"),
        ("Densidad del lecho", "800 kg/m³ húmedo → 500 kg/m³ al 15 %", "tabla 3"),
        ("Ambiente", "18 °C y 60 % (mes a mes: Paraná Aero)", "tabla 6"),
        ("Grumo", "10 mm de diámetro equivalente", "supuesto"),
        ("Aire sin contacto", "5 % esquiva cada banda; por los bordes, 0 (se estudia de 5 a 20 %)", "supuesto"),
        ("Difusividad", "5,2·10⁻⁹ m²/s a 60 °C y X = 0,5 · b = 3,4 · Ea 27 kJ/mol", "ajustada"),
        ("Isoterma", "GAB, monocapa 5,8 % b.s. a 25 °C", "Bernhart 2007"),
    ]
    datos_html = "<tbody>" + "".join(
        f'<tr><td>{a_}</td><td class="v">{b_}</td><td>{c_}</td></tr>' for a_, b_, c_ in datos) + "</tbody>"
    fuentes = [
        "Informe final del proyecto, Rev. E (24/10/2026), capítulos 4, 6, 7, 12 a 15, 19, 23 y 26, y planos 18 y 22.",
        'Ghaly, A. E. y MacDonald, K. N. (2012). Kinetics of thin layer drying of poultry manure. <i>American Journal '
        'of Biochemistry and Biotechnology</i> 8(2): 128-142. '
        '<a href="https://thescipub.com/abstract/ajbbsp.2012.128.142">thescipub.com</a>',
        'Liška, R. y Kic, P. (2011). Characteristics of drying process of poultry manure at various temperatures. '
        '<i>Scientia Agriculturae Bohemica</i> 42(2): 79-86. <a href="https://sab.czu.cz/dl/44498?lang=en">sab.czu.cz</a>',
        'Bernhart, M. (2007). <i>Characterization of Poultry Litter for Storage and Process Design</i>. Tesis, Auburn '
        'University. <a href="https://etd.auburn.edu/handle/10415/851">etd.auburn.edu</a>',
        'Reglamento (UE) 142/2011, anexo XI, capítulo I, sección 2: estiércol procesado a 70 °C durante 60 min. '
        '<a href="https://www.legislation.gov.uk/eur/2011/142/annex/XI/adopted">legislation.gov.uk</a>',
        'Ensinger, ficha de PE1000 (UHMW-PE): 80 °C en uso continuo, 130 °C a corto plazo, fusión 135 °C. '
        '<a href="https://www.ensingerplastics.com/-/media/ensinger/files/document-teaser-files/uk-documents/datasheet-pe1000-en.ashx">ensingerplastics.com</a>; '
        'APSO, PE-UHMW: fusión 130 °C. <a href="https://www.apsoparts.com/media/downloads/asset//std.lang.all/1_/en/PE-UHMW_Reg_026-01_EN.pdf">apsoparts.com</a>',
        'Ensinger, TECAFLON PTFE natural: uso continuo hasta 260 °C. '
        '<a href="https://ensingerplastics.com/en-gb/shapes/tecaflon-ptfe-natural">ensingerplastics.com</a>',
        'Clima de Paraná Aero, normales 1991-2020 (temperaturas de NOAA, humedad de NASA POWER). '
        '<a href="https://www.climate-zone.com/climate/ar/parana/">climate-zone.com</a>',
        "Wakao, N. y Kaguei, S. (1982). <i>Heat and Mass Transfer in Packed Beds</i>. Gordon and Breach.",
        "Ergun, S. (1952). Fluid flow through packed columns. <i>Chemical Engineering Progress</i> 48(2): 89-94.",
        "ASHRAE Handbook — Fundamentals, capítulo de psicrometría (presión de vapor de Hyland y Wexler).",
    ]
    fuentes_html = "\n".join(f"<li>{x}</li>" for x in fuentes)
    return hallazgos_html, cambios_html, metodo_html, datos_html, fuentes_html


NODO = r"""
const M = require(process.argv[2]), D = require(process.argv[3]);
const cfg = Object.assign({}, D.defecto, { nx: 40, nz: 5, nbis: 30, tol: 0.02, maxit: 80, acelerar: true, capas: true });
const r = M.resolver(D, cfg, null);
const plano = (o) => JSON.parse(JSON.stringify(o, (k, v) => (ArrayBuffer.isView(v) ? Array.from(v, (x) => Number(x.toPrecision(7))) : v)));
process.stdout.write(JSON.stringify({ r: plano(r) }));
"""


def inicial():
    ruta = os.path.join(AQUI, "_inicial.js")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(NODO)
    out = subprocess.run(["node", ruta, os.path.join(AQUI, "modelo.js"), os.path.join(AQUI, "datos.js")],
                         capture_output=True, text=True, check=True).stdout
    os.remove(ruta)
    return out


def main():
    with open(os.path.join(AQUI, "plantilla.html"), encoding="utf-8") as f:
        html = f.read()
    with open(os.path.join(AQUI, "modelo.js"), encoding="utf-8") as f:
        modelo = f.read()
    with open(os.path.join(AQUI, "datos.js"), encoding="utf-8") as f:
        datos = f.read()
    with open(os.path.join(AQUI, "vendor", "three.min.js"), encoding="utf-8") as f:
        three = f.read()
    with open(os.path.join(AQUI, "vendor", "OrbitControls.min.js"), encoding="utf-8") as f:
        orbit = f.read()
    with open(os.path.join(AQUI, "vista3d.js"), encoding="utf-8") as f:
        vista3d = f.read()
    h, c, m, d, fu = textos()
    html = (html.replace("/*__LIB3D__*/", three).replace("/*__ORBITA__*/", orbit).replace("/*__VISTA3D__*/", vista3d)
            .replace("/*__MODELO__*/", modelo).replace("/*__DATOS__*/", datos)
            .replace("/*__INICIAL__*/null", inicial())
            .replace("<!--__HALLAZGOS__-->", h).replace("<!--__CAMBIOS__-->", c)
            .replace("<!--__METODO__-->", m).replace("<!--__DATOS_TABLA__-->", d).replace("<!--__FUENTES__-->", fu))
    for marca in ("__LIB3D__", "__ORBITA__", "__VISTA3D__", "__MODELO__", "__DATOS__", "__INICIAL__",
                  "__HALLAZGOS__", "__CAMBIOS__", "__METODO__", "__DATOS_TABLA__", "__FUENTES__"):
        assert ("/*" + marca + "*/") not in html and ("<!--" + marca + "-->") not in html, f"quedó el marcador {marca}"
    with open(os.path.join(RAIZ, "simulador.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print("simulador.html:", round(len(html) / 1024), "kB")


if __name__ == "__main__":
    main()
