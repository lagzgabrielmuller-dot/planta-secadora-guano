# Auditoría final del proyecto «Secadora de guano 8 t/día»

**Fecha:** 11/11/2026 · **Alcance:** toda la entrega de `revD_final/` del repositorio anterior `secadora`, el estudio
de simulación térmica y la página publicada aparte · **Resultado:** repositorio nuevo e independiente
`planta-secadora-guano`, con la **Rev. F**

## 1. Resumen

Revisé el proyecto completo: cálculos, planos, modelo 3D, informe, memoria, presupuesto, visores, portada y video.
Los cálculos de base estaban bien hechos y bien documentados: las constantes de Shigley, la IEC 60364 y el balance
de masa coinciden con las fuentes. Los problemas más serios estaban en la **coherencia entre documentos**, más que en
las cuentas:

- El informe arrastraba texto de la Rev. C que contradecía los planos de la Rev. D.
- Las propuestas del estudio térmico no estaban aplicadas.
- El apellido de un integrante estaba mal escrito en 38 archivos.
- La página pública tenía números escritos a mano y descargas por una carpeta privada de Drive.

Todo quedó corregido. Las propuestas del estudio quedaron incorporadas como **Rev. F** ([`docs/REV_F.md`](docs/REV_F.md)).
Pasan las **202 pruebas automáticas** de datos y archivos y los **24 controles del sitio** (sección 6).

## 2. Método y qué se leyó

| Cómo | Archivos |
|---|---|
| **Leídos completos** | `calculos/calculos_memoria.py`, `calculos/fatiga.py`, `calculos/presupuesto.py`, `visor/build_visor.py`, `portal/portada.py` (nuevo), `CLAUDE.md`, `fuente/README.md`, `video/README.md`, el README del estudio térmico y las 9 tarjetas de la Rev. F |
| **Leídos por secciones** (las partes que tocan datos o la Rev. F) | `informe/texto_revC.md` (cap. 4.1, 6, 7, 8.2-8.3, 9.1-9.5, 13.4, 14.2 y anexo B), `informe/informe_final.py`, `planos/P02, P05, P06, P12, P18, P22, P23`, `secadora/modelo_secador.py`, `secadora/planos_sc.py`, `secadora/visor/app.js`, `visor/revD_modulo.js`, `video/escena/guion.js`, la plantilla de la portada |
| **Revisados con herramientas** (no leídos línea por línea) | Todo el Python: ruff, con reglas de errores reales (E9, F, B). Todo el JavaScript: `node --check`. Búsquedas en todos los archivos de texto y binarios (DXF, PDF, DOCX, XLSX, ZIP, STEP) de nombres, números, secretos y correos. Pruebas cruzadas de números entre los cálculos, la memoria, el informe, las láminas y la portada |
| **Datos externos** | Búsquedas web para cada dato verificable públicamente (sección 4) |

No se leyeron línea por línea el visor compilado `visor/base_revC.html` (código minificado de la Rev. C, 5.065
líneas) ni las 24 láminas P01 a P24 completas. De las láminas se controlaron los DXF (validez, textos, integrantes) y
el aspecto de las que cambiaron.

## 3. Problemas encontrados y corrección

