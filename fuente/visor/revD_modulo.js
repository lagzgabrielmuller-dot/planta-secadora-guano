/* =====================================================================
   SECADORA DE GUANO 8 t/día — AGREGADOS REV. D AL MODELO 3D
   Este archivo se inyecta dentro del visor (visor.html) por
   build_revD.py. Usa las funciones de dibujo del propio visor:
     Z   caja (x0,y0,z0,x1,y1,z1)          Be  cilindro entre dos puntos
     Ln  cilindro vertical                  Xi  barra cuadrada entre puntos
     Js  barrido de un perfil               fe  coordenadas planta -> 3D
     v   materiales del visor               Xn  textura dibujada en canvas
   Coordenadas: x hacia el Este, y hacia el Norte, z hacia arriba (m).
   No modifica ni borra nada de la Rev. C: solo agrega.
   ===================================================================== */

var __RD = { solo: !1, grupos: {}, sprites: [], partes: [] };

var __RD_SEC = { x0: 10.2, x1: 25.7, y0: 6.9, y1: 11.0, z0: -0.2, z1: 5.6 };

/* ---------------- Datos de las piezas nuevas (lista, globos y fichas) --------------- */
var __RD_PARTES = [
  // ---- agregados de seguridad, instrumentación y mantenimiento (ítems 1 a 24)
  { n: "D1", g: "seg", nom: "Puertas de inspección: manijas y microinterruptores", plano: "P17", lp: null,
    txt: "Se completan las 6 puertas 700 × 600 (4.9, una por piso y por lado) con manija, leva de accionamiento, microinterruptor de seguridad ZS-01 a ZS-06 (NC, cat. 3) y caja de conexión IP65 con caño. Abrir una puerta detiene las cintas y el dosificador (M5, M6, M7, M8)." },
  { n: "D2", g: "seg", nom: "Protecciones de transmisiones y ejes", plano: "P17", lp: null,
    txt: "Tapas cubre-eje amarillas en los 12 extremos de ejes de tambores (motrices y de reenvío), cubreacople del esparcidor (M9), de la bomba del lavador (M14) y del sinfín de cáscara (M12), y rejillas de protección en las bocas de aspiración de los ventiladores M1, M2 y M4. Los cárteres de cadena de las cintas ya existían y no se modifican." },
  { n: "D3", g: "seg", nom: "Pasarelas, plataformas, escaleras y barandas", plano: "P17", lp: [14.5, 19.6, 7.6],
    txt: "Jaula guardahombre en la escalera marinera del secador (4.13), del lavador y del silo; plataforma semicircular con baranda de 1,0 m, travesaño intermedio y rodapié en el techo del ciclón y del lavador; plataforma del cabezal del elevador con escalera; baranda perimetral en el techo del silo; escalera marinera con jaula a la plataforma de muestreo de la chimenea; barandas de distanciamiento frente al hogar." },
  { n: "D4", g: "seg", nom: "Paradas de emergencia tipo hongo", plano: "P17", lp: null,
    txt: "PE-01 zona de alimentación (tolva), PE-02 entrada del secador, PE-03 zona de mantenimiento (lado de motorreductores), PE-04 salida del secador y elevador, PE-05 zona del generador (acceso a la nave), PE-06 anexo (acceso Norte), PE-07 zaranda y envasado. Hongo rojo Ø40 con enclavamiento sobre caja amarilla, cableado al relé de seguridad cat. 3 del TGF (el TGF y el TS-1 ya tenían su propio hongo)." },
  { n: "D5", g: "seg", nom: "Sensores de instrumentación", plano: "P22", lp: null,
    txt: "TT-01 PT100 aire de entrada · TT-02/03/04 PT100 salida de cada piso · TT-05 en la tolva de retención de la descarga (≥ 70 °C durante 60 min, Rev. F) · TT-06 termocupla K humos del hogar · TT-07 PT100 chimenea · TT-08 aire ambiente con abrigo · MT-01 humedad NIR en la descarga (lazo MIC-01 en cascada sobre TIC-01, Rev. F) · MT-02 opcional sobre la cinta de alimentación · PT-01 presión diferencial del plenum · BE-01 detector de llama UV · PS-01 presostato de depresión del hogar · LS-01 nivel tolva · LS-02A/B nivel alto y bajo del silo · TS-01 temperatura del silo · LS-03 nivel y AT-01 pH del lavador · SS-01/02/03 giro de las cintas · ZS-10/11 centrado de banda." },
  { n: "D6", g: "seg", nom: "Puntos de medición (tomas de presión y temperatura)", plano: "P18", lp: null,
    txt: "Boquillas roscadas de 1/2\" con tapón y válvula en: entrada de aire caliente (2), salida de aire del secador (2), plenum inferior (1), ducto al lavador (1), retorno de recirculación (1), chimenea de humos a +8,35 m (2 tomas isocinéticas a 90°) y chimenea del lavador (1)." },
  { n: "D7", g: "seg", nom: "Recirculación parcial de aire (retorno a la entrada)", plano: "P18", lp: [19.9, 22.1, 8.6],
    txt: "Derivación Ø500 a la salida del ciclón (aire ya desempolvado) → compuerta regulable CD-03 con actuador 24 V → bajada por el muro Oeste del anexo → cámara de mezcla en la toma de aire de los ventiladores M1-M2, con compuerta de aire fresco CD-02. Rev. F (estudio térmico): con el aire ajustado al 15 % el escape sale casi saturado y la recirculación casi no ahorra (1,2 % de cáscara a 18 °C; en verano gasta 1,1 % más), así que la CD-03 queda normalmente cerrada y solo abre (0 a 35 %) si la humedad relativa de la cámara de mezcla está por debajo del 90 %. Es la opción prevista en la memoria (§6.5 y §6.7)." },
  { n: "D8", g: "seg", nom: "Compuertas de regulación y by-pass de humos", plano: "P18", lp: null,
    txt: "CD-01 entrada de aire caliente al secador, CD-02 aire fresco, CD-03 recirculación, CD-04 salida del secador (con actuadores eléctricos 24 V, señal 0-10 V) y CD-05 compuerta de by-pass de humos del hogar a la chimenea con servomotor (abre ante parada de ventiladores o sobretemperatura, memoria §10.5)." },
  { n: "D9", g: "seg", nom: "Registros, tapas y bocas de limpieza", plano: "P17", lp: null,
    txt: "Boca de inspección Ø450 en el ciclón; 2 bocas de hombre en el lavador; registros abulonados en el ducto caliente y en el ducto de aire agotado; tapas abisagradas en el sinfín de descarga; boca de limpieza en la tolva de recepción; tapas con manijas en los cabezales del intercambiador; boca de inspección en el silo." },
  { n: "D10", g: "seg", nom: "Lavador de gases: complementos", plano: "P18", lp: null,
    txt: "Anillo de boquillas de pulverización, sensor de pH AT-01, nivel LS-03, drenaje con válvula a la cámara de purga, línea de purga a tanque IBC de sulfato de amonio, dosificación de ácido sulfúrico desde IBC con bandeja antiderrame y bomba dosificadora, ducha de emergencia con lavaojos." },
  { n: "D11", g: "seg", nom: "Ciclón: complementos", plano: "P17", lp: null,
    txt: "Boca de inspección, motor de la válvula rotativa de descarga existente, conexión de mantenimiento (tapa ciega en la entrada), plataforma superior y escalera. No se cambia su tamaño ni geometría." },
  { n: "D12", g: "seg", nom: "Generador: complementos de seguridad y mantenimiento", plano: "P17", lp: null,
    txt: "Puerta de inspección y mirilla del hogar, detector de llama BE-01, termocupla TT-06, presostato PS-01, barandas de distanciamiento, cubre-acoples, quemador piloto de biogás (reemplaza el encendido manual) y compuerta de by-pass de humos CD-05." },
  { n: "D13", g: "seg", nom: "Silo de cáscara: seguridad", plano: "P15", lp: null,
    txt: "Sensores de nivel LS-02A (alto) y LS-02B (bajo), cable de temperatura TS-01, boca de hombre en el techo, venteo de alivio, válvula guillotina de corte a la salida, rociadores con anillo en el techo y montante con válvula de diluvio, jaula en la escalera y baranda perimetral." },
  { n: "D14", g: "seg", nom: "Sistema de cenizas: descarga y limpieza", plano: "P17", lp: null,
    txt: "Manga de descarga de la tolva de cenizas (16) a contenedor metálico con ruedas y tapa, tapa de limpieza del cenicero y mirilla de inspección. Las cenizas de cáscara (sílice amorfa) se retiran a diario." },
  { n: "D15", g: "seg", nom: "Canalizaciones eléctricas", plano: "P17", lp: null,
    txt: "Bandeja de instrumentación de 150 mm separada 400 mm por debajo de la bandeja de potencia existente; bandejas nuevas hacia el anexo, el lavador y la recepción; bajadas con caño flexible a cada motor y sensor; cajas de conexión. Separación mínima de 300 mm a ductos calientes (AEA 90364)." },
  { n: "D16", g: "seg", nom: "Puesta a tierra, equipotencialidad y pararrayos", plano: "P17", lp: [21.6, 25.2, 13.9],
    txt: "Anillo de cobre desnudo de 50 mm² enterrado a 0,6 m alrededor de la nave y del anexo, con 8 jabalinas Cu-Ac 5/8\" × 3 m en cámaras de inspección (PAT-1 a PAT-8; R ≤ 10 Ω, IRAM 2281 y AEA 90364). Barra equipotencial principal (BEP) en la sala de control, a la que llegan el PE del TGF y del TG2, la estructura de la nave, las bandejas, los ductos y las cañerías. Pararrayos Franklin en la chimenea de humos, la chimenea del lavador y el silo de cáscara, con bajadas de cobre de 50 mm² y guardacable de 2 m (IRAM 2184). La zona de biogás tiene su propia malla (PAT-9 y PAT-10) unida al anillo, y los tanques y la antorcha van puenteados a ella." },
  { n: "D17", g: "seg", nom: "Iluminación de emergencia y de zonas de trabajo", plano: "P15", lp: null,
    txt: "Luminarias autónomas de emergencia (3 h) con cartel SALIDA sobre cada salida, en la sala de control y en el anexo; proyectores LED sobre la plataforma de la zaranda, el ciclón y el lavador. Las 18 campanas LED de la nave ya existían." },
  { n: "D18", g: "seg", nom: "Señalización de seguridad (IRAM 10005)", plano: "P15", lp: null,
    txt: "Carteles de peligro eléctrico, superficie caliente, riesgo de atrapamiento, uso obligatorio de EPP, salida de emergencia, matafuego, parada de emergencia, prohibido fumar y riesgo de incendio, ubicados en los accesos y junto a cada riesgo, sin recargar el modelo." },
  { n: "D19", g: "seg", nom: "Protección contra incendios", plano: "P15", lp: [12.0, 19.2, 1.6],
    txt: "Soportes, chapa baliza y cartel para los 8 matafuegos existentes de la nave; 15 matafuegos nuevos (CO₂ en el TGF, agua en el acopio, anexo, silo, lavador, depósito, biogás y garita); 4 hidrantes con gabinete (HI-1 a HI-4, boca de 45 mm, manguera de 25 m); detectores de humo y térmicos; pulsadores manuales con sirena; central de incendio en la sala de control; rociadores del silo. Carga de fuego y potencial extintor según Dec. 351/79, Anexo VII (plano P16)." },
  { n: "D20", g: "seg", nom: "Drenajes y canaletas", plano: "P17", lp: null,
    txt: "Canaleta con rejilla bajo el lado Sur del secador para el lavado de bandas, cámara de enlace y caño PVC Ø110 a la cámara de lixiviados (26); canaleta perimetral del lavador con cámara de purga; rejilla del lavadero en el playón P1. Todo el líquido orgánico va al biodigestor; el del vado sanitario (con desinfectante) no." },
  { n: "D21", g: "seg", nom: "Puntos de lubricación", plano: "P22", lp: null,
    txt: "Engrasadores remotos: bloque de lubricación en el lado Sur del secador con líneas a los rodamientos de cada tambor; engraseras en rodamientos de ventiladores y cabezal del elevador; lubricadores de goteo sobre las cadenas de transmisión." },
  { n: "D22", g: "seg", nom: "Detalles de mantenimiento: tensores y tapas", plano: "P17", lp: null,
    txt: "Tornillos tensores M20 con contratuerca visibles y accesibles en los 6 soportes de los tambores de reenvío, tapas abulonadas y bulones en registros." },
  { n: "D23", g: "seg", nom: "Placas de identificación de equipos", plano: "P22", lp: null,
    txt: "Placas de aluminio con el tag del proyecto en motores (M1 a M15), ventiladores, bomba, cintas, sinfines, ciclón, lavador, generador y sensores principales." },
  { n: "D24", g: "flu", nom: "Flechas de flujo", plano: "P18", lp: [18, 9.3, 5.6],
    txt: "Guano: tolva → cinta → esparcidor → 3 cintas → descarga → elevador → acopio o zaranda. Aire: generador → intercambiador → secador → ciclón → lavador → chimenea. Recirculación: salida del ciclón → compuerta → retorno parcial a la aspiración de los ventiladores." },
  // ---- sectores nuevos de la lista inicial
  { n: "E1", g: "amp", nom: "Estación de limpieza y desinfección de vehículos", plano: "P21", lp: [4, -14.5, 5.4],
    txt: "Sobre el acceso R1, pasando la báscula: vado sanitario de H°A° de 7,0 × 5,0 m con 15 cm de solución desinfectante y arco de aspersión de 14 boquillas (bomba M17 de 1,1 kW) con sensor de paso. Tanque de 1 m³ de desinfectante con bandeja. El efluente del vado NO va al biodigestor: se retira como residuo." },
  { n: "E2", g: "amp", nom: "Lavadero de camiones en el playón P1", plano: "P21", lp: [-0.6, 20, 2.2],
    txt: "Hidrolavadora trifásica de 150 bar (M16, 4 kW) con enrollador de manguera junto al portón P1; rejilla desarenadora en el playón. El camión de guano lava caja y ruedas antes de salir; el agua va por la canaleta a la cámara de lixiviados y de ahí al biodigestor. Pediluvio y lavabotas en el acceso del personal." },
  { n: "E3", g: "amp", nom: "Ventilación de la recepción: campana, extractor y biofiltro", plano: "P18", lp: [6.9, 14.8, 6.3],
    txt: "Campana de captación de 5 × 4 m sobre la pila de descarga y la tolva, ducto Ø600, extractor M23 de 4 kW (6.000 m³/h) y biofiltro abierto de 8,5 × 4,5 m con lecho de chips y compost de 1,2 m (carga 157 m³/m²·h, contacto 28 s) detrás del muro Norte. Más 6 extractores eólicos Ø600 en la cumbrera de la nave." },
  { n: "E4", g: "amp", nom: "Separador de cáscara de huevo y plumas (zaranda rotativa)", plano: "P19", lp: [28, 12.1, 5.2],
    txt: "Válvula desviadora en el cabezal del elevador (a acopio o a envasado) → trommel Ø0,9 × 3,0 m con malla de 6 mm, 18 rpm, 5° (M18, 1,1 kW) sobre plataforma a +3,0 m con baranda y escalera. Separa cáscara de huevo, plumas y terrones (≈ 2,5 %, 66 kg/día) a un big bag; el producto limpio cae a la tolva pulmón de 1,5 m³." },
  { n: "E5", g: "amp", nom: "Ensacadora dosificadora de bolsas de 25 kg", plano: "P19", lp: [28.6, 11.7, 2.6],
    txt: "Ensacadora de boca abierta con balanza (celda de carga, ±50 g), alimentador M19, cinta de salida M21 y cosedora M20. Capacidad 180 bolsas/h: la producción diaria (≈ 62 bolsas) se envasa en 20 minutos. Pallets de 40 bolsas junto al portón P3." },
  { n: "E6", g: "amp", nom: "Envasadora de bolsas chicas (1, 2 y 5 kg) para viveros", plano: "P19", lp: [29.6, 16.6, 2.9],
    txt: "Envasadora vertical con dosificador volumétrico y sellado térmico (M22, 2,2 kW) alimentada por un transportador flexible (M24) desde la tolva pulmón. ≈ 200 bolsitas/día con rótulo y registro SENASA para viveros y locales de plantas." },
  { n: "E7", g: "amp", nom: "Depósito de producto embolsado y expedición", plano: "P13", lp: [70, 6, 6.6],
    txt: "Nave nueva de 20 × 12 m en el Sector Este, muros de ladrillo macizo (F 120), portón de 4 m con dársena de carga, salida de emergencia SE3, 12 pallets de stock, transpaleta eléctrica. Sector de incendio independiente (S4)." },
  { n: "E8.1", g: "amp", nom: "Recepción y mezcla para biogás", plano: "P20", lp: [92.5, 25.5, 4.6],
    txt: "Fosa cubierta de 4 × 3 m para el guano de fines de semana y feriados (≈ 920 t/año que la secadora no procesa) y tanque de mezcla Ø3,5 m con agitador, donde se lleva al 8 % de sólidos con lixiviados, agua de lavado y líquido recirculado. Bomba trituradora M27." },
  { n: "E8.2", g: "amp", nom: "Biodigestores BD-1 y BD-2 (silos de biogás)", plano: "P20", lp: [73, 31, 8.2],
    txt: "Dos tanques de acero vitrificado Ø6,5 × 5,0 m (141 m³ útiles c/u), aislados, a 38 °C, TRH 30 días, carga 1,87 kg SV/m³·día, agitadores sumergibles M28 y M29. Techo de doble membrana que almacena el gas (37 m³ c/u). Producción ≈ 184 m³/día de biogás al 58 % de metano." },
  { n: "E8.3", g: "amp", nom: "Tanque de digestato (post-digestor)", plano: "P20", lp: [89, 33, 6.4],
    txt: "Tanque Ø8,0 × 4,0 m (201 m³) con techo de membrana que recupera el gas residual; 73 días de almacenamiento del biofertilizante líquido. Separador de tornillo prensa (M32): fracción sólida ≈ 1,8 t/día a platea techada; parte del líquido vuelve a la mezcla." },
  { n: "E8.4", g: "amp", nom: "Sala de cogeneración y tratamiento del biogás", plano: "P20", lp: [65, 19.2, 3.6],
    txt: "Contenedor con motogenerador a biogás de 25 kWe / 40 kWt (≈ 318 kWh eléctricos por día, ≈ 12,7 h de marcha) cuyo calor calefacciona los digestores (M34). Trampa de condensados, desulfurador de óxido de hierro, soplante M33, medidor y analizador de CH₄/H₂S, detector de gas y tablero TS-BIO fuera de zona clasificada." },
  { n: "E8.5", g: "amp", nom: "Antorcha de seguridad", plano: "P20", lp: [95, 17, 7],
    txt: "Quemador de excedentes de biogás de 25 m³/h con encendido automático y arrestallamas, a más de 15 m de los gasómetros." },
  { n: "E8.6", g: "amp", nom: "Línea de biogás al hogar (quemador piloto)", plano: "P20", lp: [29.3, 19.2, 2.2],
    txt: "Cañería de PEAD enterrada con mojones de señalización desde la sala de cogeneración hasta el anexo; montante con válvula de corte, arrestallamas, regulador y manómetro; quemador de encendido de 60 kW y llama piloto de 5 kW en el hogar (≈ 12 m³/día). Reemplaza el encendido manual con cáscara y encendedores." },
  { n: "E10", g: "amp", nom: "Ventilación general de la nave: extractores Campagnoni con campana y ventiladores móviles", plano: "P24", lp: [34.2, 7.2, 7.0],
    txt: "Caudal de diseño 54.700 m³/h (nave de 4.559 m³ × 12 renovaciones por hora en verano; el balance térmico pide 33.700 m³/h). 2 extractores Campagnoni AirTEC 1215 (Ø1.215 mm, 6 palas, 54.700 m³/h, 1,5 HP trifásico, 467 rpm) con campana (cono) de descarga y persianas, en lo alto del muro Este (+4,6 a +6,0 m): instalado 109.400 m³/h, ≈ 93.000 m³/h reales (≈ 20 renovaciones por hora). El aire entra por el portón P1 y las aberturas del Oeste y barre la nave a lo largo. En invierno anda uno solo. 2 ventiladores móviles Campagnoni 50\" (51.480 m³/h, 1 HP) para el confort de los operarios en la recepción y en la zaranda; no cuentan como renovación. La campana de la recepción (E3) sigue captando el olor en el origen. Extractores (M36, M37) y ventiladores (M38, M39, en tomas 2P+T) se alimentan desde el tablero TS-VEN, circuito Q27 del TG2 (plano 23)." },
  { n: "F1", g: "amp", nom: "Rev. F: tolva de retención de 1 h y enfriador del producto", plano: "P06", lp: [26.6, 9.3, 8.6],
    txt: "Estudio térmico (Rev. F): al 15 % el producto pasa en promedio 9 min sobre 55 °C, así que no alcanza para higienizar. El elevador se prolonga de 6,3 a 8,1 m (bajo la cumbrera de 8,35 m) y descarga en una tolva de retención aislada de 0,74 m³ (1 h de producción) con el TT-05 adentro: el producto se mantiene a 70 °C o más durante 60 min (Reglamento UE 142/2011). Debajo, un enfriador a contracorriente con persianas y un ventilador centrífugo de 0,55 kW (M40, 900 m³/h) lo lleva por debajo de 40 °C antes de la válvula desviadora (acopio o envasado); el aire tibio va al ducto de escape. Ubicación de anteproyecto: el detalle de los planos 08 y 19 queda pendiente." },
  { n: "F2", g: "amp", nom: "Rev. F: escape aislado y purga de condensado", plano: "P18", lp: [14.5, 21.1, 7.8],
    txt: "Estudio térmico (Rev. F): con el aire ajustado al 15 % el escape sale a 33-37 °C con 99 % de humedad relativa, casi saturado. El ducto Ø800 (14 m) y el ciclón se aíslan con lana de roca de 50 mm y chapa de protección, el ducto se tiende con pendiente hacia el ciclón y se agrega una purga de condensado con sifón a la cámara de lixiviados." },
  { n: "E9", g: "amp", nom: "Ampliación del predio: Sector Este", plano: "P13", lp: [86, -22, 1.4],
    txt: "El predio pasa de 72 × 76 m a 120 × 76 m (0,91 ha). Calle de vinculación y playón de expedición R6, calle de servicio R7 a la zona de biogás y acceso de emergencia y servicio R8 con portón propio sobre la calle pública (acceso de bomberos). Cerco y cortina forestal perimetral." },
];

/* ------------------------------------ utilidades ------------------------------------ */
function __rdMat(c, m, r, o) {
  return new dn(Object.assign({ color: c, metalness: m === void 0 ? 0.2 : m, roughness: r === void 0 ? 0.6 : r }, o || {}));
}

var __RDM = null;
function __rdMats() {
  if (__RDM) return __RDM;
  __RDM = {
    rojoInc: __rdMat(0xc8102e, 0.25, 0.45),
    verdeSal: __rdMat(0x0b8a43, 0.1, 0.6),
    blanco: __rdMat(0xf2f2ee, 0.1, 0.55),
    gris: __rdMat(0x8a9096, 0.5, 0.45),
    grisOsc: __rdMat(0x4a5055, 0.4, 0.5),
    recirc: __rdMat(0xc8743a, 0.45, 0.45),
    gas: __rdMat(0xe8c21a, 0.3, 0.45),
    aguaInc: __rdMat(0xb3202a, 0.35, 0.45),
    pvc: __rdMat(0x9ea3a8, 0.05, 0.6),
    pead: __rdMat(0x2b2b2b, 0.05, 0.7),
    digestor: __rdMat(0x3f6f66, 0.55, 0.35),
    membrana: __rdMat(0xd3d6cf, 0.05, 0.75),
    membranaVerde: __rdMat(0x6e8b5e, 0.05, 0.8),
    hormigon: v.hormigonVisto,
    ladrillo: v.ladrillo,
    agua: new dn({ color: 0x5f8fa8, metalness: 0.1, roughness: 0.15, transparent: !0, opacity: 0.75 }),
    desinf: new dn({ color: 0x6fae9a, metalness: 0.1, roughness: 0.2, transparent: !0, opacity: 0.8 }),
    chips: __rdMat(0x7a5a34, 0, 0.95),
    bigbag: __rdMat(0xe9e4d4, 0, 0.9),
    bolsa: __rdMat(0xd9cfae, 0, 0.8),
    bolsaChica: __rdMat(0x3f7d3a, 0.05, 0.6),
    carton: __rdMat(0xb88a52, 0, 0.9),
    madera: v.madera,
    aluminio: v.aluminio,
    vidrio: v.vidrio,
    led: v.led,
    naranjaSeg: __rdMat(0xf08a24, 0.2, 0.5),
    amarillo: v.amarillo,
    negro: v.negro,
    galv: v.galv,
    inox: v.inox,
    motor: v.motor,
    reductor: v.reductor,
    estructura: v.estructura,
    rejilla: v.rejilla,
    rojo: v.rojo,
    verde: v.verde,
    emergencia: new dn({ color: 0xffffff, emissive: 0xffffff, emissiveIntensity: 0.35, roughness: 0.4 }),
    balizaRoja: new dn({ color: 0x9a1010, emissive: 0xff2a1a, emissiveIntensity: 0.7, roughness: 0.4 }),
    llama: new Qn({ color: 0xff8a2a, transparent: !0, opacity: 0.85, depthWrite: !1 }),
  };
  return __RDM;
}

