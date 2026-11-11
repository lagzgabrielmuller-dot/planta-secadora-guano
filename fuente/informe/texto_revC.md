# 1. Resumen ejecutivo
El presente Proyecto Final desarrolla la ingeniería de una planta de secado de guano de gallina ponedora con capacidad de 8 toneladas por día de material húmedo, pensada para un establecimiento avícola de la zona de Crespo, Entre Ríos. El sistema propuesto es un secador continuo de cinta transportadora de tres pisos, alimentado con aire caliente producido por un generador a biomasa que quema cáscara de arroz, subproducto abundante en la provincia.
La planta transforma un residuo problemático —el guano fresco, con 72 % de humedad, fuerte olor, presencia de moscas y patógenos, y riesgo de contaminación de suelos y napas— en un fertilizante orgánico estable, con 15 % de humedad, apto para comercializar a granel. En un turno de 8 horas se procesan 8 t de guano y se obtienen 2,6 t de producto seco, evaporando 5,4 t de agua.
El proyecto incluye el balance de masa y energía, el dimensionamiento térmico y mecánico del secador, la selección de motores y elementos de transmisión, la ingeniería eléctrica y de control (tablero, unifilar, PLC), el generador de aire caliente, el tratamiento de gases, la distribución en planta, el análisis de seguridad e higiene, el estudio de impacto ambiental, el plan de mantenimiento y la evaluación económica. Se acompaña con el juego general de {{n_planos}} planos A3, el juego aparte del secador SC-4 (6 láminas), los modelos 3D de la planta y del secador (visores interactivos y archivos STEP), la memoria de cálculo y el presupuesto con compras en la Cooperativa La Agrícola Regional (LAR).
Tabla 1. Datos principales del proyecto
| Parámetro | Valor
| Capacidad de alimentación | 8 t/día de guano húmedo (1.000 kg/h, 8 h/día)
| Humedad de entrada / salida | 72 % / 15 % (base húmeda)
| Producción de guano seco | 329 kg/h – 2,6 t/día – 650 t/año
| Agua evaporada | 671 kg/h – 5,4 t/día
| Tipo de secador | Cinta transportadora, 3 pisos, 2,0 × 12 m, 72 m² de superficie
| Temperatura de aire | Hasta 135 °C a la entrada (≈ 100 °C para 1.000 kg/h al 15 %); escape a 33-37 °C, casi saturado
| Fuente de energía térmica | Cáscara de arroz, 314 kg/h, generador de 880 kW
| Potencia eléctrica instalada | 66,9 kW en el TGF (15 motores) + {{P_TG2}} kW en el TG2 (ampliación)
| Superficie cubierta de planta | 594 m² (nave de 33 × 18 m)
| Inversión estimada | USD {{inv_total}} (planta completa con ampliación) / USD {{inv_sin_biogas}} (sin biogás)
| Ubicación | Lote junto al Parque Industrial de Crespo (RN 12, km 40,6), Entre Ríos
# 2. Introducción y planteo de la problemática
## 2.1. Contexto: la avicultura en Crespo y Entre Ríos
Entre Ríos es la principal provincia avícola de la Argentina y Crespo es reconocida como la Capital Nacional de la Avicultura. En el departamento Paraná y alrededores se concentran cientos de granjas de gallinas ponedoras, muchas de ellas con más de 50.000 aves, además de una fuerte industria de pollos parrilleros. Esta actividad genera un volumen enorme de deyecciones que, históricamente, se ha manejado de forma precaria: acopio a cielo abierto, aplicación directa en campos cercanos o simplemente acumulación debajo de las jaulas.
Una gallina ponedora en jaula produce entre 120 y 150 gramos de guano fresco por día, con una humedad del orden del 70 al 75 %. Una granja de 60.000 aves genera, por lo tanto, alrededor de 8 toneladas diarias de guano húmedo: exactamente la escala adoptada en este proyecto.
## 2.2. El problema del guano fresco
El guano fresco de gallina tiene características que lo convierten en un residuo difícil de gestionar:
- Alta humedad (70–75 %): es pastoso, no se puede almacenar en pilas estables, no se puede ensacar ni transportar a distancia con eficiencia (se paga flete por agua).
- Emisión de amoníaco y olores: el nitrógeno ureico del guano se descompone rápidamente liberando NH₃ y compuestos sulfurados, que afectan la salud de las aves, de los operarios y de los vecinos.
- Proliferación de moscas y roedores: el guano húmedo es el medio ideal para el desarrollo de larvas de mosca doméstica, con las consiguientes denuncias de vecinos y riesgo sanitario.
- Patógenos: puede contener Salmonella, E. coli, coccidios y otros microorganismos que impiden su uso directo como fertilizante en cultivos hortícolas.
- Lixiviados: las lluvias lavan nitratos y fósforo hacia suelos y napas, contaminando el agua de la zona.
- Pérdida de valor: el nitrógeno que se volatiliza es fertilizante perdido; el guano seco y estabilizado tiene un valor comercial muy superior.
## 2.3. La oportunidad
El guano de gallina es, en base seca, uno de los abonos orgánicos más ricos: contiene alrededor del 3 % de nitrógeno, 2,8 % de fósforo (P₂O₅) y 2,2 % de potasio (K₂O), además de calcio y materia orgánica. Si se lo seca rápidamente hasta un 15 % de humedad, el proceso biológico se detiene, el producto se estabiliza, se elimina la mayor parte de los patógenos por efecto de la temperatura, se reduce el volumen a un tercio y se obtiene un producto que puede venderse a productores hortícolas, viveros y empresas de fertilizantes orgánicos.
Al mismo tiempo, Entre Ríos es la primera provincia arrocera del país. La cáscara de arroz —alrededor del 20 % del peso del grano— es un subproducto de bajo costo que los molinos deben disponer, con un poder calorífico de 13 a 14 MJ/kg. Usarla como combustible para el secado cierra un círculo: un residuo agrícola sirve para valorizar otro residuo agrícola.
[img: revC_02.png]
Figura 1. Composición típica del guano de ponedora en base seca (valores promedio de bibliografía).
## 2.4. Enfoque del proyecto
El grupo decidió abordar el problema desde la ingeniería electromecánica completa: no solamente el diseño del equipo secador, sino la planta entera como sistema, con su alimentación de energía, su instalación eléctrica, su control automático, su tratamiento de emisiones, su distribución en planta, su seguridad y su viabilidad económica. Este enfoque integral es el que se espera de un Técnico Electromecánico al insertarse en la industria.
# 3. Objetivos
## 3.1. Objetivo general
Diseñar una planta de secado de guano de gallina ponedora con capacidad de 8 t/día, basada en un secador de cinta transportadora con aire caliente generado por combustión de cáscara de arroz, que convierta el residuo en un fertilizante orgánico comercializable, minimizando el impacto ambiental y garantizando la seguridad de los operarios.
## 3.2. Objetivos específicos
- Realizar el balance de masa y energía del proceso de secado y determinar el consumo de aire caliente y de combustible.
- Dimensionar la cinta transportadora (superficie, número de pisos, velocidad, tiempo de residencia) y sus elementos mecánicos (tambores, ejes, rodamientos, transmisión).
- Seleccionar los motores eléctricos, sus protecciones, conductores y arrancadores, y diseñar el tablero general de fuerza y control.
- Diseñar el sistema de control automático (PLC, sensores, lazos de regulación, enclavamientos de seguridad).
- Dimensionar el generador de aire caliente a biomasa y su intercambiador de calor.
- Definir el sistema de tratamiento de gases (ciclón y lavador de gases) para el control de polvo, olores y amoníaco.
- Proponer la distribución en planta aplicando el método de Planeamiento Sistemático de la Distribución (SLP).
- Identificar los riesgos laborales y definir las medidas de seguridad e higiene según la Ley 19.587.
- Evaluar el impacto ambiental del proyecto y proponer medidas de mitigación.
- Elaborar el plan de mantenimiento preventivo y el análisis económico de la inversión.
- Confeccionar los planos de la planta, del equipo, del generador y de la instalación eléctrica.
# 4. Marco teórico
## 4.1. Fundamentos del secado
El secado es la operación unitaria por la cual se elimina agua (u otro líquido) de un sólido mediante evaporación, aportando calor y retirando el vapor formado. En el secado con aire caliente por convección, el aire cumple dos funciones a la vez: entrega el calor necesario para evaporar el agua y arrastra el vapor producido.
### 4.1.1. Formas de expresar la humedad
La humedad de un sólido puede expresarse en base húmeda (kg de agua por kg de material total) o en base seca (kg de agua por kg de sólido seco). En este trabajo se usa base húmeda, que es la habitual en la industria, salvo aclaración:
X_bh = m_agua / (m_agua + m_sólido)       X_bs = m_agua / m_sólido
La relación entre ambas es X_bs = X_bh / (1 − X_bh). El guano con 72 % de humedad base húmeda tiene 2,57 kg de agua por cada kg de sólido seco; a la salida, con 15 %, quedan 0,176 kg de agua por kg de sólido.
### 4.1.2. Curva de secado
Cuando un sólido húmedo se expone a aire caliente, su humedad disminuye siguiendo una curva característica con tres etapas: un breve período inicial de calentamiento; un período de velocidad constante, en el que se evapora el agua libre de la superficie y el sólido se mantiene a la temperatura de bulbo húmedo del aire (entre 34 y 42 °C en nuestro caso, según la temperatura y la humedad del aire); y un período de velocidad decreciente, en que el agua debe difundir desde el interior de las partículas y la velocidad de secado cae progresivamente. La humedad final se aproxima asintóticamente a la humedad de equilibrio con el aire.
[img: revC_03.png]
Figura 2. Curva de secado esperada del guano en el secador de cinta. El diseño prevé 97 minutos de residencia para alcanzar 15 %.
Esta forma de la curva es la que justifica el uso de tres pisos con el aire en contracorriente: el aire caliente entra por debajo del piso 3, donde el producto ya está casi seco y necesita temperatura para el período decreciente, y llega al piso 1, con el material más húmedo, ya enfriado y cargado de vapor, que todavía alcanza para evaporar el agua libre. Al caer de un piso al otro el producto se voltea y renueva la superficie expuesta.
### 4.1.3. Psicrometría del aire
La capacidad del aire para absorber vapor depende de su temperatura. La humedad absoluta Y (kg de vapor por kg de aire seco) del aire ambiente en Crespo, a 18 °C y 60 % de humedad relativa, es de unos 8 g/kg. A 65 °C el aire puede contener, saturado, alrededor de 200 g/kg. En un secador de lecho atravesado, sin embargo, el aire no sale a una temperatura fija: mientras el guano tiene agua libre, el aire que atraviesa la capa se enfría y se carga de vapor hasta quedar cerca de la saturación. El modelo térmico del secador (apartado 6.7) muestra que, con el aire ajustado para obtener 15 % de humedad, el escape sale a 33-37 °C (sin recirculación y con el 25 %, respectivamente) y con una humedad relativa del 99 %: está prácticamente saturado. Por eso el ducto de escape de Ø800 mm y el ciclón se aíslan y llevan purga de condensado (apartado 23.4).
### 4.1.4. Balance de energía
El calor que hay que aportar al proceso se compone del calor sensible para llevar el agua y el sólido de la temperatura ambiente a la temperatura de secado, más el calor latente de vaporización del agua evaporada, más las pérdidas por las paredes:
Q_útil = W · [c_pw · (T_p − T_a) + h_fg] + m_s · c_ps · (T_p − T_a) + m_wr · c_pw · (T_p − T_a)
donde W es el agua evaporada, m_s el sólido seco, m_wr el agua residual que queda en el producto, c_pw y c_ps los calores específicos del agua (4,18 kJ/kg·K) y del sólido (1,5 kJ/kg·K), T_p la temperatura del producto (60 °C), T_a la ambiente (18 °C) y h_fg el calor latente a la temperatura de evaporación (2.360 kJ/kg). El aire necesario resulta del balance sobre el aire:
m_aire = Q_secador / [c_pa · (T_aire,in − T_aire,out)]
## 4.2. Tipos de secadores para residuos pecuarios
Tabla 2. Comparación de tecnologías de secado aplicables al guano
| Tecnología | Principio | Ventajas | Desventajas
| Tambor rotativo | Cilindro giratorio con paletas; el material cae en cascada a través de aire caliente en contacto directo con humos. | Robusto, admite material grosero, gran capacidad. | Alta temperatura (300–600 °C): pérdida de N, olores intensos, riesgo de incendio, humos en contacto con el producto, alto consumo.
| Cinta transportadora (bandas) | El material se distribuye en capa fina sobre una malla perforada; el aire caliente atraviesa la capa. | Baja temperatura (100–140 °C), aire limpio (indirecto), control preciso, bajo consumo eléctrico, producto de calidad, modular. | Mayor superficie ocupada; requiere capa uniforme; malla inoxidable costosa.
| Solar / invernadero con ventilación | El material se esparce en un invernadero y se voltea; el sol y ventiladores evaporan el agua. | Costo operativo mínimo, muy bajo impacto. | Necesita ~1 m² por cada 10–15 kg/día: para 8 t/día, más de 6.000 m². Dependiente del clima, olores, 15–30 días de proceso.
| Lecho fluidizado | Aire a alta velocidad suspende las partículas. | Muy alta transferencia de calor. | Requiere material granulado uniforme; el guano fresco es pastoso; alto consumo de ventiladores; arrastre de finos.
## 4.3. Propiedades del guano de gallina ponedora
Tabla 3. Propiedades del guano adoptadas para el diseño
| Propiedad | Valor | Fuente / observación
| Humedad fresco (jaula, sin cinta de secado) | 70–75 % | INTA – valores medios; adoptado 72 %
| Densidad aparente húmedo | 750–850 kg/m³ | Adoptado 800 kg/m³
| Densidad aparente seco (15 %) | 450–550 kg/m³ | Adoptado 500 kg/m³
| Calor específico sólido seco | 1,3–1,6 kJ/kg·K | Adoptado 1,5
| Nitrógeno total (base seca) | 2,5–3,5 % | Se pierde parcialmente si T > 150 °C
| pH | 7,5–8,5 | Alcalino: favorece emisión de NH₃
| Temperatura de higienización | > 55 °C durante > 1 h | Reduce Salmonella y E. coli en más de 5 log
| Temperatura máxima recomendada de aire | 130–150 °C | Evitar volatilización de N y chamuscado
## 4.4. Cintas transportadoras
Una cinta transportadora es un elemento de transporte continuo formado por una banda sin fin que se apoya sobre rodillos o guías y es accionada por un tambor motriz. En los secadores de cinta la banda es una malla metálica permeable al aire, generalmente de alambre de acero inoxidable trenzado o de placas articuladas, que permite que el aire caliente atraviese la capa de producto. Las magnitudes fundamentales para su diseño son la tensión efectiva de la banda (resultante de la fricción de los ramales cargado y de retorno más las resistencias de tambores y rodillos), la potencia en el tambor motriz (producto de la tensión por la velocidad) y la tensión admisible de la malla por metro de ancho.
F_e = μ · g · (m_ramal cargado + m_ramal retorno) · k_tambores       P = F_e · v
## 4.5. Combustión de biomasa: la cáscara de arroz
La cáscara de arroz es un combustible de baja densidad (100 a 120 kg/m³), con 10 % de humedad, un poder calorífico inferior de 13 a 14 MJ/kg y un contenido de cenizas elevado, del 16 al 20 %, compuestas casi enteramente por sílice amorfa. Esta última característica tiene dos consecuencias prácticas: las cenizas funden a más de 1.400 °C, por lo que no forman escoria en la parrilla, pero hay que prever su extracción continua porque el volumen es importante. Por su baja densidad la cáscara tiende a formar bóvedas en los silos, lo que exige silos de paredes lisas y empinadas con alimentación por sinfín.
La combustión en hogar de parrilla inclinada es la más adecuada para este combustible: la cáscara ingresa por la parte alta, se seca, desvolatiliza y quema mientras baja escalón por escalón, y la ceniza cae al cenicero en la parte inferior. El aire primario entra por debajo de la parrilla y el aire secundario por encima del lecho para completar la combustión de los volátiles.
# 5. Estudio de alternativas y justificación de la solución
## 5.1. Alternativas de tecnología de secado
Se evaluaron las cuatro tecnologías descriptas en el marco teórico mediante una matriz de decisión ponderada. Los criterios y sus pesos fueron definidos por el grupo considerando las prioridades de un establecimiento avícola mediano: calidad del producto (preservación de nitrógeno), impacto ambiental (olores y emisiones), costo de inversión, costo operativo, superficie requerida y simplicidad de operación y mantenimiento.
Tabla 4. Matriz de decisión: tecnología de secado (puntaje 1 a 5, mayor es mejor)
| Criterio | Peso | Tambor rotativo | Cinta | Solar | Lecho fluidizado
| Calidad del producto / retención de N | 20 % | 2 | 5 | 4 | 3
| Impacto ambiental (olores, emisiones) | 20 % | 2 | 4 | 2 | 3
| Inversión | 15 % | 3 | 3 | 5 | 2
| Costo operativo (energía) | 15 % | 2 | 4 | 5 | 2
| Superficie requerida | 10 % | 4 | 4 | 1 | 4
| Aptitud para material pastoso | 10 % | 4 | 4 | 3 | 1
| Simplicidad de operación y mantenimiento | 10 % | 3 | 4 | 4 | 2
| Puntaje ponderado | 100 % | 2,65 | 4,10 | 3,45 | 2,50
El secador de cinta obtiene el mayor puntaje. Su principal ventaja es que trabaja a baja temperatura con aire limpio, lo que conserva el nitrógeno del guano (que es el componente de mayor valor), produce un producto homogéneo y genera un escape de aire relativamente frío y fácil de tratar. Sus desventajas —la superficie y el costo de la malla inoxidable— quedan compensadas por el diseño en tres pisos superpuestos.
## 5.2. Alternativas de fuente de energía
Tabla 5. Matriz de decisión: fuente de energía térmica
| Criterio | Peso | Gas natural / GLP | Eléctrica | Cáscara de arroz
| Costo operativo por kWh térmico | 30 % | 3 (GLP: 1) | 1 | 5
| Disponibilidad en zona rural de Crespo | 20 % | 2 (sin red de gas) | 3 (demanda 900 kW inviable) | 5
| Inversión en generador | 15 % | 4 | 5 | 2
| Impacto ambiental (CO₂ neto) | 15 % | 2 | 3 | 4 (biomasa neutra)
| Operación y mantenimiento | 20 % | 5 | 5 | 3
| Puntaje ponderado | 100 % | 3,15 | 3,10 | 4,00
La energía eléctrica queda descartada por la magnitud de la demanda: 880 kW térmicos equivalen a una potencia contratada que ninguna granja de la zona dispone y a un costo operativo prohibitivo. El gas natural no está disponible en la mayoría de los predios rurales y el GLP en garrafones o tanque resulta caro para un consumo continuo. La cáscara de arroz, disponible a menos de 100 km en los molinos del departamento Paraná y a un costo de 20 a 30 USD/t, resulta la alternativa más conveniente, con la única contra de requerir un hogar y un intercambiador de calor, y de generar cenizas que hay que disponer.
## 5.3. Alternativa de contacto directo vs. indirecto
Dentro del secado con biomasa existe la opción de mezclar los humos de combustión con aire y hacerlos pasar directamente por el producto (contacto directo) o de calentar aire limpio mediante un intercambiador (contacto indirecto). Se adoptó el contacto indirecto porque evita que el producto se contamine con hollín y cenizas volantes, permite un control de temperatura más fino, evita que el amoníaco liberado por el guano se mezcle con la corriente de humos y separa los dos circuitos de gases para su tratamiento. El costo es una pérdida de rendimiento del orden del 10 al 15 % en el intercambiador, que se consideró aceptable.
## 5.4. Solución adoptada
| Configuración de la planta Secador continuo de cinta de malla inoxidable, tres pisos en cascada de 2,0 m de ancho por 12 m de largo, aire caliente a 135 °C producido por un generador de aire caliente a cáscara de arroz de 880 kW con intercambiador tubular humos-aire, ventiladores centrífugos de impulsión, tratamiento del aire de escape mediante ciclón y lavador de gases húmedo, alimentación por tolva y cinta con tacos con variador, descarga por sinfín y elevador a acopio cubierto, control automático por PLC con lazos de temperatura y humedad. Operación en un turno de 8 horas con dos operarios.
# 6. Ingeniería del proceso: balances de masa y energía
## 6.1. Condiciones de diseño
Tabla 6. Condiciones de diseño del proceso
| Variable | Símbolo | Valor
| Alimentación de guano húmedo | m_in | 1.000 kg/h (8 t en 8 h)
| Humedad de entrada (b.h.) | X_in | 72 %
| Humedad de salida (b.h.) | X_out | 15 %
| Temperatura ambiente de diseño | T_a | 18 °C (media anual Crespo); 60 % HR
| Temperatura del producto a la salida | T_p | 60 °C
| Temperatura del aire a la entrada del secador | T_ai | 135 °C
| Temperatura del aire a la salida | T_ao | 65 °C
| Calor latente de vaporización a 60 °C | h_fg | 2.360 kJ/kg
| Pérdidas por paredes | — | 10 % del calor útil
## 6.2. Balance de masa
El sólido seco se conserva a lo largo del secador. Con 1.000 kg/h de alimentación al 72 % de humedad:
m_s = m_in · (1 − X_in) = 1.000 · 0,28 = 280 kg/h de sólido seco
m_out = m_s / (1 − X_out) = 280 / 0,85 = 329,4 kg/h de producto seco
W = m_in − m_out = 1.000 − 329,4 = 670,6 kg/h de agua evaporada
En un turno de 8 horas se producen 2.635 kg de guano seco y se evaporan 5.365 kg de agua. Considerando 250 días de operación anual, la producción es de unas 650 toneladas de fertilizante seco por año.
## 6.3. Balance de energía
Aplicando la ecuación del apartado 4.1.4 con los valores de diseño:
Tabla 7. Balance térmico del secador
| Concepto | Cálculo | Resultado
| Calor para evaporar el agua | 670,6 · [4,18 · (60−18) + 2.360] | 1.700.000 kJ/h = 472 kW
| Calentamiento del sólido seco | 280 · 1,5 · (60−18) | 17.640 kJ/h = 5 kW
| Calentamiento del agua residual | 49,4 · 4,18 · (60−18) | 8.670 kJ/h = 2 kW
| Calor útil total | suma | 1.726.000 kJ/h = 480 kW
| Pérdidas por paredes (10 %) | 0,10 · Q_útil | 48 kW
| Calor que debe entregar el aire | Q_útil + pérdidas | 1.900.000 kJ/h = 528 kW
## 6.4. Caudal de aire de secado
El aire entra a 135 °C y sale a 65 °C; con un calor específico de 1,02 kJ/kg·K:
m_aire = 1.900.000 / [1,02 · (135 − 65)] = 26.600 kg/h
A 135 °C la densidad del aire es de 0,865 kg/m³, por lo que el caudal volumétrico en las condiciones de trabajo es de 30.700 m³/h (21.900 m³/h en condiciones normales). Este es el caudal que deben mover los ventiladores de impulsión. El aire de escape lleva 27.270 kg/h (aire más vapor), a 65 °C, con una humedad absoluta de 33 g/kg. La temperatura de salida de 65 °C es un supuesto del método de diseño, que dimensiona ventiladores y generador del lado seguro; el apartado 6.7 verifica el funcionamiento real del lecho.
## 6.5. Potencia del generador de aire caliente y consumo de combustible
El generador debe calentar los 26.600 kg/h de aire desde 18 °C hasta 135 °C:
Q_gen = 26.600 · 1,02 · (135 − 18) = 3.175.000 kJ/h = 882 kW
La diferencia entre los 882 kW aportados y los 480 kW útiles corresponde principalmente al calor sensible que se lleva el aire de escape a 65 °C (354 kW). El rendimiento térmico del secador resulta del 54 %, valor normal para secadores de cinta de baja temperatura; para mejorarlo puede recircularse una parte del aire de escape hacia la entrada, opción que se deja prevista con la compuerta regulable CD-03 (su uso real se analiza en el apartado 6.7).
[img: revC_04.png]
Figura 3. Destino de la energía térmica entregada por el generador.
Con cáscara de arroz de 13,5 MJ/kg de poder calorífico inferior y un rendimiento del conjunto hogar-intercambiador del 75 %:
m_comb = 3.175 MJ/h / (13,5 · 0,75) = 314 kg/h = 2,5 t/día
A 110 kg/m³ de densidad aparente son 2,9 m³/h, es decir 23 m³ por turno. El silo de 70 m³ da una autonomía de tres días. Las cenizas, al 18 %, suman 56 kg/h, unos 450 kg por día. El consumo específico de energía resulta de 4,7 MJ por kg de agua evaporada, dentro del rango típico de 4 a 6 MJ/kg de los secadores industriales convectivos.
## 6.6. Dimensionamiento de la superficie de secado
Para secadores de cinta de baja temperatura con capa fina de producto, la bibliografía y los fabricantes indican una capacidad de evaporación específica de 8 a 12 kg de agua por m² y por hora. Adoptando 10 kg/m²·h:
A = W / e_esp = 670,6 / 10 = 67 m²
Se adoptan tres pisos de 2,0 m de ancho útil por 12 m de largo, que suman 72 m², con un margen del 7 %. El producto entra al piso superior con una capa de 30 mm y, al caer de piso en piso, se voltea y se redistribuye. La carga promedio sobre las bandas es de 15 kg/m², el material contenido en el secador es de unos 1.080 kg y el tiempo de residencia resulta:
t_res = m_contenido / m_promedio = 1.080 / 665 = 1,62 h = 97 min
La velocidad de las bandas es de 12 m en 32 minutos, es decir 0,37 m/min (6,2 mm/s). Es una velocidad muy baja, que exige reductores de gran relación y variadores de frecuencia.
[img: revC_05.png]
Figura 4. Diagrama de flujo del proceso con tabla de corrientes (plano 06).
## 6.7. Verificación con el modelo térmico del secador (Rev. F)
El balance de los apartados 6.3 a 6.5 supone la temperatura del aire de escape. Para verificar el diseño se armó un modelo físico del secador (carpeta simulacion_termica/ de la entrega): el guano avanza con cada banda, el aire lo atraviesa de abajo hacia arriba y cada piso se resuelve en 120 posiciones a lo largo y 8 capas en el espesor, con transferencia de calor y de vapor entre el aire y los grumos (correlación de Wakao y Kaguei), difusión del agua dentro del grumo ajustada a ensayos publicados de secado de guano (Ghaly y MacDonald, 2012; Liška y Kic, 2011), isoterma de equilibrio, contracción del lecho y pérdida de carga de Ergun. Los balances cierran al 0,002 % en masa y al 0,01 % en energía, y sin recirculación a 135 °C el modelo pide 885 kW y 315 kg/h de cáscara, prácticamente lo mismo que el método de diseño (882 kW y 314 kg/h).
Tabla 7. Punto de diseño y punto de trabajo según el modelo térmico
| Condición | Método de diseño (6.3-6.5) | Modelo, aire a 135 °C | Modelo, aire ajustado al 15 % (CD-03 al 25 %) | Modelo, capacidad a 135 °C
| Alimentación | 1.000 kg/h | 1.000 kg/h | 1.000 kg/h | 1.440 kg/h
| Temperatura del aire de entrada | 135 °C | 135 °C | 102 °C | 135 °C
| Humedad del producto | 15 % | menos de 2 % | 15 % | 15 %
| Aire de escape | 65 °C, 33 g/kg | 61 °C, 44 g/kg | 37 °C, 41 g/kg, casi saturado | 38 °C, saturado
| Calor del generador | 882 kW | 814 kW | 610 kW | 885 kW
| Cáscara | 314 kg/h | 289 kg/h | 217 kg/h | 315 kg/h
| Consumo específico | 4,7 MJ/kg de agua | 4,1 MJ/kg | 3,3 MJ/kg | 3,3 MJ/kg
Las conclusiones para el proyecto son cuatro. Primero, el equipo está bien dimensionado y sobra capacidad: a 135 °C seca unos 1.440 kg/h al 15 % (apartado 12.1), así que 135 °C pasa a ser la temperatura máxima de diseño y no la de trabajo. Segundo, con 1.000 kg/h al 72 % alcanza con aire a unos 100 °C (entre 93 y 110 °C según la humedad del guano, de 65 a 78 %); si el aire se dejara fijo en 135 °C el producto saldría con menos de 2 % de humedad y a 135 °C. Por eso la humedad se controla con la temperatura del aire y no con la velocidad de las bandas (apartado 14.5.2): cerca del 15 % la humedad del producto cambia 1,8 puntos por grado de aire y casi nada con la velocidad. Tercero, el escape sale casi saturado (apartados 4.1.3 y 23.4) y, con el aire ajustado, la recirculación casi no ahorra (1,2 % de cáscara a 18 °C) y en verano gasta más (1,1 % en enero): la compuerta CD-03 queda normalmente cerrada y solo se abre si la humedad relativa de la cámara de mezcla está por debajo del 90 % (plano 18). Cuarto, con el aire ajustado se queman unas 419 t de cáscara por año en lugar de 591 t (29 % menos, unos USD 4.300 por año). Con la CD-03 cerrada, el punto de trabajo de la Rev. F es: aire a 99,5 °C, 617 kW, 219 kg/h de cáscara, escape a 33 °C con 33 g/kg y producto a 74 °C a la salida del piso 3.
El modelo tiene límites que se dicen en el estudio: el tamaño de grumo (10 mm) y el aire que pasa por los bordes sin tocar el guano son supuestos, y la cinética proviene de guano de otros lugares secado en estufa. Cada 5 % de aire que sube por la rendija entre las bandas y las paredes pide unos 4 K más de aire y unas 18 t más de cáscara por año, y grumos de 20 mm piden 12 K más: por eso se sellan los bordes (apartado 7.2.6) y el módulo piloto debe medir esos datos antes de construir el SC-4 (capítulo de conclusiones).
# 7. Ingeniería mecánica del secador
## 7.1. Descripción general y estructura
El secador es una cámara cerrada y aislada de 13,0 m de largo, 2,6 m de ancho y 3,4 m de altura total (3,0 m de cámara sobre patas de 0,4 m), dentro de la cual se disponen tres cintas transportadoras superpuestas de 2,0 m de ancho por 12 m de largo, separadas 850 mm entre niveles. El producto entra por el piso superior, recorre los 12 m, cae al segundo piso por una tolva de caída, lo recorre en sentido contrario, cae al tercero y finalmente se descarga en el sinfín de salida. El aire caliente ingresa por un plenum inferior, atraviesa las tres capas de producto de abajo hacia arriba (contracorriente respecto del producto: el aire más caliente encuentra el material más seco, lo que permite terminar el secado) y sale por una campana superior hacia el ciclón.
[img: revC_06.png]
Figura 5. Cortes longitudinal y transversal del secador (plano 02).
[img: revC_07.png]
Figura 6. Modelo 3D del secador con el panel frontal removido, mostrando las tres cintas en cascada.
### 7.1.1. Bastidor
El bastidor es una estructura de acero al carbono soldada, formada por diez columnas de perfil UPN 120 (cinco por lado, separadas entre 3,19 y 3,25 m entre ejes) unidas por vigas longitudinales IPN 140 en la base y en la parte superior, y por travesaños de perfil ángulo L 50×50×5 cada 1,0 m que sostienen las guías de las bandas. Sobre las columnas se atornillan los paneles del cerramiento. Todo el conjunto se apoya en diez placas base de 200×200×12 mm, cada una fijada a la platea de hormigón con cuatro anclajes químicos de varilla M16 clase 5.8 (profundidad efectiva 125 mm), como se detalla en el capítulo de fijación al piso y en el plano SC-05. La estructura se protege con dos manos de antióxido epoxi y esmalte poliuretánico, dado que el ambiente es corrosivo por el amoníaco y la humedad.
### 7.1.2. Cerramiento y aislación
Las paredes, el techo y el piso de la cámara son paneles sándwich de 80 mm de espesor con núcleo de lana de roca de 100 kg/m³ (incombustible, resistente hasta 200 °C), chapa interior de acero inoxidable AISI 304 de 0,6 mm y chapa exterior galvanizada prepintada. Los paneles se unen con juntas de silicona para alta temperatura para evitar fugas de aire caliente. En cada lateral se disponen tres puertas de inspección de 700×600 mm con bisagras y cierres de leva, que permiten limpiar las bandas y acceder a los rodillos; su apertura está enclavada con el sistema de control (microinterruptor de seguridad).
## 7.2. Cintas transportadoras
### 7.2.1. Banda
Cada piso lleva una banda sin fin de malla de alambre trenzado de acero inoxidable AISI 304, alambre de 2 mm, paso 5 mm, ancho 2.000 mm, con bordes reforzados por cadenas laterales y desarrollo total de aproximadamente 25 m. La malla permite el paso del aire con una pérdida de carga baja y retiene el guano fresco (que entra como pasta) gracias a su tejido cerrado. Se eligió inoxidable y no acero al carbono porque el guano húmedo, el amoníaco y los 135 °C forman una combinación fuertemente corrosiva.
Tabla 8. Cálculo de la banda transportadora (por piso)
| Magnitud | Valor | Observación
| Peso de la malla | 12 kg/m² | Dato de fabricante
| Carga de producto promedio | 20 kg/m² (30 en piso 1) | Capa 30 mm a 800 kg/m³ = 24 kg/m²
| Masa ramal cargado (12 m × 2 m) | 768 kg | malla + producto
| Masa ramal de retorno | 288 kg | solo malla
| Coeficiente de fricción μ | 0,25 | Malla sobre guías de PTFE (pisos 2 y 3) y UHMW-PE (piso 1); se mantiene 0,25 del lado seguro
| Factor por tambores y rodillos | 1,15 | Rodamientos y flexión de la malla
| Tensión efectiva F_e | 2.980 N | F_e = 0,25 · 9,81 · 1.056 · 1,15
| Tensión por metro de ancho | 1.490 N/m | Admisible de la malla: 4.000 N/m → CS 2,7
| Velocidad de la banda | 0,37 m/min = 0,0062 m/s | Regulable 0,2 a 0,9 m/min
| Potencia en el tambor | 18 W | P = F_e · v
| Motorreductor adoptado | 0,75 kW | Par de arranque, malla fría y cargada
### 7.2.2. Tambores
Cada cinta tiene un tambor motriz de 300 mm de diámetro y 2.100 mm de largo, fabricado con tubo de acero de 4 mm de espesor, discos de fondo de 12 mm y cubos maquinados, con recubrimiento de goma romboidal de 8 mm para asegurar la adherencia de la malla. En el extremo opuesto va un tambor de reenvío de 250 mm de diámetro, montado en dos unidades tensoras UCT 210 con tornillo de M20 y 150 mm de carrera, que permiten regular la tensión de la banda y corregir su alineación. El eje del reenvío es de SAE 1045 de 60 mm entre los cubos, con muñones de 50 mm en los tensores: en la revisión anterior era de 50 mm en todo el largo, y la verificación a fatiga mostró que no alcanzaba (Rev. E). En el ramal de retorno, cada 2 m, se disponen rodillos de apoyo de 89 mm de diámetro.
### 7.2.3. Eje del tambor motriz
El eje transmite un par de 471 N·m (F_e · D/2 = 2.980 · 0,158, con los 316 mm de diámetro del tambor engomado). Para acero SAE 1045 con una tensión de corte admisible de 40 MPa el diámetro mínimo por torsión es:
d = [16 · T / (π · τ_adm)]^(1/3) = [16 · 471 / (π · 40·10⁶)]^(1/3) = 0,039 m
Se adopta un eje de 60 mm de diámetro en el tramo del tambor y de los apoyos (h8 en los asientos de los cubos, que se rectifican a Ra 0,8, y h7 en los rodamientos) y de 50 mm k6 en el extremo de la corona, con un escalón de radio 2 mm, por considerar además la flexión producida por el peso del tambor y la tensión de la banda (momento máximo 1.142 N·m) y por la verificación a fatiga del capítulo correspondiente. Los apoyos son unidades con brida cuadrada UCF 212 (capacidad dinámica 52,5 kN, estática 36 kN), con reacciones de 3,5 y 4,4 kN, por lo que su vida útil supera ampliamente las 100.000 horas. La corona de la transmisión se fija al eje con una chaveta paralela de 14×9×63 DIN 6885. El plano de fabricación de los dos ejes es el SC-03.
[img: revC_08.png]
Figura 7. Tambor motriz, eje, rodamientos y transmisión por cadena (plano 03).
### 7.2.4. Transmisión
El tambor debe girar a 0,37 rpm. Se adoptó una cadena cinemática de tres etapas: motor asincrónico trifásico de 0,75 kW, 4 polos (1.400 rpm), acoplado a un reductor de sinfín-corona de relación 1:300 (salida 4,7 rpm), y de éste una transmisión por cadena de rodillos ASA 60 (paso 19,05 mm) con piñón de 15 dientes y corona de 75 dientes, relación 1:5, que lleva el tambor a 0,93 rpm a 50 Hz. El variador de frecuencia regula el motor entre 12 y 50 Hz, lo que permite velocidades de banda entre 0,2 y 0,9 m/min; el punto de diseño corresponde a unos 20 Hz. El par que puede entregar el motorreductor en el tambor supera los 4.000 N·m: sirve para arrancar con la banda cargada y fría, pero con la banda trabada ese par haría fluir el eje. Por eso el variador limita el par del motor al 150 % del nominal (706 N·m en el eje del tambor), como se justifica en la verificación a fatiga. La cadena va protegida con un cárter cerrado de chapa de 1,6 mm con tapa de inspección y se lubrica con aceite para alta temperatura.
### 7.2.5. Guías y centrado de la banda
La banda desliza sobre guías longitudinales de 40 × 20 mm atornilladas a los travesaños. Las guías quedan en el aire que entra a cada piso: bajo el piso 3 el aire llega a entre 102 y 135 °C, y el polietileno de ultra alto peso molecular (UHMW-PE) admite unos 80 °C en uso continuo. Por eso en los pisos 2 y 3 las guías son de PTFE (uso continuo hasta 260 °C; como alternativa, guías de acero inoxidable con patín de PTFE) y solo en el piso 1, donde el aire ya salió de los otros dos pisos, se mantienen de UHMW-PE. Cada banda tiene guías laterales de chapa inoxidable de 100 mm de altura que contienen el producto y un sistema de centrado con sensores inductivos en ambos bordes que actúan sobre el tensor de reenvío.
### 7.2.6. Sello de los bordes de las bandas
Entre los bordes de cada banda y las paredes de la cámara queda una rendija por la que el aire puede subir sin atravesar el guano. Ese aire no seca: según el modelo térmico, cada 5 % del caudal que se escapa por los bordes obliga a subir unos 4 K la temperatura del aire y quema unas 18 t más de cáscara por año. Se cierra la rendija con un faldón continuo a cada lado de cada banda: chapa de acero inoxidable AISI 304 atornillada a la pared con un labio de goma siliconada apta para 200 °C que apoya sobre el borde de la malla, por encima de las guías laterales. El faldón se revisa en el mantenimiento mensual y el labio se reemplaza cuando se gasta.
## 7.3. Sistema de alimentación
### 7.3.1. Tolva de recepción
La pala cargadora vuelca el guano en una tolva de recepción de 3,1 m³ (plano 12), de chapa de acero inoxidable AISI 304 de 3 mm, con boca de 2,6 × 1,6 m a 2,0 m del piso y una rejilla de barrotes cada 100 mm que retiene plumas, cuerdas y objetos extraños. Un vibrador eléctrico de 0,25 kW (M15) evita el abovedamiento del material pastoso. El fondo descarga por una ranura de 2,2 m, con faldones, sobre la cinta de alimentación.
### 7.3.2. Cinta de alimentación (dosificador)
Desde la Rev. D el guano no se dosifica con un sinfín sino con una cinta de goma con bordes y tacos (plano 12), que lo extrae de la tolva y lo eleva hasta la boca de alimentación del piso superior: banda EP 400/3 de 500 mm con bordes ondulados de 60 mm y tacos de 50 mm cada 250 mm, con un tramo horizontal bajo la tolva, una curva de radio 2 m y un tramo a 30° hasta +4,35 m (desarrollo 12,1 m y desnivel 3,70 m). Con los bolsillos llenos al 60 % mueve hasta 3,24 m³/h a 0,10 m/s; los 1,25 m³/h requeridos (1.000 kg/h a 800 kg/m³) los lleva a 3,9 cm/s, con el variador al 39 %. La potencia necesaria a 0,10 m/s es de 0,33 kW y el motorreductor elegido, de 0,75 kW (M8, tambor motriz Ø320 a 6 rpm), tiene margen para el arranque con la tolva llena. La velocidad de la cinta es la variable que fija el caudal de guano que entra al secador: para aprovechar la capacidad del secador a 135 °C (1.440 kg/h, apartado 6.7) la cinta debe llegar a unos 5,6 cm/s, con el variador al 56 %.
### 7.3.3. Esparcidor
A la salida de la cinta de alimentación, sobre el piso superior, un rodillo esparcidor de paletas de 240 mm de diámetro y 2.000 mm de largo, accionado por un motorreductor de 0,75 kW a 60 rpm, desmenuza la pasta y la distribuye en una capa uniforme de 30 mm de espesor sobre todo el ancho de la banda. Una compuerta niveladora regulable termina de emparejar la capa. La uniformidad de la capa es crítica: si hay zonas más finas, el aire pasa preferentemente por ellas y el resto queda mal secado.
## 7.4. Sistema de descarga
El producto seco cae del extremo del tercer piso a una tolva de descarga y a un sinfín transversal de 160 mm de diámetro y paso, 20 rpm, motorreductor de 1,1 kW, con capacidad de 1,16 m³/h (el requerimiento es de 0,66 m³/h a 500 kg/m³). Desde allí un elevador de cangilones de 6 m de altura y 1,5 kW lleva el producto a la playa de acopio bajo techo, donde se almacena en pila hasta su carga a granel en camión o su ensacado.
Retención y enfriamiento (Rev. F). El secado al 15 % no alcanza para higienizar: el modelo térmico da que el guano pasa en promedio unos 9 minutos por encima de 55 °C, y los grumos de la parte de arriba del piso 3 llegan como mucho a 41-59 °C. Por eso el elevador ya no descarga directo al acopio: descarga en una tolva de retención aislada de 0,7 m³ (una hora de producción a 500 kg/m³), montada junto al cabezal sobre el muro del acopio, con el TT-05 adentro. El producto entra a 74-77 °C (sin recirculación y con el 25 %) y debe mantenerse a 70 °C o más durante 60 minutos (Reglamento UE 142/2011, anexo XI); como el margen es de apenas 4 a 7 K, el TT-05 lo registra en cada lote y el módulo piloto lo debe confirmar. A la salida de la tolva el producto se enfría por debajo de 40 °C antes del acopio, para que no condense ni fermente en la pila: hay que sacarle unos 6 kW. Se usa un enfriador a contracorriente bajo la tolva de retención (cuerpo de chapa con persianas), que entrega el producto frío a la válvula desviadora (acopio o envasado): unos 900 m³/h de aire de la nave atraviesan el producto, impulsados por un ventilador centrífugo de 0,55 kW (M40, 900 m³/h a unos 1.000 Pa), y el aire tibio y con polvo se descarga en el ducto de escape, antes del ciclón. Para alojar la tolva y el enfriador sin achicar la pendiente de la bajada a la zaranda (unos 36°), el elevador se prolonga de 6,3 a unos 8,1 m, que todavía queda por debajo de la chapa del techo: está bajo la cumbrera (8,35 m) y entre los pórticos de x = 22 y 27,5 m. El motor de 1,5 kW sobra, porque elevar 329 kg/h a 8 m pide unos 7 W de potencia útil. El redibujo de los planos 08 y 19 con la prolongación queda para la ingeniería de detalle.
## 7.5. Ductos de aire
El aire caliente llega desde el generador por un ducto de chapa galvanizada de 1.200 × 600 mm, aislado con lana de vidrio de 50 mm y chapa de protección, que descarga en el plenum inferior del secador. La velocidad en el ducto es de 12 m/s. La campana de salida en el techo del secador, de 800 × 800 mm, conecta con un ducto circular de 800 mm que conduce el aire agotado al ciclón. Ambos ductos llevan compuertas de regulación y tomas para medición de temperatura y presión.
## 7.6. Lista de materiales principales
Tabla 9. Materiales del secador y equipos asociados
| Componente | Material | Justificación
| Bastidor, columnas, vigas | Acero al carbono F-24 (IRAM-IAS U 500-503), perfiles UPN 120, IPN 140, L 50×50×5 | Estructural, económico, soldable; protegido con pintura epoxi
| Paneles de cerramiento | Sándwich lana de roca 80 mm; chapa int. AISI 304 0,6 mm; chapa ext. galvanizada prepintada | Aislación térmica e incombustible; interior resistente a corrosión
| Bandas | Malla de alambre trenzado AISI 304 Ø2 mm | Permeable al aire, resistente a corrosión y temperatura
| Tambores | Tubo acero SAE 1020 Ø300×4 mm + goma romboidal 8 mm | Adherencia de la malla
| Ejes | Acero SAE 1045: Ø60 con asientos rectificados y Ø50 en los extremos | Resistencia a torsión, flexión y fatiga, maquinable
| Rodamientos | UCF 212 con brida (tambor motriz) y unidades tensoras UCT 210 (reenvío), con sello | Autoalineantes, sellados contra polvo
| Guías de deslizamiento | PTFE 40×20 mm en los pisos 2 y 3; UHMW-PE 40×20 mm en el piso 1 | Bajo rozamiento; el PTFE soporta el aire de entrada (hasta 135 °C)
| Faldones de sellado de bordes | Chapa AISI 304 1,5 mm + labio de goma siliconada (200 °C) | Evitan que el aire suba por los bordes sin tocar el guano
| Tolva, sinfines, esparcidor, guías laterales | Acero inoxidable AISI 304 | Contacto con guano húmedo (corrosivo)
| Ductos de aire caliente | Chapa galvanizada BWG 18 + aislación lana de vidrio 50 mm | Temperatura 135 °C, bajo costo
| Ducto de escape Ø800 y ciclón | Aislación de lana de roca 50 mm con chapa de protección; purga de condensado con sifón | El escape sale casi saturado (≈ 37 °C)
| Hogar del generador | Ladrillo refractario aluminoso 40 % + aislante + chapa 4 mm | Temperatura de llama 900–1.000 °C
| Tubos intercambiador (1er paso) | Acero inoxidable AISI 310 | Humos a 850 °C
| Tubos intercambiador (2do y 3er paso) | Acero al carbono ASTM A106 | Humos a menor temperatura
| Chimenea | Acero al carbono 4 mm, aislada | Humos a 200 °C
| Ciclón y scrubber | Acero inoxidable AISI 304 / PRFV | Gases húmedos con amoníaco
| Tornillería | Acero 8.8 zincada; inoxidable A2 en zonas húmedas | Resistencia y durabilidad
| Anclajes al piso | Varilla roscada M16 clase 5.8 zincada con resina epoxi | Fijación química a la platea existente, sin insertos previos
# 8. Operación de la planta y de la cinta
## 8.1. Personal
La planta funciona con dos operarios por turno: un operador de proceso, ubicado en la sala de control y en recorridas por la planta, responsable del arranque, la regulación y la parada, y un operario de campo que se ocupa de la alimentación de la tolva con la pala cargadora, del control del silo de cáscara, del retiro de cenizas y del acopio del producto. Ambos deben estar capacitados en el uso del equipo, en los riesgos del proceso y en el plan de emergencias.
## 8.2. Puesta en marcha diaria
- Inspección visual de la planta: bandas vacías y centradas, puertas de inspección cerradas, ausencia de personal en zonas de riesgo, nivel de cáscara en silo, tolva de cenizas vacía, nivel de agua en el tanque del lavador de gases.
- Energizar el tablero general (seccionador QG), verificar ausencia de alarmas en la HMI y tensión de red normal.
- Seleccionar el modo AUTO en el selector principal y pulsar MARCHA. El PLC ejecuta la secuencia enclavada: 1) extractor de gases, 2) bomba del lavador, 3) ventiladores de impulsión, 4) ventilador y alimentador del hogar (encendido), 5) cintas, 6) sinfín de descarga y elevador. El dosificador queda inhabilitado hasta alcanzar la temperatura.
- Encendido del hogar: el operario de campo carga manualmente una pequeña cantidad de cáscara y encendedores sobre la parrilla; una vez que el detector de llama confirma la combustión, el PLC habilita el sinfín de cáscara en modo de regulación de temperatura.
- Calentamiento: el sistema tarda entre 30 y 45 minutos en llevar el aire de entrada a la temperatura de arranque (100 °C). Las cintas giran en vacío a velocidad mínima para calentarse en forma uniforme.
- Con el aire en temperatura, el PLC habilita el dosificador. El operador fija la velocidad inicial de la cinta de alimentación (3,9 cm/s, variador al 39 %) y verifica que el esparcidor forme una capa uniforme de 30 mm en el primer piso.
## 8.3. Operación normal: cómo se maneja la cinta
Durante la marcha normal el operador supervisa en la HMI las tres variables fundamentales: la temperatura del aire de entrada, la temperatura del aire de salida de cada piso y la humedad del producto en la descarga. Los ajustes que puede realizar son:
- Temperatura del aire: es el ajuste principal (Rev. F). Si el producto sale con más de 15 % de humedad se sube la temperatura del aire, y si sale demasiado seco (menos de 12 %, con riesgo de polvo y pérdida de peso vendible) se baja: cerca del 15 % cada grado de aire mueve la humedad unos 1,8 puntos.
- Velocidad de las cintas: sigue al caudal del dosificador para mantener la capa de 30 mm; cambiarla casi no mueve la humedad de salida. Los tres pisos se regulan en conjunto, con una relación fija entre ellos que el PLC mantiene (el piso 1, con más material, algo más rápido). En modo AUTO este ajuste lo hace el PLC en un lazo PID con el sensor de humedad; en modo MANUAL lo hace el operador desde la HMI.
- Caudal del dosificador: fija cuánto guano entra al secador. Se ajusta según el espesor de capa deseado (30 mm) y la capacidad térmica disponible. Nunca se aumenta el caudal por encima del que la temperatura del aire puede secar: el producto saldría húmedo.
- Consigna de temperatura: en AUTO la fija el lazo de humedad entre 90 y 150 °C; con 1.000 kg/h de guano al 72 % ronda los 100 °C (93 °C con guano al 65 % y 110 °C con guano al 78 %). Nunca se supera 150 °C para no perder nitrógeno ni chamuscar el producto. El PLC la regula actuando sobre el sinfín de cáscara y el ventilador del hogar.
- Espesor de capa: se verifica visualmente en la ventana de inspección del piso 1 y se corrige con la compuerta niveladora del esparcidor.
Tabla 10. Guía rápida de regulación para el operador
| Síntoma | Causa probable | Acción
| Producto sale húmedo (> 17 %) | Guano más húmedo; capa gruesa; poca temperatura | Subir la consigna de aire 3 a 5 °C (en AUTO lo hace el lazo); verificar capa y faldones de los bordes
| Producto sale muy seco (< 12 %) y con polvo | Aire demasiado caliente; alimentación baja | Bajar la consigna de aire; subir dosificador
| Aire de entrada no llega a la consigna | Poca cáscara; cáscara húmeda; parrilla con ceniza; intercambiador sucio | Revisar silo y sinfín; limpiar parrilla; programar limpieza de tubos
| Aire de salida por encima de 75 °C | Capa muy fina o banda vacía | Subir dosificador o bajar temperatura
| Banda se desplaza lateralmente | Tensión desigual | Corregir con tensores del reenvío (el centrado automático lo hace en marcha)
| Olor intenso en el escape | Bajo caudal de agua en scrubber; pH alto | Verificar bomba; reponer solución ácida
| Alarma alta temperatura (160 °C) | Exceso de combustible; falla del lazo | El PLC corta la cáscara automáticamente; verificar y rearmar
## 8.4. Parada
La parada normal se ejecuta en orden inverso al arranque: se detiene primero el dosificador y, con la cinta aún en marcha y el aire caliente, se deja que el material contenido en el secador (unos 1.080 kg, 97 minutos) termine de secarse y se descargue; luego se corta la alimentación de cáscara y se deja que el hogar se apague; los ventiladores siguen funcionando hasta que el aire baja de 60 °C, para enfriar el intercambiador y el secador; por último se detienen las cintas, el extractor y la bomba. La parada de emergencia (pulsadores tipo hongo) detiene todo de inmediato, excepto el extractor de gases, que se mantiene 5 minutos por seguridad; en caso de emergencia con el hogar encendido, la compuerta de by-pass envía los humos directamente a la chimenea.
## 8.5. Registros
El PLC registra cada 5 minutos las temperaturas, la humedad de salida, las velocidades y el consumo eléctrico, y los guarda en la memoria de la HMI, desde donde se descargan a una planilla. El operador lleva además un parte diario con toneladas procesadas, cáscara consumida, cenizas retiradas y novedades de mantenimiento.
# 9. Ingeniería eléctrica y control
## 9.1. Suministro de energía
La planta requiere una alimentación trifásica de 3×380/220 V, 50 Hz. La potencia instalada es de 66,9 kW; considerando un factor de simultaneidad de 0,8 (los motores pequeños no funcionan todos a la vez y los ventiladores trabajan con variador por debajo de su potencia nominal), la demanda máxima es de 54 kW, unos 109 A por fase. El suministro lo presta la Cooperativa La Agrícola Regional (LAR), distribuidora de Crespo, en baja tensión. Con las cargas de la ampliación (tablero TG2) la potencia a contratar es de {{P_contratada}} kW en la tarifa T3 de grandes demandas (ver la memoria de cálculo del TG2). Si el predio se encuentra alejado de la red de baja tensión, la alternativa es una subestación aérea propia de 100 kVA, 13,2/0,4 kV, con celda de medición en media tensión.
La acometida al tablero general se realiza con cable de cobre tetrapolar 3×50 + 25 mm² (IRAM 2178, 1,1 kV) en bandeja portacables, con una caída de tensión menor al 1 % en 40 m. La corrección del factor de potencia se hace con una batería automática de capacitores de 20 kVAr en cuatro escalones, que lleva el cos φ de 0,85 a 0,95 y evita recargos en la facturación.
## 9.2. Motores eléctricos
Todos los motores son asincrónicos trifásicos de jaula de ardilla, 4 polos, 380 V, protección IP55, clase de aislación F, eficiencia IE3, aptos para alimentación por variador de frecuencia. La corriente nominal se calculó con la expresión:
I_n = P / (√3 · U · cos φ · η) = P / (√3 · 380 · 0,85 · 0,90)
Tabla 11. Lista de motores, corrientes, arranque y conductores
| N° | Motor | kW | In (A) | Arranque | Cable (Cu, mm²) | Protección
| M1 | Ventilador impulsión 1 | 15 | 29,46 | VFD + RL 3 % | 4x6 apant. | GM 24,0-32,0 A / Ir 29,5 A
| M2 | Ventilador impulsión 2 | 15 | 29,46 | VFD + RL 3 % | 4x6 apant. | GM 24,0-32,0 A / Ir 29,5 A
| M3 | Extractor de gases | 22 | 42,79 | VFD + RL 3 % | 4x10 apant. | GM 37,0-50,0 A / Ir 42,8 A
| M4 | Ventilador de combustión | 4 | 8,37 | VFD + RL 3 % | 4x1,5 apant. | GM 6,0-10,0 A / Ir 8,4 A
| M5 | Cinta piso 1 | 0,75 | 1,84 | VFD | 4x1,5 apant. | GM 1,6-2,5 A / Ir 1,8 A
| M6 | Cinta piso 2 | 0,75 | 1,84 | VFD | 4x1,5 apant. | GM 1,6-2,5 A / Ir 1,8 A
| M7 | Cinta piso 3 | 0,75 | 1,84 | VFD | 4x1,5 apant. | GM 1,6-2,5 A / Ir 1,8 A
| M8 | Cinta de alimentación | 0,75 | 1,84 | VFD | 4x1,5 apant. | GM 1,6-2,5 A / Ir 1,8 A
| M9 | Esparcidor | 0,75 | 1,84 | directo (KM) | 4x1,5 | GM 1,6-2,5 A / Ir 1,8 A
| M10 | Sinfín de descarga | 1,1 | 2,58 | directo (KM) | 4x1,5 | GM 2,5-4,0 A / Ir 2,6 A
| M11 | Elevador de cangilones | 1,5 | 3,38 | directo (KM) | 4x1,5 | GM 2,5-4,0 A / Ir 3,4 A
| M12 | Sinfín de cáscara | 0,75 | 1,84 | VFD | 4x1,5 apant. | GM 1,6-2,5 A / Ir 1,8 A
| M13 | Sinfín de cenizas | 0,55 | 1,43 | directo (KM) | 4x1,5 | GM 1,0-1,6 A / Ir 1,4 A
| M14 | Bomba del lavador | 3 | 6,42 | directo (KM) | 4x1,5 | GM 6,0-10,0 A / Ir 6,4 A
| M15 | Vibrador de tolva | 0,25 | 0,77 | directo (KM) | 4x1,5 | GM 0,63-1,0 A / Ir 0,8 A
|  | Total instalado | 66,9 | 135,7 |  |  | 
[img: revC_09.png]
Figura 8. Distribución de la potencia eléctrica instalada.
## 9.3. Criterios de arranque y protección
Se distinguen dos grupos de motores. Los que regulan el proceso —ventiladores, cintas, dosificador, alimentador de cáscara y ventilador del hogar— se accionan mediante variadores de frecuencia (VFD), que permiten ajustar en forma continua la velocidad, arrancar sin picos de corriente y ahorrar energía en los ventiladores (la potencia absorbida por un ventilador varía con el cubo de la velocidad). Los motores de función fija —esparcidor, sinfín de descarga, elevador, sinfín de cenizas, bomba y vibrador— se arrancan en forma directa con guardamotor, contactor y relé térmico.
Cada circuito de motor está protegido por un guardamotor magnetotérmico clase 10 regulado a 1,15 veces la corriente nominal, que provee protección contra cortocircuito y sobrecarga. Los variadores incorporan además protección electrónica de sobrecorriente, sobretensión, subtensión, falta de fase y sobretemperatura, y se instalan con filtro EMC y reactancia de línea en los de más de 15 kW. Todo el sistema está protegido aguas arriba por el interruptor general automático tetrapolar de 125 A con poder de corte de 25 kA y descargadores de sobretensión tipo II.
## 9.4. Tablero general de fuerza y control
El tablero general se ubica en la sala de control, alejado del polvo y del calor. Es un gabinete metálico autoportante IP54 de 2.000 × 1.000 × 400 mm, en chapa de 2 mm con pintura epoxi, con zócalo, placa de montaje galvanizada y ventilación forzada con filtros para disipar los 1,4 kW de pérdidas de los variadores. En su interior se disponen, de arriba hacia abajo: el interruptor general, los descargadores y la medición; las barras de cobre de 30×5 mm para 160 A; la fila de guardamotores; los cuatro variadores grandes; los variadores pequeños y los contactores; el PLC con sus módulos de expansión y los relés de interfaz; la batería de capacitores, el relé de seguridad y las borneras. En la puerta se montan la pantalla HMI de 7 pulgadas, ocho luces piloto de estado, ocho selectores, pulsadores de marcha y parada y el pulsador de parada de emergencia.
[img: revC_10.png]
Figura 9. Disposición interior y frontal del tablero general (plano 07).
[img: revC_11.png]
Figura 10. Esquema unifilar del tablero general de fuerza (plano 05).
Además del tablero general, se instala un tablero secundario TS-1 junto al secador, con parada de emergencia local, selectores de mantenimiento para mover cada cinta en modo manual a baja velocidad (con la puerta de inspección abierta y una persona vigilando) y tomacorrientes de 220 V para herramientas. La instalación cumple con la Reglamentación AEA 90364 para instalaciones eléctricas en inmuebles, con sistema de puesta a tierra TT, jabalinas y resistencia de tierra menor a 5 ohm, cables en bandejas perforadas separadas más de 300 mm de los ductos de aire caliente, y canalización de señales de instrumentación con cable apantallado en bandeja independiente.
## 9.5. Sistema de control automático
### 9.5.1. Arquitectura
El control se realiza con un PLC compacto Siemens S7-1200 (CPU 1214C) o equivalente, con módulos de entrada de RTD (8 canales) para las PT100, entrada analógica 4-20 mA (4 canales) para el sensor de humedad y el presostato analógico, 16 entradas y 16 salidas digitales, y comunicación Profinet con los variadores y la HMI. La HMI KTP700 de 7 pulgadas muestra un sinóptico de la planta con todas las variables, permite modificar set points, muestra alarmas y registra tendencias.
Tabla 12. Instrumentación de la planta
| Tag | Instrumento | Ubicación | Función
| TT-01 | PT100 clase A | Ducto de aire caliente, entrada secador | Variable del lazo de temperatura (consigna de 90 a 150 °C que fija MIC-01)
| TT-02/03/04 | PT100 | Salida de aire de cada piso | Supervisión del secado por piso
| TT-05 | PT100 | Dentro de la tolva de retención de la descarga | Registra la higienización (≥ 70 °C durante 60 min)
| TT-06 | Termocupla tipo K | Humos a la salida del hogar | Protección del intercambiador (máx. 950 °C)
| TT-07 | PT100 | Humos en chimenea | Rendimiento (SP 200 °C)
| TT-08 | PT100 | Aire ambiente | Referencia
| MT-01 | Sensor de humedad capacitivo / NIR | Sinfín de descarga | Variable del lazo de humedad (SP 15 %)
| MT-02 (opcional) | Sensor de humedad NIR | Sobre la cinta de alimentación | Humedad del guano fresco: ajuste anticipado del lazo de humedad
| PT-01 | Transmisor de presión diferencial | Plenum inferior del secador | Detecta obstrucción de bandas o falla de ventiladores
| BE-01 | Detector de llama UV | Hogar | Habilita la alimentación de combustible
| LS-01/02 | Sensores de nivel capacitivos | Tolva de guano / silo de cáscara | Alarma de nivel bajo
| ZS-01..06 | Microinterruptores de seguridad | Puertas de inspección | Enclavamiento: parada de cintas
| SS-01..03 | Sensores de giro inductivos | Tambores de reenvío | Detectan banda detenida o patinando
| ZS-10/11 | Sensores inductivos de borde | Bordes de banda | Centrado automático
### 9.5.2. Lazos de regulación
- Lazo 1 – Temperatura de aire de entrada (TIC-01): el PLC compara TT-01 con la consigna que le fija el lazo 2 (entre 90 y 150 °C, con rampa limitada) y, mediante un controlador PID, ajusta la velocidad del sinfín de cáscara (M12) y en proporción la del ventilador del hogar (M4). Si la temperatura supera 160 °C (TSH-01), se corta la cáscara y se abre el by-pass de humos.
- Lazo 2 – Humedad de salida (MIC-01), en cascada sobre el lazo 1 (Rev. F): el PLC compara MT-01 con el set point de 15 % y corrige la consigna de temperatura de TIC-01 entre 90 y 150 °C. Es un lazo lento (el tiempo muerto es el tiempo de residencia, unos 97 minutos), por lo que se sintoniza como PI con 0,8 K por punto de humedad y 45 minutos de tiempo integral, y no integra mientras la consigna está limitada por la rampa o por los topes. Las tres cintas (M5, M6, M7) ya no corrigen la humedad: siguen al caudal del dosificador para mantener la capa de 30 mm. Con el modelo térmico, ante un cambio del guano de 72 a 76 % el producto vuelve al 15 % (±1 punto) 1,7 h después de que llega el guano húmedo; el lazo anterior, que actuaba sobre las bandas, lo hacía oscilar entre 10 y 43 %.
- Ajuste anticipado opcional (MT-02): un sensor de humedad del guano fresco sobre la cinta de alimentación suma a la consigna 1,25 K por punto de humedad, aplicados 40 minutos después (lo que tarda el guano en llegar a la zona que decide la humedad final). Ante el mismo cambio, el pico baja de 28 a 25 % y queda 12 minutos sobre 20 %, sin llegar a la alarma de 15 minutos; a cambio, antes de que llegue el guano húmedo el producto sale un rato al 11 %.
- Lazo 3 – Presión del plenum (PIC-01): mantiene la presión del aire de impulsión en el valor de diseño (1.500 Pa) ajustando la velocidad de los ventiladores M1 y M2; compensa el ensuciamiento de las bandas.
### 9.5.3. Enclavamientos y seguridades
- Secuencia de arranque obligatoria: extractor → bomba de scrubber → ventiladores → hogar → cintas → dosificador. Ningún equipo arranca si el anterior no confirmó su marcha (contacto auxiliar del contactor o señal del variador).
- Corte de combustible ante: temperatura de aire > 160 °C, temperatura de humos > 950 °C, falla del extractor, falla de ventiladores, pérdida de llama durante más de 30 s, parada de emergencia.
- Parada de cintas y dosificador ante apertura de puertas de inspección, banda detenida (sensor de giro), sobrecarga de un motor o parada de emergencia.
- Alarma y parada de dosificador ante humedad de salida > 20 % sostenida 15 minutos (evita acumular producto húmedo en el acopio).
- Nivel bajo de cáscara en silo: alarma; nivel bajo crítico: parada programada.
- Relé de seguridad categoría 3 (EN ISO 13849) para el circuito de parada de emergencia, independiente del PLC.
## 9.6. Iluminación y tomacorrientes
La nave se ilumina con luminarias LED industriales de 150 W de alta bahía, 20 unidades, con un nivel de 300 lux en las zonas de trabajo y 500 lux en la sala de control y el taller, conforme al Decreto 351/79. Se prevé iluminación de emergencia autónoma en salidas y tablero. Los tomacorrientes son trifásicos de 32 A y monofásicos de 16 A, tipo industrial IP44, en circuitos independientes protegidos con interruptores diferenciales de 30 mA.
# 10. Generador de aire caliente a biomasa
## 10.1. Descripción
El generador de aire caliente es el equipo que provee los 882 kW térmicos al proceso. Está formado por un hogar de combustión de cáscara de arroz con parrilla inclinada escalonada, un intercambiador de calor tubular humos-aire de tres pasos, dos ventiladores centrífugos de impulsión que toman aire del ambiente, lo hacen pasar por el lado de la carcasa del intercambiador y lo envían al secador, un ciclón de humos, una chimenea de 12 m y los sistemas de alimentación de combustible y extracción de cenizas.
[img: revC_12.png]
Figura 11. Corte esquemático del generador de aire caliente (plano 04).
## 10.2. Hogar
La cámara de combustión tiene 1,8 m de ancho, 2,4 m de alto y 2,0 m de profundidad interior, revestida con ladrillo refractario aluminoso de 230 mm, capa aislante de 70 mm y carcasa de chapa de 4 mm. La parrilla es de barrotes de fundición en seis escalones, con 0,6 m² de superficie; la carga térmica específica es de 523 kg/h·m², dentro del rango de 400 a 700 kg/h·m² recomendado para cáscara de arroz. El aire primario, 70 % del total, ingresa por debajo de la parrilla impulsado por el ventilador de combustión de 4 kW; el aire secundario, 30 %, se inyecta por toberas por encima del lecho para quemar los volátiles y reducir el monóxido de carbono. La cáscara ingresa por un sinfín refrigerado de 150 mm que la deposita en el escalón superior; las cenizas caen por el escalón inferior a un cenicero con sinfín de extracción de 0,55 kW que las lleva a la tolva de cenizas de 1 m³.
Tabla 13. Balance de combustión
| Magnitud | Valor
| Consumo de cáscara | 314 kg/h (PCI 13,5 MJ/kg, 10 % humedad)
| Aire estequiométrico | 4,6 kg/kg
| Exceso de aire | 40 %
| Aire de combustión total | 2.020 kg/h = 1.685 m³/h
| Caudal de humos | 2.280 kg/h
| Temperatura de humos a la salida del hogar | 850 °C
| Temperatura de humos en chimenea | 200 °C
| Cenizas (18 %) | 56 kg/h = 450 kg/día
| Potencia térmica en el combustible | 1.178 kW
| Rendimiento global hogar + intercambiador | 75 %
## 10.3. Intercambiador de calor
Los humos circulan por el interior de tubos y el aire de proceso por el exterior, en tres pasos con flujo cruzado. Con humos de 850 a 200 °C y aire de 18 a 135 °C, la diferencia media logarítmica de temperatura es:
ΔT_ml = [(850−135) − (200−18)] / ln[(850−135)/(200−18)] = 390 K
Adoptando un coeficiente global de transferencia de 25 W/m²·K (típico para intercambiadores gas-gas de tubos lisos con humos con cenizas), la superficie necesaria es:
A = Q / (U · ΔT_ml) = 882.000 / (25 · 390) = 91 m²
Se adoptan 114 tubos de 63,5 mm de diámetro exterior y 4,0 m de largo, en tres pasos de 38 tubos, con una superficie de 91 m². Los tubos del primer paso, que reciben los humos a 850 °C, son de acero inoxidable AISI 310; los restantes, de acero al carbono ASTM A106. La velocidad de los humos en los tubos es de 8 m/s y la del aire en la carcasa de 6 m/s. La carcasa, de 4,6 m de largo, 1,6 m de alto y 2,2 m de ancho, tiene tapas desmontables en los cabezales para el deshollinado de los tubos, operación que se programa semanalmente por la elevada carga de cenizas volantes de la cáscara.
## 10.4. Ventiladores y chimenea
Los dos ventiladores centrífugos de impulsión, de 15 kW cada uno, mueven 15.400 m³/h a 1.500 Pa de presión estática (suma de las pérdidas en el intercambiador, el ducto, el plenum y las tres bandas cargadas), con un rendimiento del 70 %. Aspiran aire ambiente a través de filtros de bolsa y lo impulsan a través del intercambiador, por lo que trabajan en frío; sus motores son estándar. La chimenea, de 500 mm de diámetro y 12 m de altura, está calculada para una velocidad de humos de 5 m/s y produce un tiro natural que se complementa con el ventilador de combustión. Lleva toma de muestreo normalizada para el control de emisiones y una PT100 para el control de rendimiento.
## 10.5. Seguridades del generador
- Termocupla de humos con alarma a 900 °C y corte de combustible a 950 °C, para proteger los tubos.
- Compuerta de by-pass de humos a la chimenea, accionada por servomotor, que se abre ante parada de ventiladores o sobretemperatura.
- Presostato de depresión en el hogar: si el hogar se presuriza (falla de extracción) se corta la cáscara.
- Detector de llama y secuencia de purga de 60 segundos antes de cada encendido.
- Sinfín de alimentación refrigerado con camisa de agua y válvula rotativa cortafuego para evitar el retroceso de llama al silo.
- Silo de cáscara con sensor de temperatura y rociadores, por el riesgo de autocombustión de la biomasa almacenada.
# 11. Distribución en planta
## 11.1. Método aplicado
Para definir la ubicación de los sectores se aplicó el método de Planeamiento Sistemático de la Distribución (SLP, Systematic Layout Planning) de Richard Muther, ya utilizado por el grupo en el Trabajo Práctico de distribución en planta de Organización Industrial: se identificaron las actividades, se estableció el flujo de materiales, se elaboró la tabla relacional de actividades con los códigos A (absolutamente necesario), E (especialmente importante), I (importante), O (ordinario), U (sin importancia) y X (no deseable), se dibujó el diagrama relacional y se ajustó a la superficie disponible.
Tabla 14. Tabla relacional de actividades (resumen de relaciones principales)
| Sectores | Relación | Motivo
| Recepción de guano – Tolva – Secador | A | Flujo continuo del material húmedo, distancia mínima
| Secador – Generador de aire caliente | A | Ducto de aire caliente corto (pérdidas térmicas)
| Generador – Silo de cáscara | A | Alimentación por sinfín
| Secador – Ciclón – Scrubber | E | Ducto de gases corto
| Descarga – Acopio de producto seco | A | Flujo del producto terminado
| Sala de control – Secador | E | Visibilidad y cableado
| Recepción de guano – Vestuario / oficina | X | Olores y contaminación
| Generador (hogar) – Acopio de producto seco | X | Riesgo de incendio (producto seco combustible)
| Generador (hogar) – Silo de cáscara | X (con A) | Riesgo de incendio; se resuelve con silo exterior y sinfín con cortafuego
| Taller – Secador | I | Mantenimiento
## 11.2. Distribución adoptada
El resultado es una nave de 33 × 18 m (594 m² cubiertos) con flujo lineal de oeste a este: el guano ingresa por el portón oeste a la playa de recepción, con piso de hormigón con pendiente del 1 % hacia una canaleta de lixiviados conectada a una cámara estanca; de allí pasa a la tolva, al sinfín y al secador, que ocupa el centro de la nave; el generador de aire caliente se ubica en el extremo este del secador, con el silo de cáscara fuera de la nave, contra la pared este, y la chimenea que atraviesa el techo; el producto seco se descarga en el extremo este y se eleva a la playa de acopio, en el sector sudeste, con portón propio para la carga de camiones. El ciclón y el lavador de gases se ubican sobre el lado norte del secador, cerca de la campana de salida. La sala de control, el taller y el depósito de repuestos quedan sobre el lado norte y este, alejados de la recepción; el vestuario y la oficina en el extremo noroeste, con acceso independiente, en la zona opuesta al hogar y separados de la recepción por el depósito.
[img: revC_13.png]
Figura 12. Layout general de la planta (plano 01).
La nave es un galpón industrial de estructura metálica con cabriadas reticuladas, cubierta de chapa con aislación y ventilación cenital por lucernario, altura libre de 7 m (necesaria para el elevador y el ciclón), piso de hormigón armado de 15 cm apto para el tránsito de pala cargadora, y portones corredizos de 4 m. La zona de recepción tiene paredes lavables hasta 2 m de altura.
# 12. Seguridad e higiene en el trabajo
## 12.1. Marco legal
La planta se encuadra en la Ley Nacional 19.587 de Higiene y Seguridad en el Trabajo y su Decreto Reglamentario 351/79, que fijan las condiciones de los ambientes de trabajo (ventilación, iluminación, ruido, carga térmica), la protección contra incendios, las instalaciones eléctricas, las máquinas y herramientas y los elementos de protección personal; en la Ley 24.557 de Riesgos del Trabajo (ART, capacitación, exámenes médicos); en la Resolución SRT 295/03 (ergonomía, ruido, estrés térmico); en la Resolución SRT 905/15 (servicio de higiene y seguridad); y en la Reglamentación AEA 90364 para la instalación eléctrica. Por su superficie y cantidad de personal, el establecimiento debe contar con un servicio externo de Higiene y Seguridad y un plan de capacitación anual.
## 12.2. Identificación de riesgos
Tabla 15. Matriz de identificación y evaluación de riesgos
| Riesgo | Fuente | Consecuencia | Prob. | Grav. | Medida de control
| Atrapamiento mecánico | Tambores, cadenas, sinfines, esparcidor, elevador | Amputación, muerte | Media | Muy grave | Protecciones fijas en transmisiones; cárter en cadenas; tapas de sinfines con enclavamiento; puertas de inspección enclavadas; procedimiento de bloqueo y etiquetado (LOTO)
| Contacto térmico | Ductos, hogar, intercambiador, chimenea, paneles del secador | Quemaduras | Alta | Grave | Aislación de todas las superficies > 60 °C; barandas de distanciamiento en el hogar; guantes térmicos; señalización
| Contacto eléctrico | Tablero, motores, cables | Electrocución | Baja | Muy grave | AEA 90364; puesta a tierra; diferenciales; tablero cerrado; solo personal habilitado; herramientas aisladas
| Incendio | Hogar, silo de cáscara, guano seco, polvo orgánico | Daños, quemaduras | Media | Muy grave | Silo exterior con cortafuego; sensores de temperatura; extintores ABC y agua presurizada; hidrantes; limpieza de polvo; prohibición de fumar
| Explosión de polvo | Polvo de guano seco y cáscara en suspensión | Explosión | Baja | Muy grave | Limpieza periódica; aspiración de polvo; motores IP55; evitar acumulación en zonas cerradas
| Inhalación de amoníaco y polvo | Guano fresco en recepción; escape del secador | Irritación respiratoria, conjuntivitis | Alta | Moderada | Ventilación forzada en recepción; scrubber; máscara con filtro ABEK-P3 en recepción; medición periódica (TLV NH₃ 25 ppm)
| Riesgo biológico | Guano fresco (Salmonella, E. coli, hongos) | Infecciones, zoonosis | Media | Moderada | Guantes, ropa de trabajo exclusiva, lavado de manos, vestuario con duchas, vacunación antitetánica, lavado de ropa en planta
| Ruido | Ventiladores, extractor, pala cargadora | Hipoacusia | Alta | Moderada | Ventiladores con silenciadores; sala de control aislada; protectores auditivos (nivel estimado 85–90 dBA junto a ventiladores)
| Estrés térmico | Trabajo junto al hogar y secador en verano | Golpe de calor | Media | Moderada | Ventilación cenital; pausas; hidratación; ropa liviana
| Caídas a distinto nivel | Silo, elevador, techo del secador, plataforma del hogar | Fracturas | Media | Grave | Escaleras con guardahombre; plataformas con barandas; arnés para trabajos > 2 m
| Atropellamiento | Pala cargadora y camiones | Lesiones graves | Media | Grave | Circulación demarcada; alarma de retroceso; chaleco reflectivo; velocidad máxima 10 km/h
| Ergonómico | Carga de sacos, limpieza de bandas | Lumbalgias | Media | Leve | Carga a granel; herramientas de limpieza con mango largo; capacitación en levantamiento de cargas
## 12.3. Elementos de protección personal
Tabla 16. EPP por puesto de trabajo
| Puesto | EPP obligatorio
| Operario de campo (recepción, silo, cenizas) | Casco, botines de seguridad, guantes de nitrilo, máscara semifacial con filtro ABEK-P3, antiparras, protectores auditivos, ropa de trabajo exclusiva, chaleco reflectivo
| Operador de proceso (control y recorridas) | Casco, botines de seguridad, protectores auditivos, guantes térmicos para inspecciones, antiparras
| Mantenimiento | Lo anterior más guantes anticorte, careta facial para amolado, guantes dieléctricos clase 0 para tablero, arnés para altura
## 12.4. Protección contra incendios
La carga de fuego principal la constituyen el silo de cáscara (7,5 t, unos 100.000 MJ), el acopio de guano seco (hasta 30 t) y el hogar. Se adopta: extintores triclase ABC de 10 kg cada 15 m de recorrido y junto al tablero (uno de CO₂ de 5 kg); dos extintores de agua presurizada de 10 litros en el acopio; una red de hidrantes con dos bocas de 45 mm alimentadas por tanque de 20 m³ y bomba; rociadores en el silo de cáscara con activación por temperatura; detectores de humo en la sala de control y el depósito; salidas de emergencia señalizadas con apertura hacia afuera y luces de emergencia; y un plan de evacuación con punto de reunión y simulacros semestrales. Se prohíbe fumar en toda la planta.
## 12.5. Señalización
Toda la planta se señaliza conforme a la Norma IRAM 10005: carteles de prohibición (fumar, ingreso de personal no autorizado), obligación (uso de EPP), advertencia (riesgo eléctrico, superficie caliente, atrapamiento, carga suspendida), salvamento (salidas, extintores, duchas) e información. Las zonas de circulación de la pala cargadora se demarcan en el piso con pintura amarilla, y las partes móviles y protecciones se pintan de amarillo y negro.
## 12.6. Procedimientos de trabajo seguro
- Bloqueo y etiquetado (LOTO): antes de cualquier intervención en cintas, sinfines o hogar, se corta y bloquea con candado el seccionador del circuito y se verifica ausencia de tensión y de movimiento.
- Trabajo en el interior del secador: solo con el equipo frío (< 40 °C), ventilado, con bloqueo eléctrico, con vigía en el exterior y comunicación permanente.
- Ingreso al silo de cáscara: considerado espacio confinado; requiere permiso de trabajo, medición de oxígeno y CO, arnés con línea de vida y vigía.
- Encendido del hogar: procedimiento escrito; nunca usar líquidos inflamables; verificar purga previa.
- Capacitación inicial y anual en riesgos del puesto, uso de EPP, extintores y primeros auxilios.
# 13. Estudio de impacto ambiental
## 13.1. Marco normativo
El proyecto se rige por la Ley Nacional 25.675 General del Ambiente, que establece la obligación de evaluación de impacto ambiental para toda obra o actividad susceptible de degradar el ambiente; por la Ley Nacional 25.612 de gestión integral de residuos industriales; y, en la provincia de Entre Ríos, por la Ley 6.260 de Prevención y Control de la Contaminación por parte de las Industrias y su Decreto Reglamentario 5.837/91, que exigen la presentación de un Estudio de Impacto Ambiental ante la Secretaría de Ambiente provincial y la obtención del Certificado de Aptitud Ambiental previo a la habilitación, con renovación periódica. Son aplicables además la Ley provincial 9.172 de aguas, el Decreto 4.977/09 sobre categorización de industrias, la Resolución 66/12 de la Secretaría de Ambiente sobre establecimientos avícolas y las ordenanzas municipales de Crespo sobre radicación industrial y olores. Como industria de segunda categoría, la planta debe presentar el estudio completo, un plan de gestión ambiental y monitoreos anuales.
## 13.2. Situación sin proyecto (línea de base)
En la situación actual el guano se acumula en fosas o pilas a cielo abierto durante semanas o meses, con emisión continua de amoníaco (hasta 50 % del nitrógeno se pierde a la atmósfera), sulfuro de hidrógeno y metano; proliferación de moscas que afecta a las viviendas vecinas; escurrimiento de lixiviados ricos en nitratos, fósforo y bacterias hacia suelos, cursos de agua y napas; y aplicación de guano fresco en lotes agrícolas, que genera quemado de cultivos, olores y contaminación difusa. Es una de las principales causas de conflicto entre granjas avícolas y vecinos en la zona de Crespo.
## 13.3. Identificación de impactos del proyecto
Tabla 17. Matriz de impactos ambientales (metodología de Leopold simplificada; signo, intensidad 1–3, extensión, duración)
| Factor ambiental | Acción del proyecto | Impacto | Valoración | Medida de mitigación
| Aire – olores y NH₃ | Recepción de guano fresco | Negativo, moderado, puntual, permanente | −2 | Recepción bajo techo con ventilación forzada hacia el scrubber; tiempo de permanencia < 2 h; limpieza diaria con agua
| Aire – olores y NH₃ | Escape del secador | Negativo, alto sin tratamiento | −3 → −1 | Ciclón + lavador de gases húmedo con solución ácida (ácido sulfúrico diluido) que captura > 90 % del NH₃ formando sulfato de amonio, reutilizable como fertilizante
| Aire – material particulado | Ciclón de humos, manipulación de cenizas y producto seco | Negativo, moderado | −2 → −1 | Ciclón de alta eficiencia (> 85 % para partículas > 10 µm); cenizas en tolva cerrada; acopio bajo techo; humedecido del producto si se genera polvo
| Aire – gases de combustión | Hogar de cáscara | Negativo, bajo (CO₂ biogénico neutro; CO y NOx) | −1 | Combustión con aire secundario; control de exceso de aire; chimenea de 12 m; monitoreo semestral de CO, NOx y MP
| Aire – GEI | Sustitución de la descomposición anaeróbica del guano (CH₄, N₂O) y uso de biomasa | Positivo, alto | +3 | El secado evita emisiones de metano y óxido nitroso; la cáscara es carbono neutral
| Agua – superficial y subterránea | Lixiviados de recepción; purga del scrubber | Negativo, moderado | −2 → −1 | Piso impermeable con canaleta a cámara estanca; el líquido se incorpora al secador; purga del scrubber (sulfato de amonio) se vende o aplica como fertilizante líquido; sin vertido
| Agua – consumo | Reposición del scrubber | Negativo, bajo | −1 | Circuito cerrado con reposición de 0,5 m³/día; recolección de agua de lluvia
| Suelo | Aplicación de guano seco en lugar de fresco | Positivo, alto, regional | +3 | Fertilizante estabilizado, dosificable, sin patógenos ni quemado de cultivos
| Suelo | Disposición de cenizas (450 kg/día) | Negativo, bajo | −1 | Ceniza de cáscara (sílice amorfa) inerte: se mezcla con el fertilizante (aporta silicio) o se vende a cementeras; nunca a cielo abierto
| Fauna – vectores | Eliminación de acopios de guano fresco | Positivo, alto | +3 | Reducción drástica de moscas y roedores
| Ruido | Ventiladores y pala cargadora | Negativo, bajo | −1 | Silenciadores; nave cerrada; nivel en el límite del predio < 55 dBA diurno
| Paisaje | Nave y chimenea de 12 m | Negativo, bajo | −1 | Cortina forestal perimetral; colores integrados
| Socioeconómico | Empleo, valorización de residuos, reducción de conflictos vecinales | Positivo, alto | +3 | 2 puestos directos; ingresos por fertilizante; mejor relación con la comunidad
| Etapa de construcción | Movimiento de suelos, tránsito, residuos de obra | Negativo, bajo, temporal | −1 | Gestión de residuos de obra; horarios de trabajo; riego de caminos
## 13.4. Sistema de tratamiento del aire de escape
El aire agotado del secador (27.270 kg/h; con el aire ajustado al 15 % sale a 33-37 °C y casi saturado de vapor, con olores, amoníaco y polvo) es el efluente ambiental más relevante y su tratamiento se diseñó en dos etapas. La primera es un ciclón de 1,8 m de diámetro y 5,5 m de altura, en acero inoxidable, que retiene el material particulado grueso (partículas de guano seco arrastradas por el aire, con una eficiencia mayor al 85 % para partículas de más de 10 micrones), que se descarga por una válvula rotativa y se reincorpora al producto. Como el escape sale casi saturado, el ducto de Ø800 mm y el ciclón se aíslan con lana de roca de 50 mm y chapa de protección, el ducto se tiende con pendiente hacia el ciclón y se prevé una purga de condensado con sifón en el fondo del ciclón y en los puntos bajos del ducto, conducida a la cámara de lixiviados. La segunda es un lavador de gases húmedo de relleno (scrubber) de 2,2 m de diámetro y 6 m de altura, en PRFV, donde el gas asciende en contracorriente con una solución de agua acidulada con ácido sulfúrico a pH 3, recirculada por una bomba de 3 kW. El amoníaco reacciona con el ácido formando sulfato de amonio, un fertilizante soluble, y los compuestos odoríferos se absorben en el agua. La eficiencia esperada es de más del 90 % para el amoníaco y del 80 % para los olores. El extractor de 22 kW aguas abajo del scrubber vence las pérdidas de carga de todo el circuito y descarga el aire limpio, a menos de 40 °C y saturado (en invierno se ve un penacho de vapor), por una chimenea de 10 m de altura. La purga del scrubber, de unos 0,5 m³ por día, se almacena en un tanque y se vende como fertilizante líquido o se aplica en lotes propios.
## 13.5. Emisiones de la chimenea de humos
Los humos de combustión de la cáscara de arroz (2.280 kg/h a 200 °C) pasan por un ciclón de cenizas volantes antes de la chimenea. Las emisiones esperadas, en base a bibliografía de combustión de cáscara en parrilla, son: material particulado 50–150 mg/Nm³ luego del ciclón, monóxido de carbono 100–300 mg/Nm³, óxidos de nitrógeno 150–250 mg/Nm³ y óxidos de azufre despreciables (la cáscara casi no tiene azufre). Estos valores cumplen con los límites del Decreto 5.837/91 de Entre Ríos para fuentes fijas de combustión de biomasa. Se prevé un monitoreo semestral por laboratorio habilitado con toma de muestra isocinética en la chimenea.
## 13.6. Plan de gestión ambiental
- Programa de monitoreo: olores en el límite del predio (olfatometría, trimestral), emisiones de chimenea (semestral), calidad del agua de la cámara de lixiviados y de dos freatímetros (semestral), ruido perimetral (anual).
- Programa de gestión de residuos: cenizas (registro de generación y destino), purga del scrubber (registro y destino), residuos de mantenimiento (aceites, filtros, trapos: gestor habilitado de residuos peligrosos, Ley 24.051), residuos sólidos urbanos.
- Programa de contingencias: derrame de guano fresco, derrame de ácido del scrubber (kit de neutralización, duchas y lavaojos), incendio del silo, falla del scrubber (parada del secador en menos de 30 minutos).
- Programa de capacitación ambiental del personal y de comunicación con los vecinos (canal de reclamos por olores).
- Auditoría ambiental anual y renovación del Certificado de Aptitud Ambiental.
| Balance ambiental del proyecto El impacto neto del proyecto es claramente positivo: transforma una fuente permanente de olores, vectores y contaminación de suelos y aguas en una planta cerrada con emisiones controladas, elimina la emisión de metano y óxido nitroso de la descomposición del guano, usa una fuente de energía renovable y devuelve al suelo, en forma segura, los nutrientes que las gallinas extrajeron del alimento. Los impactos negativos residuales (emisiones de combustión, cenizas, ruido) son de baja magnitud y mitigables con las medidas previstas.
# 14. Plan de mantenimiento
## 14.1. Estrategia
Se adopta un mantenimiento preventivo programado, con inspecciones diarias del operador, tareas semanales y mensuales del propio personal y tareas semestrales y anuales con apoyo de terceros (alineación y balanceo de ventiladores, termografía del tablero, inspección del refractario). Las fallas más probables son el desgaste y descentrado de las bandas, el ensuciamiento de los tubos del intercambiador por cenizas volantes, la obstrucción del scrubber y el desgaste de las hélices de los sinfines por abrasión del guano y de la sílice de la cáscara. Se recomienda tener en depósito los repuestos críticos: un tramo de malla de 2 m, rodamientos UCF 212 y unidades UCT 210, cadena y piñones, correas de los ventiladores, PT100, un módulo de PLC y un variador de 0,75 kW.
## 14.2. Programa de mantenimiento preventivo
Tabla 18. Plan de mantenimiento preventivo
| Equipo | Tarea | Frecuencia | Responsable
| Cintas | Inspección visual de malla, centrado, tensión; limpieza de restos adheridos con rasqueta y agua a presión al final del turno | Diaria | Operador
| Cintas | Verificar guías (PTFE en los pisos 2 y 3, UHMW-PE en el piso 1), rodillos de retorno, cadenas laterales; lubricar cadenas de transmisión con aceite de alta temperatura | Semanal | Mantenimiento
| Cintas | Revisar los faldones de sellado de los bordes y reemplazar el labio de goma gastado | Mensual | Mantenimiento
| Escape | Purgar el condensado del ciclón y de los puntos bajos del ducto Ø800; verificar el sifón | Semanal | Operador
| Descarga | Verificar el registro del TT-05 (≥ 70 °C durante 60 min) y la temperatura del producto enfriado (< 40 °C) | Diaria | Operador
| Cintas | Medir desgaste de malla y guías; reemplazar tramos dañados; verificar alineación de tambores | Semestral | Mantenimiento
| Motorreductores | Control de nivel y fugas de aceite; ruido y temperatura | Semanal | Operador
| Motorreductores | Cambio de aceite sintético (sinfín-corona) | Anual (o 5.000 h) | Mantenimiento
| Rodamientos UCF / UCT | Reengrase con grasa de litio para alta temperatura (2 golpes de bomba) | Mensual | Mantenimiento
| Ejes de tambores | Control por partículas magnéticas de escalones y chaveteros (ver pruebas) | Cada 2 años | Especialista
| Anclajes y placas base | Reapriete a 80 N·m y control de fisuras del grout | Anual | Mantenimiento
| Sinfines | Verificar espesor de hélice, holgura con canaleta, rodamientos de extremo | Mensual | Mantenimiento
| Esparcidor | Verificar paletas, reponer las desgastadas | Mensual | Mantenimiento
| Hogar | Retiro de cenizas del cenicero; limpieza de parrilla | Diaria | Operario de campo
| Hogar | Inspección del refractario; reparación de grietas con mortero refractario | Semestral | Especialista
| Intercambiador | Deshollinado de tubos con cepillo o aire comprimido por los cabezales; retiro de cenizas de la carcasa | Semanal | Mantenimiento
| Intercambiador | Inspección de tubos del primer paso (corrosión, deformación); prueba de estanqueidad | Anual | Especialista
| Ventiladores | Limpieza de filtros de aspiración; verificar vibraciones y ruido | Semanal | Operador
| Ventiladores | Limpieza de rodete; balanceo dinámico; cambio de rodamientos | Anual | Especialista
| Ciclón y scrubber | Control de pH y nivel de la solución; limpieza de boquillas; purga | Diaria / semanal | Operador
| Ciclón y scrubber | Limpieza del relleno; inspección de la bomba; reposición de ácido | Mensual | Mantenimiento
| Silo de cáscara | Control de nivel y temperatura; verificar sinfín y válvula cortafuego | Diaria | Operario de campo
| Tablero eléctrico | Limpieza de filtros de ventilación; verificar alarmas de VFD | Mensual | Mantenimiento
| Tablero eléctrico | Reapriete de borneras; termografía; prueba de diferenciales y parada de emergencia; medición de puesta a tierra | Anual | Electricista matriculado
| Instrumentación | Verificación de PT100 con termómetro patrón; calibración del sensor de humedad con estufa de laboratorio | Trimestral | Mantenimiento
| Paneles y ductos | Inspección de juntas y aislación; reparación de fugas de aire caliente | Semestral | Mantenimiento
| Estructura | Inspección de corrosión y soldaduras; retoque de pintura | Anual | Mantenimiento
| Protección contra incendios | Control de carga de extintores; prueba de hidrantes y rociadores | Mensual / anual | Servicio de H&S
## 14.3. Indicadores
Se propone medir la disponibilidad de la planta (horas de marcha sobre horas programadas, objetivo mayor al 92 %), el tiempo medio entre fallas (MTBF) y el tiempo medio de reparación (MTTR), el consumo específico de cáscara (kg por tonelada de agua evaporada, objetivo 470) y el consumo eléctrico específico (kWh por tonelada de producto, objetivo menor a 170). Una desviación en el consumo de cáscara es el primer indicio de ensuciamiento del intercambiador.
# 16. Beneficios del proyecto
## 16.1. Beneficios ambientales
- Eliminación de los acopios de guano fresco a cielo abierto y de sus olores, moscas, roedores y lixiviados.
- Reducción de las emisiones de gases de efecto invernadero: se evita la generación de metano y óxido nitroso de la descomposición anaeróbica y se emplea biomasa renovable en lugar de combustibles fósiles.
- Captura del amoníaco en el lavador de gases y su conversión en sulfato de amonio, evitando la contaminación atmosférica y recuperando nitrógeno.
- Protección de suelos y napas: el fertilizante seco se dosifica con precisión y no se lava con las lluvias.
- Valorización de dos residuos agroindustriales de la provincia: el guano avícola y la cáscara de arroz.
## 16.2. Beneficios sanitarios
- Higienización del producto por temperatura (más de 55 °C durante más de una hora), con eliminación de Salmonella, E. coli y parásitos: el fertilizante puede aplicarse en cultivos hortícolas.
- Mejora de las condiciones sanitarias de la propia granja (menos amoníaco y moscas en los galpones, mejor bienestar animal y productividad de las aves).
- Mejores condiciones de trabajo para los operarios respecto de la manipulación de guano fresco.
## 16.3. Beneficios económicos
- Conversión de un costo (retiro y disposición del guano) en un ingreso (venta de fertilizante), con un beneficio neto anual del orden de USD {{neto_1t}} en un turno y USD {{neto_2t}} en dos turnos.
- Reducción del volumen y del peso a transportar a un tercio, lo que abarata el flete y amplía el radio de comercialización.
- Producto estable, almacenable durante meses y vendible en el momento de mejor precio.
- Independencia energética respecto del gas y de la electricidad para el proceso térmico, con un combustible local de precio estable.
- Posibilidad de escalar a dos turnos o a peletizado con inversiones marginales.
## 16.4. Beneficios sociales y de cumplimiento
- Cumplimiento de la normativa ambiental provincial y municipal, y eliminación de la principal causa de conflictos con vecinos y de sanciones a las granjas.
- Generación de empleo calificado (operadores de proceso, mantenimiento electromecánico) en la zona.
- Imagen de empresa responsable, cada vez más valorada por los compradores de huevos y por las certificaciones de producción.
- Desarrollo de tecnología nacional: todos los componentes principales pueden fabricarse en talleres metalúrgicos de Crespo y Paraná.
# Bibliografía
- Mujumdar, A. S. (2014). Handbook of Industrial Drying (4ª ed.). CRC Press.
- Perry, R. H. y Green, D. W. (2008). Perry's Chemical Engineers' Handbook (8ª ed.). McGraw-Hill. Sección 12: Psychrometry, evaporative cooling and solids drying.
- McCabe, W., Smith, J. y Harriott, P. (2007). Operaciones unitarias en ingeniería química (7ª ed.). McGraw-Hill.
- Groover, M. P. (2007). Fundamentos de manufactura moderna (3ª ed.). McGraw-Hill.
- Sobrevila, M. A. (1985). Máquinas eléctricas. Ed. Marymar.
- Fraile Mora, J. (2008). Máquinas eléctricas (6ª ed.). McGraw-Hill.
- Muther, R. (1981). Distribución en planta (4ª ed.). Hispano Europea.
- Palacios Acero, L. C. (2016). Ingeniería de métodos, movimientos y tiempos (2ª ed.). Ecoe Ediciones.
- Shigley, J. E. y Mischke, C. R. (2008). Diseño en ingeniería mecánica (8ª ed.). McGraw-Hill.
- CEMA (2014). Belt Conveyors for Bulk Materials (7ª ed.). Conveyor Equipment Manufacturers Association.
- Asociación Electrotécnica Argentina (2006). Reglamentación para la ejecución de instalaciones eléctricas en inmuebles, AEA 90364.
- INTA (2019). Manejo de residuos en granjas avícolas de postura. Estación Experimental Agropecuaria Concepción del Uruguay.
- INTA (2015). Caracterización de la cama de pollo y el guano de ponedoras como enmienda orgánica. Ediciones INTA.
- Kanawaty, G. (1996). Introducción al estudio del trabajo (4ª ed.). Oficina Internacional del Trabajo.
- Ley Nacional 19.587 de Higiene y Seguridad en el Trabajo y Decreto 351/79.
- Ley Nacional 25.675 General del Ambiente; Ley 24.051 de Residuos Peligrosos.
- Ley 6.260 de la Provincia de Entre Ríos y Decreto Reglamentario 5.837/91; Decreto 4.977/09.
- Blank, L. y Tarquin, A. (2012). Ingeniería económica (7ª ed.). McGraw-Hill.
- Catálogos técnicos: Siemens (S7-1200, SINAMICS G120), WEG (motores W22), SKF (rodamientos), Ashworth (bandas de malla).
# Anexo B. Memoria de cálculo resumida
Tabla 24. Resumen de cálculos
| Cálculo | Expresión | Resultado
| Sólido seco | m_in·(1−X_in) | 280 kg/h
| Producto seco | m_s/(1−X_out) | 329 kg/h
| Agua evaporada | m_in − m_out | 671 kg/h
| Calor útil | W·(cp·ΔT + h_fg) + m_s·cp_s·ΔT + m_wr·cp·ΔT | 480 kW
| Calor con pérdidas | 1,10 · Q_útil | 528 kW
| Aire de secado | Q/(cp_a·ΔT_aire) | 26.600 kg/h – 30.700 m³/h
| Humedad absoluta salida | Y_in + W/m_aire | 33 g/kg
| Potencia generador | m_aire·cp_a·(135−18) | 882 kW
| Combustible | Q_gen/(PCI·η) | 314 kg/h
| Cenizas | 0,18 · m_comb | 56 kg/h
| Superficie de secado | W/10 kg/m²h | 67 m² → 72 m² adoptados
| Tiempo de residencia | m_contenido/m_promedio | 97 min
| Velocidad de banda | L/(t_res/3) | 0,37 m/min
| Tensión efectiva banda | μ·g·(m_c + m_r)·1,15 | 2.980 N
| Par en tambor | F_e·D/2 | 471 N·m
| Diámetro eje (torsión) | (16T/πτ)^(1/3) | 39 mm → 60 mm (Ø50 en la corona)
| Velocidad tambor | v/(π·D) | 0,37 rpm
| Relación total de transmisión | 1.400/0,37 | 1:3.780 (300 × 5 × VFD ≈ 20 Hz)
| Cinta de alimentación (DIN 22101) | 3,24 m³/h a 0,10 m/s | 1,25 m³/h a 3,9 cm/s
| Sinfín descarga | 47,1·D²·s·n·φ | 1,16 m³/h
| Ventiladores impulsión | Q·Δp/η | 18,3 kW eje → 2 × 15 kW
| Corriente motores | P/(√3·U·cosφ·η) | ver la tabla de motores del capítulo eléctrico
| Demanda máxima | Σ P × 0,8 | 54 kW – 109 A
| LMTD intercambiador | (ΔT1−ΔT2)/ln(ΔT1/ΔT2) | 390 K
| Superficie intercambiador | Q/(U·LMTD) | 91 m² – 114 tubos
| Aire de combustión | m_comb·4,6·1,4 | 2.020 kg/h
| Carga de parrilla | m_comb/A_parrilla | 523 kg/h·m²
| Silo de cáscara | 3 días · 2,5 t / 110 kg/m³ | 68 m³ → 70 m³
| Eje motriz a fatiga (S1) | DE-Goodman, Shigley | n = {{n_eje}} ≥ 1,5
| Eje de reenvío a fatiga | DE-Goodman, Ø60 / Ø50 | n = {{n_reenvio}} ≥ 1,5
| Anclajes químicos M16 | uso al corte V/V_Rd | {{uso_anclaje}} %
# Anexo C. Distribución de tareas del grupo
Tabla 25. Responsabilidades
| Integrante | Área
| Gabriel Müller | Coordinación, ingeniería del proceso, balances, informe
| Baltazar Goette | Ingeniería mecánica: cintas, tambores, transmisiones
| Pablo Hofstetter | Ingeniería eléctrica: motores, tablero, unifilar
| Facundo Stegmann | Control automático, instrumentación, PLC
| Martín Bernhardt | Generador de aire caliente, combustión, intercambiador
| Bautista Belluzzo | Seguridad e higiene, impacto ambiental, mantenimiento, economía
(Distribución propuesta; el grupo puede modificarla según la participación real de cada integrante.)
