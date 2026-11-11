# Simulación térmica del secador SC-4

Modelo físico del secador de cinta de tres pisos del proyecto final "Secadora de guano" (E.P.N.M. y S. N.º 35, Crespo). Usa los datos de la última revisión: informe final Rev. E (24/10/2026) y planos 18 y 22. Sirve para ver cómo se seca el guano dentro del secador, cuánta cáscara se quema, qué pasa con el aire de escape y cómo responde el lazo de humedad, y para defender el diseño con números.

El mismo modelo corre en el navegador: abrí `simulador.html` (doble clic, no hace falta internet). Muestra el SC-4 en 3D, con el frente abierto, el guano de cada piso coloreado por su humedad y el aire subiendo coloreado por su temperatura. También está publicado como página interactiva.

## Qué hay en la carpeta

| Archivo o carpeta | Qué es |
|---|---|
| `secado/` | El paquete del modelo: `parametros.py` (todos los datos con su fuente), `psicrometria.py`, `guano.py` (isoterma, difusividad, contracción), `nucleo.py` (una capa del lecho y un piso, compilado con numba), `secador.py` (secador completo en régimen), `dinamica.py` (simulación en el tiempo con el lazo MIC-01), `clima.py` (clima del turno en Crespo), `graficos.py` (estilo de las figuras) |
| `validar.py` | Compara la cinética con ensayos publicados, verifica el cierre de los balances y la malla, y compara con la memoria |
| `ajustar_cinetica.py` | Ajuste de la difusividad a los ensayos de estufa (unos 15 minutos) |
| `escenarios.py` | Los cálculos del estudio (perfiles, ventana de operación, capacidad, recirculación, sensibilidad, clima, control, aire por los bordes, higiene) |
| `correr_todo.py` | Corre los escenarios que falten, guarda `resultados/*.json` y dibuja `figuras/*.png` |
| `figuras.py` | Las láminas 01 a 12 y 14 (la 13 la dibuja `validar.py`) |
| `figuras/` | Láminas PNG listas para el informe o la presentación |
| `resultados/` | Resultados en JSON (se pueden abrir con cualquier editor) |
| `simulador.html` | El simulador armado (usa las láminas de `figuras/`) |
| `web/` | Fuentes del simulador: `modelo.js` (el mismo modelo en JavaScript), `vista3d.js` (la vista 3D), `plantilla.html`, `construir.py` (arma `simulador.html`), `probar_js.js` (compara JavaScript con Python) y `vendor/` (three.js r128, licencia MIT) |

## Cómo correrlo

Hace falta Python 3.10 o más nuevo:

```
pip install -r requirements.txt
python validar.py            # 1 minuto: valida y dibuja la lámina 13
python correr_todo.py        # usa los resultados guardados y redibuja las figuras
python correr_todo.py --rehacer      # recalcula todo: unos 35 minutos en una PC de 2 núcleos
python correr_todo.py --solo clima   # recalcula un solo grupo
```

La primera vez numba compila el núcleo (un minuto). Para probar un caso propio:

```python
from secado import secador as s
r = s.resolver(s.config(T_aire=110, alimentacion=1200, humedad_entrada=0.74))
print(s.resumen(r))
r, estado = s.buscar_temperatura(s.config())   # temperatura de aire que deja 15 %
r = s.con_regla_cd03(s.resolver, s.config())  # con la regla de la CD-03 del plano 18
```

Todas las opciones están en `secador.config()`: caudal y humedad del guano, temperatura y caudal de aire, recirculación, clima, velocidad de bandas, aire en contracorriente o en paralelo, mezcla o inversión entre pisos, aire que sube por los bordes (`bypass_pila=0.1`) y cualquier parámetro del guano (`prm=dict(d0=0.02)` cambia el grumo a 20 mm).

Para el simulador (opcional, con Node.js): `python exportar_web.py`, `node web/probar_js.js` (debe decir que JavaScript coincide con Python) y `python web/construir.py`.

## El modelo

El secador se resuelve en régimen. El guano avanza con la banda y el aire caliente lo atraviesa de abajo hacia arriba; cada piso se divide en 120 posiciones a lo largo de la banda y en 8 capas de igual masa en el espesor.

