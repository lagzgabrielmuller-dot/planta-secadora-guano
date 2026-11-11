"""Datos de diseño del secador SC-4 (Rev. D/E) y parámetros del modelo.

Todo lo que viene del proyecto está tomado de la última revisión:
  - Informe_Final_Secadora_Guano.docx (24/10/2026), capítulos 4, 6, 7, 12, 13, 14, 15 y 19.
  - Plano 18 (recirculación D7, compuertas) y plano 22 (ficha técnica Rev. E).
Lo que no figura en el proyecto (cinética de secado, isoterma, tamaño de grumo, coeficientes de
transferencia) se toma de bibliografía y se indica la fuente al lado. Los valores marcados
"ajustado" se calibraron contra datos publicados (ver validar.py).

Unidades: SI, salvo que se indique. Temperaturas en °C.
"""
import numpy as np

# ---------------------------------------------------------------------------------------------
# 1. Proceso (informe cap. 6, plano 22 tabla 1)
# ---------------------------------------------------------------------------------------------
ALIMENTACION_KG_H = 1000.0        # guano húmedo, 8 t en un turno de 8 h
HUMEDAD_ENTRADA_BH = 0.72         # base húmeda (INTA, adoptado 72 %)
HUMEDAD_SALIDA_BH = 0.15          # objetivo (lazo MIC-01, SP 15 %)
T_AIRE_ENTRADA = 135.0            # SP del lazo TIC-01 (TT-01)
T_AIRE_MAX = 150.0                # nunca superar (pérdida de N, riesgo de incendio)
AIRE_SECO_KG_H = 26600.0          # caudal de aire de secado (aire seco)
RECIRCULACION = 0.25              # D7, plano 18: 25 % del aire vuelve a la cámara de mezcla
RECIRC_MAX = 0.35                 # CD-03 regula de 0 a 35 %
Y_MAX_RECIRC = 0.045              # CD-03 cierra si Y > 45 g/kg
T_AMBIENTE_DISENO = 18.0          # media anual Crespo (informe tabla 6)
HR_AMBIENTE_DISENO = 0.60
DT_NAVE = 3.0                     # la nave está 3 K por encima del exterior (ventilación E10, cap. 19)
P_ATM = 100.3e3                   # Pa, Crespo / Paraná Aero a ~80 m s.n.m.

# ---------------------------------------------------------------------------------------------
# 2. Secador SC-4 (informe cap. 7, 12.1, 13; plano 22)
# ---------------------------------------------------------------------------------------------
N_PISOS = 3
ANCHO_BANDA = 2.0                 # m
LARGO_BANDA = 12.0                # m
VEL_BANDA_DISENO = 0.37 / 60.0    # m/s (0,37 m/min)
VEL_BANDA_MIN = 0.2 / 60.0        # VFD 12 Hz
VEL_BANDA_MAX = 0.9 / 60.0        # VFD 50 Hz
CAPA_DISENO_MM = 30.0             # capa del esparcidor en el piso 1
CAPA_MIN_MM, CAPA_MAX_MM = 20.0, 40.0    # límites de uso del SC-4 (informe 12.1)
DENS_APARENTE_HUMEDO = 800.0      # kg/m³ (informe tabla 3)
DENS_APARENTE_SECO = 500.0        # kg/m³ al 15 % (informe tabla 3)
CP_SOLIDO = 1500.0                # J/kg·K, sólido seco (informe tabla 3)

# Cámara: 13,0 × 2,6 m, 3,0 m de alto sobre patas de 0,4 m; pisos a +0,93 / +1,78 / +2,63 m
CAMARA_L, CAMARA_A = 13.0, 2.6
Z_PISO_CAMARA, Z_TECHO = 0.40, 3.40
Z_PISO3, Z_PISO2, Z_PISO1 = 0.93, 1.78, 2.63
U_PANEL = 0.50                    # W/m²·K, sándwich lana de roca 80 mm + puentes térmicos
#   (0,46 por conducción con películas; el informe cap. 19 calcula 6,1 kW de pérdida total)
Q_DUCTO_W = 3000.0                # pérdidas del ducto caliente dentro de la nave (cap. 19)

