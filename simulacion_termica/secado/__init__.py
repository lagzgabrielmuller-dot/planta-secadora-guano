"""Simulación térmica del secador de guano SC-4 (Proyecto final 7.º, E.P.N.M. y S. N° 35, Crespo).

Módulos:
  parametros   datos de la Rev. D/E y parámetros del modelo, con su fuente
  psicrometria aire húmedo y propiedades de transporte
  guano        isoterma GAB, difusividad, contracción y estructura del lecho
  nucleo       avance del producto en un piso (numba)
  secador      solución estacionaria del secador y su circuito de aire
  dinamica     simulación en el tiempo con el lazo de humedad (PID)
"""