| # | Área | Severidad | Problema | Corrección |
|---|---|---|---|---|
| 1 | Datos | Alta | Apellido de un integrante sin la «r» final en lugar de **Hofstetter** en 7 fuentes y 38 salidas: rótulo de las 30 láminas, informe, memoria y manual (Word y PDF), portada, video | Corregido en las fuentes y regenerado todo. Una prueba lo controla en todos los archivos |
| 2 | Coherencia | Alta | El informe (texto de la Rev. C) describía un **sinfín dosificador de 1,5 kW** y una tolva de 2,0 m³. Desde la Rev. D es una cinta con tacos M8 de 0,75 kW y una tolva de 3,1 m³ (plano 12). Por eso el TGF figuraba con 67,7 kW en el informe y con 66,9 kW en los planos 05 y 22, y la fatiga verificaba un sinfín que ya no existe | Informe 5.4, 7.3, 13.2, 14.1, 14.2 y anexo B alineados con los planos. Tabla de motores tomada del plano 05. Fila del sinfín fuera de la fatiga y de la lámina SC |
| 3 | Ingeniería | Alta | Propuestas del estudio térmico sin aplicar: 135 °C seca de más, la humedad se controlaba con las bandas, guías de UHMW-PE con aire a 102-135 °C (aguantan 80 °C), escape casi saturado sin aislar, regla de la CD-03 que oscila, higienización no lograda (9 min sobre 55 °C) | **Rev. F**: 9 cambios en informe, planos, modelo 3D, presupuesto, tablero y visor ([`docs/REV_F.md`](docs/REV_F.md)) |
| 4 | Datos | Media | Informe 4.1.3: «el escape está lejos de la saturación, sin riesgo de condensación». Es falso según el modelo térmico: sale casi saturado | Apartado corregido; aislación y purga de condensado (23.4) |
| 5 | Datos | Media | Informe 4.1.2: el aire de 135 °C entraba «al primer piso», pero el flujo es en contracorriente y entra por el piso 3. Bulbo húmedo de «45 a 60 °C»; el real es de 34 a 42 °C | Corregido con la psicrometría del estudio |
| 6 | Datos | Media | Plano 18: la recirculación «ahorra 10 % de cáscara» (282 contra 314 kg/h). Con el aire ajustado ahorra 1,2 %, y en verano gasta 1,1 % más | Tabla del plano 18 rehecha con el modelo; CD-03 regulada por la humedad relativa de la cámara de mezcla |
| 7 | Datos | Media | La planta de biogás vecina figuraba como «existente». Es un proyecto: el predio se presentó el 24/09/2026 | Informe 16.3 y 28 corregidos |
| 8 | Código | Media | `calc_tg2`: si un circuito no verificaba, agregaba la nota «sección aumentada» pero no aumentaba la sección | Ahora sube a la sección comercial siguiente hasta verificar. Además controla la caída de tensión total desde el pilar (AEA 90364-7-771: 3 % iluminación, 5 % fuerza) e I2 ≤ 1,45·Iz en la acometida. Las dos cosas tienen prueba |
| 9 | Cálculo | Baja | Ménsula soldada: Sse = 0,67·Se. Shigley (ec. 6-26, ejemplo 9-6) usa kc = 0,59 a corte | n pasa de 18,2 a 17,3 (sigue verificando de sobra) |
| 10 | Código | Baja | `fatiga.py`: `· Kfs / Kfs` sin efecto en la tensión de atasco; variable `fe` sin uso | Limpiado sin cambiar resultados (la prueba de JSON al día lo confirma) |
| 11 | Código | Baja | `presupuesto.py`: el monto «sin biogás» se calculaba dos veces | Una sola vez |
| 12 | Código | Baja | 46 avisos de ruff: importaciones y variables sin uso, variables de bucle sin uso. Uno era un falso positivo que habría roto P01 al limpiarlo | Corregidos con regeneración de las láminas. Ruff da 0 avisos |
| 13 | Entorno | Media | P04, P08, P18 y P24 fallaban en Linux sin Arial (PIL «cannot open resource») | `lamina_secadora.fuente_pil()`: usa Liberation Sans, de iguales medidas |
| 14 | Dependencias | Media | El `requirements.txt` del repositorio anterior era de otro programa (openai, anthropic). `scipy` figuraba como requisito y no se usa | `requirements.txt` del proyecto y `tests/requirements.txt` |
| 15 | Arquitectura | Media | Dos portadas: `entrega.html` y una página publicada aparte, con unos 30 números escritos a mano y descargas por una carpeta **privada** de Drive (inaccesible para el público y con su identificador expuesto) | Una sola portada (`index.html`) que arma `portada.py` con los números de los cálculos y descargas directas. `entrega.html` redirige |
| 16 | Legal | Alta | Video con música no libre de derechos («Addiction») en lugares públicos | Versión pública sin música. La original queda en el repositorio privado anterior |
| 17 | Seguridad | Alta | El historial del repositorio anterior tiene claves de API reales en un `.env` (commit `e30da75`) | El repositorio nuevo no tiene secretos (escaneado). **Revocar esas claves** y mantener privado el repositorio anterior |
| 18 | UX | Baja | Plano 02: textos que se salían de las celdas (tabla DATOS) | Abreviados |
| 19 | Datos | Baja | La portada daba la TIR y el repago solo en dos turnos | Ahora da los dos escenarios (dos turnos: 17,7 % / 5,2 años; un turno: 4,4 % / 10,8 años) |
| 20 | Visor | Baja | El panel «Datos de diseño» del visor de la planta (Rev. C) decía 135 → 65 °C y 314 kg/h | Reemplazos controlados en `build_visor.py` |