# Guías de deslizamiento de las bandas (informe 7.2.5): UHMW-PE
UHMW_SERVICIO_CONTINUO = 80.0     # °C, ficha Ensinger PE1000 / APSO PE-UHMW
UHMW_FUSION = 130.0               # °C (130-135 según fabricante)

# ---------------------------------------------------------------------------------------------
# 3. Generador de aire caliente (informe cap. 15)
# ---------------------------------------------------------------------------------------------
PCI_CASCARA = 13.5e6              # J/kg (10 % de humedad)
REND_GENERADOR = 0.75             # hogar + intercambiador
CENIZAS = 0.18                    # fracción de la cáscara
VENTILADORES_PRESION = 1500.0     # Pa (intercambiador + ducto + plenum + 3 bandas cargadas)
VENTILADORES_REND = 0.70
VENTILADORES_CAUDAL = 2 * 15400.0 # m³/h
PRECIO_CASCARA_USD_T = 25.0       # puesta en planta (informe cap. 26)
PRECIO_ENERGIA_ARS_KWH = 185.0    # tarifa T3 LAR (referencia del informe)
DOLAR_ARS = 1550.0                # BNA vendedor 23/10/2026 (informe cap. 26)
DIAS_ANIO = 250
HORAS_TURNO = 8.0

# ---------------------------------------------------------------------------------------------
# 4. Guano: estructura del lecho (supuestos del modelo, ver README)
# ---------------------------------------------------------------------------------------------
DENS_PARTICULA_HUMEDA = 1000.0    # kg/m³ del grumo al 72 % (Ghaly y MacDonald 2012: 960 kg/m³)
DIAMETRO_GRUMO = 0.010            # m, grumo equivalente que deja el esparcidor de paletas
CONTRACCION_PARTICULA = 0.80      # fracción del volumen de agua evaporada que se contrae el grumo
FRACCION_BYPASS = 0.05            # aire que pasa por bordes/rajaduras sin atravesar producto

# ---------------------------------------------------------------------------------------------
# 5. Cinética de secado (bibliografía; ver validar.py)
# ---------------------------------------------------------------------------------------------
# Difusividad efectiva del agua en el guano: Arrhenius en T y exponencial en la humedad X
# (la pasta húmeda mueve el agua por capilaridad, mucho más rápido que el grumo casi seco):
#   D = D_REF · exp(D_B·(X − X_DREF)) · exp(−Ea/R·(1/T − 1/T_REF))
# Ajuste conjunto (validar.py) a 9 ensayos de Ghaly y MacDonald (2012, 40-60 °C, capas de 1 a 3 cm:
# tiempo de secado y velocidad inicial) y a 2 de Liška y Kic (2011, 70 y 110 °C): error típico ±20 %.
D_REF = 5.2e-9                    # m²/s a 60 °C y X = 0,5
D_B = 3.4                         # 1/(kg/kg): con X > 1 el agua llega sola a la superficie
X_DREF = 0.5
EA_DIFUSION = 27.0e3              # J/mol
T_REF_DIFUSION = 60.0

# Isoterma GAB (desorción). Monocapa de cama de pollo 5,8 % b.s. a 25 °C (Bernhart 2007, Auburn).
GAB_XM_25 = 0.058
GAB_XM_DT = -0.003                # 1/K, la monocapa baja con la temperatura
GAB_C_25 = 10.0
GAB_C_H = 600.0                   # K, dependencia de C con 1/T
GAB_K = 0.85
# Calor de sorción: h_eff = hfg·(1 + A·exp(−B·X))
SORC_A, SORC_B = 0.5, 12.0

