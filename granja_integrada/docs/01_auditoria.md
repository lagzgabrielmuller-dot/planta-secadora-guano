# Fases 1 y 2 — Auditoría del proyecto y recuperación de diseños

Granja avícola integrada con planta central de secado de guano · Crespo, Entre Ríos · 19/11/2026

Este documento revisa lo que ya existe, separa lo que se reutiliza de lo que se elimina y deja anotado lo que falta
antes de rediseñar. Nada de lo revisado se modificó: el proyecto anterior queda tal cual y todo lo nuevo está en
`granja_integrada/`.

**Tipos de dato** (se usan en todo el proyecto nuevo):

| Letra | Significado |
|---|---|
| R | Del proyecto de la secadora (Rev. F, 11/11/2026): diseño calculado, no medido |
| S | Del TP San Jorge (relevado en el establecimiento o en la imagen satelital) |
| V | Verificado con una fuente externa citada |
| P | Preliminar: propuesta de este rediseño, con su criterio; a confirmar con el fabricante o en obra |
| H | Hipótesis: no hay dato publicado ni relevado |

## 1. Qué se revisó

| Fuente | Contenido usado |
|---|---|
| Repositorio `planta-secadora-guano`, Rev. F | Datos de la planta (`fuente/datos/layout_planta.json`), modelo CadQuery del secador SC-4 (84 piezas), visor de la planta con los agregados D1–D24, E1–E10, F1–F2, láminas P01–P24 y SC-01–SC-06, cálculos eléctricos (TGF y TG2), memoria y estudio térmico |
| Análisis económico (17/11/2026) | Variante sin biogás: cargas eléctricas, potencia contratada y balance de guano |
| TP San Jorge, versión 1 (robot pórtico) y versión 2 (transelevador) | Galpones, depósito, cintas de huevos, armado y guardado de palets, tableros y PLC; informes en Claude Docs y modelos 3D |

## 2. Planta secadora Rev. F: lo que se conserva

| Elemento | Datos de base | Tipo |
|---|---|---|
| Nave de proceso | 33 × 18 m, pórticos cada 5,5 m (7 ejes), columnas IPN 300, cabriadas de tubo, correas C 120, zócalo de H° de 0,6 m, chapa trapezoidal; alero +7,00 m, cumbrera +8,35 m | R |
| Secador SC-4 | Cinta de malla de 3 pisos, cámara de 13,0 × 2,6 × 3,4 m, bandas AISI 304 de 2.000 mm, tambores Ø300/Ø250 × 2.100, UCF 212, UCT 210, motorreductores 0,75 kW 1:300 con cadena ASA 60 (M5–M7), paneles sándwich de 80 mm, 6 puertas de inspección | R |
| Capacidad | 1.000 kg/h de guano al 72 % → 329,4 kg/h al 15 %; máximo 1.440 kg/h con aire a 135 °C | R |
| Generador de aire caliente | Hogar de cáscara de arroz e intercambiador de 114 tubos en el anexo Norte (8 × 6,5 m); ventiladores de impulsión M1–M2 (15 kW), combustión M4 (4 kW), extractor M3 (22 kW) | R |
| Tratamiento de gases | Ciclón Ø1,8 m, lavador Ø2,2 m (bomba M14), extractor y chimenea Ø0,8 × 10 m; ducto de agotado aislado (Rev. F) | R |
| Alimentación del secador | Tolva de 3,1 m³ con vibrador M15 y cinta con bordes y tacos de 500 mm a 30° (M8, 0,75 kW) hasta la cabeza del secador | R |
| Descarga | Esparcidor M9, sinfín M10, elevador de cangilones M11 prolongado a 8,1 m, tolva de retención de 1 h a ≥ 70 °C y enfriador con ventilador M40 (Rev. F) | R |
| Cáscara y cenizas | Silo Ø3,6 m, sinfín M12, sinfín de cenizas M13 | R |
| Control del secado | TIC-01 (aire de 90 a 150 °C), lazo de humedad MIC-01 en cascada, compuerta CD-03 por humedad relativa, detector de llama BE-01, TT-06, PS-01 | R |
| Tableros | TGF de 15 circuitos (M1–M15) y TG2 (consumos Rev. D–F), puesta a tierra con anillo y 8 jabalinas, pararrayos | R |
| Envasado y expedición | Zaranda M18, ensacadora M19–M21, bolsas chicas M22, depósito de embolsado (E4–E7) | R |
| Seguridad | Barandas, pasarelas, paradas de emergencia, protecciones de transmisiones, incendio (D1–D23) | R |

