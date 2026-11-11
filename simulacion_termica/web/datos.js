/* Datos de planta del SC-4 (Rev. D/E) exportados desde Python: exportar_web.py */
const DATOS_SC4 = {
 "prm": {
  "P": 100300.0,
  "cps": 1500.0,
  "rhop0": 1000.0,
  "d0": 0.01,
  "betap": 0.8,
  "rhob0": 800.0,
  "rhobf": 500.0,
  "xf_ref": 0.17647058823529413,
  "dref": 5.2e-09,
  "ea": 27000.0,
  "tref": 60.0,
  "xm25": 0.058,
  "xmdt": -0.003,
  "c25": 10.0,
  "ch": 600.0,
  "k": 0.85,
  "sa": 0.5,
  "sb": 12.0,
  "x0": 2.571428571428571,
  "byp": 0.05,
  "d70": 11.5,
  "z": 38.26179849646908,
  "db": 3.4,
  "xdref": 0.5
 },
 "dt_nave": 3.0,
 "ancho": 2.0,
 "largo": 12.0,
 "area_zonas": [
  50.336000000000006,
  26.52,
  26.519999999999996,
  57.824000000000005
 ],
 "vel_min": 0.0033333333333333335,
 "vel_max": 0.015000000000000001,
 "q_ducto": 3000.0,
 "pci": 13500000.0,
 "rend_gen": 0.75,
 "cenizas": 0.18,
 "vent_presion": 1500.0,
 "vent_rend": 0.7,
 "uhmw_continuo": 80.0,
 "uhmw_fusion": 130.0,
 "t_aire_max": 150.0,
 "y_max_recirc": 0.045,
 "meses": [
  "Ene",
  "Feb",
  "Mar",
  "Abr",
  "May",
  "Jun",
  "Jul",
  "Ago",
  "Sep",
  "Oct",
  "Nov",
  "Dic"
 ],
 "clima": [
  {
   "T": 28.47222222222222,
   "HR": 0.4971435120265511
  },
  {
   "T": 26.805555555555557,
   "HR": 0.5381010469534869
  },
  {
   "T": 25.555555555555557,
   "HR": 0.5756144047295428
  },
  {
   "T": 21.38888888888889,
   "HR": 0.6339387369054604
  },
  {
   "T": 18.055555555555554,
   "HR": 0.6740340717708383
  },
  {
   "T": 15.138888888888888,
   "HR": 0.6862878971803024
  },
  {
   "T": 14.722222222222221,
   "HR": 0.6542139896945685
  },
  {
   "T": 16.666666666666668,
   "HR": 0.6022900367901222
  },
  {
   "T": 19.02777777777778,
   "HR": 0.565652218619175
  },
  {
   "T": 21.666666666666668,
   "HR": 0.5558712272627097
  },
  {
   "T": 23.88888888888889,
   "HR": 0.5237040574306812
  },
  {
   "T": 26.944444444444443,
   "HR": 0.5003686024459629
  }
 ],
 "defecto": {
  "alimentacion": 1000.0,
  "humedad_entrada": 0.72,
  "humedad_objetivo": 0.15,
  "T_aire": 135.0,
  "aire_seco": 26600.0,
  "recirc": 0.25,
  "T_amb": 18.0,
  "HR_amb": 0.6,
  "vel": 0.006166666666666667,
  "factores_vel": [
   1.0,
   1.0,
   1.0
  ],
  "modo_aire": "contracorriente",
  "distribuir": true,
  "transferencia": "mezcla",
  "U_panel": 0.5,
  "bypass_pila": 0.0,
  "nx": 60,
  "nz": 6,
  "tol": 0.02,
  "maxit": 60,
  "relajacion": 0.9,
  "nbis": 40
 }
};
if (typeof module !== "undefined") module.exports = DATOS_SC4;
