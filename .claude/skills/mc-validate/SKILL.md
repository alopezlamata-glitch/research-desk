---
name: mc-validate
description: Valida con Monte Carlo que un estimador recupera los parámetros verdaderos con el tamaño de muestra disponible, antes de aplicarlo a datos reales. Úsalo con cualquier estimador nuevo, no estándar o con T pequeño.
---

Regla de CLAUDE.md: todo estimador nuevo o no estándar se valida con Monte Carlo antes de usarse con datos
reales. Herramienta: `tools/mc.py` (con tests en `tools/test_symcheck_mc.py`).

1. **DGP de la desk de Teoría** (`papers/<slug>/theory/dgp.py`): simula datos con parámetros verdaderos
   conocidos, con el **mismo T**, la misma frecuencia y una persistencia parecida a la de los datos reales.
2. **El estimador del análisis, sin cambios:** la misma función que se usará con los datos reales y que
   devuelve `(estimaciones, errores_estándar)`.
3. **Ejecuta** `mc.validate(dgp, estimador, true={...}, T=T_real, reps=500, seed=...)`. Mide con T y T/2:
   sesgo, RMSE, cobertura del IC al 95 % y potencia.
4. **Regla de parada:** si la cobertura con T queda fuera de [0,92, 0,98], `validate` lanza
   `CoverageOutOfBand`. Entonces **no se aplica a datos reales**: se documenta en `TASKS.md` con `[!]` y se
   escala a la Dirección. No se ajusta el estimador para que pase.
5. **Guarda la tabla** (`MCResult.row()` de cada parámetro) en `output/tables/mc_<estimador>.txt` y cítala
   en la tarea. Con 500 réplicas, la cobertura tiene un error de Monte Carlo de ±0,01.
6. Si hay parámetros calibrados, repite el MC con la calibración alternativa más desfavorable del grid de
   sensibilidad.