## 4. Datos verificados y no verificables

| Dato del proyecto | Valor | Verificación | Estado |
|---|---|---|---|
| Dólar BNA vendedor 23/10/2026 | $ 1.550 | Dólar Histórico, cierre del 23/10/2026: compra $ 1.500 y venta $ 1.550 | ✔ Verificado |
| PCI de la cáscara de arroz / cenizas | 13,5 MJ/kg (10 % hum.) / 16-20 % | Literatura (BioResources, OSTI y otras): 13-16 MJ/kg en base seca y cenizas de 15 a 24 % | ✔ Dentro del rango |
| Biogás de guano | 184 m³/día con 526 kg SV/día (0,35 m³/kg SV) | Literatura: 0,25 a 0,4 m³/kg SV para cama y guano, hasta 0,6 | ✔ Dentro del rango |
| PCI del biogás | 20,8 MJ/m³ (58 % de CH4) | 0,58 × 35,8 MJ/m³ del metano | ✔ Cuenta verificada |
| Aceros SAE 1045 y 1020 HR, factores de Marin, kb, ke, Neuber, f | Ver `fatiga.py` | Shigley-Budynas 8.ª ed.: tablas A-20, 6-2 y 6-5; ec. 6-8, 6-20, 6-35 y fig. 6-18 | ✔ Coinciden |
| Electrodo E60xx / Kfs del filete | 427 MPa / 2,7 | Shigley, tablas 9-3 y 9-5 | ✔ |
| Iz de cables (métodos E y D1), factores, k = 115 | Ver `calculos_memoria.py` | IEC 60364-5-52 (base de la AEA 90364-7-771) | ✔ |
| Balance de masa | 8 t al 72 % → 2,635 t al 15 % | Recalculado | ✔ (prueba automática) |
| Generador | 882 kW, 314 kg/h | 3.175 MJ/h ÷ (13,5 × 0,75); el modelo térmico da 885 kW y 315 kg/h | ✔ |
| Higienización | 70 °C durante 60 min | Reglamento (UE) 142/2011, anexo XI (citado en el estudio) | ✔ |
| UHMW-PE y PTFE | 80 °C y 260 °C de uso continuo | Fichas de Ensinger y APSO (citadas en el estudio) | ✔ |
| Lana de roca de 50 mm | $ 24.250/m² | Rollo Acuflex de 3 m² a $ 72.760 (Mercado Libre, 11/2026) | ✔ |
| Planta de biogás vecina «Ñande Zukunft» | Proyecto con 24 biodigestores | Elonce (24/09/2026), iProfesional y Econojournal (proyecto Dosbio con financiamiento alemán) | ✔ como proyecto; «Bioenergía Virch S.A.» y «32,76 ha» **no verificados** |
| Acceso por la RN 12 km 40,6 | — | No hay fuente pública con ese mojón: un proyecto de ley de 2021 ubica el Parque Industrial sobre la RN 12, a unos 36,8 km de Paraná | ✖ No verificable |
| Tarifa T3 de la LAR, potencia contratada, conexión de G1 | Estimaciones | Sin publicación de la cooperativa | ✖ A confirmar con la LAR (ya figuraba) |
| Precios de PTFE, perfil de silicona y ventilador centrífugo | Estimaciones | Sin precio público en Argentina | ✖ Marcados «a cotizar» (fuente `REVF`) |
| Resto de los precios del presupuesto | ± 25 % | Referencias citadas en `presupuesto.py` (10/2026), no revisadas una por una | ⚠ Vigencia a confirmar |

## 5. Cambios de arquitectura y mejoras

- **Repositorio nuevo e independiente**, con estructura limpia. Sin el respaldo de la Rev. D, el video con música,
  temporales, dependencias ni credenciales. El repositorio anterior no se modificó.
- **Portada única generada** (`fuente/portal/portada.py`) a partir de una plantilla. Toma los números de los JSON,
  calcula los tamaños y las páginas de cada archivo, arma las miniaturas de las 30 láminas, arma los ZIP de los DXF
  con fecha fija y controla que existan los 105 enlaces.