/* ------------------------- motores IEC detallados (Rev. C y Rev. D) -------------------------
   Los motores del visor eran cilindros lisos. Se envuelve la primitiva Be (cilindro entre dos puntos)
   para que, cuando el material es v.motor, le agregue al cilindro las aletas de refrigeración, los
   escudos, la tapa del ventilador con su rejilla, la caja de bornes con prensacable y el eje. El extremo
   p0 es el lado de accionamiento. Las piezas van como hijas del cilindro, así acompañan al despiece. */
var __rdBeOrig = Be;
Be = function (g, p0, p1, r, m, seg, o) {
  var mesh = __rdBeOrig.apply(this, arguments);
  if (m && typeof v !== "undefined" && m === v.motor && !(o && (o.open || o.r2 !== void 0))) {
    try { __rdDetallarMotor(mesh, mesh.geometry.parameters.height, r); } catch (e) { console.warn("motor", e); }
  }
  return mesh;
};
function __rdDetallarMotor(body, L, r) {
  if (!(L > 0.03 && r > 0.02)) return;
  var inv = body.quaternion.clone().invert();
  var up = new F(0, 1, 0).applyQuaternion(inv); up.y = 0;
  if (up.lengthSq() < 0.04) up.set(1, 0, 0);
  up.normalize();
  var a0 = Math.atan2(up.z, up.x), y0 = -L / 2;
  var azul = [], negro = [], acero = [];
  var cil = function (lista, rad, s0, s1, seg) { var g = new on(rad, rad, Math.abs(s1 - s0), seg || 22, 1); g.translate(0, y0 + (s0 + s1) / 2, 0); lista.push(g.toNonIndexed()); };
  var caja = function (lista, rad, tang, ax, s, R0, ang) {
    var g = new en(rad, ax, tang); g.rotateY(-ang); g.translate(R0 * Math.cos(ang), y0 + s, R0 * Math.sin(ang)); lista.push(g.toNonIndexed());
  };
  var n = 16;
  for (var k = 1; k < n; k++) caja(azul, 0.16 * r, 0.055 * r, 0.7 * L, 0.47 * L, 1.02 * r, a0 + 2 * Math.PI * k / n);
  cil(azul, 1.05 * r, -0.02 * L, 0.08 * L, 26);                 // escudo del lado de accionamiento (brida)
  cil(azul, 1.04 * r, 0.84 * L, 0.92 * L, 26);                  // escudo trasero
  cil(azul, 0.98 * r, 0.92 * L, 1.14 * L, 26);                  // tapa del ventilador
  cil(negro, 0.86 * r, 1.14 * L, 1.155 * L, 26);                // rejilla de la tapa
  caja(azul, 0.42 * r, 0.62 * r, 0.32 * L, 0.42 * L, 1.18 * r, a0);       // caja de bornes
  caja(negro, 0.16 * r, 0.16 * r, 0.1 * L, 0.42 * L, 1.18 * r, a0 + 0.55); // prensacable
  cil(acero, 0.22 * r, -0.25 * L, -0.02 * L, 14);               // punta de eje
  [[azul, v.motor], [negro, v.negro], [acero, v.inox]].forEach(function (p) {
    if (!p[0].length) return;
    var mm = new ge(ya(p[0], !1), p[1]);
    mm.castShadow = !0; mm.receiveShadow = !0; mm.userData.noMerge = !0;
    body.add(mm);
  });
}

/* Texturas de carteles (IRAM 10005: color de seguridad + pictograma + texto) */
var __rdTexCache = {};
function __rdSign(tipo, texto, pict) {
  var key = tipo + "|" + texto + "|" + (pict || "");
  if (__rdTexCache[key]) return __rdTexCache[key];
  var W = 256, H = 320;
  var col = { adv: "#f2c230", proh: "#c8102e", obl: "#1f5fa8", salv: "#0b8a43", inc: "#c8102e" }[tipo];
  var tex = Xn(W, H, function (c) {
    c.fillStyle = "#ffffff";
    c.fillRect(0, 0, W, H);
    c.lineJoin = "round";
    var cx = W / 2, cy = 118;
    if (tipo === "adv") {
      c.fillStyle = col; c.strokeStyle = "#111"; c.lineWidth = 12;
      c.beginPath(); c.moveTo(cx, 22); c.lineTo(cx + 100, 200); c.lineTo(cx - 100, 200); c.closePath(); c.fill(); c.stroke();
      __rdPict(c, pict || "!", cx, 138, "#111");
    } else if (tipo === "proh") {
      __rdPict(c, pict || "fumar", cx, cy, "#111");
      c.strokeStyle = col; c.lineWidth = 18;
      c.beginPath(); c.arc(cx, cy, 86, 0, Math.PI * 2); c.stroke();
      c.beginPath(); c.moveTo(cx - 61, cy - 61); c.lineTo(cx + 61, cy + 61); c.stroke();
    } else if (tipo === "obl") {
      c.fillStyle = col; c.beginPath(); c.arc(cx, cy, 92, 0, Math.PI * 2); c.fill();
      __rdPict(c, pict || "casco", cx, cy, "#fff");
    } else {
      c.fillStyle = col; c.fillRect(18, 18, W - 36, 200);
      __rdPict(c, pict || "salida", cx, cy, "#fff");
    }
    var bg = tipo === "adv" ? col : tipo === "proh" || tipo === "inc" ? "#c8102e" : col;
    c.fillStyle = bg;
    c.fillRect(0, 226, W, 94);
    c.fillStyle = tipo === "adv" ? "#111" : "#fff";
    c.textAlign = "center"; c.textBaseline = "middle";
    var lin = texto.split("|");
    var fs = lin.length > 1 ? 32 : 36;
    c.font = "700 " + fs + "px Barlow Condensed, Arial Narrow, sans-serif";
    lin.forEach(function (t, i) { c.fillText(t, W / 2, 273 + (i - (lin.length - 1) / 2) * (fs + 4), W - 16); });
    c.strokeStyle = "#111"; c.lineWidth = 4; c.strokeRect(2, 2, W - 4, H - 4);
  });
  tex.wrapS = tex.wrapT = 1001;
  __rdTexCache[key] = tex;
  return tex;
}

function __rdPict(c, p, x, y, col) {
  c.save();
  c.fillStyle = col; c.strokeStyle = col; c.lineCap = "round"; c.lineJoin = "round";
  if (p === "!") {
    c.fillRect(x - 9, y - 58, 18, 62); c.beginPath(); c.arc(x, y + 28, 11, 0, 7); c.fill();
  } else if (p === "rayo") {
    c.beginPath(); c.moveTo(x + 14, y - 62); c.lineTo(x - 26, y + 6); c.lineTo(x - 2, y + 6); c.lineTo(x - 16, y + 52);
    c.lineTo(x + 28, y - 14); c.lineTo(x + 4, y - 14); c.lineTo(x + 22, y - 62); c.closePath(); c.fill();
  } else if (p === "calor") {
    c.lineWidth = 8;
    for (var i = -1; i <= 1; i++) {
      c.beginPath();
      for (var t = 0; t <= 1; t += 0.05) { var yy = y + 20 - t * 70, xx = x + i * 26 + Math.sin(t * 9) * 8; t === 0 ? c.moveTo(xx, yy) : c.lineTo(xx, yy); }
      c.stroke();
    }
    c.fillRect(x - 50, y + 26, 100, 12);
  } else if (p === "atrap") {
    c.lineWidth = 8;
    c.beginPath(); c.arc(x - 22, y + 10, 26, 0, 7); c.stroke();
    c.beginPath(); c.arc(x + 26, y + 10, 26, 0, 7); c.stroke();
    c.beginPath(); c.moveTo(x - 30, y - 50); c.lineTo(x + 2, y - 8); c.stroke();
    c.beginPath(); c.moveTo(x - 20, y - 56); c.lineTo(x + 12, y - 16); c.stroke();
  } else if (p === "fuego") {
    c.beginPath(); c.moveTo(x, y - 62);
    c.bezierCurveTo(x + 44, y - 20, x + 40, y + 40, x, y + 44);
    c.bezierCurveTo(x - 40, y + 40, x - 44, y - 10, x - 10, y - 30);
    c.bezierCurveTo(x - 8, y - 6, x + 4, y - 8, x, y - 62); c.fill();
  } else if (p === "gas") {
    c.lineWidth = 7; c.beginPath(); c.arc(x, y - 10, 36, 0, 7); c.stroke();
    c.font = "700 40px Barlow Condensed, Arial Narrow, sans-serif"; c.textAlign = "center"; c.textBaseline = "middle"; c.fillText("Ex", x, y - 8);
    c.fillRect(x - 40, y + 34, 80, 10);
  } else if (p === "fumar") {
    c.fillRect(x - 58, y - 8, 96, 22); c.fillRect(x + 44, y - 8, 14, 22);
    c.lineWidth = 5; c.beginPath(); c.moveTo(x + 50, y - 16); c.bezierCurveTo(x + 40, y - 36, x + 64, y - 44, x + 52, y - 66); c.stroke();
  } else if (p === "casco") {
    c.beginPath(); c.arc(x, y + 6, 50, Math.PI, 0); c.fill(); c.fillRect(x - 66, y + 4, 132, 14);
    c.fillStyle = col === "#fff" ? "#1f5fa8" : "#fff"; c.fillRect(x - 6, y - 44, 12, 46);
  } else if (p === "salida") {
    c.beginPath(); c.arc(x - 18, y - 52, 13, 0, 7); c.fill();
    c.lineWidth = 13;
    c.beginPath(); c.moveTo(x - 22, y - 34); c.lineTo(x - 30, y + 8); c.lineTo(x - 52, y + 44); c.stroke();
    c.beginPath(); c.moveTo(x - 30, y + 8); c.lineTo(x - 4, y + 26); c.lineTo(x - 10, y + 56); c.stroke();
    c.beginPath(); c.moveTo(x - 52, y - 12); c.lineTo(x - 24, y - 28); c.lineTo(x - 2, y - 10); c.stroke();
    c.fillRect(x + 14, y - 48, 6, 104); c.fillRect(x + 14, y - 48, 50, 6); c.fillRect(x + 58, y - 48, 6, 104);
    c.beginPath(); c.moveTo(x + 22, y + 10); c.lineTo(x + 52, y + 10); c.stroke();
  } else if (p === "matafuego") {
    c.beginPath(); c.roundRect ? c.roundRect(x - 22, y - 30, 44, 90, 12) : c.rect(x - 22, y - 30, 44, 90); c.fill();
    c.fillRect(x - 10, y - 52, 20, 24); c.fillRect(x - 2, y - 60, 44, 10);
    c.lineWidth = 7; c.beginPath(); c.moveTo(x + 40, y - 55); c.bezierCurveTo(x + 64, y - 40, x + 60, y, x + 30, y + 10); c.stroke();
  } else if (p === "hidrante") {
    c.lineWidth = 10; c.beginPath(); c.arc(x, y, 44, 0, 7); c.stroke();
    c.beginPath(); c.arc(x, y, 22, 0, 7); c.stroke(); c.fillRect(x + 36, y - 6, 34, 12);
  } else if (p === "hongo") {
    c.beginPath(); c.arc(x, y - 6, 46, Math.PI, 0); c.fill(); c.fillRect(x - 14, y - 6, 28, 50); c.fillRect(x - 40, y + 40, 80, 14);
  }
  c.restore();
}

function __rdPlateTex(lineas, opt) {
  opt = opt || {};
  var W = opt.w || 256, H = opt.h || 88;
  return Xn(W, H, function (c) {
    c.fillStyle = opt.bg || "#d9dde0"; c.fillRect(0, 0, W, H);
    c.strokeStyle = "#555"; c.lineWidth = 4; c.strokeRect(3, 3, W - 6, H - 6);
    c.fillStyle = "#222";
    [[10, 10], [W - 10, 10], [10, H - 10], [W - 10, H - 10]].forEach(function (p) { c.beginPath(); c.arc(p[0], p[1], 4, 0, 7); c.fill(); });
    c.fillStyle = opt.fg || "#111"; c.textAlign = "center"; c.textBaseline = "middle";
    var n = lineas.length;
    lineas.forEach(function (t, i) {
      var fs = i === 0 ? (n > 1 ? 34 : 44) : 22;
      c.font = (i === 0 ? "700 " : "600 ") + fs + "px Barlow Condensed, Arial Narrow, sans-serif";
      c.fillText(t, W / 2, n === 1 ? H / 2 : i === 0 ? H * 0.36 : H * 0.36 + 18 + (i - 1) * 22, W - 20);
    });
  });
}

function __rdLabelTex(texto, color) {
  var lin = texto.split("|");
  var W = 512, H = 64 + (lin.length - 1) * 44;
  return Xn(W, H, function (c) {
    c.clearRect(0, 0, W, H);
    c.fillStyle = "rgba(20,20,19,0.78)";
    if (c.roundRect) { c.beginPath(); c.roundRect(4, 4, W - 8, H - 8, 14); c.fill(); } else c.fillRect(4, 4, W - 8, H - 8);
    c.fillStyle = color || "#ffffff"; c.fillRect(4, 4, 12, H - 8);
    c.fillStyle = "#fff"; c.textAlign = "left"; c.textBaseline = "middle";
    lin.forEach(function (t, i) {
      c.font = (i === 0 ? "700 34px " : "500 28px ") + "Barlow Condensed, Arial Narrow, sans-serif";
      c.fillText(t, 30, 34 + i * 44, W - 44);
    });
  });
}

