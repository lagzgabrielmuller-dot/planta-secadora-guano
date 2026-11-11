# Registro de cambios

## Rev. F · 11/11/2026: auditoría integral, estudio térmico y repositorio nuevo

**Estudio térmico del secador SC-4** ([`docs/REV_F.md`](docs/REV_F.md)):
- lazo de humedad MIC-01 en cascada sobre TIC-01 (90 a 150 °C) y MT-02 opcional;
- guías de PTFE en los pisos 2 y 3;
- faldones de sellado de bordes (pieza 4.21);
- escape aislado con purga de condensado;
- CD-03 por humedad relativa;
- tolva de retención de 1 h más enfriador con ventilador M40 en el TG2;
- capacidad de 1.440 kg/h a 135 °C;
- módulo piloto;
- apartado 6.7 nuevo del informe.

**Láminas revisadas:** P02 E, P06 E, P18 E, P22 F, P23 G, SC-01 a SC-06 B.

**Correcciones de coherencia:**
- alimentación por cinta M8 (Rev. D) en todo el informe y TGF de 66,9 kW;
- curva de secado y bulbo húmedo;
- recirculación del plano 18;
- planta de biogás vecina como proyecto;
- apellido **Hofstetter** en las 30 láminas, el informe, la memoria, el manual y la portada.

**Cálculos:**
- `calc_tg2` aumenta la sección de verdad y verifica la caída de tensión total y el I2 de la acometida;
- ménsula con kc = 0,59;
- limpieza sin cambiar resultados (fatiga y presupuesto).

**Presupuesto:** cáscara de 419 t/año por turno (modelo térmico), ítems B17 y B18 y precios con fuente o
«a cotizar». Inversión de USD 999.841; dos turnos: TIR 17,7 %, repago 5,2 años.

**Repositorio nuevo `planta-secadora-guano`:**
- portada única generada (`portada.py`);
- `visor.html`;
- `fuente/regenerar.py`;
- pruebas pytest y Playwright, y CI;
- documentación y `AUDITORIA_FINAL.md`;
- video público sin música;
- sin respaldos ni temporales.

**3D:**
- visor del secador con oclusión ambiental (GTAO), antialiasing multimuestra, materiales físicos y rótulos que no se
  pisan; vistas del informe, de las láminas SC y del manual sacadas de nuevo con este visor;
- visor de la planta con la tolva de retención, el enfriador, el elevador prolongado y el escape aislado.

**Video:** cinco tramos dibujados de nuevo sobre el original de máxima calidad (créditos con Hofstetter, nave de
33 × 18 m, secador de 9.538 kg, 117,0 kW instalados). Versiones públicas sin audio y en rango de color de TV, como el
original.

**Lámina SC-01:** la tabla de datos pasa a 72 % → 15 % de humedad y aire a ≈ 100 °C (máx. 135), como el resto del
proyecto.

**Publicación:** GitHub Pages desde `main`. La CI ya no instala paquetes del sistema para la prueba del sitio y cada
trabajo tiene un tiempo máximo.

## Rev. E · 23-24/10/2026: entrega final

- Verificación a fatiga (Shigley-Budynas): eje motriz con asientos rectificados (n = 1,59), eje de reenvío Ø60/Ø50 y
  límite de par del variador (706 N·m). También anclajes químicos, cadena, rodamientos y ensayo de Wöhler.
- Secador SC-4 como entregable aparte (CadQuery, visor, manual de armado, láminas SC-01 a SC-06).
- Presupuesto con la Cooperativa La Agrícola Regional (LAR) y evaluación económica en 4 escenarios.
- P23 Rev. F: acometida de 4 × 35 mm² y Q25/Q26 con potencia. P24: punto de funcionamiento de los AirTEC.
- Informe definitivo en Word y video de presentación.

## Rev. D · 09-10/2026: ampliación

- Ítems de seguridad y mantenimiento D1-D24 y ampliación E1-E10: lavado de vehículos, biofiltro, zaranda,
  ensacadora, envasadora, depósito, biogás con cogeneración G1 de 25 kWe, Sector Este y ventilación de la nave.
- Tablero TG2 nuevo y visor 3D ampliado.
- Alimentación por cinta con tacos en lugar del sinfín (plano 12, Rev. B).

## Rev. C · 09/2026

- Informe original del proyecto: secador de cinta de 3 pisos, generador a cáscara de arroz, tratamiento de gases y
  visor 3D.