En cada capa:

- **Transferencia externa** de calor y de vapor entre el aire y los grumos, con la correlación de Wakao y Kaguei para lechos: Nu = 2 + 1,1·Re^0,6·Pr^(1/3) (y lo mismo para Sh con Sc). La eficiencia de la capa es 1 − e^(−NTU).
- **Resistencia interna** del grumo (esfera) con fuerza impulsora lineal: dX/dt = −15·D/R²·(X − Xs). La humedad de la superficie Xs sale de igualar el agua que llega desde adentro con la que se lleva el aire; mientras hay agua libre la superficie está saturada (velocidad constante) y después aparece el período decreciente.
- **Difusividad efectiva**: D = D_ref·e^(b·(X − 0,5))·e^(−Ea/R·(1/T − 1/333 K)), con D_ref = 5,2·10⁻⁹ m²/s, b = 3,4 y Ea = 27 kJ/mol. La dependencia con X representa que la pasta húmeda mueve el agua por capilaridad.
- **Equilibrio** con la isoterma GAB (monocapa de 5,8 % b.s. a 25 °C) y **calor de sorción** que crece cuando el guano está casi seco (al secar y, si pasa, al volver a tomar agua).
- **Balance de energía** de la capa con el calor latente del agua a la temperatura del grumo. Si el guano está más frío que el punto de rocío del aire, condensa (pasa en la entrada del piso 1).
- **Contracción** del grumo y del lecho: la densidad aparente pasa de 800 kg/m³ al 72 % a 500 kg/m³ al 15 % (tabla 3 del informe).
- **Pérdida de carga** de Ergun; el aire se reparte a lo largo de la banda para que todos los caminos tengan la misma ΔP (las zonas secas y finas reciben más aire). Un 5 % del aire esquiva cada banda sin tocar el producto y se mezcla antes del piso siguiente.

En el secador completo, el aire pasa en serie por los pisos 3, 2 y 1 (contracorriente), se mezcla entre pisos y pierde calor por los paneles de cada zona. Aparte, una opción manda una fracción del aire del plenum directo a la campana, por las rendijas entre las bandas y las paredes, sin tocar ningún piso (si las rendijas quedan alineadas, ese aire no se mezcla en el camino). A la salida, el 25 % vuelve a la cámara de mezcla (plano 18) y el generador lo calienta hasta la consigna de TT-01; la función `con_regla_cd03` aplica la regla del plano 18, que cierra la CD-03 si el escape pasa de 45 g/kg. Entre pisos el guano cae y se mezcla. El circuito se itera hasta que cierran los balances. Si al mezclar dos corrientes casi saturadas el aire queda sobresaturado, el exceso se cuenta como niebla.

La simulación en el tiempo (`dinamica.py`) divide cada piso en 96 celdas que avanzan con la banda, con el aire cuasi estacionario, el sensor de humedad MT-01 en el sinfín de descarga (2 min de retardo y 1 min de constante de tiempo), el PLC cada 30 s y el generador siguiendo su consigna con 5 min de constante de tiempo. El lazo no integra mientras su salida está recortada por los topes o por la rampa.

## Datos

| Dato | Valor | Fuente |
|---|---|---|
| Guano | 1.000 kg/h al 72 %, sale al 15 % | informe, tabla 6 |
| Aire | 26.600 kg/h a 135 °C | 6.4 |
| Recirculación | CD-03 al 25 %; cierra si el escape pasa de 45 g/kg | plano 18 |
| Bandas | 3 × 2,0 × 12 m, 0,37 m/min (0,2 a 0,9), capa de 30 mm (20 a 40) | 6.6, 7.2, 12.1 |
| Cámara | 13,0 × 2,6 m, 3,0 m de alto; pisos a +0,93, +1,78 y +2,63 m | 7.1, plano 22 |
| Paneles | lana de roca de 80 mm, U = 0,5 W/m²·K (cap. 19.2 calcula 6,1 kW de pérdidas) | 7.1.2, 19.2 |
| Generador | cáscara de 13,5 MJ/kg, rendimiento 75 %, 3 kW de pérdida del ducto | cap. 15, 19.2 |
| Guano | cp del sólido 1,5 kJ/kg·K; densidad aparente 800 → 500 kg/m³ | tabla 3 |
| Ambiente | 18 °C y 60 %; mes a mes, turno de 8 h en Paraná Aero | tabla 6, climate-zone.com |
| Grumo | 10 mm de diámetro equivalente, densidad 1.000 kg/m³ | supuesto |
| Aire sin contacto | 5 % esquiva cada banda; por los bordes, 0 (se estudia de 5 a 20 %) | supuesto |
| Cinética | D_ref, b y Ea ajustados a 11 ensayos de estufa | Ghaly y MacDonald 2012, Liška y Kic 2011 |
| Isoterma | GAB de cama de pollo | Bernhart 2007 |
| Vista 3D | medidas del visor 3D del proyecto (Rev. D, "Solo secadora") | `visor.html` del proyecto |

