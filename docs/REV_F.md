# Revisión F (11/11/2026): cambios del estudio térmico del secador SC-4

La Rev. F incorpora al proyecto los cambios que propuso el estudio **«Simulación térmica del secador SC-4»**, en
[`simulacion_termica/`](../simulacion_termica/). Las propuestas estaban escritas en dos lugares: el README del
estudio («Cambios que propone el estudio») y el simulador («Cambios que proponemos para la Rev. F», nueve tarjetas).
Al aplicarlos aparecieron además inconsistencias que venían de revisiones anteriores; también se corrigieron y
figuran al final.

Todos los números salen de los resultados guardados del estudio (`simulacion_termica/resultados/*.json`), de los
cálculos del proyecto (`fuente/calculos/`) o de los planos vigentes. Donde no hay precio público el presupuesto lo
marca «a cotizar»: fuente `REVF`.

## Los nueve cambios propuestos

| # | Cambio | Dónde quedó |
|---|---|---|
| 1 | **Lazo de humedad en cascada.** MIC-01 corrige la consigna de TIC-01 entre 90 y 150 °C, con PI de 0,8 K por punto y Ti de 45 min, sin integrar mientras la consigna está limitada. Las bandas siguen al caudal de la cinta de alimentación (capa de 30 mm). | Informe 13.3 (operación) y 14.5.2 (lazos) con la figura 12 del estudio; plano 06 (señal MIC-01 → TIC-01, lazo FY-01, tabla de lazos) |
| 2 | **Ajuste anticipado opcional.** MT-02 mide la humedad del guano fresco sobre la cinta de alimentación y suma 1,25 K por punto, aplicados 40 min después. | Informe 14.5.1 (tabla de instrumentos) y 14.5.2; visor (D5) |
| 3 | **Guías de PTFE** en los pisos 2 y 3. El aire entra a 102-135 °C y el UHMW-PE admite unos 80 °C; el piso 1 queda con UHMW-PE. | Informe 7.2.1, 7.2.5, 7.6, 9 (materiales) y 24 (mantenimiento); planos 02 y 22; modelo CadQuery (pieza 4.7, material y masa); láminas SC; manual (paso 6); presupuesto |
| 4 | **Sello de los bordes de las bandas.** Faldón de chapa AISI 304 de 1,5 mm con labio de silicona apto 200 °C. Cada 5 % de aire que sube por la rendija pide unos 4 K más y unas 18 t de cáscara por año. | Informe 7.2.6 (nuevo), 7.6, 9 y 24; modelo CadQuery (pieza nueva 4.21, sin interferencias); planos 02 y 22; láminas SC; manual; presupuesto |
| 5 | **Escape casi saturado.** Al 15 % el aire sale a 33-37 °C con una humedad relativa del 99 %. Se aíslan el ducto Ø800 (14 m) y el ciclón y se agrega una purga de condensado con sifón. | Informe 4.1.3 (corregido), 6.4, 23.4 y 24; plano 06 (corrientes); visor; presupuesto (B18) |
| 6 | **Recirculación CD-03.** Con el aire ajustado ahorra solo 1,2 % de cáscara y en enero gasta 1,1 % más. Queda normalmente cerrada y abre solo con la humedad relativa de la cámara de mezcla por debajo del 90 %. La regla anterior (Y > 45 g/kg) caía justo en el punto de trabajo. | Plano 18 (tabla de compuertas, balance con y sin recirculación, rótulos); informe 6.5 y 6.7; visor (D7) |
| 7 | **Higienización y enfriamiento.** Tolva de retención aislada de 0,7 m³ con el TT-05 adentro (≥ 70 °C durante 60 min, Reglamento UE 142/2011) y un enfriador a contracorriente de 900 m³/h con ventilador M40 de 0,55 kW, que lleva el producto por debajo de 40 °C. | Informe 7.4, 14.5.1 y 24; plano 06 (corriente 16); tablero TG2 (M40 en Q21, plano 23 Rev. G); presupuesto (B17); visor (F1). La tolva va a la salida del elevador, que se prolonga de 6,3 a 8,1 m: entra bajo la cumbrera de 8,35 m, entre los pórticos de x = 22 y 27,5 m, y se mantiene la pendiente de unos 36° de la bajada a la zaranda |
| 8 | **Capacidad.** A 135 °C el mismo equipo seca unos 1.440 kg/h: las 16 t de dos turnos entran en 11,1 h. La cinta de alimentación tiene que llegar a unos 5,6 cm/s (variador al 56 %). | Informe 6.7, 7.3.2 y 12.1 |
| 9 | **Módulo piloto.** Que mida el grumo, la curva de secado, la humedad del escape y el aire que pasa por los bordes, para ajustar el modelo antes de construir el SC-4. | Informe 28 (conclusiones) |