/* ------------------------------------ construcción ------------------------------------ */
function __revDBuild(root, R, D) {
  var G = D.G, M = __rdMats();
  var cur = null;
  var parte = function (id) {
    var g = new Qe();
    g.userData.part = id;
    R.parts[id] = g;
    root.add(g);
    cur = g;
    __RD.grupos[id] = g;
    return g;
  };
  // primitivas
  var B = function (x0, y0, z0, x1, y1, z1, m, o) { return Z(cur, x0, y0, z0, x1, y1, z1, m, o || {}); };
  var C = function (p0, p1, r, m, seg, o) { return Be(cur, p0, p1, r, m, seg || 14, o || {}); };
  var V = function (x, y, z0, z1, r, m, seg, o) { return Ln(cur, x, y, z0, z1, r, m, seg || 20, o || {}); };
  var BAR = function (p0, p1, s, m) { return Xi(cur, p0, p1, s, m); };
  var SPH = function (x, y, z, r, m) { var s = new ge(new fi(r, 14, 10), m); s.position.copy(fe(x, y, z)); s.castShadow = !0; cur.add(s); return s; };
  var TUBO = function (pts, r, m, seg) { for (var i = 0; i < pts.length - 1; i++) C(pts[i], pts[i + 1], r, m, seg || 10); for (var j = 1; j < pts.length - 1; j++) SPH(pts[j][0], pts[j][1], pts[j][2], r, m); };
  var CONO = function (p, dir, r, h, m) {
    var g = new ge(new Pl(r, h, 16), m);
    var d = fe(dir[0], dir[1], dir[2]).normalize();
    g.quaternion.setFromUnitVectors(new F(0, 1, 0), d);
    g.position.copy(fe(p[0], p[1], p[2])).addScaledVector(d, h / 2);
    g.castShadow = !0; cur.add(g); return g;
  };
  var TORO = function (x, y, z, R0, r, m) { var t = new ge(new Hl(R0, r, 8, 36), m); t.rotation.x = Math.PI / 2; t.position.copy(fe(x, y, z)); cur.add(t); return t; };
  // plano vertical (cartel/placa). rot: 0 mira al Sur, PI al Norte, PI/2 al Este, -PI/2 al Oeste
  var PLANO = function (x, y, z, w, h, rot, mat, dos) {
    var p = new ge(new Pn(w, h), mat);
    p.position.copy(fe(x, y, z)); p.rotation.y = rot; cur.add(p);
    if (dos) { var q = new ge(new Pn(w, h), mat); q.position.copy(fe(x, y, z)); q.rotation.y = rot + Math.PI; cur.add(q); }
    return p;
  };
  var off = function (rot, d) { return [Math.sin(rot) * d, -Math.cos(rot) * d]; };
  var matCache = {};
  var CARTEL = function (tipo, texto, pict, x, y, z, rot, esc, dos) {
    esc = esc || 0.4;
    var kk = tipo + texto + pict;
    var mat = matCache[kk] || (matCache[kk] = new dn({ map: __rdSign(tipo, texto, pict), roughness: 0.55, metalness: 0.05 }));
    var o = off(rot, 0.012);
    return PLANO(x + o[0], y + o[1], z, esc * 0.8, esc, rot, mat, dos);
  };
  var PLACA = function (lineas, x, y, z, rot, w, h, opt) {
    var mat = new dn({ map: __rdPlateTex(lineas, opt), roughness: 0.4, metalness: 0.5 });
    var o = off(rot, 0.008);
    return PLANO(x + o[0], y + o[1], z, w || 0.3, h || 0.1, rot, mat);
  };
  var ETIQ = function (texto, x, y, z, esc, color) {
    var tex = __rdLabelTex(texto, color);
    var sp = new El(new uo({ map: tex, transparent: !0, depthWrite: !1 }));
    var lin = texto.split("|").length;
    var h = (64 + (lin - 1) * 44) / 512;
    sp.scale.set(esc || 2.6, (esc || 2.6) * h, 1);
    sp.position.copy(fe(x, y, z));
    sp.renderOrder = 3;
    cur.add(sp);
    __RD.sprites.push(sp);
    return sp;
  };
  var FLECHA = function (p0, p1, r, m) {
    var d = [p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]];
    var L = Math.hypot(d[0], d[1], d[2]);
    var hl = Math.min(L * 0.45, r * 5);
    var q = [p1[0] - d[0] / L * hl, p1[1] - d[1] / L * hl, p1[2] - d[2] / L * hl];
    C(p0, q, r, m, 10);
    CONO(q, d, r * 2.6, hl, m);
  };
  var HONGO = function (x, y, z, rot, poste) {
    var o = off(rot, 0.06);
    if (poste) { B(x - 0.03, y - 0.03, 0, x + 0.03, y + 0.03, z - 0.08, M.galv); B(x - 0.12, y - 0.12, 0, x + 0.12, y + 0.12, 0.02, M.galv); }
    var bx = Math.abs(Math.sin(rot)) > 0.5 ? [0.06, 0.05] : [0.05, 0.06];
    B(x - bx[0], y - bx[1], z - 0.08, x + bx[0], y + bx[1], z + 0.06, M.amarillo);
    C([x + o[0] * 0.8, y + o[1] * 0.8, z], [x + o[0] * 1.4, y + o[1] * 1.4, z], 0.02, M.negro, 10);
    C([x + o[0] * 1.4, y + o[1] * 1.4, z], [x + o[0] * 1.8, y + o[1] * 1.8, z], 0.035, M.rojo, 16);
  };
  if (!M.baliza) M.baliza = new dn({ map: Xn(64, 64, function (c) { c.fillStyle = "#fff"; c.fillRect(0, 0, 64, 64); c.fillStyle = "#c8102e"; for (var k = -64; k < 128; k += 22) { c.beginPath(); c.moveTo(k, 64); c.lineTo(k + 11, 64); c.lineTo(k + 75, 0); c.lineTo(k + 64, 0); c.closePath(); c.fill(); } }), roughness: 0.6 });
  var MATAFUEGO = function (x, y, rot, tipo, existente) {
    // chapa baliza detrás, soporte y cartel; el cilindro solo si es nuevo (mismo alto que los existentes)
    var o = off(rot, 1);
    var nx = o[0], ny = o[1];
    var sx = Math.abs(nx) > 0.5 ? 0.012 : 0.3, sy = Math.abs(nx) > 0.5 ? 0.3 : 0.012;
    var bx = x - nx * 0.11, by = y - ny * 0.11;
    if (tipo !== "rod") {
      B(bx - sx, by - sy, 0.25, bx + sx, by + sy, 1.05, M.baliza);
      B(bx + nx * 0.02 - 0.03, by + ny * 0.02 - 0.03, 0.72, bx + nx * 0.06 + 0.03, by + ny * 0.06 + 0.03, 0.78, M.negro);
    }
    if (!existente) {
      var r = tipo === "CO2" ? 0.075 : tipo === "rod" ? 0.16 : 0.085;
      var h = tipo === "CO2" ? 0.62 : tipo === "rod" ? 0.8 : 0.55;
      var z0 = tipo === "rod" ? 0.12 : 0.35;
      V(x, y, z0, z0 + h, r, tipo === "CO2" ? M.grisOsc : M.rojoInc, 16);
      V(x, y, z0 + h, z0 + h + 0.08, 0.03, M.negro, 8);
      if (tipo === "CO2") C([x, y, z0 + h + 0.05], [x + nx * 0.12, y + ny * 0.12, z0 + h - 0.2], 0.03, M.negro, 8);
      if (tipo === "rod") { C([x - 0.25, y, 0.12], [x + 0.25, y, 0.12], 0.12, M.negro, 14); BAR([x, y + 0.16, 0.2], [x, y + 0.35, 1.1], 0.03, M.negro); }
    }
    CARTEL("inc", "MATAFUEGO", "matafuego", bx + nx * 0.005, by + ny * 0.005, tipo === "rod" ? 1.55 : 1.4, rot, 0.34);
  };
  var BARANDA = function (pts, h, m) {
    // baranda de 1,0 m con travesaño intermedio y rodapié (Dec. 351/79)
    h = h || 1.0; m = m || M.amarillo;
    for (var i = 0; i < pts.length - 1; i++) {
      var a = pts[i], b = pts[i + 1];
      var L = Math.hypot(b[0] - a[0], b[1] - a[1]);
      var n = Math.max(1, Math.ceil(L / 1.5));
      for (var k = 0; k <= n; k++) {
        if (i > 0 && k === 0) continue;
        var t = k / n, x = a[0] + (b[0] - a[0]) * t, y = a[1] + (b[1] - a[1]) * t;
        BAR([x, y, a[2]], [x, y, a[2] + h], 0.04, m);
      }
      BAR([a[0], a[1], a[2] + h], [b[0], b[1], b[2] + h], 0.04, m);
      BAR([a[0], a[1], a[2] + h / 2], [b[0], b[1], b[2] + h / 2], 0.03, m);
      BAR([a[0], a[1], a[2] + 0.07], [b[0], b[1], b[2] + 0.07], 0.012, m);
      BAR([a[0], a[1], a[2] + 0.02], [b[0], b[1], b[2] + 0.12], 0.012, m);
    }
  };
  var JAULA = function (x, y, z0, z1, dir) {
    // jaula guardahombre de escalera marinera; dir = sentido hacia afuera [dx, dy]
    var R0 = 0.36, cx = x + dir[0] * R0, cy = y + dir[1] * R0;
    var ang0 = Math.atan2(-dir[1], -dir[0]);
    for (var z = z0; z <= z1 + 0.01; z += 0.9) {
      var prev = null;
      for (var k = 0; k <= 10; k++) {
        var a = ang0 + Math.PI * 0.33 + (k / 10) * Math.PI * 1.34;
        var p = [cx + R0 * Math.cos(a), cy + R0 * Math.sin(a), z];
        if (prev) BAR(prev, p, 0.022, M.amarillo);
        prev = p;
      }
    }
    for (var s = 0; s < 5; s++) {
      var a2 = ang0 + Math.PI * 0.33 + (s / 4) * Math.PI * 1.34;
      BAR([cx + R0 * Math.cos(a2), cy + R0 * Math.sin(a2), z0], [cx + R0 * Math.cos(a2), cy + R0 * Math.sin(a2), z1], 0.018, M.amarillo);
    }
  };
  var ESCALERA = function (x, y, z0, z1, eje, ancho) {
    // escalera marinera: eje 'x' -> largueros separados en x
    ancho = ancho || 0.45;
    var a = ancho / 2;
    var p0 = eje === "x" ? [[x - a, y], [x + a, y]] : [[x, y - a], [x, y + a]];
    p0.forEach(function (p) { BAR([p[0], p[1], z0], [p[0], p[1], z1 + 1.0], 0.04, M.amarillo); });
    for (var z = z0 + 0.3; z < z1 + 0.05; z += 0.3) BAR([p0[0][0], p0[0][1], z], [p0[1][0], p0[1][1], z], 0.025, M.amarillo);
  };
  var PLATAFORMA = function (x0, y0, x1, y1, z) {
    B(x0, y0, z - 0.04, x1, y1, z, M.rejilla, { shadow: !1 });
    B(x0, y0, z - 0.14, x0 + 0.06, y1, z - 0.04, M.estructura);
    B(x1 - 0.06, y0, z - 0.14, x1, y1, z - 0.04, M.estructura);
  };
  var ANILLO_PLAT = function (x, y, z, r0, r1, a0, a1) {
    // plataforma en arco (anillo) con baranda exterior
    var n = 16, pts = [];
    for (var k = 0; k < n; k++) {
      var t0 = a0 + (a1 - a0) * k / n, t1 = a0 + (a1 - a0) * (k + 1) / n, tm = (t0 + t1) / 2, rm = (r0 + r1) / 2;
      var w = (r1 - r0), L = rm * (t1 - t0);
      var g = new ge(new en(L + 0.02, 0.04, w), M.rejilla);
      g.position.copy(fe(x + rm * Math.cos(tm), y + rm * Math.sin(tm), z - 0.02));
      g.rotation.y = tm + Math.PI / 2;
      cur.add(g);
    }
    for (var k2 = 0; k2 <= n; k2++) { var t = a0 + (a1 - a0) * k2 / n; pts.push([x + r1 * Math.cos(t), y + r1 * Math.sin(t), z]); }
    BARANDA(pts, 1.0);
    for (var k3 = 0; k3 <= 4; k3++) { var t3 = a0 + (a1 - a0) * k3 / 4; BAR([x + r0 * Math.cos(t3), y + r0 * Math.sin(t3), z - 0.04], [x + r1 * Math.cos(t3), y + r1 * Math.sin(t3), z - 0.3], 0.05, M.estructura); }
  };
  var SENSOR = function (x, y, z, dir, tag, tipo) {
    // cabezal de sensor con vaina hacia el equipo (dir apunta hacia afuera del equipo)
    var L = tipo === "corto" ? 0.08 : 0.14;
    var p1 = [x + dir[0] * L, y + dir[1] * L, z + (dir[2] || 0) * L];
    C([x, y, z], p1, 0.012, M.inox, 8);
    var cab = tipo === "nir" ? [0.09, 0.07] : [0.045, 0.06];
    C(p1, [p1[0] + dir[0] * cab[1], p1[1] + dir[1] * cab[1], p1[2] + (dir[2] || 0) * cab[1]], cab[0], tipo === "nir" ? M.grisOsc : M.azulSensor || M.gris, 14);
    if (tag) {
      var pr = [p1[0] + dir[0] * (cab[1] + 0.02), p1[1] + dir[1] * (cab[1] + 0.02)];
      var rot = Math.abs(dir[0]) > 0.5 ? (dir[0] > 0 ? Math.PI / 2 : -Math.PI / 2) : dir[1] < -0.5 ? 0 : dir[1] > 0.5 ? Math.PI : 0;
      if (Math.abs(dir[2] || 0) < 0.5) PLACA([tag], pr[0], pr[1], p1[2] + 0.1, rot, 0.16, 0.06, { bg: "#f4f4f0" });
    }
  };
  var BOQUILLA = function (x, y, z, dir) {
    var L = 0.1, p1 = [x + dir[0] * L, y + dir[1] * L, z + (dir[2] || 0) * L];
    C([x, y, z], p1, 0.018, M.galv, 10);
    C(p1, [p1[0] + dir[0] * 0.035, p1[1] + dir[1] * 0.035, p1[2] + (dir[2] || 0) * 0.035], 0.028, M.rojo, 10);
  };
  var CAJA = function (x, y, z, rot, w, h, m) { w = w || 0.14; h = h || 0.14; var o = off(rot, 0.07); var sx = Math.abs(o[0]) > 0.03 ? 0.035 : w / 2, sy = Math.abs(o[0]) > 0.03 ? w / 2 : 0.035; B(x + o[0] / 2 - sx, y + o[1] / 2 - sy, z - h / 2, x + o[0] / 2 + sx, y + o[1] / 2 + sy, z + h / 2, m || M.gris); };
  M.azulSensor = M.azulSensor || __rdMat(0x2f5f8f, 0.3, 0.45);

  var sec = G.secador, x0s = sec.x0, y0s = sec.y0;
  var X = function (s) { return x0s + s; };
  var Y = function (s) { return y0s + s; };

  /* ===================================================== D1 PUERTAS DE INSPECCIÓN */
  parte("D1");
  var zsN = 1;
  sec.puertas.forEach(function (Pd) {
    [[-0.02, -1], [sec.A + 0.02, 1]].forEach(function (f) {
      var yf = Y(f[0]), s = f[1], xc = X(Pd.x), zm = (Pd.z0 + Pd.z1) / 2;
      var mov = [];
      // manija (se mueve con la hoja)
      mov.push(B(xc + 0.19, yf + s * 0.015, zm - 0.1, xc + 0.21, yf + s * 0.05, zm - 0.08, M.negro));
      mov.push(B(xc + 0.19, yf + s * 0.015, zm + 0.08, xc + 0.21, yf + s * 0.05, zm + 0.1, M.negro));
      mov.push(B(xc + 0.19, yf + s * 0.05, zm - 0.1, xc + 0.215, yf + s * 0.065, zm + 0.1, M.negro));
      // leva del microinterruptor sobre el borde de la hoja
      mov.push(B(xc + 0.3, yf + s * 0.015, Pd.z1 - 0.1, xc + 0.355, yf + s * 0.03, Pd.z1 - 0.06, M.negro));
      mov.forEach(function (m) {
        m.userData.expVec = fe(0, s * 2.2, 0);
        if (s < 0) m.userData.corte = "hide";
      });
      // microinterruptor ZS fijo al panel + caja de conexión + caño
      B(xc + 0.37, yf + s * 0.0, Pd.z1 - 0.13, xc + 0.42, yf + s * 0.045, Pd.z1 - 0.03, M.amarillo);
      B(xc + 0.36, yf + s * 0.01, Pd.z1 - 0.1, xc + 0.37, yf + s * 0.035, Pd.z1 - 0.06, M.rojo);
      B(xc + 0.5, yf, Pd.z1 - 0.12, xc + 0.62, yf + s * 0.06, Pd.z1 + 0.0, M.gris);
      C([xc + 0.42, yf + s * 0.025, Pd.z1 - 0.08], [xc + 0.5, yf + s * 0.025, Pd.z1 - 0.06], 0.008, M.negro, 6);
      C([xc + 0.56, yf + s * 0.03, Pd.z1], [xc + 0.56, yf + s * 0.03, sec.H - 0.08], 0.01, M.galv, 6);
      PLACA(["ZS-0" + zsN++], xc + 0.395, yf + s * 0.001, Pd.z1 + 0.03, s < 0 ? 0 : Math.PI, 0.12, 0.045, { bg: "#f4f4f0" });
    });
  });

  /* ===================================================== D2 PROTECCIONES */
  parte("D2");
  sec.pisos.forEach(function (Pz) {
    var zm = Pz.zc - sec.r_motriz, zr = Pz.zc - sec.r_reenvio;
    // extremos Norte de los ejes motrices y extremos de los ejes de reenvío
    C([X(Pz.cabeza), Y(2.68), zm], [X(Pz.cabeza), Y(2.8), zm], 0.055, M.amarillo, 16);
    C([X(Pz.cola), Y(2.72), zr], [X(Pz.cola), Y(2.84), zr], 0.05, M.amarillo, 16);
    C([X(Pz.cola), Y(-0.24), zr], [X(Pz.cola), Y(-0.12), zr], 0.05, M.amarillo, 16);
  });
  // cubreacople del esparcidor (M9)
  C([X(sec.esparcidor_x), Y(-0.07), 2.9], [X(sec.esparcidor_x), Y(0.0), 2.9], 0.06, M.amarillo, 16);
  // rejillas de aspiración de ventiladores M1, M2 y del ventilador de combustión M4
  G.anexo.ventiladores.forEach(function (S) {
    var g = new ge(new on(0.34, 0.34, 0.02, 24), M.rejilla);
    g.rotation.z = Math.PI / 2; g.position.copy(fe(S.x + 0.57, S.y, 0.75)); cur.add(g);
    TORO(0, 0, 0, 0.34, 0.015, M.amarillo).position.copy(fe(S.x + 0.575, S.y, 0.75));
    cur.children[cur.children.length - 1].rotation.set(0, Math.PI / 2, 0);
  });
  var vc = G.anexo.vent_comb;
  (function () { var g = new ge(new on(0.35, 0.35, 0.02, 24), M.rejilla); g.rotation.z = Math.PI / 2; g.position.copy(fe(vc.x - 0.17, vc.y, 0.5)); cur.add(g); })();
  // cubreacople bomba M14 y sinfín de cáscara M12
  C([G.bomba.x - 0.02, G.bomba.y, 0.3], [G.bomba.x + 0.1, G.bomba.y, 0.3], 0.16, M.amarillo, 16);
  var Lc = G.sinfin_cascara;
  C([Lc.x0 + 0.02, Lc.y, Lc.z0 - 0.01], [Lc.x0 + 0.12, Lc.y, Lc.z0 - 0.03], 0.1, M.amarillo, 16);
  var ex = G.extractor;
  // cinta de alimentación: tapas en ejes del tambor de cola
  var ci = G.cinta;
  [-1, 1].forEach(function (s) { C([ci.x_cola, ci.y + s * 0.4, 0.65 - ci.D_cola / 2], [ci.x_cola, ci.y + s * 0.5, 0.65 - ci.D_cola / 2], 0.045, M.amarillo, 14); });

  /* ===================================================== D3 PASARELAS, ESCALERAS, BARANDAS */
  parte("D3");
  // jaula en la escalera marinera existente del secador (x = x0 - 0.52, y 8.2..8.7)
  JAULA(X(-0.52), Y(0.45), 2.2, sec.H + 0.9, [-1, 0]);
  // ciclón: escalera marinera al Oeste + plataforma semicircular en el techo
  var cy = G.ciclon;
  ESCALERA(cy.x - 1.25, cy.y, 0, cy.z_cil1, "y");
  JAULA(cy.x - 1.25, cy.y, 2.4, cy.z_cil1 + 0.9, [-1, 0]);
  ANILLO_PLAT(cy.x, cy.y, cy.z_cil1, 0.92, 1.7, Math.PI * 0.62, Math.PI * 1.3);
  // lavador: la escalera existe (lado Sur); se agrega jaula y plataforma superior
  var sc = G.scrubber;
  JAULA(sc.x, sc.y - sc.D / 2 - 0.07, 2.4, sc.z1 + 0.9, [0, -1]);
  ANILLO_PLAT(sc.x, sc.y, sc.z1, sc.D / 2 + 0.02, sc.D / 2 + 0.8, -Math.PI * 0.95, -Math.PI * 0.05);
  // silo: jaula en la escalera existente (lado Norte) + baranda perimetral del techo
  var si = G.silo, ki = si.z_boca + si.h_cono + si.h_cil;
  JAULA(si.x, si.y + si.D / 2 + 0.07, 2.4, ki + 0.9, [0, 1]);
  (function () { var pts = []; for (var k = 0; k <= 24; k++) { var a = (k / 24) * Math.PI * 2; pts.push([si.x + (si.D / 2 + 0.05) * Math.cos(a), si.y + (si.D / 2 + 0.05) * Math.sin(a), ki]); } BARANDA(pts, 1.0); })();
  // elevador: plataforma de cabezal y escalera marinera con jaula
  var el = G.elevador;
  PLATAFORMA(el.x - 0.75, el.y + 0.5, el.x + 0.75, el.y + 1.6, 5.7);
  BARANDA([[el.x - 0.75, el.y + 0.5, 5.7], [el.x - 0.75, el.y + 1.6, 5.7], [el.x + 0.75, el.y + 1.6, 5.7], [el.x + 0.75, el.y + 0.5, 5.7]], 1.0);
  ESCALERA(el.x + 0.2, el.y + 1.62, 0, 5.7, "x");
  JAULA(el.x + 0.2, el.y + 1.62, 2.4, 6.6, [0, 1]);
  BAR([el.x - 0.7, el.y + 0.55, 0], [el.x - 0.7, el.y + 0.55, 5.66], 0.08, M.estructura);
  BAR([el.x + 0.7, el.y + 1.55, 0], [el.x + 0.7, el.y + 1.55, 5.66], 0.08, M.estructura);
  // chimenea de humos: escalera marinera con jaula a la plataforma existente (+7,80)
  var ch = G.anexo.chimenea;
  ESCALERA(ch.x, ch.y + 0.33, 0.25, 7.8, "x", 0.4);
  JAULA(ch.x, ch.y + 0.33, 2.4, 8.7, [0, 1]);
  // barandas de distanciamiento frente al hogar (con paso de 0,8 m frente a la puerta RF-60)
  var ho = G.anexo.hogar;
  BARANDA([[ho.x0 - 0.3, ho.y0 - 0.1, 0], [ho.x0 - 0.3, ho.y0 - 0.75, 0], [26.2, ho.y0 - 0.75, 0]], 1.0);
  BARANDA([[27.0, ho.y0 - 0.75, 0], [ho.x1 + 0.42, ho.y0 - 0.75, 0], [ho.x1 + 0.42, ho.y0 - 0.1, 0]], 1.0);
  C([26.2, ho.y0 - 0.75, 0.95], [27.0, ho.y0 - 0.75, 0.9], 0.012, M.amarillo, 6);

  /* ===================================================== D4 PARADAS DE EMERGENCIA */
  parte("D4");
  [
    [4.4, 7.95, 1.25, 0, !0, "PE-01"],
    [X(-0.2), Y(-0.9), 1.25, 0, !0, "PE-02"],
    [18.2, Y(-0.85), 1.25, 0, !0, "PE-03"],
    [X(13.25), Y(-0.9), 1.25, 0, !0, "PE-04"],
    [26.7, 18.0 - 0.02, 1.35, 0, !1, "PE-05"],
    [23.55, G.anexo.y1 - 0.06, 1.35, 0, !1, "PE-06"],
    [30.7, 10.25, 1.25, 0, !0, "PE-07"],
  ].forEach(function (p) {
    HONGO(p[0], p[1], p[2], p[3], p[4]);
    CARTEL("inc", "PARADA DE|EMERGENCIA", "hongo", p[0], p[1] - 0.075, p[2] + 0.35, 0, 0.26);
    PLACA([p[5]], p[0], p[1] - 0.075, p[2] - 0.16, 0, 0.14, 0.05, { bg: "#f4f4f0" });
  });

  /* ===================================================== D5 SENSORES */
  parte("D5");
  var dc = G.ducto_caliente;
  SENSOR(dc.x1, 11.2, 1.9, [1, 0, 0], "TT-01");
  sec.pisos.forEach(function (Pz, i) { SENSOR(X(1.6), Y(sec.A), Pz.zc + 0.42, [0, 1, 0], "TT-0" + (i + 2)); });
  SENSOR(24.55, G.sinfin_desc.y + 0.11, 0.25, [0, 1, 0], "TT-05", "corto");
  (function () { // MT-01 NIR sobre la descarga
    var sd = G.sinfin_desc;
    B(25.19, sd.y - 0.06, 0.34, 25.31, sd.y + 0.06, 0.42, M.inox);
    B(25.15, sd.y - 0.1, 0.42, 25.35, sd.y + 0.1, 0.58, M.grisOsc);
    PLACA(["MT-01"], 25.25, sd.y - 0.1, 0.66, 0, 0.16, 0.06, { bg: "#f4f4f0" });
  })();
  SENSOR(ho.x0 + 0.3, 21.3, ho.z1, [0, 0, 1], null);
  PLACA(["TT-06"], ho.x0 + 0.3, ho.y0 - 0.01, 2.75, 0, 0.16, 0.06, { bg: "#f4f4f0" });
  SENSOR(ch.x + ch.D / 2, ch.y, 6.2, [1, 0, 0], "TT-07");
  (function () { // TT-08 con abrigo meteorológico en el muro Sur exterior
    B(4.4, -0.2, 2.2, 4.6, -0.02, 2.45, M.blanco);
    for (var z = 2.24; z < 2.44; z += 0.05) B(4.38, -0.22, z, 4.62, -0.2, z + 0.02, M.blanco);
    PLACA(["TT-08"], 4.5, -0.23, 2.55, 0, 0.16, 0.06, { bg: "#f4f4f0" });
  })();
  (function () { // PT-01 transmisor de presión diferencial del plenum
    var xs = X(sec.entrada_aire.x0) - 0.45, yf = Y(sec.A);
    B(xs - 0.09, yf, 0.62, xs + 0.09, yf + 0.08, 0.8, M.azulSensor);
    C([xs - 0.05, yf + 0.02, 0.62], [xs - 0.05, yf + 0.02, 0.5], 0.006, M.negro, 6);
    C([xs + 0.05, yf + 0.02, 0.62], [xs + 0.05, yf + 0.02, 0.5], 0.006, M.negro, 6);
    PLACA(["PT-01"], xs, yf + 0.085, 0.89, Math.PI, 0.16, 0.06, { bg: "#f4f4f0" });
  })();
  // BE-01 detector de llama UV y PS-01 presostato en la cara Sur del hogar
  C([27.45, ho.y0, 2.0], [27.45, ho.y0 - 0.12, 2.0], 0.02, M.inox, 8);
  C([27.45, ho.y0 - 0.12, 2.0], [27.45, ho.y0 - 0.26, 2.0], 0.05, M.naranjaSeg, 14);
  PLACA(["BE-01"], 27.45, ho.y0 - 0.005, 2.25, 0, 0.16, 0.06, { bg: "#f4f4f0" });
  B(25.8, ho.y0 - 0.1, 2.35, 25.95, ho.y0, 2.5, M.azulSensor);
  PLACA(["PS-01"], 25.875, ho.y0 - 0.105, 2.6, 0, 0.16, 0.06, { bg: "#f4f4f0" });
  // LS-01 tolva de recepción
  var tv = G.tolva;
  B(2.4, tv.y0 - 0.1, 1.45, 2.56, tv.y0, 1.6, M.azulSensor);
  PLACA(["LS-01"], 2.48, tv.y0 - 0.105, 1.7, 0, 0.16, 0.06, { bg: "#f4f4f0" });
  // LS-02A / LS-02B y TS-01 en el silo (lado Oeste, hacia el anexo)
  SENSOR(si.x - si.D / 2, si.y + 0.4, ki - 0.8, [-1, 0, 0], "LS-02A");
  SENSOR(si.x - si.D / 2, si.y + 0.4, si.z_boca + si.h_cono + 0.6, [-1, 0, 0], "LS-02B");
  V(si.x + 0.5, si.y + 0.3, ki + 0.35, ki + 0.6, 0.06, M.azulSensor, 12);
  // LS-03 y AT-01 del lavador
  var ts = G.tanque_sol;
  V(ts.x, ts.y, ts.h, ts.h + 0.12, 0.05, M.inox, 12);
  V(ts.x, ts.y, ts.h + 0.12, ts.h + 0.26, 0.08, M.azulSensor, 14);
  PLACA(["LS-03"], ts.x, ts.y - 0.09, ts.h + 0.4, 0, 0.16, 0.06, { bg: "#f4f4f0" });
  (function () { var bx = G.bomba.x + 0.6, by = 22.6; B(bx - 0.12, by - 0.09, 0.9, bx - 0.04, by + 0.09, 1.12, M.azulSensor); PLACA(["AT-01 pH"], bx - 0.13, by, 1.25, -Math.PI / 2, 0.18, 0.06, { bg: "#f4f4f0" }); })();
  // SS-01..03 sensores de giro (tambor de reenvío, lado Norte) y ZS-10/11 de borde
  sec.pisos.forEach(function (Pz, i) {
    var zr = Pz.zc - sec.r_reenvio, xc = X(Pz.cola);
    B(xc - 0.05, Y(2.86), zr - 0.12, xc + 0.05, Y(2.9), zr + 0.12, M.estructura);
    C([xc, Y(2.9), zr + 0.07], [xc, Y(2.98), zr + 0.07], 0.018, M.azulSensor, 10);
    PLACA(["SS-0" + (i + 1)], xc, Y(2.991), zr + 0.2, Math.PI, 0.14, 0.05, { bg: "#f4f4f0" });
    [0.32, 2.28].forEach(function (yy) { var s = B(xc + (Pz.sentido > 0 ? 0.35 : -0.45), Y(yy) - 0.03, Pz.zc + 0.02, xc + (Pz.sentido > 0 ? 0.45 : -0.35), Y(yy) + 0.03, Pz.zc + 0.08, M.azulSensor); s.userData.zona = "sec"; });
  });

  /* ===================================================== D6 PUNTOS DE MEDICIÓN */
  parte("D6");
  BOQUILLA(dc.x1, 11.2, 1.4, [1, 0, 0]);
  BOQUILLA(22.5, 11.5, 1.4, [0, 1, 0]);
  var ag = [X(sec.campana_x), sec.yc];
  var nB = cur.children.length;
  BOQUILLA(ag[0] + 0.4, ag[1], 5.4, [1, 0, 0]);
  BOQUILLA(ag[0], ag[1] + 0.4, 5.4, [0, 1, 0]);
  cur.children.slice(nB).forEach(function (m) { m.userData.zona = "otro"; });
  BOQUILLA(X(1.2), Y(sec.A), 0.66, [0, 1, 0]);
  BOQUILLA(15.8 + 0.4, 22.1, 3.6, [1, 0, 0]);
  BOQUILLA(ch.x, ch.y - ch.D / 2, 8.35, [0, -1, 0]);
  BOQUILLA(ch.x - ch.D / 2, ch.y, 8.35, [-1, 0, 0]);
  BOQUILLA(ex.chim_x, ex.chim_y - ex.chim_D / 2, 2.6, [0, -1, 0]);

  /* ===================================================== D7 RECIRCULACIÓN */
  parte("D7");
  var rc = [[15.2, 22.1, 7.5], [15.2, 22.1, 8.05], [19.9, 22.1, 8.05], [19.9, 22.1, 3.25], [19.9, 19.6, 3.25], [19.9, 19.6, 2.45]];
  TUBO(rc, 0.25, M.recirc, 18);
  V(15.2, 22.1, 7.45, 7.62, 0.29, M.recirc, 18);
  // cámara de mezcla con compuerta de aire fresco (sobre la toma existente del anexo)
  B(19.55, 18.65, 0.45, 20.25, 20.55, 2.45, M.galv);
  for (var zl = 0.6; zl < 2.3; zl += 0.16) B(19.5, 18.75, zl, 19.55, 20.45, zl + 0.07, M.grisOsc);
  B(19.45, 19.3, 1.2, 19.5, 19.55, 1.45, M.azulSensor); // actuador CD-02
  PLACA(["CD-02 AIRE FRESCO"], 19.49, 19.6, 2.25, -Math.PI / 2, 0.36, 0.09, { bg: "#f4f4f0" });
  // soportes: pórtico y ménsulas al muro Oeste del anexo
  BAR([19.05, 22.7, 0], [19.05, 22.7, 7.8], 0.1, M.estructura);
  BAR([15.2, 22.85, 0], [15.2, 22.85, 7.8], 0.1, M.estructura);
  BAR([15.2, 22.85, 7.8], [19.05, 22.7, 7.8], 0.08, M.estructura);
  BAR([15.2, 22.1, 7.78], [15.2, 22.85, 7.78], 0.06, M.estructura);
  BAR([19.05, 22.1, 7.78], [19.05, 22.7, 7.78], 0.06, M.estructura);
  [6.2, 4.4].forEach(function (z) { BAR([19.9, 22.1, z], [20.3, 22.1, z], 0.06, M.estructura); });
  BAR([19.9, 20.8, 3.25], [20.3, 20.8, 3.25], 0.06, M.estructura);
  // compuerta CD-03 con actuador
  V(19.9, 22.1, 5.4, 5.55, 0.29, M.grisOsc, 18);
  B(20.1, 21.95, 5.35, 20.28, 22.25, 5.6, M.azulSensor);
  PLACA(["CD-03 RECIRC."], 19.64, 22.1, 5.95, -Math.PI / 2, 0.3, 0.09, { bg: "#f4f4f0" });
  BOQUILLA(19.9 - 0.25, 22.1, 4.8, [-1, 0, 0]);

  /* ===================================================== D8 COMPUERTAS Y BY-PASS */
  parte("D8");
  // CD-01 entrada de aire caliente (tramo vertical del ducto caliente)
  B(dc.x0 - 0.05, 10.85, 2.3, dc.x1 + 0.05, 11.55, 2.42, M.grisOsc);
  B(dc.x1 + 0.05, 11.1, 2.28, dc.x1 + 0.26, 11.3, 2.48, M.azulSensor);
  PLACA(["CD-01"], dc.x1 + 0.155, 11.095, 2.6, 0, 0.14, 0.05, { bg: "#f4f4f0" });
  // CD-04 salida del secador (ducto de aire agotado vertical)
  V(ag[0], ag[1], 4.75, 4.9, 0.45, M.grisOsc, 24).userData.zona = "otro";
  B(ag[0] + 0.45, ag[1] - 0.1, 4.7, ag[0] + 0.65, ag[1] + 0.1, 4.95, M.azulSensor).userData.zona = "otro";
  PLACA(["CD-04"], ag[0] + 0.55, ag[1] - 0.105, 5.1, 0, 0.14, 0.05, { bg: "#f4f4f0" }).userData.zona = "otro";
  // CD-05 by-pass de humos: hogar -> chimenea
  var bp = [[26.8, 21.9, ho.z1], [26.8, 21.9, 4.25], [26.8, 24.15, 4.25], [ch.x, 24.15, 4.25], [ch.x, ch.y - 0.25, 4.25]];
  TUBO(bp, 0.22, M.grisOsc, 16);
  V(24.3, 24.15, 4.03, 4.47, 0.24, M.galv, 16).rotation.z = 0;
  B(24.2, 24.39, 4.1, 24.45, 24.55, 4.4, M.azulSensor);
  PLACA(["CD-05 BY-PASS"], 24.3, 24.38, 4.62, 0, 0.3, 0.08, { bg: "#f4f4f0" });

  /* ===================================================== D9 REGISTROS Y BOCAS DE LIMPIEZA */
  parte("D9");
  // ciclón: boca de inspección Ø450 al Este
  C([cy.x + cy.D / 2 - 0.02, cy.y, 5.2], [cy.x + cy.D / 2 + 0.1, cy.y, 5.2], 0.24, M.inox, 20);
  for (var bk = 0; bk < 8; bk++) { var ab = bk / 8 * Math.PI * 2; SPH(cy.x + cy.D / 2 + 0.11, cy.y + 0.2 * Math.cos(ab), 5.2 + 0.2 * Math.sin(ab), 0.015, M.negro); }
  C([cy.x + cy.D / 2 + 0.1, cy.y - 0.08, 5.2], [cy.x + cy.D / 2 + 0.18, cy.y - 0.08, 5.2], 0.012, M.negro, 6);
  // lavador: dos bocas de hombre (Sudoeste)
  [[1.4, 1.25 * Math.PI], [4.9, 1.12 * Math.PI]].forEach(function (b) {
    var ca = Math.cos(b[1]), sa = Math.sin(b[1]), r0 = sc.D / 2 - 0.02;
    C([sc.x + r0 * ca, sc.y + r0 * sa, b[0]], [sc.x + (r0 + 0.14) * ca, sc.y + (r0 + 0.14) * sa, b[0]], 0.3, v.prfv, 20);
    C([sc.x + (r0 + 0.14) * ca, sc.y + (r0 + 0.14) * sa, b[0]], [sc.x + (r0 + 0.18) * ca, sc.y + (r0 + 0.18) * sa, b[0]], 0.34, M.grisOsc, 20);
  });
  // registros abulonados en ducto caliente (horizontal) y ducto agotado
  B(dc.x1, 14.6, 3.35, dc.x1 + 0.03, 15.3, 3.7, M.grisOsc);
  B(dc.x1 + 0.03, 14.9, 3.47, dc.x1 + 0.06, 15.0, 3.58, M.negro);
  B(ag[0] - 0.2, 13.4, 6.06, ag[0] + 0.2, 14.0, 6.12, M.grisOsc);
  // tapa abisagrada del sinfín de descarga
  var sd2 = G.sinfin_desc;
  B(sd2.x0 + 0.05, sd2.y - 0.13, 0.34, sd2.x0 + 1.05, sd2.y + 0.13, 0.37, M.inox);
  [sd2.x0 + 0.3, sd2.x0 + 0.8].forEach(function (x) { B(x - 0.04, sd2.y + 0.13, 0.35, x + 0.04, sd2.y + 0.16, 0.39, M.negro); });
  // tolva de recepción: boca de limpieza
  B(tv.x1 - 0.05, 9.0, 1.05, tv.x1 + 0.02, 9.6, 1.45, M.inox);
  // intercambiador: tapas de cabezales con manijas
  var ic = G.anexo.intercambiador;
  B(ic.x0 - 0.04, ic.y0 + 0.2, 1.72, ic.x0, ic.y1 - 0.2, ic.z1 - 0.1, M.grisOsc);
  [0.6, 1.6].forEach(function (d) { B(ic.x0 - 0.1, ic.y0 + d - 0.12, 2.12, ic.x0 - 0.04, ic.y0 + d + 0.12, 2.16, M.negro); });
  // silo: boca de inspección lateral
  C([si.x - si.D / 2 + 0.02, si.y - 0.6, si.z_boca + si.h_cono + 1.2], [si.x - si.D / 2 - 0.1, si.y - 0.6, si.z_boca + si.h_cono + 1.2], 0.25, M.galv, 18);

  /* ===================================================== D10 LAVADOR: COMPLEMENTOS */
  parte("D10");
  TORO(sc.x, sc.y, 5.0, sc.D / 2 - 0.25, 0.035, M.pvc).userData.corte = "";
  for (var nz = 0; nz < 8; nz++) { var an = nz / 8 * Math.PI * 2; C([sc.x + (sc.D / 2 - 0.25) * Math.cos(an), sc.y + (sc.D / 2 - 0.25) * Math.sin(an), 5.0], [sc.x + (sc.D / 2 - 0.25) * Math.cos(an), sc.y + (sc.D / 2 - 0.25) * Math.sin(an), 4.9], 0.02, M.negro, 6); }
  // drenaje del tanque de solución a la cámara de purga
  TUBO([[ts.x, ts.y + 0.9, 0.12], [ts.x, ts.y + 1.5, 0.12], [13.7, ts.y + 1.5, 0.08]], 0.04, M.pvc);
  C([ts.x, ts.y + 1.2, 0.12], [ts.x, ts.y + 1.2, 0.3], 0.05, M.rojo, 10);
  B(13.35, 25.1, -0.02, 14.0, 25.75, 0.05, M.hormigon);
  B(13.4, 25.15, 0.05, 13.95, 25.7, 0.07, M.rejilla);
  // purga a IBC de sulfato de amonio
  (function ibc(xc, yc, liq) {
    B(xc - 0.6, yc - 0.5, 0, xc + 0.6, yc + 0.5, 0.15, M.madera);
    B(xc - 0.55, yc - 0.45, 0.15, xc + 0.55, yc + 0.45, 1.15, new dn({ color: 0xe8e8e0, transparent: !0, opacity: 0.55, roughness: 0.3 }));
    B(xc - 0.53, yc - 0.43, 0.16, xc + 0.53, yc + 0.43, 0.7, liq);
    for (var gx = -0.55; gx <= 0.56; gx += 0.275) BAR([xc + gx, yc - 0.46, 0.15], [xc + gx, yc - 0.46, 1.16], 0.012, M.galv);
    for (var gz = 0.4; gz < 1.2; gz += 0.25) BAR([xc - 0.56, yc - 0.46, gz], [xc + 0.56, yc - 0.46, gz], 0.012, M.galv);
    V(xc, yc, 1.15, 1.22, 0.1, M.negro, 12);
  })(12.6, 25.6, new dn({ color: 0xbfd8e6, roughness: 0.2 }));
  TUBO([[G.bomba.x + 0.6, G.bomba.y, 0.3], [G.bomba.x + 0.6, 26.3, 0.3], [12.9, 26.3, 1.3], [12.9, 25.8, 1.3]], 0.025, M.pvc);
  PLACA(["PURGA", "SULFATO DE AMONIO"], 12.6, 25.09, 0.95, 0, 0.36, 0.12);
  // dosificación de ácido: IBC con bandeja antiderrame + bomba dosificadora
  B(11.6, 22.3, 0, 13.1, 23.8, 0.25, M.naranjaSeg);
  (function (xc, yc) {
    B(xc - 0.55, yc - 0.45, 0.25, xc + 0.55, yc + 0.45, 1.25, new dn({ color: 0xe8e8e0, transparent: !0, opacity: 0.55, roughness: 0.3 }));
    B(xc - 0.53, yc - 0.43, 0.26, xc + 0.53, yc + 0.43, 0.9, new dn({ color: 0xd9c86a, roughness: 0.25 }));
    V(xc, yc, 1.25, 1.32, 0.1, M.negro, 12);
  })(12.35, 23.05);
  B(13.15, 22.9, 0, 13.4, 23.15, 0.3, M.azulSensor);
  TUBO([[13.27, 23.02, 0.3], [13.27, 23.02, 1.1], [ts.x - 0.62, ts.y - 0.4, 1.9]], 0.012, M.pvc);
  CARTEL("adv", "ÁCIDO|CORROSIVO", "!", 12.35, 22.59, 1.55, 0, 0.36);
  // ducha de emergencia con lavaojos
  (function (xd, yd) {
    V(xd, yd, 0, 2.3, 0.03, M.verde, 10);
    C([xd, yd, 2.3], [xd + 0.35, yd, 2.3], 0.025, M.verde, 8);
    V(xd + 0.35, yd, 2.12, 2.26, 0.14, M.verde, 16, { rTop: 0.03 });
    C([xd, yd, 1.05], [xd + 0.3, yd, 1.05], 0.02, M.verde, 8);
    V(xd + 0.3, yd, 1.05, 1.12, 0.12, M.verde, 16);
    CARTEL("salv", "DUCHA Y|LAVAOJOS", "salida", xd, yd - 0.04, 2.0, 0, 0.3);
  })(11.0, 21.4);

  /* ===================================================== D11 CICLÓN */
  parte("D11");
  C([cy.x + 0.2, cy.y, cy.z_cono0 - 0.2], [cy.x + 0.45, cy.y, cy.z_cono0 - 0.2], 0.08, M.motor, 12);
  PLACA(["CI-18 CICLÓN Ø1800"], cy.x, cy.y - cy.D / 2 - 0.005, 4.4, 0, 0.5, 0.12);
  B(cy.x - 0.45, 20.0, 6.35, cy.x - 0.41, 20.6, 6.75, M.grisOsc);

  /* ===================================================== D12 GENERADOR */
  parte("D12");
  // puerta de inspección y mirilla del hogar (cara Sur)
  B(26.35, ho.y0 - 0.05, 0.9, 26.95, ho.y0, 1.5, M.grisOsc);
  B(26.85, ho.y0 - 0.11, 1.15, 26.9, ho.y0 - 0.05, 1.25, M.negro);
  [26.4, 26.9].forEach(function (x) { B(x - 0.03, ho.y0 - 0.07, 0.95, x + 0.03, ho.y0 - 0.02, 1.02, M.negro); });
  C([26.65, ho.y0, 1.85], [26.65, ho.y0 - 0.06, 1.85], 0.06, M.negro, 16);
  C([26.65, ho.y0 - 0.06, 1.85], [26.65, ho.y0 - 0.065, 1.85], 0.04, new dn({ color: 0xff7a1a, emissive: 0xff5a10, emissiveIntensity: 0.9 }), 16);
  CARTEL("adv", "SUPERFICIE|CALIENTE", "calor", 25.5, ho.y0 - 0.76, 1.35, 0, 0.32);
  PLACA(["GAC-9 HOGAR 882 kW"], 27.4, ho.y0 - 0.005, 2.7, 0, 0.44, 0.11);
  // aislación del ducto de by-pass y cenicero (tapas)
  B(27.0, ho.y1, 0.1, 27.5, ho.y1 + 0.05, 0.5, M.grisOsc);

  /* ===================================================== D13 SILO */
  parte("D13");
  V(si.x - 0.4, si.y - 0.3, ki + 0.05, ki + 0.35, 0.3, M.galv, 18); // boca de hombre
  V(si.x + 0.8, si.y - 0.6, ki - 0.1, ki + 0.55, 0.22, M.galv, 16); // venteo de alivio
  V(si.x + 0.8, si.y - 0.6, ki + 0.55, ki + 0.62, 0.3, M.grisOsc, 16);
  // válvula guillotina en el cono de descarga (sobre el sinfín)
  B(si.x - 0.4, si.y - 0.14, 1.25, si.x + 0.4, si.y + 0.14, 1.33, M.grisOsc);
  B(si.x + 0.4, si.y - 0.05, 1.24, si.x + 0.72, si.y + 0.05, 1.34, M.azulSensor);
  // rociadores: anillo exterior en el borde del techo + montante con válvula de diluvio
  var rR = si.D / 2 + 0.17;
  TORO(si.x, si.y, ki + 0.12, rR, 0.03, M.aguaInc);
  for (var rz = 0; rz < 8; rz++) { var ar = rz / 8 * Math.PI * 2; C([si.x + rR * Math.cos(ar), si.y + rR * Math.sin(ar), ki + 0.12], [si.x + (rR - 0.12) * Math.cos(ar), si.y + (rR - 0.12) * Math.sin(ar), ki + 0.04], 0.018, M.inox, 6); }
  var mx = 28.95, my = 22.6, ar0 = Math.PI * 0.93;
  TUBO([[mx, my, 0.2], [mx, my, ki + 0.12], [si.x + rR * Math.cos(ar0), si.y + rR * Math.sin(ar0), ki + 0.12]], 0.04, M.aguaInc);
  B(mx - 0.15, my - 0.15, 0.7, mx + 0.15, my + 0.15, 1.1, M.aguaInc);
  PLACA(["VÁLVULA DE DILUVIO", "ROCIADORES DEL SILO"], mx, my - 0.155, 1.35, 0, 0.4, 0.13);
  CARTEL("adv", "RIESGO DE|INCENDIO", "fuego", si.x - 0.62, si.y - si.D / 2 - 0.01, 4.9, 0, 0.5);
  CARTEL("proh", "PROHIBIDO|FUMAR", "fumar", si.x + 0.62, si.y - si.D / 2 - 0.01, 4.9, 0, 0.5);

  /* ===================================================== D14 CENIZAS */
  parte("D14");
  var cz = G.anexo.cenizas;
  V(cz.x, cz.y, 0.62, 0.5, 0.12, M.galv, 12);
  C([cz.x, cz.y, 0.5], [cz.x, cz.y, 0.62], 0.13, M.negro, 12);
  B(cz.x - 0.37, cz.y - 0.3, 0.12, cz.x + 0.37, cz.y + 0.3, 0.42, M.grisOsc);
  B(cz.x - 0.38, cz.y - 0.31, 0.42, cz.x + 0.38, cz.y + 0.31, 0.45, M.galv);
  [[-0.28, -0.24], [0.28, -0.24], [-0.28, 0.24], [0.28, 0.24]].forEach(function (d) { C([cz.x + d[0], cz.y + d[1] - 0.03, 0.06], [cz.x + d[0], cz.y + d[1] + 0.03, 0.06], 0.06, M.negro, 10); });
  B(cz.x + 0.5, cz.y - 0.2, 0.7, cz.x + 0.52, cz.y + 0.2, 1.05, M.grisOsc);
  B(cz.x + 0.52, cz.y - 0.05, 0.85, cz.x + 0.55, cz.y + 0.05, 0.9, M.negro);
  PLACA(["CENIZAS"], cz.x, cz.y - 0.515, 1.2, 0, 0.22, 0.07);

  /* ===================================================== D15 CANALIZACIONES */
  parte("D15");
  var bandeja = function (pts, ancho) { Js(cur, pts, [[-ancho / 2, 0.06], [-ancho / 2, 0], [ancho / 2, 0], [ancho / 2, 0.06]], M.galv, { up: [0, 0, 1], openProfile: !0 }).userData.zona = "otro"; };
  var bandejaV = function (x, y, z0, z1, ancho, eje) {
    var a = ancho / 2;
    if (eje === "x") { B(x - a, y - 0.005, z0, x + a, y + 0.005, z1, M.galv); B(x - a, y, z0, x - a + 0.005, y + 0.06, z1, M.galv); B(x + a - 0.005, y, z0, x + a, y + 0.06, z1, M.galv); }
    else { B(x - 0.005, y - a, z0, x + 0.005, y + a, z1, M.galv); B(x, y - a, z0, x + 0.06, y - a + 0.005, z1, M.galv); B(x, y + a - 0.005, z0, x + 0.06, y + a, z1, M.galv); }
  };
  // instrumentación (150 mm) separada 400 mm de la de potencia existente (+5,30 en y = 7,40)
  bandeja([[4.4, 7.75, 4.9], [27.1, 7.75, 4.9]], 0.15);
  bandeja([[20.45, 7.75, 4.9], [20.45, 0.85, 4.9], [25.15, 0.85, 4.0]], 0.15);
  bandejaV(25.15, 0.65, 2.1, 4.0, 0.15, "x");
  bandeja([[27.1, 7.75, 4.9], [27.1, 17.6, 4.9], [27.1, 18.35, 4.45], [21.2, 18.35, 4.45]], 0.15);
  // potencia: extensión hacia el anexo (desde la troncal existente)
  bandeja([[24.6, 7.4, 5.3], [26.6, 7.4, 5.3], [26.6, 17.6, 5.3], [26.6, 18.8, 4.3], [21.2, 18.8, 4.3]], 0.3);
  // potencia: al lavador y al extractor (exterior Norte)
  bandeja([[18.75, 7.4, 5.3], [18.75, 17.6, 5.3], [18.75, 18.4, 4.2], [18.75, 22.6, 4.2], [16.5, 22.6, 4.2]], 0.3);
  BAR([18.75, 20.4, 0], [18.75, 20.4, 4.14], 0.08, M.estructura);
  // potencia: a la recepción (tolva y vibrador)
  bandeja([[11.4, 7.4, 5.3], [4.0, 7.4, 5.3], [4.0, 7.9, 5.25]], 0.3);
  // bajadas a motores con caño flexible y caja de conexión
  var bajada = function (x, y, zt, zb) { V(x, y, zb, zt, 0.018, M.negro, 8).userData.zona = "otro"; B(x - 0.07, y - 0.05, zb - 0.1, x + 0.07, y + 0.05, zb + 0.04, M.gris).userData.zona = "otro"; };
  [[23.9, 7.45, 5.3, 2.45], [24.25, 7.45, 5.3, 0.6], [12.35, 7.45, 5.3, 1.45], [13.1, 7.45, 5.3, 3.1],
   [4.0, 7.9, 5.25, 2.0], [26.6, 9.3, 5.3, 0.5], [21.55, 18.8, 4.3, 1.0], [24.0, 18.8, 4.3, 1.0], [16.6, 22.6, 4.2, 0.9]].forEach(function (b) { bajada(b[0], b[1], b[2], b[3]); });
  CARTEL("adv", "RIESGO|ELÉCTRICO", "rayo", 25.25, 0.44, 2.45, 0, 0.3);

  /* ===================================================== D16 PUESTA A TIERRA Y PARARRAYOS */
  parte("D16");
  M.cobre = M.cobre || __rdMat(0xb87333, 0.8, 0.35);
  // cámaras de inspección de las jabalinas (anillo enterrado: no se dibuja)
  var camaraPAT = function (x, y, tag) {
    B(x - 0.2, y - 0.2, -0.02, x + 0.2, y + 0.2, 0.05, M.hormigon).userData.zona = "otro";
    B(x - 0.15, y - 0.15, 0.05, x + 0.15, y + 0.15, 0.07, M.grisOsc).userData.zona = "otro";
    V(x + 0.24, y, 0, 0.55, 0.02, M.galv, 8).userData.zona = "otro";
    PLACA([tag], x + 0.24, y - 0.025, 0.5, 0, 0.16, 0.06, { bg: "#f4f4f0" });
  };
  [[-0.6, -0.6, "PAT-1"], [33.6, -0.6, "PAT-2"], [-0.6, 18.6, "PAT-3"], [20.0, 25.0, "PAT-4"],
   [29.2, 25.0, "PAT-5"], [33.6, 18.6, "PAT-6"], [24.0, -0.6, "PAT-7"], [16.4, 25.6, "PAT-8"],
   [61.2, 17.0, "PAT-9"], [84.5, 24.0, "PAT-10"]].forEach(function (p) { camaraPAT(p[0], p[1], p[2]); });
  // barra equipotencial principal (BEP) en la sala de control
  B(23.0, 0.12, 0.45, 23.6, 0.16, 0.5, M.cobre).userData.zona = "otro";
  [23.08, 23.2, 23.32, 23.44, 23.56].forEach(function (xb) { V(xb, 0.18, 0.45, 0.5, 0.012, M.galv, 6).userData.zona = "otro"; });
  PLACA(["BEP · BARRA EQUIPOTENCIAL"], 23.3, 0.11, 0.62, Math.PI, 0.5, 0.07, { bg: "#f4f4f0" });
  // pararrayos Franklin con bajada de cobre y guardacable
  var pararrayos = function (x, y, ztop, r, lado) {
    V(x, y, ztop, ztop + 1.5, 0.015, M.inox, 8);
    CONO([x, y, ztop + 1.5], [0, 0, 1], 0.03, 0.2, M.inox);
    var bx = x + lado[0] * (r + 0.04), by = y + lado[1] * (r + 0.04);
    C([x, y, ztop + 0.05], [bx, by, ztop + 0.05], 0.006, M.cobre, 6);
    C([bx, by, ztop + 0.05], [bx, by, 0.05], 0.006, M.cobre, 6);
    V(bx, by, 0, 2.0, 0.022, M.pvc, 8);
  };
  var chx = G.anexo.chimenea;
  pararrayos(chx.x, chx.y, chx.h, chx.D / 2, [-1, 0]);
  pararrayos(G.extractor.chim_x, G.extractor.chim_y, G.extractor.chim_h, G.extractor.chim_D / 2, [1, 0]);
  pararrayos(si.x, si.y, ki + si.h_techo, si.D / 2, [0, -1]);

  /* ===================================================== D17 ILUMINACIÓN */
  parte("D17");
  var emerg = function (x, y, z, rot, conCartel) {
    var o = off(rot, 1), sx = Math.abs(o[0]) > 0.5 ? 0.04 : 0.17, sy = Math.abs(o[0]) > 0.5 ? 0.17 : 0.04;
    B(x - sx, y - sy, z, x + sx, y + sy, z + 0.1, M.blanco);
    B(x - sx * 0.8 + o[0] * 0.035, y - sy * 0.8 + o[1] * 0.035, z + 0.01, x + sx * 0.8 + o[0] * 0.045, y + sy * 0.8 + o[1] * 0.045, z + 0.04, M.emergencia);
    if (conCartel) CARTEL("salv", "SALIDA", "salida", x + o[0] * 0.05, y + o[1] * 0.05, z + 0.32, rot, 0.34);
  };
  // salidas: SE1 (Este), SE2 (Oeste), PP1 (Sur), P1, P2, P3 y puerta RF-60
  emerg(32.95, 15.6, 2.45, -Math.PI / 2, !0);
  emerg(0.05, 2.6, 2.45, Math.PI / 2, !0);
  emerg(19.5, 0.05, 2.45, Math.PI, !0);
  emerg(0.05, 14.6, 4.75, Math.PI / 2, !0);
  emerg(30.0, 0.05, 4.75, Math.PI, !0);
  emerg(32.95, 13.65, 3.45, -Math.PI / 2, !0);
  emerg(26.7, 17.95, 2.35, 0, !1);
  emerg(24.6, G.anexo.y1 - 0.25, 2.3, 0, !0);
  emerg(24.3, 4.8, 2.7, 0, !1);
  // proyectores LED sobre plataformas y zonas de trabajo
  var proy = function (x, y, z, dx, dy) { B(x - 0.12, y - 0.12, z, x + 0.12, y + 0.12, z + 0.08, M.grisOsc); var g = B(x - 0.1 + dx * 0.02, y - 0.1 + dy * 0.02, z - 0.01, x + 0.1 + dx * 0.02, y + 0.1 + dy * 0.02, z, M.led); g.castShadow = !1; };
  proy(15.3, 20.3, 8.6, 0, 1);
  proy(17.3, 19.8, 7.8, 0, 1);
  proy(28.0, 12.2, 6.1, 0, 0);

  /* ===================================================== D18 SEÑALIZACIÓN */
  parte("D18");
  [
    ["adv", "RIESGO DE|ATRAPAMIENTO", "atrap", 12.6, 7.94, 1.7, 0],
    ["adv", "RIESGO DE|ATRAPAMIENTO", "atrap", 23.6, 7.94, 1.7, 0],
    ["adv", "SUPERFICIE|CALIENTE", "calor", 17.5, 7.94, 1.7, 0],
    ["adv", "RIESGO DE|ATRAPAMIENTO", "atrap", 3.3, 8.47, 1.55, 0],
    ["obl", "USO OBLIGATORIO|DE EPP", "casco", 1.2, -0.07, 2.6, 0],
    ["obl", "USO OBLIGATORIO|DE EPP", "casco", 18.5, -0.07, 2.6, 0],
    ["proh", "PROHIBIDO|FUMAR", "fumar", 20.5, -0.07, 2.6, 0],
    ["adv", "SUPERFICIE|CALIENTE", "calor", 24.0, 17.93, 2.4, 0],
    ["adv", "RIESGO DE|INCENDIO", "fuego", 31.5, 8.88, 1.45, 0],
    ["adv", "SUPERFICIE|CALIENTE", "calor", 25.9, G.anexo.y1 + 0.21, 2.5, Math.PI],
    ["proh", "PROHIBIDO|FUMAR", "fumar", 23.3, G.anexo.y1 + 0.21, 2.5, Math.PI],
    ["adv", "RIESGO|ELÉCTRICO", "rayo", 14.0, 7.3, 2.25, 0],
  ].forEach(function (s) { CARTEL(s[0], s[1], s[2], s[3], s[4], s[5], s[6], 0.42); });

  /* ===================================================== D19 PROTECCIÓN CONTRA INCENDIOS */
  parte("D19");
  // existentes en la nave: soporte + chapa baliza + cartel
  [[0.25, 5.5, Math.PI / 2], [0.25, 11, Math.PI / 2], [5.5, 0.25, Math.PI], [16.5, 0.25, Math.PI], [11, 17.75, 0], [27.5, 17.75, 0], [32.75, 11, -Math.PI / 2], [22, 0.25, Math.PI]].forEach(function (m) {
    var o = off(m[2], -0.085);
    MATAFUEGO(m[0], m[1], m[2], "ABC", !0);
  });
  // nuevos
  MATAFUEGO(25.75, 1.6, -Math.PI / 2, "CO2");
  MATAFUEGO(32.75, 4.5, -Math.PI / 2, "agua");
  MATAFUEGO(25.6, G.anexo.y1 - 0.12, 0, "ABC");
  MATAFUEGO(20.62, 19.4, Math.PI / 2, "ABC");
  var gabinete = function (x, y, rot, conMF, conManguera) {
    var o = off(rot, 1), porX = Math.abs(o[0]) > 0.5;
    var sx = porX ? 0.15 : 0.35, sy = porX ? 0.35 : 0.15;
    BAR([x - o[0] * 0.1, y - o[1] * 0.1, 0], [x - o[0] * 0.1, y - o[1] * 0.1, 1.0], 0.07, M.galv);
    B(x - sx, y - sy, 1.0, x + sx, y + sy, 1.8, M.rojoInc);
    var fx = x + o[0] * (sx + 0.004), fy = y + o[1] * (sy + 0.004);
    if (porX) B(fx - 0.004, y - 0.28, 1.08, fx + 0.004, y + 0.28, 1.72, M.vidrio);
    else B(x - 0.28, fy - 0.004, 1.08, x + 0.28, fy + 0.004, 1.72, M.vidrio);
    if (conManguera) TORO(x + o[0] * 0.02, y + o[1] * 0.02, 1.4, 0.2, 0.05, M.blanco).rotation.set(0, rot, 0);
    else V(x + o[0] * 0.02, y + o[1] * 0.02, 1.08, 1.6, 0.085, M.rojoInc, 14);
    CARTEL("inc", conManguera ? "HIDRANTE" : "MATAFUEGO", conManguera ? "hidrante" : "matafuego", fx, fy, 2.1, rot, 0.34);
  };
  gabinete(29.3, 24.3, Math.PI, !0, !1);
  gabinete(10.8, 24.2, Math.PI / 2, !0, !1);
  // hidrantes HI-1..HI-4 (poste + gabinete con manguera)
  var hidrante = function (x, y, rot, tag) {
    V(x, y, 0, 0.75, 0.09, M.rojoInc, 14);
    C([x, y, 0.6], [x + 0.2, y, 0.6], 0.04, M.rojoInc, 10);
    V(x, y, 0.75, 0.85, 0.11, M.rojoInc, 14);
    gabinete(x + off(rot, -0.5)[0], y + off(rot, -0.5)[1], rot, !1, !0);
    PLACA([tag], x, y - 0.1, 0.4, 0, 0.14, 0.05, { bg: "#f4f4f0" });
  };
  hidrante(-1.3, 4.6, -Math.PI / 2, "HI-1");
  hidrante(12.0, 19.2, 0, "HI-2");
  hidrante(35.6, 9.5, Math.PI / 2, "HI-3");
  hidrante(82.0, 14.0, 0, "HI-4");
  // detectores de humo y térmicos (techo de locales y anexo)
  [[11.25, 2.2, 2.99], [15.25, 2.2, 2.99], [20, 2.2, 2.99], [24.25, 2.2, 2.99], [22.8, 21.3, 4.79], [26.5, 23.5, 4.79]].forEach(function (d) { V(d[0], d[1], d[2] - 0.05, d[2], 0.06, M.blanco, 14); V(d[0], d[1], d[2] - 0.06, d[2] - 0.05, 0.02, M.balizaRoja, 8); });
  // pulsadores manuales + sirena con baliza junto a cada salida
  var pulsador = function (x, y, rot) { var o = off(rot, 1); var sx = Math.abs(o[0]) > 0.5 ? 0.03 : 0.07, sy = Math.abs(o[0]) > 0.5 ? 0.07 : 0.03; B(x - sx, y - sy, 1.3, x + sx, y + sy, 1.44, M.rojoInc); B(x - sx, y - sy, 2.6, x + sx, y + sy, 2.72, M.rojoInc); V(x + o[0] * 0.05, y + o[1] * 0.05, 2.72, 2.8, 0.035, M.balizaRoja, 10); };
  pulsador(32.95, 16.6, -Math.PI / 2); pulsador(0.05, 3.6, Math.PI / 2); pulsador(18.7, 0.05, Math.PI); pulsador(0.05, 12.3, Math.PI / 2); pulsador(27.4, 0.05, Math.PI);
  // central de incendio en la sala de control (muro Este)
  B(25.8, 3.0, 1.35, 25.85, 3.5, 1.8, M.rojoInc);
  PLACA(["CENTRAL DE INCENDIO"], 25.795, 3.25, 1.9, -Math.PI / 2, 0.44, 0.08);

  /* ===================================================== D20 DRENAJES */
  parte("D20");
  B(X(0.2), Y(-0.68), -0.02, X(12.9), Y(-0.4), 0.004, M.hormigon);
  B(X(0.25), Y(-0.65), 0.004, X(12.85), Y(-0.43), 0.012, M.rejilla, { shadow: !1 });
  B(X(-0.9), Y(-0.9), -0.02, X(-0.3), Y(-0.3), 0.012, M.hormigon);
  B(X(-0.85), Y(-0.85), 0.012, X(-0.35), Y(-0.35), 0.016, M.rejilla, { shadow: !1 });
  // caño PVC (enterrado, se muestra con mojones) a la cámara de lixiviados
  [[9.5, 7.4], [6, 8.2], [2.5, 9.2]].forEach(function (p) { V(p[0], p[1], 0, 0.12, 0.04, M.pvc, 8); });
  // canaleta perimetral del lavador
  B(sc.x - 1.25, sc.y - 1.35, -0.02, sc.x + 1.25, sc.y - 1.2, 0.01, M.rejilla);
  B(sc.x + 1.2, sc.y - 1.35, -0.02, sc.x + 1.35, sc.y + 1.25, 0.01, M.rejilla);

  /* ===================================================== D21 LUBRICACIÓN */
  parte("D21");
  // bloque de lubricación remoto en el lado Sur del secador (a 1,2 m) con líneas a rodamientos
  [X(1.0), X(12.0)].forEach(function (xb) {
    B(xb - 0.12, Y(-0.06), 1.1, xb + 0.12, Y(-0.02), 1.4, M.grisOsc);
    for (var k = 0; k < 5; k++) SPH(xb - 0.09 + k * 0.045, Y(-0.07), 1.25, 0.01, M.amarillo);
    sec.pisos.forEach(function (Pz) { C([xb, Y(-0.05), 1.4], [xb, Y(-0.05), Pz.zc - 0.15], 0.005, M.negro, 5); });
  });
  sec.pisos.forEach(function (Pz) {
    var zm = Pz.zc - sec.r_motriz;
    [Y(-0.07), Y(2.75)].forEach(function (yb) { SPH(X(Pz.cabeza), yb, zm + 0.1, 0.015, M.amarillo); });
    var ac = sec.acc[Pz.n - 1];
    V(X(Pz.cabeza) + ac.dx / 2 + 0.25, Y(-0.3), zm + 0.3, zm + 0.42, 0.03, new dn({ color: 0xd9b24a, transparent: !0, opacity: 0.75, roughness: 0.2 }), 10);
  });
  G.anexo.ventiladores.forEach(function (S) { SPH(S.x + 0.3, S.y - 0.35, 0.95, 0.015, M.amarillo); SPH(S.x - 0.3, S.y - 0.35, 0.95, 0.015, M.amarillo); });
  SPH(el.x + 0.2, el.y - 0.52, 6.6, 0.015, M.amarillo);

  /* ===================================================== D22 TENSORES */
  parte("D22");
  sec.pisos.forEach(function (Pz) {
    var zr = Pz.zc - sec.r_reenvio, xc = X(Pz.cola), s = Pz.sentido > 0 ? -1 : 1;
    [Y(-0.105) + 0.035, Y(sec.A + 0.035) + 0.035].forEach(function (yy) {
      C([xc + s * 0.26, yy, zr], [xc + s * 0.52, yy, zr], 0.012, M.inox, 8);
      C([xc + s * 0.44, yy, zr], [xc + s * 0.47, yy, zr], 0.022, M.negro, 6);
      B(xc + s * 0.47 - 0.02, yy - 0.05, zr - 0.06, xc + s * 0.47 + 0.02, yy + 0.05, zr + 0.06, M.estructura);
    });
  });

  /* ===================================================== D23 PLACAS */
  parte("D23");
  var mot = [
    ["M5 CINTA PISO 1", "0,75 kW · VFD", X(sec.pisos[0].cabeza) + sec.acc[0].dx, Y(-0.53), sec.pisos[0].zc - sec.r_motriz + sec.acc[0].dz + 0.2],
    ["M6 CINTA PISO 2", "0,75 kW · VFD", X(sec.pisos[1].cabeza) + sec.acc[1].dx, Y(-0.53), sec.pisos[1].zc - sec.r_motriz + sec.acc[1].dz + 0.2],
    ["M7 CINTA PISO 3", "0,75 kW · VFD", X(sec.pisos[2].cabeza) + sec.acc[2].dx, Y(-0.53), sec.pisos[2].zc - sec.r_motriz + sec.acc[2].dz + 0.2],
    ["M9 ESPARCIDOR", "0,75 kW · directo", X(sec.esparcidor_x), Y(-0.41), 3.12],
    ["M10 SINFÍN DESC.", "1,1 kW · directo", 26.2, 9.3 - 0.13, 0.5],
    ["M13 SINFÍN CENIZAS", "0,55 kW", cz.x, cz.y - 0.51, 0.95],
    ["M14 BOMBA LAVADOR", "3 kW · directo", G.bomba.x, G.bomba.y - 0.26, 0.55],
  ];
  mot.forEach(function (m) { PLACA([m[0], m[1]], m[2], m[3], m[4], 0, 0.3, 0.11); });
  G.anexo.ventiladores.forEach(function (S, i) { PLACA(["M" + (i + 1) + " VENT. IMPULSIÓN", "15 kW · 15.400 m³/h"], S.x, S.y - 0.625, 0.75, 0, 0.36, 0.13); });
  PLACA(["M3 EXTRACTOR", "22 kW · VFD"], ex.x, ex.y - 0.625, 0.9, 0, 0.36, 0.13);
  PLACA(["M4 VENT. COMBUSTIÓN", "4 kW · VFD"], vc.x + 0.3, vc.y + 0.125, 0.5, Math.PI, 0.3, 0.11);
  PLACA(["LV-19 LAVADOR", "PRFV Ø2200 · pH 3"], sc.x - 0.55, sc.y - sc.D / 2 + 0.13, 2.0, 0, 0.44, 0.14);
  PLACA(["SI-13 SILO CÁSCARA", "70 m³"], si.x, si.y - si.D / 2 - 0.01, 6.0, 0, 0.6, 0.18);
  PLACA(["SC-4 SECADOR DE CINTA", "3 pisos · 72 m² · 8 t/día"], X(6.5), Y(-0.001), 3.1, 0, 0.9, 0.25);
  PLACA(["EL-7 ELEVADOR", "1,5 kW · 6 m"], el.x, el.y - el.ay / 2 - 0.002, 1.5, 0, 0.36, 0.13);

  /* ===================================================== D24 FLECHAS DE FLUJO */
  parte("D24");
  var mG = __rdMat(0xa0672e, 0.1, 0.6, { emissive: 0x3a2008, emissiveIntensity: 0.4 });
  var mA = __rdMat(0xe0443a, 0.1, 0.5, { emissive: 0x5a0e08, emissiveIntensity: 0.4 });
  var mH = __rdMat(0x3aa06a, 0.1, 0.5, { emissive: 0x0c3a20, emissiveIntensity: 0.4 });
  var mR = __rdMat(0xf08a24, 0.1, 0.5, { emissive: 0x5a2a04, emissiveIntensity: 0.4 });
  var mS = __rdMat(0x8f989d, 0.1, 0.5, { emissive: 0x202428, emissiveIntensity: 0.3 });
  // guano
  FLECHA([2.5, 8.1, 2.3], [2.5, 8.1, 1.35], 0.05, mG);
  FLECHA([4.3, 8.55, 0.9], [6.6, 8.55, 1.1], 0.05, mG);
  FLECHA([8.2, 8.55, 2.3], [10.4, 8.55, 3.55], 0.05, mG);
  FLECHA([X(1.0), Y(-1.1), 3.6], [X(3.2), Y(-1.1), 3.6], 0.06, mG);
  FLECHA([X(9.5), Y(-1.1), 2.75], [X(12.0), Y(-1.1), 2.75], 0.06, mG);
  FLECHA([X(12.0), Y(-1.1), 1.9], [X(9.5), Y(-1.1), 1.9], 0.06, mG);
  FLECHA([X(9.5), Y(-1.1), 1.05], [X(12.0), Y(-1.1), 1.05], 0.06, mG);
  FLECHA([25.3, 8.4, 1.0], [25.3, 8.4, 3.2], 0.05, mG);
  FLECHA([26.6, 8.2, 4.8], [27.8, 7.1, 3.6], 0.05, mG);
  FLECHA([26.6, 9.9, 5.4], [27.5, 10.4, 4.7], 0.05, mG);
  // aire caliente (rojo) y aire agotado (verde)
  FLECHA([24.0, 19.9, 0.2], [24.0, 20.9, 0.2], 0.06, mA);
  FLECHA([23.5, 13.0, 4.25], [23.5, 11.8, 4.25], 0.07, mA);
  FLECHA([23.4, 11.9, 1.4], [23.4, 11.9, 0.7], 0.06, mA);
  FLECHA([X(sec.campana_x) - 0.7, sec.yc, 4.2], [X(sec.campana_x) - 0.7, sec.yc, 5.6], 0.07, mH);
  FLECHA([13.8, 13.0, 6.5], [13.8, 16.5, 6.5], 0.07, mH);
  FLECHA([13.6, 21.1, 7.8], [13.6, 21.1, 5.0], 0.06, mH);
  FLECHA([16.6, 22.9, 3.0], [16.6, 22.9, 5.8], 0.06, mH);
  FLECHA([18.25, 23.2, 8.0], [18.25, 23.2, 9.8], 0.06, mH);
  // humos (gris)
  FLECHA([ch.x + 0.5, ch.y, 9.5], [ch.x + 0.5, ch.y, 11.2], 0.06, mS);
  // recirculación (naranja)
  FLECHA([16.0, 21.75, 8.45], [18.8, 21.75, 8.45], 0.07, mR);
  FLECHA([19.45, 22.4, 7.2], [19.45, 22.4, 5.0], 0.07, mR);
  FLECHA([19.45, 21.6, 3.7], [19.45, 20.2, 3.7], 0.07, mR);
  ETIQ("FLUJO DE GUANO|tolva → cinta → esparcidor → 3 cintas → descarga", X(6.5), Y(-1.4), 4.6, 3.4, "#b07334");
  ETIQ("AIRE CALIENTE ≈ 100 °C (máx. 135)|generador → intercambiador → secador", 24.4, 14.5, 5.0, 3.2, "#e0443a");
  ETIQ("AIRE A TRATAR 33-37 °C, CASI SATURADO|secador → ciclón (aislado) → lavador", 13.3, 15.0, 7.6, 3.2, "#3aa06a");
  ETIQ("RECIRCULACIÓN (CD-03 CERRADA)|abre solo con HR de mezcla < 90 %", 17.6, 21.6, 9.3, 3.0, "#f08a24");

  /* ===================================================== E1 LIMPIEZA Y DESINFECCIÓN DE VEHÍCULOS */
  parte("E1");
  (function () {
    // sobre el carril de la báscula (el semáforo existente queda al Oeste, en x = 3,35)
    var y0 = -16.9, y1 = -12.2, xa = 4.1, xb = 7.5;
    B(xa, y0, -0.2, xb, y1, 0.014, M.hormigon);
    B(xa + 0.2, y0 + 0.9, -0.05, xb - 0.2, y1 - 0.9, 0.016, M.desinf, { shadow: !1 });
    [y0, y1].forEach(function (yy) { B(xa, yy - 0.02, 0.0, xb, yy + 0.02, 0.022, M.amarillo, { shadow: !1 }); });
    // arco de aspersión
    var ya = -14.6;
    [xa - 0.35, xb + 0.35].forEach(function (x) { BAR([x, ya, 0], [x, ya, 4.9], 0.16, M.galv); });
    BAR([xa - 0.35, ya, 4.9], [xb + 0.35, ya, 4.9], 0.14, M.galv);
    TUBO([[xa - 0.2, ya - 0.12, 0.4], [xa - 0.2, ya - 0.12, 4.75], [xb + 0.2, ya - 0.12, 4.75], [xb + 0.2, ya - 0.12, 0.4]], 0.03, M.pvc);
    for (var k = 0; k < 7; k++) { var x = xa + 0.3 + k * (xb - xa - 0.6) / 6; C([x, ya - 0.12, 4.75], [x, ya - 0.12, 4.62], 0.02, M.negro, 6); }
    for (var k2 = 0; k2 < 4; k2++) { var z = 0.8 + k2 * 1.1; C([xa - 0.2, ya - 0.12, z], [xa - 0.05, ya - 0.12, z], 0.018, M.negro, 6); C([xb + 0.2, ya - 0.12, z], [xb + 0.05, ya - 0.12, z], 0.018, M.negro, 6); }
    B(xb + 0.2, ya - 0.1, 1.2, xb + 0.3, ya + 0.1, 1.35, M.azulSensor); // sensor de paso
    var mat = new dn({ map: Sr([{ t: "DESINFECCIÓN DE VEHÍCULOS", s: 26 }, { t: "PASO A 5 km/h · NO DETENERSE", s: 18 }], { w: 384, h: 96, bg: "#0b8a43" }), roughness: 0.6 });
    PLANO((xa + xb) / 2, ya - 0.2, 4.6, 3.4, 0.85, 0, mat, !0);
    // tanque de desinfectante + bomba M17 sobre platea
    B(-2.6, -17.3, 0, -0.6, -15.3, 0.12, M.hormigon);
    B(-2.5, -17.2, 0.12, -1.3, -16.0, 0.3, M.naranjaSeg);
    (function (xc, yc) { B(xc - 0.5, yc - 0.45, 0.3, xc + 0.5, yc + 0.45, 1.3, new dn({ color: 0xe8e8e0, transparent: !0, opacity: 0.55, roughness: 0.3 })); B(xc - 0.48, yc - 0.43, 0.31, xc + 0.48, yc + 0.43, 0.9, new dn({ color: 0x6fae9a, roughness: 0.2 })); })(-1.9, -16.6);
    B(-1.1, -16.3, 0.12, -0.7, -15.9, 0.45, M.motor);
    TUBO([[-0.9, -16.1, 0.45], [-0.9, -14.62, 0.45], [xa - 0.2, -14.62, 0.4]], 0.025, M.pvc);
    PLACA(["M17 BOMBA ARCO", "1,1 kW"], -0.9, -16.31, 0.65, 0, 0.3, 0.11);
    CARTEL("adv", "PRODUCTO|QUÍMICO", "!", -1.9, -17.1, 1.6, 0, 0.36);
    gabinete(-1.6, -18.0, 0, !0, !1);
    MATAFUEGO(-4.2, -31.2, -Math.PI / 2, "ABC");
    // pediluvio y lavabotas en el acceso del personal (PP1)
    B(18.9, -1.4, 0, 20.1, -0.5, 0.06, M.grisOsc);
    B(18.95, -1.35, 0.06, 20.05, -0.55, 0.07, M.desinf, { shadow: !1 });
    B(20.6, -0.6, 0, 21.2, -0.2, 0.95, M.blanco);
    V(20.9, -0.4, 0.95, 1.05, 0.08, M.grisOsc, 12);
    PLACA(["PEDILUVIO · LAVABOTAS"], 20.9, -0.61, 0.8, 0, 0.5, 0.09);
  })();

  /* ===================================================== E2 LAVADERO DE CAMIONES (P1) */
  parte("E2");
  (function () {
    var xw = -0.35, yw = 20.0;
    B(xw - 0.5, yw - 0.7, 0, xw, yw + 0.7, 1.1, M.azulSensor);
    B(xw - 0.52, yw - 0.6, 0.2, xw - 0.5, yw + 0.6, 0.9, M.grisOsc);
    TORO(xw - 0.55, yw, 1.55, 0.3, 0.05, M.negro).rotation.set(0, Math.PI / 2, 0);
    B(xw - 0.1, yw - 0.08, 1.1, xw, yw + 0.08, 1.9, M.galv);
    C([xw - 0.5, yw + 0.4, 0.5], [xw - 2.0, yw + 1.2, 0.02], 0.02, M.negro, 6);
    PLACA(["M16 HIDROLAVADORA", "4 kW · 150 bar"], xw - 0.505, yw, 1.25, -Math.PI / 2, 0.36, 0.13);
    CARTEL("obl", "USO OBLIGATORIO|DE EPP", "casco", xw - 0.01, yw - 1.2, 2.3, -Math.PI / 2, 0.42);
    B(-7.5, 8.6, -0.05, -1.0, 9.0, 0.02, M.rejilla, { shadow: !1 });
  })();

  /* ===================================================== E3 CAMPANA, EXTRACTOR, BIOFILTRO, EÓLICOS */
  parte("E3");
  (function () {
    var pg = G.pila_guano;
    // campana piramidal truncada sobre la pila (por encima de la caja del camión volcando, ≈ +5,4 m)
    var zc0 = 5.95, zc1 = 6.5;
    var x0 = 4.4, x1 = 9.2, y0 = 12.6, y1 = 16.9;
    var hood = new dn({ color: 0xb9c0c3, metalness: 0.55, roughness: 0.42, side: wn });
    u0(cur, [[x0, y0, zc0], [x1, y0, zc0], [x1, y1, zc0], [x0, y1, zc0]], [[pg.x - 0.35, pg.y - 0.35, zc1], [pg.x + 0.35, pg.y - 0.35, zc1], [pg.x + 0.35, pg.y + 0.35, zc1], [pg.x - 0.35, pg.y + 0.35, zc1]], hood, !1);
    B(x0, y0, zc0 - 0.08, x1, y0 + 0.05, zc0, M.galv);
    B(x0, y1 - 0.05, zc0 - 0.08, x1, y1, zc0, M.galv);
    TUBO([[pg.x, pg.y, zc1], [pg.x, pg.y, 6.72], [pg.x, 17.6, 6.72], [pg.x, 18.6, 6.72], [5.0, 18.9, 6.72], [5.0, 18.9, 1.6]], 0.3, M.galv, 16);
    [[pg.x, 15.5], [pg.x, 17.3]].forEach(function (p) { BAR([p[0], p[1], 7.0], [p[0], p[1], 7.02], 0.04, M.estructura); });
    [[x0 + 0.2, y0 + 0.2], [x1 - 0.2, y0 + 0.2], [x0 + 0.2, y1 - 0.2], [x1 - 0.2, y1 - 0.2]].forEach(function (p) { C([p[0], p[1], zc0 + 0.02], [p[0], p[1], 7.0], 0.012, M.negro, 5); });
    // extractor M23 y biofiltro al Norte de la recepción
    Be(cur, [4.6, 19.4, 0.9], [5.4, 19.4, 0.9], 0.55, M.galv, 28);
    Be(cur, [4.6, 19.4, 0.9], [4.0, 19.4, 0.9], 0.2, M.motor, 18);
    B(3.8, 18.8, 0, 5.6, 20.0, 0.18, M.estructura);
    TUBO([[5.0, 18.9, 1.6], [5.0, 19.4, 1.45]], 0.3, M.galv, 16);
    TUBO([[5.4, 19.4, 0.9], [6.1, 19.4, 0.9], [6.1, 20.2, 0.4]], 0.3, M.galv, 16);
    PLACA(["M23 EXTRACTOR RECEPCIÓN", "4 kW · 6.000 m³/h"], 4.95, 18.85, 1.65, 0, 0.44, 0.13);
    var bx0 = 0.5, bx1 = 9.0, by0 = 20.2, by1 = 24.7;
    [[bx0, by0, bx1, by0 + 0.2], [bx0, by1 - 0.2, bx1, by1], [bx0, by0, bx0 + 0.2, by1], [bx1 - 0.2, by0, bx1, by1]].forEach(function (w) { B(w[0], w[1], 0, w[2], w[3], 1.5, M.hormigon); });
    B(bx0 + 0.2, by0 + 0.2, 0, bx1 - 0.2, by1 - 0.2, 0.3, M.grisOsc);
    B(bx0 + 0.2, by0 + 0.2, 0.3, bx1 - 0.2, by1 - 0.2, 1.4, M.chips);
    var mat = new dn({ map: Sr([{ t: "BIOFILTRO", s: 30 }, { t: "lecho de chips y compost 1,2 m · 38 m²", s: 17 }], { w: 384, h: 96, bg: "#3f6b3a" }), roughness: 0.6 });
    PLANO((bx0 + bx1) / 2, by0 - 0.02, 1.0, 2.4, 0.6, 0, mat);
    // extractores eólicos en la cumbrera
    [2.75, 8.25, 19.25, 24.75, 30.25, 13.75].forEach(function (x) {
      V(x, 9, 8.3, 8.55, 0.2, M.galv, 16);
      var g = new ge(new fi(0.32, 16, 10, 0, Math.PI * 2, 0, Math.PI / 2), M.aluminio);
      g.position.copy(fe(x, 9, 8.62)); g.scale.set(1, 1.1, 1); cur.add(g);
      V(x, 9, 8.55, 8.66, 0.3, M.aluminio, 16);
    });
  })();

  /* ===================================================== E4 ZARANDA + VÁLVULA DESVIADORA */
  parte("E4");
  (function () {
    // válvula desviadora en el cabezal del elevador y bajada a la zaranda
    B(el.x + 0.25, el.y - 0.3, 5.8, el.x + 0.6, el.y + 0.2, 6.25, M.galv);
    B(el.x + 0.6, el.y - 0.12, 5.95, el.x + 0.74, el.y + 0.03, 6.1, M.azulSensor);
    PLACA(["M35 DESVIADORA"], el.x + 0.425, el.y - 0.305, 6.38, 0, 0.26, 0.07);
    C([el.x + 0.5, el.y + 0.2, 5.85], [28.0, 10.45, 4.45], 0.1, M.galv, 12);
    // plataforma a +3,00 con baranda, columnas y escalera
    var px0 = 26.6, px1 = 29.4, py0 = 10.2, py1 = 14.2, pz = 3.0;
    PLATAFORMA(px0, py0, px1, py1, pz);
    [[px0 + 0.05, py0 + 0.05], [px1 - 0.05, py0 + 0.05], [px0 + 0.05, py1 - 0.05], [px1 - 0.05, py1 - 0.05]].forEach(function (p) { BAR([p[0], p[1], 0], [p[0], p[1], pz - 0.04], 0.1, M.estructura); });
    BARANDA([[px1, py1 - 0.9, pz], [px1, py0, pz], [px0, py0, pz], [px0, py1, pz], [px1 - 0.9, py1, pz]], 1.0);
    // escalera inclinada 60° con pasamanos
    var sx0 = px1 + 1.5, sx1 = px1;
    [py1 - 0.85, py1 - 0.05].forEach(function (yy) { BAR([sx0, yy, 0], [sx1, yy, pz], 0.05, M.amarillo); BAR([sx0, yy, 1.0], [sx1, yy, pz + 1.0], 0.035, M.amarillo); });
    for (var k = 1; k < 12; k++) { var t = k / 12; B(sx0 + (sx1 - sx0) * t - 0.1, py1 - 0.85, pz * t - 0.02, sx0 + (sx1 - sx0) * t + 0.1, py1 - 0.05, pz * t, M.rejilla); }
    // trommel inclinado 5° sobre soportes
    var zt = 3.85, L = 3.0, Rt = 0.45;
    var p0 = [28.0, 10.6, zt + 0.13], p1 = [28.0, 13.6, zt - 0.13];
    C(p0, p1, Rt, new dn({ color: 0xffffff, metalness: 0.6, roughness: 0.4, map: Ne.malla, transparent: !0, opacity: 0.85 }), 28);
    [p0, p1].forEach(function (p) { TORO(p[0], p[1], p[2], Rt, 0.04, M.inox).rotation.set(0, 0, 0); cur.children[cur.children.length - 1].rotation.x = 0; });
    B(27.35, 10.4, pz, 28.65, 13.8, pz + 0.12, M.estructura);
    [10.5, 13.5].forEach(function (yy) { B(27.4, yy - 0.08, pz + 0.12, 27.52, yy + 0.08, zt - 0.3, M.estructura); B(28.48, yy - 0.08, pz + 0.12, 28.6, yy + 0.08, zt - 0.3, M.estructura); });
    // cubierta de protección (media caña) y motor M18
    C([28.0, 10.5, zt + 0.55], [28.0, 13.7, zt + 0.3], 0.03, M.amarillo, 8);
    B(27.3, 10.45, zt + 0.35, 28.7, 13.75, zt + 0.4, new dn({ color: 0xf2c230, transparent: !0, opacity: 0.35, roughness: 0.4, depthWrite: !1 }));
    Be(cur, [28.55, 10.2, zt - 0.1], [28.95, 10.2, zt - 0.1], 0.1, M.motor, 14);
    B(28.35, 10.1, zt - 0.25, 28.6, 10.35, zt + 0.05, M.reductor);
    PLACA(["M18 ZARANDA", "1,1 kW · malla 6 mm"], 28.75, 10.19, zt + 0.15, 0, 0.3, 0.11);
    // rechazo: bajada a big bag
    C([28.0, 13.75, zt - 0.3], [28.0, 14.6, 1.25], 0.12, M.galv, 12);
    B(27.5, 14.1, 0, 28.5, 15.1, 0.12, M.madera);
    B(27.55, 14.15, 0.12, 28.45, 15.05, 1.15, M.bigbag);
    PLACA(["RECHAZO", "cáscara de huevo y plumas"], 28.0, 14.14, 0.8, 0, 0.44, 0.13);
    CARTEL("adv", "RIESGO DE|ATRAPAMIENTO", "atrap", 26.6, 11.5, pz + 1.5, -Math.PI / 2, 0.36);
  })();

  /* ===================================================== E5 ENSACADORA 25 kg */
  parte("E5");
  (function () {
    // tolva pulmón bajo la plataforma
    u0(cur, [[27.35, 11.0, 2.95], [28.65, 11.0, 2.95], [28.65, 12.5, 2.95], [27.35, 12.5, 2.95]], [[27.8, 11.45, 2.05], [28.2, 11.45, 2.05], [28.2, 12.05, 2.05], [27.8, 12.05, 2.05]], M.inox, !1);
    B(27.35, 11.0, 2.9, 28.65, 12.5, 2.95, M.inox);
    // balanza y boca ensacadora
    B(27.7, 11.35, 1.55, 28.3, 12.15, 2.05, M.galv);
    B(27.85, 11.55, 1.25, 28.15, 11.95, 1.55, M.inox);
    B(27.72, 11.3, 1.1, 28.28, 12.2, 1.2, M.negro);
    [[27.62, 11.25], [28.38, 11.25], [27.62, 12.25], [28.38, 12.25]].forEach(function (p) { BAR([p[0], p[1], 0], [p[0], p[1], 2.05], 0.06, M.estructura); });
    B(28.3, 11.45, 1.6, 28.46, 11.75, 1.85, M.azulSensor);
    // bolsa en llenado, cinta de salida y cosedora
    B(27.78, 11.52, 0.55, 28.22, 11.98, 1.12, M.bolsa);
    B(27.7, 11.4, 0.45, 31.0, 12.1, 0.55, M.goma || v.goma);
    for (var x = 27.8; x < 31.0; x += 0.6) B(x, 11.38, 0, x + 0.06, 11.44, 0.45, M.estructura), B(x, 12.06, 0, x + 0.06, 12.12, 0.45, M.estructura);
    B(29.4, 12.15, 0, 29.55, 12.3, 1.5, M.galv);
    B(29.2, 11.9, 1.2, 29.7, 12.3, 1.45, M.azulSensor);
    B(29.3, 11.62, 0.55, 29.72, 11.88, 1.05, M.bolsa);
    B(30.35, 11.6, 0.55, 30.77, 11.9, 1.05, M.bolsa);
    PLACA(["ENSACADORA 25 kg", "M19 · M20 · M21"], 28.0, 11.28, 1.9, 0, 0.36, 0.13);
    // pallets de producto embolsado (el matafuego existente del muro Este queda libre)
    [[31.2, 9.4], [31.2, 10.65]].forEach(function (p) {
      B(p[0], p[1], 0, p[0] + 1.2, p[1] + 1.0, 0.14, M.madera);
      for (var cz2 = 0; cz2 < 5; cz2++) B(p[0] + 0.02, p[1] + 0.02, 0.14 + cz2 * 0.13, p[0] + 1.18, p[1] + 0.98, 0.26 + cz2 * 0.13, M.bolsa);
    });
    // portón P3 (nuevo, muro Este, y = 12,4 a 14,9) marcado con marco y cartel
    B(32.95, 12.4, 0, 33.06, 12.52, 3.1, M.amarillo);
    B(32.95, 14.78, 0, 33.06, 14.9, 3.1, M.amarillo);
    B(32.95, 12.4, 3.0, 33.06, 14.9, 3.1, M.amarillo);
    var mat = new dn({ map: Sr([{ t: "PORTÓN P3 · 2,5 m", s: 24 }, { t: "pallets a depósito de expedición", s: 16 }], { w: 320, h: 80, bg: "#2d3a40" }), roughness: 0.6 });
    PLANO(33.08, 13.65, 3.4, 2.0, 0.5, Math.PI / 2, mat);
  })();

  /* ===================================================== E6 BOLSAS CHICAS */
  parte("E6");
  (function () {
    // transportador flexible desde la tolva pulmón
    TUBO([[28.2, 12.3, 2.1], [28.9, 15.2, 1.4], [29.6, 16.4, 2.75]], 0.06, M.inox, 12);
    B(28.7, 15.0, 0, 29.1, 15.4, 0.6, M.motor);
    // envasadora vertical
    B(29.0, 16.0, 0, 30.2, 17.2, 0.25, M.grisOsc);
    B(29.05, 16.05, 0.25, 30.15, 17.15, 2.2, M.inox);
    u0(cur, [[29.3, 16.3, 2.9], [29.9, 16.3, 2.9], [29.9, 16.9, 2.9], [29.3, 16.9, 2.9]], [[29.5, 16.5, 2.2], [29.7, 16.5, 2.2], [29.7, 16.7, 2.2], [29.5, 16.7, 2.2]], M.inox, !1);
    B(29.3, 15.99, 1.2, 29.9, 16.0, 1.9, M.vidrio);
    B(29.9, 15.95, 1.5, 30.1, 16.0, 1.75, M.pantalla || v.pantalla);
    // mesa con bolsitas y cajas
    B(30.4, 16.6, 0.8, 31.9, 17.4, 0.85, M.galv);
    for (var k = 0; k < 6; k++) B(30.5 + k * 0.23, 16.75, 0.85, 30.66 + k * 0.23, 16.85, 1.1, M.bolsaChica);
    [[30.5, 17.0], [31.0, 17.0], [31.5, 17.0]].forEach(function (p) { B(p[0], p[1], 0.85, p[0] + 0.4, p[1] + 0.35, 1.1, M.carton); });
    PLACA(["ENVASADORA BOLSAS 1-2-5 kg", "M22 · M24 · viveros"], 29.6, 16.04, 2.35, 0, 0.5, 0.14);
  })();

  /* ===================================================== E7 DEPÓSITO DE EXPEDICIÓN */
  parte("E7");
  (function () {
    var dx0 = 60, dx1 = 80, dy0 = 0, dy1 = 12, h = 6.0;
    B(dx0 - 0.3, dy0 - 0.3, -0.02, dx1 + 0.3, dy1 + 0.3, 0.01, M.hormigon);
    var muro = function (a, b, c, d, z0, z1) { B(a, b, z0, c, d, z1, M.ladrillo, { uv: 2 }); };
    // muros de ladrillo macizo hasta 3,0 m y chapa arriba (semitransparente)
    muro(dx0, dy1 - 0.2, dx1, dy1, 0, 3.0);
    muro(dx0, dy0, dx0 + 0.2, dy1, 0, 3.0);
    muro(dx1 - 0.2, dy0, dx1, 7.0, 0, 3.0); muro(dx1 - 0.2, 8.2, dx1, dy1, 0, 3.0); muro(dx1 - 0.2, 7.0, dx1, 8.2, 2.1, 3.0);
    muro(dx0, dy0, 68, dy0 + 0.2, 0, 3.0); muro(72, dy0, dx1, dy0 + 0.2, 0, 3.0); muro(68, dy0, 72, dy0 + 0.2, 4.2, 4.5);
    var ch2 = v.chapa.clone(); ch2.opacity = 0.35;
    [[dx0, dy1 - 0.02, dx1, dy1], [dx0, dy0, dx0 + 0.02, dy1], [dx1 - 0.02, dy0, dx1, dy1]].forEach(function (w) { B(w[0], w[1], 3.0, w[2], w[3], h, ch2, { shadow: !1 }); });
    B(dx0, dy0, 4.5, dx1, dy0 + 0.02, h, ch2, { shadow: !1 });
    // columnas y techo a un agua
    for (var x = dx0; x <= dx1 + 0.01; x += 5) [dy0 + 0.1, dy1 - 0.1].forEach(function (y) { B(x - 0.12, y - 0.12, 0, x + 0.12, y + 0.12, h + (y > 6 ? 0.6 : 0), M.estructura); });
    var te = v.techo.clone(); te.opacity = 0.25;
    u0(cur, [[dx0 - 0.4, dy0 - 0.4, h], [dx1 + 0.4, dy0 - 0.4, h], [dx1 + 0.4, dy1 + 0.4, h + 0.6], [dx0 - 0.4, dy1 + 0.4, h + 0.6]], [[dx0 - 0.4, dy0 - 0.4, h + 0.05], [dx1 + 0.4, dy0 - 0.4, h + 0.05], [dx1 + 0.4, dy1 + 0.4, h + 0.65], [dx0 - 0.4, dy1 + 0.4, h + 0.65]], te, !0);
    for (var x2 = dx0; x2 <= dx1 + 0.01; x2 += 5) BAR([x2, dy0, h], [x2, dy1, h + 0.6], 0.14, M.estructura);
    // portón seccional y dársena de carga
    B(68, dy0 - 0.05, 0, 72, dy0 + 0.05, 4.2, new dn({ color: 0x9aa4ab, metalness: 0.5, roughness: 0.4 }));
    B(67.2, dy0 - 1.2, -0.02, 72.8, dy0, 0.02, M.amarillo);
    for (var k = 0; k < 6; k++) B(67.4 + k * 0.9, dy0 - 1.15, 0.02, 67.8 + k * 0.9, dy0 - 0.05, 0.025, M.negro, { shadow: !1 });
    // salida de emergencia SE3 (Este)
    B(dx1 - 0.05, 7.0, 0, dx1 + 0.02, 8.2, 2.1, M.verde);
    // pallets de stock (12) y transpaleta
    for (var i = 0; i < 12; i++) {
      var px = 61.2 + (i % 6) * 1.6, py = i < 6 ? 9.2 : 7.3;
      B(px, py, 0, px + 1.2, py + 1.0, 0.14, M.madera);
      for (var cz3 = 0; cz3 < 8; cz3++) B(px + 0.02, py + 0.02, 0.14 + cz3 * 0.13, px + 1.18, py + 0.98, 0.26 + cz3 * 0.13, M.bolsa);
    }
    [[72.5, 9.0], [74.2, 9.0]].forEach(function (p) { B(p[0], p[1], 0, p[0] + 1.2, p[1] + 1.0, 0.14, M.madera); for (var r = 0; r < 4; r++) B(p[0] + 0.05, p[1] + 0.05, 0.14 + r * 0.28, p[0] + 1.15, p[1] + 0.95, 0.4 + r * 0.28, M.carton); });
    B(66.5, 3.0, 0, 67.2, 4.5, 1.2, M.naranjaSeg);
    var mat = new dn({ map: Sr([{ t: "DEPÓSITO DE EXPEDICIÓN", s: 26 }, { t: "producto embolsado · sector de incendio S4", s: 16 }], { w: 384, h: 96, bg: "#2d3a40" }), roughness: 0.6 });
    PLANO(70, dy0 - 0.08, 5.0, 4.0, 1.0, 0, mat);
    // iluminación interior
    // 6 campanas LED de 150 W en 2 filas de 3 (cálculo luminotécnico de la memoria: E = 212 lx)
    [[63.35, 3], [70, 3], [76.65, 3], [63.35, 9], [70, 9], [76.65, 9]].forEach(function (p) {
      V(p[0], p[1], h - 0.4, h - 0.3, 0.26, M.led, 16);
      V(p[0], p[1], h - 0.3, h - 0.05, 0.012, M.negro, 6);
    });
    MATAFUEGO(60.3, 1.0, Math.PI / 2, "ABC");
    MATAFUEGO(79.7, 6.6, -Math.PI / 2, "ABC");
    MATAFUEGO(70.0, 11.7, 0, "ABC");
    MATAFUEGO(64.0, 11.7, 0, "agua");
    emerg(dx1 - 0.25, 7.6, 2.4, -Math.PI / 2, !0);
    emerg(70, dy0 + 0.25, 4.7, Math.PI, !0);
    [[65, 6], [75, 6]].forEach(function (p) { V(p[0], p[1], h - 0.06, h - 0.01, 0.06, M.blanco, 12); });
    CARTEL("proh", "PROHIBIDO|FUMAR", "fumar", 66.0, dy0 - 0.02, 2.4, 0, 0.45);
  })();

  /* ===================================================== E9 AMPLIACIÓN DEL PREDIO */
  parte("E9");
  (function () {
    var pav = function (x0, y0, x1, y1) { B(x0, y0, -0.01, x1, y1, 0.013, v.pav, { shadow: !1, uv: 4.5 }); };
    pav(44, -9, 96, -2);
    pav(84, -2, 92, 22);
    pav(84, 16, 96, 22);
    pav(86, -36, 92, -9);
    pav(86, -39, 92, -36);
    // cordones
    [[44, -9.08, 86, -9.0], [92, -9.08, 96, -9.0], [44, -2.0, 60, -1.92], [80, -2.0, 84, -1.92]].forEach(function (c) { B(c[0], c[1], 0, c[2], c[3], 0.13, v.cordon); });
    // portón del acceso de emergencia y servicio (R8)
    var s = G.predio;
    [86, 92].forEach(function (x) { B(x - 0.1, s.y0 - 0.1, 0, x + 0.1, s.y0 + 0.1, 2.4, M.galv); });
    B(86.1, s.y0 - 0.04, 0.1, 91.9, s.y0 + 0.04, 2.0, v.alambrado.clone());
    var mat = new dn({ map: Sr([{ t: "ACCESO DE EMERGENCIA Y SERVICIO", s: 22 }, { t: "BOMBEROS · BIOGÁS · MANTENER LIBRE", s: 16 }], { w: 384, h: 96, bg: "#b3202a" }), roughness: 0.6 });
    PLANO(89, s.y0 + 0.3, 2.9, 3.0, 0.75, 0, mat, !0);
    [[86, s.y0 + 0.2], [92, s.y0 + 0.2]].forEach(function (p) { BAR([p[0], p[1], 0], [p[0], p[1], 2.6], 0.06, M.galv); });
    // cortina forestal del Sector Este
    var troncos = [];
    for (var y = -31; y <= 36; y += 5.5) { troncos.push([97.0, y]); }
    for (var x = 52; x <= 92; x += 5.5) { troncos.push([x, 39.0]); }
    troncos.forEach(function (t, i) {
      if (t[0] > 85 && t[0] < 93 && t[1] < -8) return;
      if (t[0] > 96 && t[1] > 10 && t[1] < 26) return;
      V(t[0], t[1], 0, 2.6, 0.14, v.tronco, 8);
      var g = new ge(new fi(1.3 + (i % 3) * 0.2, 8, 6), __rdMat([0x4f7d3a, 0x5d8a44, 0x466f33][i % 3], 0, 0.95, { flatShading: !0 }));
      g.position.copy(fe(t[0], t[1], 3.6 + (i % 2) * 0.3)); g.scale.set(1, 1.35, 1); g.castShadow = !0; cur.add(g);
    });
    // farolas
    [[58, -10.2], [82, -10.2], [93, 10], [93, 30], [58, 20]].forEach(function (f) {
      V(f[0], f[1], 0, 7, 0.07, M.galv, 10);
      C([f[0], f[1], 7], [f[0] + 0.9, f[1], 7.1], 0.04, M.galv, 8);
      B(f[0] + 0.7, f[1] - 0.15, 6.95, f[0] + 1.2, f[1] + 0.15, 7.05, M.led);
    });
    var mat2 = new dn({ map: Sr([{ t: "SECTOR ESTE · AMPLIACIÓN REV. D", s: 22 }, { t: "expedición · biogás · acceso de bomberos", s: 16 }], { w: 384, h: 96, bg: "#1f4f3a" }), roughness: 0.6 });
    PLANO(89, -24, 2.2, 3.0, 0.75, 0, mat2, !0);
    BAR([87.7, -24, 0], [87.7, -24, 1.85], 0.06, M.galv); BAR([90.3, -24, 0], [90.3, -24, 1.85], 0.06, M.galv);
  })();

  /* ===================================================== E8 SISTEMA DE BIOGÁS */
  // cerco interno de la zona clasificada
  parte("E8.4");
  (function () {
    var fx0 = 60, fx1 = 96, fy0 = 16, fy1 = 38;
    var alam = v.alambrado.clone(); alam.map = Ne.alambrado.clone(); alam.map.needsUpdate = !0;
    var tramo = function (a, b) {
      var L = Math.hypot(b[0] - a[0], b[1] - a[1]);
      var m = alam.clone(); m.map = Ne.alambrado.clone(); m.map.repeat.set(L / 0.2, 1.9 / 0.2); m.map.needsUpdate = !0;
      var p = new ge(new Pn(L, 1.9), m);
      p.position.copy(fe((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, 1.0)); p.rotation.y = Math.atan2(b[1] - a[1], b[0] - a[0]); p.userData.noMerge = !0; cur.add(p);
      for (var k = 0; k <= Math.ceil(L / 3); k++) { var t = k / Math.ceil(L / 3); V(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, 0, 2.05, 0.03, M.galv, 6); }
    };
    tramo([fx0, fy0], [63.5, fy0]); tramo([65, fy0], [84, fy0]); tramo([90, fy0], [fx1, fy0]);
    tramo([fx0, fy0], [fx0, fy1]); tramo([fx0, fy1], [fx1, fy1]); tramo([fx1, fy0], [fx1, fy1]);
    var mat = new dn({ map: Sr([{ t: "ZONA DE BIOGÁS · ATEX", s: 24 }, { t: "PROHIBIDO FUMAR Y LLAMAS · SOLO PERSONAL AUTORIZADO", s: 13 }], { w: 384, h: 96, bg: "#e8c21a", fg: "#111", borde: "#111" }), roughness: 0.6 });
    PLANO(87, fy0 - 0.05, 2.2, 2.8, 0.7, 0, mat, !0);
    CARTEL("adv", "GAS|INFLAMABLE", "gas", 82.0, fy0 - 0.05, 1.6, 0, 0.45, !0);
    CARTEL("proh", "PROHIBIDO|FUMAR", "fumar", 83.0, fy0 - 0.05, 1.6, 0, 0.45, !0);
    // sala de cogeneración (contenedor) y tratamiento del gas
    var cx0 = 62, cx1 = 68.1, cy0 = 18, cy1 = 20.44;
    B(cx0, cy0 - 0.2, -0.02, cx1 + 3.6, cy1 + 0.4, 0.15, M.hormigon);
    B(cx0, cy0, 0.15, cx1, cy1, 2.75, new dn({ color: 0x3d6b52, metalness: 0.4, roughness: 0.5 }));
    for (var x = cx0 + 0.15; x < cx1; x += 0.3) B(x, cy0 - 0.02, 0.2, x + 0.08, cy0, 2.7, new dn({ color: 0x335c46, metalness: 0.4, roughness: 0.5 }));
    B(cx1 - 1.0, cy0 - 0.03, 0.15, cx1 - 0.15, cy0, 2.2, M.grisOsc);
    for (var zz = 0.5; zz < 2.4; zz += 0.18) B(cx0 + 0.4, cy0 - 0.05, zz, cx0 + 1.6, cy0 - 0.02, zz + 0.08, M.grisOsc);
    V(cx0 + 2.6, cy0 + 1.2, 2.75, 5.4, 0.12, M.inox, 12);
    V(cx0 + 2.6, cy0 + 1.2, 5.4, 5.55, 0.18, M.negro, 12);
    var mat2 = new dn({ map: Sr([{ t: "COGENERACIÓN 25 kWe", s: 26 }, { t: "motogenerador a biogás · calor a digestores", s: 15 }], { w: 384, h: 96, bg: "#1f4f3a" }), roughness: 0.6 });
    PLANO((cx0 + cx1) / 2 + 1.2, cy0 - 0.06, 2.3, 2.8, 0.7, 0, mat2);
    // desulfurador, trampa de condensados, soplante, antorcha y tablero
    V(70.6, 19.3, 0.15, 2.5, 0.5, M.galv, 20);
    V(70.6, 19.3, 2.5, 2.8, 0.52, M.grisOsc, 20, { rTop: 0.2 });
    PLACA(["DESULFURADOR"], 70.6, 18.79, 1.6, 0, 0.36, 0.09);
    B(69.2, 19.0, 0.15, 69.8, 19.6, 0.7, M.grisOsc);
    PLACA(["TRAMPA COND."], 69.5, 18.99, 0.9, 0, 0.3, 0.08);
    B(71.4, 18.3, 0.15, 71.6 + 0.4, 18.9, 0.35, M.estructura);
    Be(cur, [71.5, 18.6, 0.6], [71.9, 18.6, 0.6], 0.18, M.gas, 16);
    Be(cur, [71.5, 18.6, 0.6], [71.2, 18.6, 0.6], 0.1, M.motor, 12);
    PLACA(["M33 SOPLANTE BIOGÁS"], 71.7, 18.29, 0.95, 0, 0.36, 0.09);
    B(62.4, 21.2, 0, 63.4, 21.6, 1.9, M.grisOsc);
    B(62.45, 21.18, 0.3, 63.35, 21.2, 1.8, M.blanco);
    PLACA(["TS-BIO"], 62.9, 21.17, 1.6, 0, 0.3, 0.09);
    CARTEL("adv", "RIESGO|ELÉCTRICO", "rayo", 62.9, 21.17, 2.15, 0, 0.3);
    // detectores de gas y baliza
    [[66, 20.5, 2.9], [78, 26.5, 1.8], [90, 28.5, 1.8]].forEach(function (d) { B(d[0] - 0.07, d[1] - 0.04, d[2], d[0] + 0.07, d[1] + 0.04, d[2] + 0.18, M.amarillo); V(d[0], d[1], d[2] + 0.18, d[2] + 0.28, 0.05, M.balizaRoja, 10); });
    MATAFUEGO(68.4, 20.6, 0, "CO2");
    MATAFUEGO(83.0, 17.2, 0, "rod");
  })();

  parte("E8.2");
  (function () {
    var dig = function (xc, yc, tag, mot) {
      var Rr = 3.25, H = 5.0;
      V(xc, yc, -0.02, 0.25, Rr + 0.5, M.hormigon, 36);
      V(xc, yc, 0.25, H, Rr, M.digestor, 48);
      for (var z = 0.9; z < H; z += 1.1) V(xc, yc, z, z + 0.04, Rr + 0.015, new dn({ color: 0x355f57, metalness: 0.55, roughness: 0.35 }), 48);
      // techo de doble membrana (casquete)
      var g = new ge(new fi(Rr, 40, 16, 0, Math.PI * 2, 0, Math.PI / 2), M.membrana);
      g.position.copy(fe(xc, yc, H)); g.scale.set(1, 2.0 / Rr, 1); g.castShadow = !0; cur.add(g);
      TORO(xc, yc, H, Rr, 0.08, M.grisOsc);
      // válvula de sobre/depresión, salida de gas, mirilla, agitador y escalera
      V(xc + 0.9, yc, H + 1.75, H + 2.1, 0.12, M.grisOsc, 12);
      V(xc - 0.6, yc + 0.5, H + 1.85, H + 2.05, 0.08, M.gas, 10);
      C([xc - Rr + 0.3, yc, H - 0.3], [xc - Rr - 0.25, yc, H - 0.3], 0.09, M.gas, 10);
      TUBO([[xc - Rr - 0.25, yc, H - 0.3], [xc - Rr - 0.25, yc, 0.6], [xc - Rr - 0.25, yc - 4.5, 0.6]], 0.045, M.gas);
      C([xc, yc - Rr + 0.02, 3.6], [xc, yc - Rr - 0.06, 3.6], 0.12, M.negro, 16);
      C([xc + 1.2, yc - Rr + 0.05, H - 0.4], [xc + 1.6, yc - Rr - 0.6, H - 0.4], 0.08, M.estructura, 10);
      Be(cur, [xc + 1.6, yc - Rr - 0.6, H - 0.4], [xc + 1.6, yc - Rr - 0.6, H + 0.1], 0.13, M.motor, 12);
      ESCALERA(xc + 2.0, yc - Rr + 0.05 - 0.55, 0, H - 0.4, "x", 0.45);
      PLATAFORMA(xc + 1.1, yc - Rr - 1.1, xc + 2.6, yc - Rr - 0.15, H - 0.4);
      BARANDA([[xc + 1.1, yc - Rr - 0.15, H - 0.4], [xc + 1.1, yc - Rr - 1.1, H - 0.4], [xc + 2.6, yc - Rr - 1.1, H - 0.4], [xc + 2.6, yc - Rr - 0.15, H - 0.4]], 1.0);
      PLACA([tag + " BIODIGESTOR", "Ø6,5 × 5,0 m · 141 m³ · 38 °C"], xc - 1.5, yc - Rr + 0.18, 2.2, -0.45, 0.9, 0.26);
      PLACA([mot + " AGITADOR", "4 kW"], xc + 1.6, yc - Rr - 0.73, H - 0.05, 0, 0.26, 0.1);
      // circuito de agua caliente aislado (desde la cogeneración)
      TUBO([[xc - 1.6, yc - Rr + 0.05, 0.9], [xc - 1.6, 24.4, 0.9], [66.4, 24.4, 0.9], [66.4, 20.5, 0.9]], 0.05, M.rojo);
    };
    dig(68, 31, "BD-1", "M28");
    dig(78.5, 31, "BD-2", "M29");
    // colector de gas → trampa de condensados → desulfurador
    TUBO([[64.5, 26.5, 0.6], [84.4, 26.5, 0.6]], 0.05, M.gas);
    TUBO([[69.5, 26.5, 0.6], [69.5, 19.8, 0.6], [69.5, 19.6, 0.7]], 0.05, M.gas);
    TUBO([[69.8, 19.3, 0.6], [70.1, 19.3, 0.6]], 0.05, M.gas);
    CARTEL("adv", "GAS|INFLAMABLE", "gas", 73.2, 27.6, 1.6, 0, 0.5, !0);
    BAR([73.2, 27.62, 0], [73.2, 27.62, 1.35], 0.05, M.galv);
  })();

  parte("E8.1");
  (function () {
    // fosa cubierta de recepción del guano excedente
    B(86.0, 17.0, -0.3, 90.0, 20.0, 0.25, M.hormigon);
    B(86.1, 17.1, 0.25, 90.0 - 0.1, 20.0 - 0.1, 0.3, M.grisOsc);
    B(86.2, 17.2, 0.3, 87.9, 19.9, 0.35, M.galv);
    var g = B(88.0, 17.2, 0.3, 89.8, 19.9, 0.35, M.galv); g.rotation.x = 0;
    PLACA(["FOSA GUANO EXCEDENTE", "fines de semana y feriados"], 88.0, 16.99, 0.2, 0, 0.6, 0.18);
    // tanque de mezcla con agitador y bomba trituradora
    V(92.5, 25.5, 0, 3.0, 1.75, M.hormigon, 32);
    V(92.5, 25.5, 3.0, 3.1, 1.8, M.grisOsc, 32);
    Be(cur, [92.5, 25.5, 3.1], [92.5, 25.5, 3.6], 0.14, M.motor, 12);
    B(91.6, 23.0, 0, 92.4, 23.5, 0.5, M.motor);
    PLACA(["M27 BOMBA TRITURADORA", "4 kW"], 92.0, 22.99, 0.75, 0, 0.36, 0.11);
    PLACA(["TANQUE DE MEZCLA 8 % ST"], 92.5, 23.74, 2.4, 0, 0.5, 0.1);
    TUBO([[91.8, 23.0, 0.4], [91.8, 21.3, 0.4], [78.5, 21.3, 0.4], [78.5, 27.6, 0.4]], 0.06, M.pvc);
    TUBO([[78.5, 21.3, 0.4], [68.0, 21.3, 0.4], [68.0, 27.6, 0.4]], 0.06, M.pvc);
    TUBO([[89.8, 18.5, 0.15], [91.0, 23.8, 0.15]], 0.08, M.pvc);
  })();

  parte("E8.3");
  (function () {
    var xc = 89, yc = 33, Rr = 4.0, H = 4.0;
    V(xc, yc, -0.02, 0.25, Rr + 0.4, M.hormigon, 40);
    V(xc, yc, 0.25, H, Rr, M.digestor, 48);
    for (var z = 0.9; z < H; z += 1.1) V(xc, yc, z, z + 0.04, Rr + 0.015, new dn({ color: 0x355f57, metalness: 0.55, roughness: 0.35 }), 48);
    var g = new ge(new fi(Rr, 40, 16, 0, Math.PI * 2, 0, Math.PI / 2), M.membranaVerde);
    g.position.copy(fe(xc, yc, H)); g.scale.set(1, 1.2 / Rr, 1); g.castShadow = !0; cur.add(g);
    TORO(xc, yc, H, Rr, 0.08, M.grisOsc);
    PLACA(["T3 TANQUE DE DIGESTATO", "Ø8,0 × 4,0 m · 201 m³"], xc - 2.4, yc - Rr + 0.62, 2.0, -0.6, 0.9, 0.26);
    TUBO([[xc - Rr + 0.2, yc - 1.0, H - 0.3], [84.4, yc - 1.0, H - 0.3], [84.4, yc - 1.0, 0.6], [84.4, 26.5, 0.6]], 0.045, M.gas);
    TUBO([[81.75, 31.3, 0.5], [85.1, 31.3, 0.5]], 0.07, M.pvc);
    // separador de tornillo prensa sobre plataforma y platea techada de sólidos
    PLATAFORMA(83.2, 25.6, 86.0, 27.4, 2.2);
    [[83.25, 25.65], [85.95, 25.65], [83.25, 27.35], [85.95, 27.35]].forEach(function (p) { BAR([p[0], p[1], 0], [p[0], p[1], 2.16], 0.08, M.estructura); });
    BARANDA([[83.2, 27.4, 2.2], [83.2, 25.6, 2.2], [86.0, 25.6, 2.2], [86.0, 27.4, 2.2]], 1.0);
    Be(cur, [83.6, 26.5, 2.6], [85.6, 26.5, 2.6], 0.2, M.inox, 16);
    Be(cur, [85.6, 26.5, 2.6], [85.95, 26.5, 2.6], 0.1, M.motor, 12);
    PLACA(["M32 SEPARADOR SÓLIDO-LÍQUIDO"], 84.6, 25.59, 3.5, 0, 0.5, 0.09);
    B(82.0, 22.0, -0.02, 86.0, 25.0, 0.2, M.hormigon);
    [[82.0, 22.0, 82.2, 25.0], [85.8, 22.0, 86.0, 25.0], [82.0, 24.8, 86.0, 25.0]].forEach(function (w) { B(w[0], w[1], 0.2, w[2], w[3], 1.4, M.hormigon); });
    var pl = Zu(cur, 84.0, 23.6, 1.1, 0.8, v.pila); pl.userData.noMerge = !0;
    B(81.8, 21.7, 3.3, 86.2, 25.3, 3.36, new dn({ color: 0xb9c0c3, metalness: 0.5, roughness: 0.45, side: wn }));
    [[81.9, 21.8], [86.1, 21.8], [81.9, 25.2], [86.1, 25.2]].forEach(function (p) { BAR([p[0], p[1], 0], [p[0], p[1], 3.3], 0.08, M.estructura); });
    B(86.3, 29.2, 0, 87.0, 29.8, 0.6, M.motor);
    PLACA(["M31 BOMBA DIGESTATO"], 86.65, 29.19, 0.8, 0, 0.36, 0.09);
    MATAFUEGO(84.0, 29.0, 0, "ABC");
  })();

  parte("E8.5");
  (function () {
    var xa = 95, ya = 18.2;
    B(xa - 0.6, ya - 0.6, -0.02, xa + 0.6, ya + 0.6, 0.2, M.hormigon);
    V(xa, ya, 0.2, 6.0, 0.17, M.inox, 16);
    V(xa, ya, 6.0, 6.5, 0.25, M.grisOsc, 16);
    V(xa, ya, 6.5, 6.9, 0.26, M.grisOsc, 16, { open: !0 });
    B(xa - 0.35, ya - 0.2, 1.0, xa - 0.18, ya + 0.2, 1.5, M.grisOsc);
    for (var k = 0; k < 3; k++) { var a = k * 2.1; BAR([xa, ya, 5.0], [xa + 1.6 * Math.cos(a), ya + 1.6 * Math.sin(a), 0.1], 0.02, M.galv); }
    TUBO([[72.0, 18.6, 0.9], [72.0, 21.75, 0.9], [xa, 21.75, 0.9], [xa, ya + 0.3, 0.9], [xa, ya + 0.17, 1.0]], 0.04, M.gas);
    PLACA(["ANTORCHA 25 m³/h"], xa, ya - 0.18, 2.0, 0, 0.36, 0.09);
  })();

  parte("E8.6");
  (function () {
    // línea enterrada señalizada con mojones + montante en el anexo + quemador piloto
    var ruta = [[61.5, 17.4], [61.5, 16.5], [35.5, 16.5], [35.5, 19.2], [29.1, 19.2]];
    TUBO([[71.3, 18.6, 0.6], [71.3, 17.4, 0.6], [61.5, 17.4, 0.6], [61.5, 17.4, 0.05]], 0.035, M.gas);
    for (var i = 0; i < ruta.length - 1; i++) {
      var a = ruta[i], b = ruta[i + 1], L = Math.hypot(b[0] - a[0], b[1] - a[1]), n = Math.max(1, Math.round(L / 6));
      for (var k = 0; k <= n; k++) {
        if (i > 0 && k === 0) continue;
        var t = k / n, x = a[0] + (b[0] - a[0]) * t, y = a[1] + (b[1] - a[1]) * t;
        B(x - 0.07, y - 0.07, 0, x + 0.07, y + 0.07, 0.5, M.gas);
        B(x - 0.075, y - 0.075, 0.42, x + 0.075, y + 0.075, 0.5, M.negro);
      }
      B(Math.min(a[0], b[0]) - 0.15, Math.min(a[1], b[1]) - 0.15, -0.005, Math.max(a[0], b[0]) + 0.15, Math.max(a[1], b[1]) + 0.15, 0.004, new dn({ color: 0x8a7a50, roughness: 1 }), { shadow: !1 });
    }
    var mx2 = 29.1, my2 = 19.2;
    TUBO([[mx2, my2, 0.05], [mx2, my2, 1.2], [28.72, my2, 1.2]], 0.035, M.gas);
    B(mx2 - 0.1, my2 - 0.1, 0.55, mx2 + 0.1, my2 + 0.1, 0.8, M.grisOsc);
    C([mx2, my2 - 0.1, 0.95], [mx2, my2 - 0.22, 0.95], 0.06, M.rojo, 10);
    V(mx2, my2, 1.25, 1.45, 0.07, M.blanco, 14);
    PLACA(["BIOGÁS · CORTE", "arrestallamas · regulador"], mx2, my2 - 0.11, 1.65, 0, 0.36, 0.13);
    TUBO([[28.52, my2, 1.05], [28.2, my2, 1.05], [28.2, 20.45, 1.05], [28.05, 20.45, 1.05]], 0.03, M.gas);
    B(28.02, 20.3, 0.95, 28.35, 20.6, 1.15, M.grisOsc);
    var fl = new ge(new Pl(0.06, 0.25, 10, 1, !0), M.llama); fl.rotation.z = Math.PI / 2; fl.position.copy(fe(27.9, 20.45, 1.05)); cur.add(fl);
    PLACA(["QUEMADOR PILOTO", "biogás 60 / 5 kW"], 28.18, 20.29, 1.35, 0, 0.3, 0.11);
    CARTEL("adv", "GAS|INFLAMABLE", "gas", mx2 + 0.12, my2 - 0.12, 2.2, 0, 0.36);
  })();


  /* ===================================================== E10 VENTILACIÓN GENERAL DE LA NAVE */
  /* ===================================================== REV. F: RETENCIÓN, ENFRIAMIENTO Y ESCAPE AISLADO */
  parte("F1");
  (function () {
    // el elevador queda bajo la cumbrera (8,35 m) entre los pórticos de x = 22 y 27,5 m: se prolonga hasta 8,1 m
    var e = G.elevador, xh = e.x + e.ax / 2 + 0.6, yh = e.y;
    var aisl = new dn({ color: 0xd3d8dc, metalness: 0.7, roughness: 0.38 });
    B(e.x - e.ax / 2, e.y - e.ay / 2, e.h, e.x + e.ax / 2, e.y + e.ay / 2, 7.85, M.galv);
    B(e.x - e.ax / 2 - 0.06, e.y - e.ay / 2 - 0.06, 7.85, e.x + e.ax / 2 + 0.06, e.y + e.ay / 2 + 0.06, 8.1, M.galv);
    C([e.x + e.ax / 2, e.y, 7.97], [xh - 0.38, yh, 7.78], 0.1, M.galv, 12);        // bajada del cabezal a la tolva (≈ 60°)
    // tolva de retención aislada Ø1,1 m: cilindro 0,6 m + cono 0,4 m ≈ 0,74 m³, con el TT-05
    V(xh, yh, 7.15, 7.75, 0.57, aisl, 28);
    V(xh, yh, 7.0, 7.15, 0.45, aisl, 24); V(xh, yh, 6.86, 7.0, 0.32, aisl, 20); V(xh, yh, 6.74, 6.86, 0.19, aisl, 16);
    SENSOR(xh + 0.57, yh, 7.4, [1, 0, 0], "TT-05", "corto");
    // enfriador a contracorriente con persianas y ventilador centrífugo M40; entrega a la válvula desviadora (E4)
    B(xh - 0.32, yh - 0.32, 6.3, xh + 0.32, yh + 0.32, 6.72, M.inox);
    for (var k = 0; k < 4; k++) B(xh + 0.32, yh - 0.28, 6.35 + k * 0.09, xh + 0.36, yh + 0.28, 6.39 + k * 0.09, M.grisOsc);
    V(xh, yh - 0.55, 6.33, 6.7, 0.19, M.azulSensor, 20);
    C([xh, yh - 0.36, 6.52], [xh, yh - 0.32, 6.52], 0.09, M.galv, 12);
    TUBO([[xh, yh + 0.32, 6.55], [xh, yh + 0.75, 6.55], [xh, yh + 0.75, 7.9], [xh - 1.6, yh + 0.75, 7.9]], 0.1, M.galv, 12);  // aire tibio al escape
    [[-0.5, -0.5], [0.5, -0.5], [-0.5, 0.5], [0.5, 0.5]].forEach(function (d) {
      BAR([xh + d[0], yh + d[1], 0], [xh + d[0], yh + d[1], 6.3], 0.08, M.estructura); });
    PLACA(["TOLVA DE RETENCIÓN 1 h", "≥ 70 °C · TT-05"], xh, yh - 0.58, 7.45, 0, 0.62, 0.16, { bg: "#f4f4f0" });
    PLACA(["ENFRIADOR · M40"], xh, yh - 0.33, 6.8, 0, 0.42, 0.08, { bg: "#f4f4f0" });
  })();
  parte("F2");
  (function () {
    var aisl = new dn({ color: 0xd3d8dc, metalness: 0.7, roughness: 0.38 });
    TUBO(G.ducto_agotado.recorrido, G.ducto_agotado.D / 2 + 0.05, aisl, 24);      // ducto Ø800 aislado
    var cy = G.ciclon;
    V(cy.x, cy.y, cy.z_cil0, cy.z_cil1, cy.D / 2 + 0.05, aisl, 32);
    for (var j = 0; j < 3; j++) {                                                  // cono revestido en tres tramos
      var z0 = cy.z_cono0 + (cy.z_cil0 - cy.z_cono0) * j / 3, z1 = cy.z_cono0 + (cy.z_cil0 - cy.z_cono0) * (j + 1) / 3;
      V(cy.x, cy.y, z0, z1, 0.25 + (cy.D / 2 - 0.2) * (j + 0.5) / 3, aisl, 28);
    }
    C([cy.x + 0.25, cy.y, cy.z_cono0], [cy.x + 0.25, cy.y, 0.35], 0.03, M.grisOsc, 8);   // purga con sifón
    PLACA(["AISLADO · PURGA DE CONDENSADO"], cy.x, cy.y - cy.D / 2 - 0.1, 4.4, 0, 0.95, 0.08, { bg: "#f4f4f0" });
  })();

  parte("E10");
  (function () {
    var conoMat = new dn({ color: 0xb9c0c4, metalness: 0.55, roughness: 0.4, side: wn });
    [4.6, 9.9].forEach(function (yc, i) {
      var zc = 5.3, xw = 33.0;
      // marco galvanizado 1,40 × 1,40 con persianas (lado interior)
      B(xw - 0.05, yc - 0.7, zc - 0.7, xw + 0.35, yc + 0.7, zc - 0.62, M.galv);
      B(xw - 0.05, yc - 0.7, zc + 0.62, xw + 0.35, yc + 0.7, zc + 0.7, M.galv);
      B(xw - 0.05, yc - 0.7, zc - 0.62, xw + 0.35, yc - 0.62, zc + 0.62, M.galv);
      B(xw - 0.05, yc + 0.62, zc - 0.62, xw + 0.35, yc + 0.7, zc + 0.62, M.galv);
      for (var k = 0; k < 7; k++) { var zz = zc - 0.54 + k * 0.18; B(xw - 0.07, yc - 0.62, zz - 0.012, xw - 0.03, yc + 0.62, zz + 0.012, M.aluminio); }
      // hélice de 6 palas, maza y motor
      for (var a = 0; a < 3; a++) {
        var t = a * Math.PI / 3, dy = Math.cos(t) * 0.58, dz = Math.sin(t) * 0.58;
        BAR([xw + 0.2, yc - dy, zc - dz], [xw + 0.2, yc + dy, zc + dz], 0.05, M.grisOsc);
      }
      C([xw + 0.12, yc, zc], [xw + 0.3, yc, zc], 0.1, M.grisOsc, 14);
      C([xw + 0.35, yc, zc], [xw + 0.62, yc, zc], 0.15, M.motor, 16);
      // campana (cono) de descarga y rejilla de protección
      var cn = new ge(new on(0.86, 0.64, 1.0, 28, 1, !0), conoMat);
      cn.rotation.z = -Math.PI / 2; cn.position.copy(fe(xw + 0.85, yc, zc)); cn.castShadow = !0; cur.add(cn);
      var rj = new ge(new on(0.86, 0.86, 0.02, 28), M.rejilla); rj.rotation.z = Math.PI / 2; rj.position.copy(fe(xw + 1.36, yc, zc)); cur.add(rj);
      [-1, 1].forEach(function (sg) { BAR([xw + 0.35, yc + sg * 0.66, zc - 0.66], [xw + 1.2, yc + sg * 0.8, zc - 0.78], 0.03, M.galv); });
      PLACA(["EX-0" + (i + 1) + " CAMPAGNONI AirTEC 1215", "54.700 m³/h · 1,5 HP · 380 V"], xw - 0.09, yc, zc - 0.92, -Math.PI / 2, 0.9, 0.16);
      // bajada de cable al termostato / tablero
      V(xw - 0.12, yc + 0.75, 3.6, zc, 0.018, M.negro, 8);
    });
    // termostato de comando (ambiente)
    B(32.85, 7.2, 1.5, 32.95, 7.45, 1.8, M.blanco);
    PLACA(["TERMOSTATO EX-01/02"], 32.84, 7.32, 1.95, -Math.PI / 2, 0.36, 0.08);
    // ventiladores móviles 50" (circuladores) para los puestos de trabajo
    [[24.6, 14.0, Math.PI * 0.85], [6.0, 5.5, Math.PI * 0.25]].forEach(function (v) {
      var x = v[0], y = v[1], ang = v[2], ca = Math.cos(ang), sa = Math.sin(ang);
      var P = function (u, w) { return [x + ca * u - sa * w, y + sa * u + ca * w]; };
      var zc = 1.0, r = 0.61;
      // ruedas y base
      [[-0.25, -0.55], [-0.25, 0.55], [0.25, -0.55], [0.25, 0.55]].forEach(function (q) { var pp = P(q[0], q[1]); SPH(pp[0], pp[1], 0.08, 0.08, M.negro); });
      var b0 = P(-0.3, -0.6), b1 = P(-0.3, 0.6), b2 = P(0.3, -0.6), b3 = P(0.3, 0.6);
      BAR([b0[0], b0[1], 0.16], [b1[0], b1[1], 0.16], 0.05, M.galv); BAR([b2[0], b2[1], 0.16], [b3[0], b3[1], 0.16], 0.05, M.galv);
      BAR([b0[0], b0[1], 0.16], [b2[0], b2[1], 0.16], 0.05, M.galv); BAR([b1[0], b1[1], 0.16], [b3[0], b3[1], 0.16], 0.05, M.galv);
      // aro, rejilla y motor (eje según "ang")
      var c0 = P(-0.12, 0), c1 = P(0.12, 0);
      var aro = new ge(new on(r + 0.04, r + 0.04, 0.3, 28, 1, !0), conoMat);
      aro.quaternion.setFromUnitVectors(new F(0, 1, 0), fe(ca, sa, 0).normalize()); aro.position.copy(fe(x, y, zc + 0.08)); cur.add(aro);
      [c0, c1].forEach(function (cc) { var g = new ge(new on(r, r, 0.015, 28), M.rejilla); g.quaternion.copy(aro.quaternion); g.position.copy(fe(cc[0], cc[1], zc + 0.08)); cur.add(g); });
      var m0 = P(0.15, 0), m1 = P(0.42, 0);
      C([m0[0], m0[1], zc + 0.08], [m1[0], m1[1], zc + 0.08], 0.13, M.motor, 14);
      [-1, 1].forEach(function (sg) { var a0 = P(0, sg * (r + 0.04)), a1 = P(0, sg * 0.6); BAR([a0[0], a0[1], zc + 0.08], [a1[0], a1[1], 0.18], 0.04, M.galv); });
      var pl = P(0.18, 0);
      PLACA(["VENTILADOR MÓVIL 50\"", "Campagnoni · 1 HP"], pl[0], pl[1], zc + 0.45, -ang + Math.PI / 2, 0.42, 0.12);
    });
  })();

  /* ===================================================== TABLEROS DEL TG2 (plano 23) */
  (function () {
    var gris7035 = __rdMat(0xd7d9d6, 0.25, 0.5);
    // gabinete con la cara frontal en (cx, cy); rot como PLANO: 0 Sur, PI Norte, PI/2 Este, -PI/2 Oeste
    var gab = function (id, tag, sub, cx, cy, w, d, z0, z1, rot, cuerpo) {
      if (__RD.grupos[id]) cur = __RD.grupos[id];
      var n = off(rot, 1), t = [Math.cos(rot), Math.sin(rot)];
      var px = [cx - t[0] * w / 2, cx + t[0] * w / 2, cx - t[0] * w / 2 - n[0] * d, cx + t[0] * w / 2 - n[0] * d];
      var py = [cy - t[1] * w / 2, cy + t[1] * w / 2, cy - t[1] * w / 2 - n[1] * d, cy + t[1] * w / 2 - n[1] * d];
      B(Math.min.apply(null, px), Math.min.apply(null, py), z0, Math.max.apply(null, px), Math.max.apply(null, py), z1, cuerpo || gris7035);
      var hx = cx + n[0] * 0.012 + t[0] * w * 0.36, hy = cy + n[1] * 0.012 + t[1] * w * 0.36;
      B(hx - 0.015, hy - 0.015, (z0 + z1) / 2 - 0.06, hx + 0.015, hy + 0.015, (z0 + z1) / 2 + 0.06, M.negro);
      PLACA([tag, sub], cx, cy, z1 - 0.12, rot, Math.min(0.62, w * 0.85), 0.13);
      CARTEL("adv", "RIESGO|ELÉCTRICO", "rayo", cx, cy, z0 + (z1 - z0) * 0.45, rot, 0.22);
    };
    gab("D15", "TG2", "tablero general de la ampliación · Q21 a Q27", 23.6, 0.42, 0.8, 0.3, 0.0, 2.0, Math.PI);
    gab("D19", "CI", "central de incendio (Q26)", 22.85, 0.27, 0.42, 0.14, 1.25, 1.75, Math.PI, __rdMat(0xc8102e, 0.2, 0.5));
    gab("E4", "TS-ENS", "zaranda y envasado (Q21)", 32.86, 13.0, 0.6, 0.22, 0.9, 1.9, -Math.PI / 2);
    gab("E10", "TS-VEN", "extractores y ventiladores (Q27)", 32.86, 8.15, 0.5, 0.2, 1.0, 1.7, -Math.PI / 2);
    gab("E2", "TS-LAV", "limpieza de vehículos (Q22) · IP65", -0.25, 17.5, 0.6, 0.22, 0.8, 1.8, -Math.PI / 2, M.inox);
    gab("E7", "TL2", "iluminación del Sector Este (Q25)", 60.36, 1.2, 0.5, 0.2, 1.0, 1.7, Math.PI / 2);
  })();

  /* ===================================================== ENTORNO: CRESPO, RN 12, PIC Y PLANTA DE BIOGÁS
     Croquis del plano 14 llevado al 3D (posiciones relativas orientativas, sin escala catastral):
     calle J. M. de Rosas al Oeste del lote, planta de biogás «Ñande Zukunft I» al otro lado de la calle,
     el Parque Industrial más al Oeste y la Ruta Nacional N° 12 al Sur, hacia Paraná y hacia Nogoyá. */
  (function () {
    var ent = new Qe(); ent.userData.lamOff = !0; ent.name = "entorno"; root.add(ent); cur = ent;
    __RD.entorno = ent;
    // campos alrededor (mosaico de lotes agrícolas de 3 × 3 km, por debajo del pasto del predio)
    var texCampo = Xn(1024, 1024, function (c) {
      var col = ["#a9bf86", "#b8c98f", "#9fb47a", "#c9c48e", "#b5a978", "#8fa86e", "#c2cf9a", "#a3b07c"];
      var semilla = 7, rnd = function () { semilla = (semilla * 16807) % 2147483647; return semilla / 2147483647; };
      c.fillStyle = "#adc08a"; c.fillRect(0, 0, 1024, 1024);
      for (var gx = 0; gx < 1024; gx += 64) for (var gy = 0; gy < 1024; gy += 48) {
        var w = 64 * (1 + Math.floor(rnd() * 2)), h = 48 * (1 + Math.floor(rnd() * 2));
        c.fillStyle = col[Math.floor(rnd() * col.length)]; c.fillRect(gx, gy, w, h);
        c.strokeStyle = "rgba(90,100,70,0.35)"; c.lineWidth = 2; c.strokeRect(gx, gy, w, h);
        if (rnd() < 0.5) { c.strokeStyle = "rgba(255,255,255,0.10)"; for (var l = 0; l < w; l += 6) { c.beginPath(); c.moveTo(gx + l, gy); c.lineTo(gx + l, gy + h); c.stroke(); } }
      }
    });
    var campo = new ge(new Pn(3200, 3200), new dn({ map: texCampo, roughness: 1, metalness: 0 }));
    campo.rotation.x = -Math.PI / 2; campo.position.copy(fe(-60, 0, -0.09)); campo.receiveShadow = !0; ent.add(campo);
    var texRuta = Xn(256, 64, function (c) {
      c.fillStyle = "#55595c"; c.fillRect(0, 0, 256, 64);
      c.fillStyle = "#f2f2ee"; c.fillRect(0, 3, 256, 3); c.fillRect(0, 58, 256, 3);
      c.fillStyle = "#f2c94c"; c.fillRect(10, 30, 110, 4);
    });
    texRuta.wrapS = 1000; texRuta.wrapT = 1001;
    var calzada = function (x0, y0, x1, y1, ancho, z, rep) {
      var dx = x1 - x0, dy = y1 - y0, L = Math.hypot(dx, dy);
      var t = texRuta.clone(); t.needsUpdate = !0; t.repeat.set(L / (rep || 14), 1);
      var g = new Qe(); g.position.copy(fe((x0 + x1) / 2, (y0 + y1) / 2, z || -0.02)); g.rotation.y = Math.atan2(dy, dx);
      var p = new ge(new Pn(L, ancho), new dn({ map: t, roughness: 0.92, metalness: 0 }));
      p.rotation.x = -Math.PI / 2; p.receiveShadow = !0; g.add(p); ent.add(g);
      var b = new ge(new Pn(L, ancho + 5), new dn({ color: 0xa79d82, roughness: 1 }));
      b.rotation.x = -Math.PI / 2; b.position.y = -0.006; g.add(b);
      return g;
    };
    // Ruta Nacional N° 12 (NO → SE) y calle J. M. de Rosas (N-S, al Oeste del lote)
    calzada(-436, -150, 464, -320, 7.3, -0.02, 14);
    calzada(-31, -210, -31, 300, 7.0, -0.021, 12);
    // planta de biogás vecina: 12 de sus 24 biodigestores, gasómetro, sala de motores y antorcha
    var dig = __rdMat(0x3f6f66, 0.5, 0.4), memb = __rdMat(0xdfe2dc, 0.05, 0.8), galp = __rdMat(0xcfd3d6, 0.35, 0.5);
    var techo = __rdMat(0x8f979c, 0.5, 0.45);
    [-75, -112, -149, -186].forEach(function (x) {
      [25, 62, 99].forEach(function (y) {
        V(x, y, 0, 6.5, 14, dig, 40);
        var dome = new ge(new fi(14, 32, 12, 0, Math.PI * 2, 0, Math.PI / 2), memb);
        dome.scale.set(1, 0.32, 1); dome.position.copy(fe(x, y, 6.5)); dome.castShadow = !0; ent.add(dome);
      });
    });
    B(-150, 135, 0, -110, 152, 7, galp); B(-151, 134, 7, -109, 153, 7.6, techo);
    V(-80, 140, 0, 12, 0.6, M.grisOsc, 12);
    V(-80, 140, 12, 13.2, 0.9, M.naranjaSeg, 12);
    // cerco perimetral de la planta vecina
    [[-215, -15, -45, -14.6], [-215, 175, -45, 175.4], [-215, -15, -214.6, 175], [-45.4, -15, -45, 175]].forEach(function (c) {
      B(c[0], c[1], 0, c[2], c[3], 2.0, M.galv, { shadow: !1 });
    });
    // Parque Industrial Crespo: naves industriales esquemáticas
    [[-420, 20, 55, 30], [-350, 20, 45, 28], [-420, 90, 50, 35], [-345, 95, 40, 30], [-410, 170, 60, 30], [-330, 175, 35, 25]].forEach(function (n, i) {
      var x = n[0], y = n[1], a = n[2], b = n[3], hh = 7 + (i % 3) * 1.5;
      B(x, y, 0, x + a, y + b, hh, galp);
      B(x - 0.5, y - 0.5, hh, x + a + 0.5, y + b + 0.5, hh + 0.6, techo);
    });
    calzada(-440, 140, -260, 140, 7.0, -0.022, 12);
    calzada(-260, -170, -260, 230, 7.0, -0.023, 12);
    // cortinas forestales (eucaliptos y casuarinas) a lo largo de la ruta y entre predios
    var copa = new fi(1, 10, 8), tronco = new on(0.12, 0.18, 1, 6, 1);
    var pts = [];
    for (var k = 0; k < 60; k++) { var u = k / 59; pts.push([-430 + u * 880, -150 + u * (-170) + 16]); }
    for (var k2 = 0; k2 < 26; k2++) pts.push([-222, -10 + k2 * 7.5]);
    for (var k3 = 0; k3 < 18; k3++) pts.push([-436 + k3 * 9, 215]);
    var ic = new oi(copa, __rdMat(0x4c6b3c, 0, 0.9), pts.length), it = new oi(tronco, __rdMat(0x5a4632, 0, 0.9), pts.length);
    pts.forEach(function (p, i) {
      var esc = 3.2 + ((i * 37) % 10) / 6, h = 6 + ((i * 13) % 7) * 0.6;
      var m = new Ee().makeScale(esc, esc * 1.35, esc); m.setPosition(fe(p[0], p[1], h));
      ic.setMatrixAt(i, m);
      var mt = new Ee().makeScale(esc * 0.6, h, esc * 0.6); mt.setPosition(fe(p[0], p[1], h / 2));
      it.setMatrixAt(i, mt);
    });
    ic.castShadow = !0; ent.add(ic); ent.add(it);
    // carteles del entorno (sprites que no se pierden en la niebla)
    var cartel = function (texto, x, y, z, esc, color) {
      var sp = ETIQ(texto, x, y, z, esc, color);
      sp.material.fog = !1; sp.material.depthTest = !1; sp.renderOrder = 5;
      sp.visible = !1; sp.userData.entorno = !0;          // solo en la vista de Crespo (ver __rdAplicarCapas)
      return sp;
    };
    cartel("RUTA NACIONAL N° 12|km 40,6 · acceso a Crespo", -120, -200, 22, 95, "#9aa5b1");
    cartel("← a PARANÁ (≈ 40 km)", -390, -150, 14, 70, "#9aa5b1");
    cartel("a NOGOYÁ →", 400, -300, 14, 60, "#9aa5b1");
    cartel("PLANTA DE BIOGÁS «ÑANDE ZUKUNFT I»|Bioenergía Virch S.A. · 24 biodigestores", -130, 80, 34, 105, "#3f6f66");
    cartel("PARQUE INDUSTRIAL CRESPO (PIC)|54 ha ReNPI · ampliación prevista ≈ 70 ha", -370, 110, 28, 105, "#1f5fa8");
    cartel("calle J. M. de Rosas", -31, 250, 10, 55, "#9aa5b1");
    cartel("← CRESPO (planta urbana, ≈ 2 km)", -400, 270, 16, 85, "#9aa5b1");
    cartel("LOTE DE LA SECADORA|120 × 76 m · energía: Coop. LAR", 38, 2, 40, 95, "#c0392b");
  })();
  cur = null;

  /* --------- globos, clasificación por zonas y fusión de mallas (rendimiento) --------- */
  __RD_PARTES.forEach(function (p) { if (p.lp && R.parts[p.n]) R.labelPos[p.n] = p.lp; });
  Object.keys(__RD.grupos).forEach(function (id) { __rdMerge(__RD.grupos[id], R); });
}