## Validación

- **Cinética** (lámina 13): con los mismos parámetros sigue los 9 ensayos de Ghaly y MacDonald (40 a 60 °C, capas de 1 a 3 cm) con un error típico de 23 % en el tiempo de secado y de 10 % en la velocidad de las primeras 2 h, y los puntos de Liška y Kic a 70 y 110 °C. Son los ensayos con los que se ajustó, así que muestra la calidad del ajuste y no es una prueba independiente. La velocidad inicial a 70 °C sale más baja que la medida (0,60 contra 0,85-1,00 kg/kg·h). Los ensayos no separan bien D_ref de b: `ajustar_cinetica.py` encuentra D_ref = 1,0·10⁻⁸ m²/s, b = 5,4 y Ea = 22 kJ/mol con el mismo error (0,738 contra 0,741), y con esos valores la temperatura para el 15 % pasa de 102,2 a 101,5 °C.
- **Balances**: masa al 0,002 % y energía al 0,01 % del calor del generador en siete casos distintos. El destino del calor (evaporar, calentar el producto, sorción, paredes y escape) suma el calor del generador con menos de 0,1 kW de diferencia.
- **Malla**: 120 × 8 difiere de 320 × 20 en menos de 0,1 punto de humedad. La temperatura de la capa de arriba sí depende de la malla (ver Resultados, punto 6).
- **Memoria**: sin recirculación y a 135 °C el modelo pide 885 kW y 315 kg/h de cáscara; la memoria calcula 882 kW y 314 kg/h. Las pérdidas por paredes dan 6,9 kW (el capítulo 19.2 calcula 6,1 kW).
- **JavaScript**: el simulador da lo mismo que Python (diferencias de 10⁻¹¹ en la misma malla, también con aire por los bordes).

## Resultados principales

| | Memoria (Rev. E) | Modelo, diseño 135 °C | Modelo, aire a 102 °C | Modelo, 135 °C con 1.440 kg/h |
|---|---|---|---|---|
| Humedad de salida | 15 % | menos de 2 % | 15,0 % | 15,0 % |
| Guano a la descarga | 60 °C | 135 °C | 77 °C | 92 °C |
| Aire de escape | 65 °C, 33 g/kg | 61 °C, 44 g/kg, HR 32 % | 37 °C, 41 g/kg, HR 99 % | 38 °C, 44 g/kg, saturado con niebla |
| Recirculación | 25 % | 25 % | 25 % | cerrada por su regla |
| Calor del generador | 882 kW | 814 kW | 610 kW | 885 kW |
| Cáscara | 314 kg/h (2,3 t/día con recirculación) | 289 kg/h | 217 kg/h | 315 kg/h |
| Calor que va al guano | 53 % (54 % con la cuenta de la memoria) | 62 % | 77 % | 76 % |
| Consumo específico | 4,7 MJ/kg de agua | 4,1 | 3,3 | 3,3 |
| Más de 55 °C (promedio / capa de arriba) | > 1 h | 73 / 65 min | 9 / 0 min | 10 / 0 min |

