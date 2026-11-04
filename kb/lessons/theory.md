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

## 2026-11-04 · p01 · Nido TFG1 ⊂ TFG2: el límite rígido no se alcanza dentro del modelo
Estado: candidata
Derivando las KKT de TFG2 se obtiene $I_u=\omega p_f/a+(1-\omega)g$, $\omega=\gamma^2a/(\mathcal B+\gamma^2a)$. Con $\mathcal B=\kappa_F Q(z_F)\in(0,\kappa_F)$,
$\omega\ge\omega_{\min}=\gamma^2a/(\kappa_F+\gamma^2a)>0$ (0,146 en TFG2 con $A_P=2$): el cero de TFG1 y el caso IOPO ($I_u=g$) son esquinas (reserva fija o $\kappa_F\to\infty$), no puntos interiores.
Verificado: `papers/p01-liquidity/theory/check_nesting.py`. **Regla:** al afirmar que un modelo «es caso límite» de otro, calcula el rango del parámetro que lo indexa con su definición estructural, no solo el límite formal.

## 2026-11-04 · p01 · Agregación con banco común: la curvatura propia no incluye $\psi/N$
Estado: candidata
Con $r_L=r_f+(\psi/N)L$, cada empresa toma $r_L$ como dado: su curvatura es $a_0=b+\eta v$ y $\psi/N$ solo entra por el precio. Fórmula general (tipos $j$, peso $\omega_j$, alivio $g_j$):
$L_u=(\bar G+\Theta p_f)/(1+\phi\Theta)$, $\Theta=\sum s_j\omega_j/a_j$, $\bar G=\sum s_j(1-\omega_j)g_j$, $\phi=\psi/N$. La derivación a mano del abogado del diablo vale solo con restringidas rígidas ($\omega_j=0$);
con reserva ajustable subestima (3,11 frente a 3,97 en un equilibrio no lineal). Verificado: `check_aggregation.py` (SymPy + equilibrio con `scipy`).
**Regla:** una derivación hecha «a mano» con restringidas rígidas no se reutiliza para el modelo de reserva ajustable; y todo agregado se contrasta con el equilibrio no lineal por diferencias finitas.

## 2026-11-04 · p01 · No hay cota calibration-free del efecto de quitar la varianza de política
Estado: candidata
Régimen interior: $\Delta=\eta v_{pol}/(b+\eta v_0+\psi/N)$, sin cota superior (10,3 % con $A_P=2$ y 64,5 % con $A_P=0,2$ en TFG2); solo hay cota de nivel $p_f/(b+\psi/N)$. Con restricción activa,
$\sigma_F$ eleva $I$ sin cambiar $v$ y el efecto sobre la pendiente $I_u$ tiene signo libre ($\partial I_u/\partial B\propto ag-p_f$). Distinguir **peso en $a$** ($\eta v/a$) de **subida de la pendiente** ($\text{share}/(1-\text{share})$).
Verificado: `check_coordination.py`. **Regla:** una «cota» en un paper es una función de la calibración o un teorema; si es un valor numérico, lleva su calibración y se genera con código.