function __rdMerge(g, R) {
  g.updateMatrixWorld(!0);
  var inv = g.matrixWorld.clone().invert();
  var buckets = new Map(), victims = [];
  var bb = new gi(), c = new F();
  g.traverse(function (o) {
    if (!o.isMesh || o.isInstancedMesh || o.userData.noMerge || Array.isArray(o.material) || o.children.length) return;
    bb.setFromObject(o); bb.getCenter(c);
    var px = c.x, py = -c.z, pz = c.y, S = __RD_SEC;
    var zona = o.userData.zona || (px > S.x0 && px < S.x1 && py > S.y0 && py < S.y1 && pz > S.z0 && pz < S.z1 ? "sec" : "otro");
    var ev = o.userData.expVec ? o.userData.expVec.toArray().map(function (n) { return n.toFixed(2); }).join(",") : "";
    var key = o.material.uuid + "|" + (o.castShadow ? "s" : "n") + "|" + (o.userData.corte || "") + "|" + zona + "|" + ev;
    if (!buckets.has(key)) buckets.set(key, { zona: zona, corte: o.userData.corte || "", ev: o.userData.expVec, list: [] });
    buckets.get(key).list.push(o);
    victims.push(o);
  });
  var sub = {};
  var getSub = function (z) {
    if (!sub[z]) { var s = new Qe(); s.userData.dyn = !0; s.userData.zona = z; g.add(s); sub[z] = s; }
    return sub[z];
  };
  var m4 = new Ee();
  buckets.forEach(function (b) {
    var geos = b.list.map(function (o) {
      var gg = o.geometry.index ? o.geometry.toNonIndexed() : o.geometry.clone();
      Object.keys(gg.attributes).forEach(function (k) { if (k !== "position" && k !== "normal" && k !== "uv") gg.deleteAttribute(k); });
      if (!gg.attributes.normal) gg.computeVertexNormals();
      if (!gg.attributes.uv) gg.setAttribute("uv", new ze(new Float32Array(gg.attributes.position.count * 2), 2));
      gg.clearGroups();
      gg.applyMatrix4(m4.multiplyMatrices(inv, o.matrixWorld));
      return gg;
    });
    var merged = ya(geos, !1);
    if (!merged) return;
    var mesh = new ge(merged, b.list[0].material);
    mesh.castShadow = b.list[0].castShadow; mesh.receiveShadow = !0;
    mesh.userData.part = g.userData.part;
    if (b.corte) { mesh.userData.corte = b.corte; R.corte.push(mesh); }
    if (b.ev) { mesh.userData.expBase = new F(); mesh.userData.expVec = b.ev.clone(); R.explode.push(mesh); }
    getSub(b.zona).add(mesh);
  });
  victims.forEach(function (o) { o.parent && o.parent.remove(o); });
}