Además se agregó el apartado **6.7 «Verificación con el modelo térmico del secador»**, con una tabla de punto de
diseño contra punto de trabajo y dos láminas del estudio. El método de diseño de 6.3 a 6.5 (135 °C de entrada y
65 °C de salida) queda como dimensionamiento del lado seguro: 135 °C pasa a ser la temperatura máxima, no la de
trabajo.

## Punto de trabajo de la Rev. F

Datos para 1.000 kg/h de guano al 72 %, ambiente a 18 °C y 60 %, CD-03 cerrada (`resultados/recirculacion.json`):

| Magnitud | Antes (método de diseño) | Rev. F (modelo) |
|---|---|---|
| Aire a la entrada del secador | 135 °C | 99,5 °C (consigna de 90 a 150 °C) |
| Aire de escape | 65 °C, 33,2 g/kg | 33,3 °C, 33,0 g/kg, HR 99 % |
| Calor del generador | 882 kW | 617 kW (882 kW es el máximo) |
| Cáscara de arroz | 314 kg/h | 219 kg/h; 419 t/año por turno |
| Producto a la salida del piso 3 | 60 °C | 74 °C, que va a la tolva de retención y al enfriador |
| Consumo específico | 4,7 MJ/kg de agua | 3,3 MJ/kg de agua |

## Efecto en los números del proyecto (los recalculan los programas)

| Magnitud | Rev. E | Rev. F |
|---|---|---|
| TG2: potencia instalada / demanda | 49,54 kW / 24,7 kW (44,2 A) | 50,09 kW / 25,1 kW (44,8 A) |
| Balance sin G1 / margen sobre 100 kW | 91,2 kW / 8,8 % | 91,6 kW / 8,4 % |
| Secador SC-4: piezas / masa CAD | 65 / 9.157 kg | 68 / 9.538 kg |
| Inversión total | USD 985.204 | USD 999.841 |
| Escenario C (2 turnos): TIR / repago | 17,2 % / 5,3 años | 17,7 % / 5,2 años |
| Escenario A (1 turno): TIR / repago | 4,0 % / 11,1 años | 4,4 % / 10,8 años |
| Ménsula soldada, n | 18,2 | 17,3 (corrección de kc = 0,59, ver la auditoría) |

## Inconsistencias encontradas al aplicar la Rev. F (también corregidas)

1. **Alimentación del secador.** El texto del informe venía de la Rev. C y seguía describiendo un sinfín
   dosificador de 1,5 kW y una tolva de 2,0 m³. Desde la Rev. D (plano 12, Rev. B) la alimentación es una cinta con
   bordes y tacos: M8 de 0,75 kW, tolva de 3,1 m³. Se corrigieron:
   - el informe: apartados 5.4, 7.3.1, 7.3.2, 7.3.3, 13.2 y anexo B;
   - la tabla de motores 14.2, que ahora es la del plano 05;
   - la potencia instalada del TGF: 66,9 kW (no 67,7) y 109 A de demanda;
   - la portada y el video;
   - la verificación a fatiga del sinfín, que ya no existía: sale del informe y de la lámina SC de fatiga;
   - el nombre de la pieza 4.19c del modelo.
2. **Curva de secado (4.1.2).** El texto decía que el aire de 135 °C entraba al piso 1. El aire va en
   contracorriente: entra por debajo del piso 3. La temperatura de bulbo húmedo era de 34 a 42 °C, no de 45 a 60 °C.
3. **Planta de biogás vecina.** El informe la llamaba «existente». Es un proyecto: el predio se presentó el
   24/09/2026 (Elonce) y en esa fecha estaba en etapa de estudios.

## Láminas revisadas (fila nueva en la tabla de revisiones de cada una)

P02 Rev. E · P06 Rev. E · P18 Rev. E · P22 Rev. F · P23 Rev. G · SC-01 a SC-06 Rev. B. La corrección del apellido
«Hofstetter» en el rótulo de todas las láminas es editorial y no cambia la letra de revisión.

## Pendientes que dependen de terceros

- Cotizar el PTFE, el perfil de silicona, el ventilador centrífugo del enfriador y los sifones. El presupuesto usa
  estimaciones marcadas «a cotizar».
- Confirmar con el módulo piloto que el producto llega a 70 °C en la tolva de retención: el margen es de 4 a 7 K.
- MT-02 es opcional: decidir si se instala, según cuánto varíe la humedad del guano que llega.
- Ingeniería de detalle: redibujar los planos 08 y 19 con la prolongación del elevador, la tolva de retención y el enfriador. Hoy figuran en el informe, en el diagrama 06 y en el visor 3D (F1).