1. **A 135 °C el SC-4 seca de más** (láminas 01 y 14). El guano está seco al final del piso 2 y sale a 135 °C. La memoria supone que el aire sale a 65 °C; en un lecho atravesado, mientras el guano tiene agua el aire sale casi saturado y aprovecha mucho más calor. Al 15 % alcanza con aire a 102 °C, o 106 a 111 °C si entre 5 y 10 % del aire sube por los bordes sin tocar el guano.
2. **Sobra capacidad** (láminas 05 y 06): a 135 °C seca unos 1.440 kg/h al 15 % (el escape pasa de 45 g/kg y la CD-03 se cierra) y cada grado de aire suma unos 12 kg/h; con 10 % de aire por los bordes, 1.300 kg/h. La temperatura necesaria va de 93 °C (guano al 65 %) a 110 °C (78 %).
3. **La humedad se controla con el aire, no con las bandas** (láminas 03, 04 y 12). Cerca del 15 % la humedad cambia 1,8 puntos por grado de aire y casi nada con la velocidad. Si el guano pasa de 72 a 76 %, el húmedo tarda 1,6 h en llegar a la salida y ningún lazo que mida ahí evita el primer pico (28 %). Después, el lazo MIC-01 del informe (bandas, simulado sin el ajuste por TT-04 porque con él fue peor) hace oscilar el producto entre 10 y 43 %; con el MIC-01 corrigiendo la consigna de TIC-01 vuelve al 15 % (±1 punto) 1,7 h después de que llega el guano húmedo. Midiendo la humedad del guano fresco el pico baja a 25 % y queda 12 min sobre 20 %, menos que los 15 min de la alarma; a cambio, antes de que llegue el guano húmedo el producto sale un rato al 11 %. Las pruebas de sintonía están en `resultados/sintonia_pruebas.json`.
4. **El escape sale casi saturado** (láminas 07 y 09): al 15 % condensa en el ducto Ø800 y en el ciclón (con 10 % de aire por los bordes sale a 45 °C y 65 %, y condensa más adelante). Al 15 %, la CD-03 al 25 % ahorra 1,2 % de cáscara a 18 °C y 1,9 % en julio con la cámara de mezcla saturada, y en enero gasta 1,1 % más; solo rinde a 135 °C (8 %). La regla de los 45 g/kg cae justo en el punto de trabajo: en verano cerraría la compuerta y, cerrada, el escape baja de 45 g/kg y la volvería a abrir.
5. **Las guías de UHMW-PE quedan en el aire que entra a cada piso** (lámina 10): bajo el piso 3, entre 102 y 135 °C (el material aguanta 80 °C en uso continuo).
6. **Higienización** (láminas 02 y 11): al 15 % el guano pasa en promedio 9 min sobre 55 °C y los grumos de arriba del piso 3 llegan como mucho a 41-59 °C según el espesor de capa que se tome (capas de un grumo dan 59 °C). El 15 % es un promedio: arriba salen grumos con 27-37 % de humedad y abajo con 1,5-2,8 %. El TT-05 mide la mezcla (77 °C) y no lo ve.
7. **El grumo y el sellado de los bordes pesan más que la cinética** (lámina 08): duplicar o dividir por dos la difusividad mueve la temperatura necesaria 1 K; los caudales, ±8 K por ±10 %; grumos de 20 mm, +12 K; 10 % de aire por los bordes, +9 K. Con grumos de 30 mm el diseño a 135 °C ya no llega al 15 %.
8. **Cáscara por año** (lámina 09): 419 t ajustando el aire contra 591 t a 135 °C con la CD-03 siguiendo su regla (−29 %, unos USD 4.300 por año a USD 25/t). Con 10 % de aire por los bordes el ahorro baja a 133 t.

## Cambios que propone el estudio

Todos quedaron incorporados al proyecto en la **Rev. F (11/11/2026)**: informe (apartados 4.1.3, 6.7, 7.2.5, 7.2.6, 7.3.2, 7.4, 12.1, 13 y 14.5, 23.4, 24 y conclusiones), planos 02, 06, 18 y 22, láminas SC del secador, modelo 3D (guías de PTFE y faldones de sellado), presupuesto (cáscara, ítems nuevos) y tablero TG2 (ventilador M40 del enfriador). El detalle está en `docs/REV_F.md` del repositorio.