/* ------------------------------ UI: capas, vistas y solo secadora ------------------------------ */
var __RD_SOLO_OK = function (id) { return /^4(\.\d+)?$/.test(id) || id === "5" || /^D\d+$/.test(id); };

function __rdAplicarCapas() {
  if (!He) return;
  var seg = Zt("#c-rd-seg") ? Zt("#c-rd-seg").checked : !0;
  var flu = Zt("#c-rd-flu") ? Zt("#c-rd-flu").checked : !0;
  var amp = Zt("#c-rd-amp") ? Zt("#c-rd-amp").checked : !0;
  var solo = __RD.solo;
  __RD_PARTES.forEach(function (p) {
    var g = He.parts[p.n];
    if (!g) return;
    var on = p.g === "seg" ? seg : p.g === "flu" ? flu : amp;
    if (solo && !__RD_SOLO_OK(p.n)) on = !1;
    g.visible = on;
    if (solo) g.children.forEach(function (s) { if (s.userData.zona) s.visible = s.userData.zona === "sec"; });
    else g.children.forEach(function (s) { if (s.userData.zona) s.visible = !0; });
  });
  if (__RD.entorno) __RD.entorno.visible = !solo;
  __RD.sprites.forEach(function (sp) {
    if (sp.userData.entorno) { sp.visible = !solo && !!__RD.vistaLejos; return; }
    var p = sp.position;
    sp.visible = !solo || (p.x > __RD_SEC.x0 && p.x < __RD_SEC.x1 && -p.z > __RD_SEC.y0 - 1.5 && -p.z < __RD_SEC.y1);
  });
  Object.keys(He.parts).forEach(function (id) {
    if (__RD_PARTES.some(function (p) { return p.n === id; })) return;
    var g = He.parts[id];
    if (solo) { g.userData.__rdVis === void 0 && (g.userData.__rdVis = g.visible); g.visible = __RD_SOLO_OK(id); }
    else if (g.userData.__rdVis !== void 0) { g.visible = g.userData.__rdVis; delete g.userData.__rdVis; }
  });
  if (solo) for (var t of M2) He.parts[t] && (He.parts[t].visible = !1);
  __rdGlobos();
  Tn = !0;
}