## 3. Sistema de biogás: qué se elimina

Antes de sacar cada elemento se revisó qué otros sistemas dependían de él.

| Elemento (código Rev. D) | Acción | Dependencia encontrada y cómo se resuelve |
|---|---|---|
| E8.1 Recepción y mezcla para biogás | Se elimina | — |
| E8.2 Biodigestores BD-1 y BD-2 (Ø6,5 × 5,0 m, agitadores M28 y M29) | Se eliminan | El 2,52 t/día de guano que iba al biodigestor vuelve a la secadora, que con eso trabaja a su capacidad de diseño |
| E8.3 Tanque de digestato | Se elimina | — |
| E8.4 Sala de cogeneración (motogenerador G1 de 25 kWe, desulfurador, soplante M33, M34) | Se elimina | El balance eléctrico deja de restar los 25 kWe del G1: la demanda se cubre toda desde la red (ver Fase 7) |
| E8.5 Antorcha de 25 m³/h | Se elimina | — |
| E8.6 Línea de biogás al hogar y quemador piloto de biogás (D12) | Se elimina | El hogar necesita un encendido: se reemplaza por un **piloto a GLP** con electroválvula, transformador de encendido y el mismo detector de llama BE-01 (P) |
| Tablero TS-BIO y circuito Q23 del TG2 (22,85 kW) | Se eliminan | Se recalcula el TG2 sin esas cargas |
| Malla de puesta a tierra PAT-9 y PAT-10 de la zona de biogás | Se elimina | El anillo de la nave y las 8 jabalinas no cambian |
| Zona clasificada ATEX, cartelería y calle de servicio R7 | Se eliminan | Desaparece la única zona clasificada de la planta |
| Destino de lixiviados (D20, E2, F2): «todo el líquido orgánico va al biodigestor» | Se cambia | Pasa a un **tanque de efluentes** cerrado de 15 m³ con retiro periódico por camión atmosférico (P) |
| Lámina P20 y cálculos de biogás de la memoria | No se usan | Quedan en el proyecto anterior como antecedente |

**Resultado:** no queda ningún componente de biogás en el proyecto nuevo, y lo único que cambia en sistemas que sí se
conservan es el encendido del hogar y el destino de los efluentes.

## 4. Galpones automáticos y palets de huevos (TP San Jorge)

### 4.1 Lo que existe

| Dato | Valor | Tipo |
|---|---|---|
| Galpones de postura | 2, de 100 m × 6 m, paralelos, con los ejes a unos 31 m | S |
| Depósito | 21,8 × 16,0 m por fuera (21,4 × 15,6 m por dentro), junto a la cabecera oeste del galpón norte; alto libre adoptado 5,0 m | S |
| Producción | 180 cajones por día de 12 maples de 30 huevos (64.800 huevos), 7,2 palets de 25 cajones (≈ 625 kg) | S |
| Llegada de los huevos | Una cinta desde cada galpón hasta su estación de armado (E1 y E2) dentro del depósito | S (el medio es un supuesto del TP) |
| Guardado y carga (versión 2) | Transelevador de 1.000 kg sobre riel de 17 m, 24 lugares al fondo, muelle en U con 2 mesas elevadoras a 1,25 m, transpaleta eléctrica | S |
| Control (versión 2) | PLC SIMATIC S7-1200 (CPU 1214C), periferia ET 200SP, pantallas KTP700 y KTP400, 3 variadores G120C, relé de seguridad Flexi Soft, escáneres SICK | S |

### 4.2 Lo que nunca se diseñó

El TP estudió el transporte de palets dentro del depósito. El interior de los galpones (jaulas, alimentación, agua,
ventilación, recolección de huevos y manejo del guano) no se definió en ninguna de las dos versiones: en los modelos 3D
los galpones son volúmenes de fondo.