- MIC-01 en cascada sobre la consigna de TIC-01 (90 a 150 °C, sintonía de partida 0,8 K por punto y 45 min, sin integrar mientras la consigna está limitada por la rampa o los topes) y bandas atadas al caudal del dosificador (capa de 30 mm). Opcional: medir la humedad del guano fresco para un ajuste anticipado (1,25 K por punto, 40 min después).
- Guías de PTFE (hasta 260 °C) en los pisos 2 y 3.
- Sello entre los bordes de las bandas y las paredes: cada 5 % de aire que sube por la rendija pide unos 4 K más de aire y unas 18 t más de cáscara por año.
- Aislar el ducto de escape y el ciclón, con purga de condensado; corregir el apartado 4.1.3.
- Con el aire ajustado al 15 %, dejar la CD-03 cerrada o regularla por la humedad relativa de la cámara de mezcla (cerrar sobre 90 %), no por Y > 45 g/kg.
- Tolva aislada de retención de 1 h a la salida (≈ 0,7 m³) con el TT-05 adentro: el guano entra a 77 °C, apenas 7 K sobre los 70 °C que pide la Unión Europea, así que hay que comprobarlo. Después, enfriar el producto a menos de 40 °C antes del acopio (unos 6 kW).
- Usar el módulo piloto para medir el grumo, la curva de secado, la humedad del escape y cuánto aire pasa por los bordes, y ajustar el modelo.

## Límites del modelo

- El tamaño de grumo (10 mm) y el aire que no toca el guano son supuestos: conviene medirlos.
- El lecho tiene pocos grumos de espesor y el modelo lo trata como un medio continuo; la temperatura de la capa de arriba depende de en cuántas capas se lo divida (la lámina 11 usa 8).
- La cinética viene de guano de otros lugares secado en estufa, no de guano de Crespo en un secador de cinta.
- La isoterma es de cama de pollo; a más de 100 °C y aire seco la humedad de equilibrio sale de extrapolarla (por eso a 135 °C se informa "menos de 2 %").
- El generador se representa por su rendimiento (75 %) y la consigna se cumple con un primer orden de 5 min.
- No se modela la emisión de amoníaco ni la pérdida de nitrógeno.

## Fuentes

- Informe final del proyecto, Rev. E (24/10/2026), capítulos 4, 6, 7, 12 a 15, 19, 23 y 26, y planos 18 y 22.
- Visor 3D del proyecto, Rev. D (vista "Solo secadora"), para las medidas de la vista 3D.
- Ghaly, A. E. y MacDonald, K. N. (2012). Kinetics of thin layer drying of poultry manure. *American Journal of Biochemistry and Biotechnology* 8(2): 128-142. https://thescipub.com/abstract/ajbbsp.2012.128.142
- Liška, R. y Kic, P. (2011). Characteristics of drying process of poultry manure at various temperatures. *Scientia Agriculturae Bohemica* 42(2): 79-86. https://sab.czu.cz/dl/44498?lang=en
- Bernhart, M. (2007). *Characterization of Poultry Litter for Storage and Process Design*. Tesis, Auburn University. https://etd.auburn.edu/handle/10415/851
- Reglamento (UE) 142/2011, anexo XI, capítulo I, sección 2. https://www.legislation.gov.uk/eur/2011/142/annex/XI/adopted
- Ensinger, ficha de PE1000 (UHMW-PE). https://www.ensingerplastics.com/-/media/ensinger/files/document-teaser-files/uk-documents/datasheet-pe1000-en.ashx
- APSO, PE-UHMW. https://www.apsoparts.com/media/downloads/asset//std.lang.all/1_/en/PE-UHMW_Reg_026-01_EN.pdf
- Ensinger, TECAFLON PTFE natural. https://ensingerplastics.com/en-gb/shapes/tecaflon-ptfe-natural
- Clima de Paraná Aero, normales 1991-2020. https://www.climate-zone.com/climate/ar/parana/
- Wakao, N. y Kaguei, S. (1982). *Heat and Mass Transfer in Packed Beds*. Gordon and Breach.
- three.js r128 (licencia MIT), para la vista 3D. https://threejs.org