var __RD_IDS = null;
function __rdGlobos() {
  if (!He) return;
  if (!__RD_IDS) __RD_IDS = new Set(__RD_PARTES.map(function (p) { return p.n; }));
  for (var i = 0; i < Xo.length; i++) {
    var e = Xo[i], idp = e.id;
    if (__RD.solo && !__RD_SOLO_OK(idp)) e.vis = !1;
    if (__RD.solo && __RD_IDS.has(idp) && idp !== "D24") e.vis = !1;
    if (__RD_IDS.has(idp) && He.parts[idp] && !He.parts[idp].visible) e.vis = !1;
  }
}

function __rdSolo(on) {
  __RD.solo = on;
  var ch = Zt("#c-rd-solo"); ch && (ch.checked = on);
  Zt("#app").classList.toggle("rd-solo", on);
  if (on) {
    __RD._prev = { nave: _t.nave, aire: _t.aire, prod: _t.prod, vehic: _t.vehic };
    _t.nave = !1; _t.aire = !1; _t.prod = !1; _t.vehic = !1;
    ["#c-nave", "#c-aire", "#c-prod", "#c-vehic"].forEach(function (s) { var el = Zt(s); el && (el.checked = !1); });
    Es();
    __rdAplicarCapas();
    Or(); Aa(!1);
    ds(fe(4.5, -9.5, 9.5), fe(18, 9.3, 1.7), 1.1);
  } else {
    var p = __RD._prev || { nave: !0, aire: !0, prod: !0, vehic: !0 };
    _t.nave = p.nave; _t.aire = p.aire; _t.prod = p.prod; _t.vehic = p.vehic;
    Zt("#c-nave").checked = p.nave; Zt("#c-aire").checked = p.aire; Zt("#c-prod").checked = p.prod; Zt("#c-vehic").checked = p.vehic;
    Es();
    __rdAplicarCapas();
  }
}