**Criterio adoptado:** se reutiliza todo lo que existe (medidas exteriores de 100 × 6 m, separación de 31 m entre
ejes, depósito con cintas de huevos, estaciones E1 y E2, transelevador, muelle y su control) y el interior se diseña
ahora como propuesta preliminar (P), con equipos comerciales de referencia y respetando el ancho de 6 m.

### 4.3 Discrepancia que hay que confirmar

Con 2 filas de jaulas de 4 pisos en 6 m de ancho entran unas 14.800 gallinas por galpón (Fase 3). La producción que
informa San Jorge (64.800 huevos por día en 2 galpones) supone más de 70.000 gallinas, que no entran en dos galpones de
6 m con jaulas de 4 pisos. Puede ser que el ancho medido en la imagen satelital esté corto o que las jaulas tengan
más pisos. **Hay que confirmar con el establecimiento el ancho real, el sistema de jaulas y la cantidad de gallinas.**
El rediseño usa 4 galpones de ≈ 14.800 gallinas (≈ 59.000 en total), que producen el guano de diseño de la secadora
(8 t/día).

## 5. Datos que faltan

| Dato | Para qué hace falta | Qué se usa mientras tanto |
|---|---|---|
| Gallinas por galpón y sistema de jaulas de San Jorge | Caudal de guano y huevos | 14.784 por galpón (P) |
| Ancho real de los galpones | Distribución interior | 6 m (S) |
| Tasa de postura media | Huevos por día | 85 % (H) |
| Densidad del guano fresco | Volumen de la tolva pulmón | 950 kg/m³ (H, a medir) |
| Distancias mínimas de la Res. SENASA 1699/2019 | Implantación | Separaciones conservadoras (Fase 3), a verificar con el texto vigente |
| Potencias de las cintas de guano | Instalación eléctrica | Cálculo preliminar por fórmula (Fase 4) |
| Estudio de suelos | Fundaciones | Bases tipo, solo representativas |

## 6. Qué se reutiliza en el rediseño

| De dónde | Qué | Dónde va |
|---|---|---|
| Planta Rev. F | Nave, secador SC-4, generador, gases, alimentación, descarga, cáscara, envasado, seguridad | Planta central (copiada y ampliada) |
| Planta Rev. F | Datos geométricos (`layout_planta.json`) y resultados eléctricos | `datos/base/` (copias) |
| Láminas | Formato A3 IRAM y rótulo de la escuela | Planos `GI-xx` |
| San Jorge | Galpón de 100 × 6 m y par de galpones a 31 m | 4 galpones (2 pares) |
| San Jorge | Depósito con cintas de huevos, estaciones E1–E2, transelevador y muelle | Un depósito por par de galpones |
| San Jorge | Arquitectura de control S7 con periferia ET 200SP y pantallas | Base de la automatización de la planta |

## Fuentes consultadas en esta fase

- Big Dutchman (s. f.). *Residue treatment* y *SuperTripleDeck* (fichas técnicas): cinta de guano y cinta transversal;
  jaula de 610 × 483 mm con 6 aves (490 cm² por ave). https://www.bigdutchmanusa.com/wp-content/uploads/2023/01/Residue-Treatment_Eng.pdf
- Proveedores de cintas de guano de polipropileno (listados comerciales): banda de PP de 1,0–1,2 mm, 10–12 m/min,
  accionamiento de 1–1,5 kW hasta 100 m. Valores a confirmar con el fabricante que se elija.
- Big Dutchman (s. f.). *Requirements for ventilation systems in aviary houses*: velocidad de túnel de 1,0 a 2,5 m/s.
  https://www.bigdutchman.com/en/news-stories/news/requirements-for-ventilation-systems-in-aviary-houses/
- OMAFRA (2024). *Tunnel ventilation in livestock barns*. https://www.ontario.ca/files/2024-04/omafra-tunnel%20ventilation-in-livestock-barns-evaporative-cooling-24-007-en-2024-04-09.pdf
- SENASA. Resolución 1699/2019 (requisitos de bioseguridad de granjas avícolas comerciales).
  https://argentina.gob.ar/sites/default/files/res._senasa_1699-2019.pdf
