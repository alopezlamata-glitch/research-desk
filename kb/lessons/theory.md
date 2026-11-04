# Lecciones — Teoría

## 2026-11-03 · p01 · Convexidad de la función de absorción de deuda (v22, ec. 10, 34, 35)
Estado: candidata
$\delta(d) = 1-e^{-\theta d^\gamma}$ (forma de CDF de Weibull). Derivando:
$\delta''(d) = \theta\gamma e^{-\theta d^\gamma} d^{\gamma-2}\,[(\gamma-1) - \theta\gamma d^\gamma]$.
Es **convexa por debajo** del umbral $D^* = [(\gamma-1)/(\theta\gamma)]^{1/\gamma}$ y **cóncava por encima**.
v22 tiene el corchete con el signo cambiado y afirma lo contrario.
Además, con $\theta=\ln 2$ y $\gamma=1.3$, $D^*\approx 0.43$, no $0.04$. Como toda la muestra está en
$\tilde d\in[0.72,1.56] > D^*$, la absorción es **cóncava** en la muestra: decelera, no acelera.
En consecuencia, $TE\propto e^{-\theta d^\gamma}$ es **convexa** en $d$ ahí, y el Corolario 1.2 de v22 está
invertido (la propia ec. 35 de v22 es > 0, no < 0).
Confirmado con SymPy el 2026-11-03 (`papers/p01-liquidity/theory/check_debt_absorption.py`: 4/4 tests).
**Regla:** todo signo de una segunda derivada y todo umbral numérico se verifica con SymPy y se evalúa
numéricamente en la calibración.

## 2026-11-04 · Biblioteca de p01 (kb/library)
Estado: candidata
- **Lo que funcionó:** NBER por URL directa `nber.org/system/files/working_papers/w<N>/w<N>.pdf` (mejor que `/papers/w<N>.pdf`); Fed Board `federalreserve.gov/econres/feds/files/<año><nº>pap.pdf`; BIS, BoE, BCE, FRBSF y Philadelphia Fed; OpenAlex `oa_url` por DOI (cubre ~45 de 83 a la primera). Para los demás: buscar el WP equivalente (NBER/CEPR/Fed) y probar la URL.
- **Trampas:** (1) OpenAlex a veces devuelve la landing HTML (BIS `r_qt*.pdf`, ijcb.org, SNB): comprobar `%PDF`. (2) Algunos WP de NBER antiguos son escaneos sin texto: la comprobación de título falla (BGG w6455); usar el capítulo del Handbook. (3) Windows/Python da `CERTIFICATE_VERIFY_FAILED` en ecb.europa.eu y bancaditalia.it; `curl` o contexto sin verificación + comprobar PDF y título. (4) Editoriales (AEA, Elsevier, repositorio BoF) dan 403 a scripts aunque la página exista. (5) Salida de Python en cp1252: `reconfigure(encoding='utf8')` o `PYTHONIOENCODING`.
- **Errores del .bib detectados** (no corregidos, ver notas de `kb/library/INDEX.md`): URL de LakdawalaMoreland2026 es un CV; Jeenas2026/AngeletosLianWolf2025 con clave y año desfasados; Sims (2010, ECB) no es Sims (1994); orden de autores de GrobZullig2024; Eusepi–Giannoni–Preston circulaba como "On the Limits of Monetary Policy".
- **Regla:** descartar copias en carpetas de curso/terceros (p. ej. Jordà 2005 en nd.edu) aunque sean PDF válidos: no hay garantía de legalidad.