var __RD_VISTAS = {
  interior: { nave: !1, abrir: !0, aire: !0, prod: !0, pos: [16.5, -2.8, 4.6], tgt: [18.5, 9.3, 1.6] },
  aire: { nave: !1, abrir: !0, aire: !0, prod: !1, pos: [2, -6, 17], tgt: [19, 15, 3.5] },
  alimentacion: { nave: !1, abrir: !1, aire: !1, prod: !0, pos: [-4.5, 1.5, 6.5], tgt: [5.5, 10.5, 1.8] },
  mantenimiento: { nave: !1, abrir: !1, aire: !1, prod: !1, flu: !1, pos: [20.4, 5.5, 2.6], tgt: [24.0, 7.9, 1.4] },
  incendio: { nave: !0, abrir: !1, aire: !1, prod: !1, pos: [-18, -44, 46], tgt: [30, 6, 0] },
  envasado: { nave: !1, abrir: !1, aire: !1, prod: !1, pos: [35.5, 4.5, 7.5], tgt: [28.8, 12.8, 2.0] },
  biogas: { nave: !0, abrir: !1, aire: !1, prod: !1, pos: [58, -6, 26], tgt: [80, 27, 1.5] },
  ubicacion: { nave: !0, abrir: !1, aire: !0, prod: !0, pos: [-40, -95, 80], tgt: [38, 2, 0] },
  crespo: { nave: !0, abrir: !1, aire: !1, prod: !1, flu: !1, pos: [-120, -470, 300], tgt: [-60, 40, 0], lejos: !0 },
};