# ---------------------------------------------------------------------------------------------
# 6. Higienización
# ---------------------------------------------------------------------------------------------
HIG_T_MEMORIA, HIG_MIN_MEMORIA = 55.0, 60.0     # criterio de la memoria: > 55 °C durante > 1 h
HIG_T_UE, HIG_MIN_UE = 70.0, 60.0               # Reg. (UE) 142/2011 anexo XI: 70 °C durante 60 min
# Salmonella en cama de pollo (Kim et al. 2012, citado por Ghaly y MacDonald 2012):
# 7 log en 80 min a 70 °C y en 44 min a 80 °C  ->  D70 = 11,5 min, z = 38 °C
SALM_D70_MIN = 80.5 / 7.0
SALM_Z = 10.0 / np.log10((80.5 / 7.0) / (44.1 / 7.0))

# ---------------------------------------------------------------------------------------------
# 7. Clima de Paraná Aero (1991-2020). Temperaturas: climate-zone.com sobre datos NOAA;
#    humedad relativa: NASA POWER (misma fuente).
# ---------------------------------------------------------------------------------------------
MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
_F = np.array
T_MAX_F = _F([88, 86, 83, 75, 69, 63, 63, 67, 71, 76, 80, 86], float)
T_MED_F = _F([78, 75, 73, 66, 60, 55, 54, 57, 61, 66, 70, 75], float)
T_MIN_F = _F([67, 65, 63, 57, 51, 46, 45, 47, 50, 56, 60, 64], float)
HR_MES = _F([59, 64, 68, 74, 79, 80, 77, 72, 68, 66, 62, 60], float) / 100.0
T_MAX_MES = (T_MAX_F - 32) / 1.8
T_MED_MES = (T_MED_F - 32) / 1.8
T_MIN_MES = (T_MIN_F - 32) / 1.8
DIAS_MES = _F([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31], float)

# ---------------------------------------------------------------------------------------------
# Vector de parámetros para el núcleo compilado (numba). Índices con nombre.
# ---------------------------------------------------------------------------------------------
I_P, I_CPS, I_RHOP0, I_D0, I_BETAP, I_RHOB0, I_RHOBF, I_XF_REF, I_DREF, I_EA, I_TREF, \
    I_XM25, I_XMDT, I_C25, I_CH, I_K, I_SA, I_SB, I_X0, I_BYP, I_D70, I_Z, I_DB, I_XDREF = range(24)
N_PRM = 24


def vector_parametros(**cambios):
    """Arma el vector de parámetros físicos. Se puede pisar cualquier valor por nombre."""
    v = dict(
        P=P_ATM, cps=CP_SOLIDO, rhop0=DENS_PARTICULA_HUMEDA, d0=DIAMETRO_GRUMO,
        betap=CONTRACCION_PARTICULA, rhob0=DENS_APARENTE_HUMEDO, rhobf=DENS_APARENTE_SECO,
        xf_ref=HUMEDAD_SALIDA_BH / (1 - HUMEDAD_SALIDA_BH), dref=D_REF, ea=EA_DIFUSION,
        tref=T_REF_DIFUSION, xm25=GAB_XM_25, xmdt=GAB_XM_DT, c25=GAB_C_25, ch=GAB_C_H, k=GAB_K,
        sa=SORC_A, sb=SORC_B, x0=HUMEDAD_ENTRADA_BH / (1 - HUMEDAD_ENTRADA_BH),
        byp=FRACCION_BYPASS, d70=SALM_D70_MIN, z=SALM_Z, db=D_B, xdref=X_DREF)
    for k, val in cambios.items():
        if k not in v:
            raise KeyError(f"parámetro desconocido: {k}")
        v[k] = float(val)
    orden = ["P", "cps", "rhop0", "d0", "betap", "rhob0", "rhobf", "xf_ref", "dref", "ea", "tref",
             "xm25", "xmdt", "c25", "ch", "k", "sa", "sb", "x0", "byp", "d70", "z", "db", "xdref"]
    return np.array([v[k] for k in orden], dtype=np.float64)