- **`fuente/regenerar.py`**: rehace toda la entrega en orden (12 pasos) en Windows o Linux.
- **El visor de la planta pasa a `visor.html`** y `index.html` es la portada. Se actualizaron todas las referencias:
  láminas P10, P13 a P24, informe, video y STEP.
- **Pruebas automáticas** (`tests/`) y **CI** (`.github/workflows/pruebas.yml`).
- **Modelo 3D:**
  - Secador SC-4: guías de PTFE y faldones de sellado (68 piezas, sin interferencias, controlado con CadQuery).
  - Visor del secador: oclusión ambiental GTAO, antialiasing multimuestra, materiales físicos con barniz en el
    acero pintado y botón «Calidad» (normal automática en celulares).
  - Visor de la planta: tolva de retención, enfriador, prolongación del elevador (verificada contra la cumbrera de
    8,35 m), escape aislado con purga y textos de la Rev. F.
- **Estudio térmico** incorporado al repositorio (`simulacion_termica/`), con el simulador marcando los cambios como
  incorporados.

## 6. Pruebas ejecutadas (resultados reales)

| Prueba | Herramienta | Resultado |
|---|---|---|
| Regenerar toda la entrega desde el entorno nuevo (venv con Python 3.12, `npm ci`, fuentes Liberation): CadQuery, 30 láminas, memoria, informe, manual, visores, renders y portada | `fuente/regenerar.py` | ✔ Sin errores; DXF con 0 errores de auditoría de ezdxf |
| Cálculos, datos cruzados entre documentos, archivos de la entrega, integrantes en DXF, PDF y DOCX, Rev. F | pytest (`tests/`) | ✔ **202 pasaron**, 0 fallaron |
| Lint | ruff (E9, F, B) en `fuente/` y `simulacion_termica/` | ✔ 0 avisos |
| Sintaxis JavaScript | `node --check` en todos los .js y .mjs | ✔ |
| Sitio por HTTP: enlaces (104), video (3:51), galería, páginas de equipos, visor ampliado, textos alternativos, redirección, visores 3D y simulador sin errores, celular (iPhone 13) sin desplazamiento horizontal | Playwright (`tests/e2e/probar_sitio.js`) | ✔ **24 de 24** |
| Interferencias de las piezas nuevas del SC-4 | CadQuery (`intersect().Volume()`) | ✔ Ninguna |
| Secretos y datos personales | Búsqueda de patrones de claves, correos, Drive y metadatos de DOCX, PDF y STEP | ✔ Nada que publicar por error |

## 7. Pendientes (no se pueden cerrar desde el proyecto)

- Materia y docente en las portadas del informe y de la memoria: siguen como `[COMPLETAR]`, resaltados.
- Cotizaciones formales: LAR (tarifa T3, potencia, paralelo de G1); PTFE, perfil de silicona y ventilador M40.
- Ingeniería de detalle de la Rev. F: redibujar los planos 08 y 19 con la prolongación del elevador, la tolva de
  retención y el enfriador. Hoy están en el informe, en el diagrama 06 (corriente 16) y en el visor.
- Módulo piloto: medir el grumo, la curva de secado, la humedad del escape y el aire por los bordes, y confirmar
  los 70 °C de la tolva (el margen es de 4 a 7 K).
- Ensayo de Wöhler del acero de los ejes y capítulo IX de González Arias (ya figuraban).
- **Video:** la versión pública no tiene música. Los créditos con «Hofstetter» y los números de la Rev. F (masa
  9.538 kg, 117,0 kW) están corregidos en el guion (`fuente/video/escena/guion.js`). Para volver a renderizar esos
  tramos hacen falta los datos del mapa satelital, que no se guardan en el repositorio. El estado final del video
  está en el README.
- Revocar las claves de API que quedaron en el historial del repositorio anterior.

## 8. Evaluación final

El proyecto quedó **coherente de punta a punta**:
- cada número que aparece en la memoria, el informe, los planos y la portada sale de los programas de cálculo;
- hay una prueba automática que falla si alguno queda viejo.

La Rev. F mejora el diseño con fundamento físico. El secador ahora trabaja a unos 100 °C en lugar de 135 °C, quema
29 % menos cáscara, higieniza con una tolva de retención, no condensa en el escape sin control y protege las guías.
Con eso, el escenario de dos turnos pasa a una TIR del 17,7 %.

Lo que sigue pendiente depende de terceros (cotizaciones, el docente, la LAR) o de la ingeniería de detalle, y quedó
escrito.