function __rdVista(k) {
  var vv = __RD_VISTAS[k];
  if (!vv) return;
  if (__RD.solo) __rdSolo(!1);
  __RD.vistaLejos = !!vv.lejos;
  _t.nave = vv.nave; Zt("#c-nave").checked = vv.nave;
  _t.aire = vv.aire; Zt("#c-aire").checked = vv.aire;
  _t.prod = vv.prod; Zt("#c-prod").checked = vv.prod;
  O2(vv.abrir);
  ["#c-rd-seg", "#c-rd-flu", "#c-rd-amp"].forEach(function (s) { var el = Zt(s); el && (el.checked = s === "#c-rd-flu" ? vv.flu !== !1 : !0); });
  __rdAplicarCapas();
  Or(); Aa(!1);
  // en la vista de Crespo se abre la niebla para ver el entorno; en las demás vuelve a la del visor
  if (typeof Ti !== "undefined" && Ti && Ti.fog) { Ti.fog.near = vv.lejos ? 450 : 130; Ti.fog.far = vv.lejos ? 1500 : 420; }
  if (typeof Di !== "undefined" && Di) Di.maxDistance = vv.lejos ? 1100 : 240;
  ds(fe(vv.pos[0], vv.pos[1], vv.pos[2]), fe(vv.tgt[0], vv.tgt[1], vv.tgt[2]), 1.1);
}

function __revDSetup() {
  // 1) predio ampliado (Sector Este)
  vs.G.predio.x1 = 98;
  // 2) piezas nuevas en la lista y en la ficha
  __RD_PARTES.forEach(function (p) { Bs[p.n] = { n: p.n, nom: p.nom, txt: p.txt, plano: p.plano }; });
  S0.push({ t: "Rev. D · Seguridad, instrumentación y mantenimiento", items: __RD_PARTES.filter(function (p) { return p.g === "seg"; }).map(function (p) { return p.n; }) });
  S0.push({ t: "Rev. D · Flujos", items: ["D24"] });
  S0.push({ t: "Rev. D · Limpieza y ventilación", items: ["E1", "E2", "E3", "E10"] });
  S0.push({ t: "Rev. D · Separación y envasado", items: ["E4", "E5", "E6", "E7"] });
  S0.push({ t: "Rev. D · Biogás", items: ["E8.1", "E8.2", "E8.3", "E8.4", "E8.5", "E8.6"] });
  S0.push({ t: "Rev. D · Predio", items: ["E9"] });
  // 3) planos nuevos
  __RD_PLANOS.forEach(function (p) { fc.push({ id: p.id, t: p.t, e: p.e, rev: "D" }); $4[p.id] = p.c; });
  // revisión vigente de cada lámina (10/2026): las 01 a 12 pasan a D (redibujo vectorial, hojas x/24);
  // 17, 22, 23 y 24 pasan a E (puesta a tierra D16 y extractores E10 en el TG2)
  fc.forEach(function (p) { p.rev = ["P17", "P22", "P23", "P24"].indexOf(p.id) >= 0 ? "E" : "D"; });
  // 4) controles de capas y vistas
  var pane = document.querySelector('.pane[data-pane="capas"]');
  if (pane) {
    var box = document.createElement("div");
    box.innerHTML =
      '<hr class="sep"><p class="kicker">Rev. D · agregados</p>' +
      '<label class="sw"><span class="sl">Seguridad e instrumentación<span class="sd">Ítems D1 a D23: puertas, protecciones, sensores, puesta a tierra, incendio…</span></span><input type="checkbox" id="c-rd-seg" checked></label>' +
      '<label class="sw"><span class="sl">Flechas de flujo<span class="sd">Guano, aire y recirculación</span></span><input type="checkbox" id="c-rd-flu" checked></label>' +
      '<label class="sw"><span class="sl">Ampliación y sistemas nuevos<span class="sd">Envasado, limpieza, biofiltro, biogás, Sector Este</span></span><input type="checkbox" id="c-rd-amp" checked></label>' +
      '<label class="sw"><span class="sl">Solo la secadora<span class="sd">Oculta la nave y el resto de la planta</span></span><input type="checkbox" id="c-rd-solo"></label>' +
      '<p class="kicker" style="margin-top:10px">Vistas guiadas</p><div class="rd-vistas">' +
      [["interior", "Interior: 3 cintas"], ["aire", "Circulación de aire"], ["alimentacion", "Alimentación"], ["mantenimiento", "Mantenimiento"], ["envasado", "Zaranda y envasado"], ["incendio", "Seguridad e incendio"], ["biogas", "Biogás"], ["ubicacion", "Predio ampliado"], ["crespo", "Ubicación en Crespo"]]
        .map(function (b) { return '<button class="btn" data-rdv="' + b[0] + '">' + b[1] + "</button>"; }).join("") +
      "</div>";
    var leg = pane.querySelector(".legend");
    var hr = leg ? leg.previousElementSibling && leg.previousElementSibling.previousElementSibling : null;
    pane.insertBefore(box, hr || null);
    box.querySelector("#c-rd-seg").onchange = __rdAplicarCapas;
    box.querySelector("#c-rd-flu").onchange = __rdAplicarCapas;
    box.querySelector("#c-rd-amp").onchange = __rdAplicarCapas;
    box.querySelector("#c-rd-solo").onchange = function (e) { __rdSolo(e.target.checked); };
    box.querySelectorAll("[data-rdv]").forEach(function (b) { b.onclick = function () { __rdVista(b.dataset.rdv); }; });
  }
  // mantener capas y "solo secadora" cuando el visor refresca visibilidad y globos
  var es0 = Es;
  Es = function () { es0(); if (He && He.parts) __rdAplicarCapas(); };
  var rc0 = Rc;
  Rc = function () { rc0(); __rdGlobos(); };
  var st = document.createElement("style");
  st.textContent = ".rd-vistas{display:grid;grid-template-columns:1fr 1fr;gap:6px}.rd-vistas .btn{justify-content:center;font-size:12px;padding:6px 8px;min-height:32px}";
  document.head.appendChild(st);
  window.__revD = { solo: __rdSolo, vista: __rdVista, capas: __rdAplicarCapas, partes: __RD_PARTES,
    // cámara a pedido (x, y, z de planta en m), para capturas automáticas
    camara: function (pos, tgt, dur) { ds(fe(pos[0], pos[1], pos[2]), fe(tgt[0], tgt[1], tgt[2]), dur === void 0 ? 0.3 : dur); } };
}

var __RD_PLANOS = [
  { id: "P13", t: "Implantación general ampliada (Sector Este)", e: "1:500", c: "Implantación Rev. D" },
  { id: "P14", t: "Ubicación: Parque Industrial de Crespo", e: "S/E", c: "Ubicación Crespo" },
  { id: "P15", t: "Protección contra incendios y medios de escape", e: "1:250", c: "Incendio" },
  { id: "P16", t: "Estudio de carga de fuego (Dec. 351/79)", e: "S/E", c: "Carga de fuego" },
  { id: "P17", t: "Nave: seguridad, accesos y mantenimiento", e: "1:150", c: "Seguridad nave" },
  { id: "P18", t: "Aire: recirculación, compuertas y ventilación", e: "1:100", c: "Aire y ventilación" },
  { id: "P19", t: "Zaranda y envasado (25 kg y bolsas chicas)", e: "1:50", c: "Envasado" },
  { id: "P20", t: "Sistema de biogás: planta, corte y balance", e: "1:250", c: "Biogás" },
  { id: "P21", t: "Limpieza y desinfección de vehículos", e: "1:100", c: "Limpieza" },
  { id: "P22", t: "Ficha técnica completa de la secadora", e: "S/E", c: "Ficha técnica" },
  { id: "P23", t: "Esquema unifilar TG2 (consumos Rev. D)", e: "S/E", c: "Unifilar TG2" },
  { id: "P24", t: "Ventilación general de la nave: extractores y ventiladores", e: "1:200", c: "Ventilación nave" },
];
