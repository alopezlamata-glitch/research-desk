# p01-liquidity — SPEC

Estado: **Diseño F; etapa 1 rediseñada por los autores (2026-11-07) para ganar potencia** (Romer-Romer, h = 4..12, tres
variantes de Volcker; ver Desviaciones). Datos (F7) y citas (F8) hechos; **en curso: F9**, Monte Carlo de `s1r_*`
(Econometría). Después, F10 (auditoría del Referee) y F11 (prerregistro nuevo, que aprueban los autores), **antes** de
estimar con la inversión.

## Intuición de partida (de los autores)
Hay una serie de factores que afectan a la liquidez, con **regímenes no lineales**: el mismo impulso
tiene efectos distintos según la situación de la economía. v22 fue un intento de formalizarlo
(tres canales multiplicativos), pero no funcionó por:
- pocos datos para demasiados parámetros;
- endogeneidad generalizada;
- causalidades cruzadas.

## Principio de la Fase 0
**No partimos de una estructura predefinida**, tampoco de la de v22. Partimos de todo lo disponible:
- la literatura de los autores;
- las propuestas descartadas;
- v22 y su diagnóstico.

A partir de ahí se elige el diseño con **mejor ajuste al problema, más prometedor y más ambicioso**,
con una evaluación explícita.

## Entradas
- `prior/`: v22 y su diagnóstico.
- `exploration/discarded/`: una ficha por cada propuesta descartada (idea, por qué se descartó, qué es salvable).
- `kb/topics/<topic>/papers/`: fichas de la literatura de los autores.
- `exploration/candidates/`: diseños candidatos. El candidato B ya existe y se evalúa como uno más.

## Rúbrica de evaluación (cada criterio de 1 a 5, con justificación escrita)

| Criterio | Pregunta |
|---|---|
| **Ajuste a la intuición** | ¿Captura varios factores y regímenes no lineales sin imponer la forma de antemano? |
| **Ambición / contribución** | ¿Qué sabría el campo después que hoy no sabe? ¿En qué revista encaja? |
| **Identificación** | ¿Qué variación identifica el resultado principal? ¿Resiste la endogeneidad y las causalidades cruzadas? |
| **Datos / potencia** | ¿Cuántas observaciones frente a parámetros? ¿Existen los datos gratis? Monte Carlo rápido de potencia |
| **Riesgo** | ¿Qué tiene que salir bien? ¿Hay un paper publicable aunque el resultado sea negativo? |
| **Coste** | Semanas de trabajo de las desks hasta el primer resultado |

Una puntuación alta en ambición no compensa una identificación de 1 o 2.

## Decisión
La toman **los autores**, a partir del informe de la Fase 0 (`exploration/REPORT.md`). Después, esta
SPEC se reescribe con la pregunta, las hipótesis prerregistradas y la identificación del diseño
elegido. La plantilla está en `papers/_template/SPEC.md`.

## Prerregistro de la etapa 1: EE. UU. (aprobado por los autores el 2026-11-04)

La justificación completa, con páginas, está en `exploration/PREREG_DRAFT.md` (Director científico, F3). Aquí queda lo que obliga.
Las cuatro decisiones de los autores sobre el borrador están en Desviaciones (2026-11-04).

**Pregunta.** ¿Sigue transmitiéndose un choque monetario a la inversión no residencial de EE. UU. cuando la liquidez de las empresas no
financieras está por debajo de su tendencia, en subidas y en bajadas, como predice el margen interior de reservas (ω ≥ ω_min > 0)?

**Especificación (`s1_liq`).** LP de un estado con subidas y bajadas separadas, sobre ȳ_t = (1/5) Σ_{h=0..4} 100·[log I_{t+h} − log I_{t−1}]:
- `I` = `inv_nonres_q`; choque ε = `mps_bs23_orth`, con ε⁺ = max(ε,0) y ε⁻ = min(ε,0).
- `D_{t−1}` = 1 si `s_{t−1}` < mediana muestral, con s = log(`liq_broad_debt`) menos su media móvil de 12 trimestres hacia atrás.
- Regresores: D, D·ε⁺, (1−D)·ε⁺, D·ε⁻ y (1−D)·ε⁻, más 2 retardos sin interactuar de Δlog inversión, Δlog PIB real, Δlog deflactor,
  Δ`y2_mean` y `ebp`.
- Errores estándar Newey-West (Bartlett, 5 retardos), salvo que F4 valide otro método (en ese caso, Desviación **antes** de estimar).
- Forma reducida (no LP-IV).
- La IRF h = 0..12 se presenta, pero no decide.

**Muestra.** t ∈ 1988Q2–2023Q4, sin ZLB (`ffr` < 0,25) ni 2019Q1–2021Q4. Da N = 102, con celdas de 22, 29, 28 y 23
(`data/clean/SAMPLE_COUNTS.md`). Datos en última revisión, congelados por el hash del MANIFEST; refrescarlos es una Desviación.

**Hipótesis** (β < 0: la inversión cae tras una subida y sube tras una bajada):
- **H0** (`s1_lin`): β_lin < 0. Si no se confirma, H1 no se interpreta y se escala al Director.
- **H1⁺ / H1⁻** (`s1_liq`): β⁺_C < 0 y β⁻_C < 0 en el estado restringido. Sale de I_u = ω p_f/a + (1−ω) g con ω ≥ ω_min > 0 y g ≥ 0
  (`theory/check_nesting.py`, `check_aggregation.py`).
  - **Supuesto declarado A-g:** la exposición neta a la repreciación es g ≥ 0. Una refutación refuta "el nido con g ≥ 0".

**Reglas de decisión** (sobre ȳ; α = 0,05 unilateral; Holm sobre {H1⁺, H1⁻}):
- **Confirma H1^d:** β^d_C < 0 con p de Holm < 0,05.
- **Refuta H1^d:** se cumple una de estas dos condiciones:
  - (a) β^d_C > 0 con p < 0,05;
  - (b) el IC al 90 % de β^d_C queda entero en (−0,146·|β̂^d_U|, +∞).
    Aquí 0,146 = ω_min con la calibración de TFG2 (`check_nesting.py::test_minimum_transmission_with_g0_at_tfg2_calibration`).
- **No concluyente:** en cualquier otro caso. Si la potencia de F4 frente a la alternativa de referencia es < 0,8, un β_C no
  significativo es "no concluyente por potencia", nunca refutación.
- **Diagnósticos que se publican siempre:**
  - D1: observaciones por celda;
  - D2: suma de |ε| por celda;
  - D3: test de balance ε ~ D_{t−1} + s_{t−1};
  - D4: estabilidad de la mediana sin 1988–93.

**Exploratorio** (lista cerrada en `PREREG_DRAFT.md` §4):
- E1, la diferencia entre estados (si la falta de liquidez amplifica o atenúa), que se presenta como medición;
- la asimetría;
- la interacción exposición × restricción;
- la interacción triple;
- la coordinación;
- la STAR;
- otras variables de resultado;
- h > 4;
- 2024–26;
- la etapa 2.

Ids prerregistrados (los lee `tools/research.py`; cualquier otra especificación solo puede registrarse como exploratoria):
```prereg
# --- confirmatorias (deciden) ---
s1_lin
s1_liq
# --- robustez prerregistrada (no deciden) ---
r_dsr
r_bs25me
r_bs23orth_1994
r_bs23raw
r_zlb_in
r_covid_in
r_liq_narrow_assets
r_state_q25
r_state_logistic
r_ctrl_interact
r_lags4
r_balance_ctrl
r_inv_nfc
```

prereg_commit: af1c346 (aprobación de los autores, 2026-11-04). Lo que va de `## Prerregistro` a este bloque está
congelado: cambiarlo exige una Desviación con su huella (`tools/integrity.py`, check `prereg`).

**Replicación cruzada:** `s1_lin` y `s1_liq` en R (`code/replication_r/`, `fixest`), con paridad `estimates_py.csv` = `estimates_r.csv`.

**Requisito previo a estimar:**
- ~~Teoría añade los tests de `L_u > 0` con g ≥ 0 y de `∂I_u/∂g = 1−ω`~~ (hecho 2026-11-04: `check_aggregation.py::test_L_u_positive_with_nonnegative_g_and_w_above_min`, `check_nesting.py::test_dI_dg_is_one_minus_w_and_its_sign`);
- F4 valida con `mc-validate` esta especificación con N = 102 y da la potencia.

## Desviaciones
- 2026-11-04 · El borrador inicial (candidato B) se retira como SPEC y pasa a `exploration/candidates/`
  por decisión de los autores: primero se revisa todo el material.
- 2026-11-04 · **Los autores aprueban el diseño F** (`exploration/DEVILS_ADVOCATE_2026-11-04.md` §4–5), propuesto
  en común por el Director científico y la Coordinación. La Fase 0 se cierra sin el `REPORT.md` previsto: el informe
  del abogado del diablo puntúa con la rúbrica el planteamiento de `FIRST_PRINCIPLES.md` y 5 alternativas.
  - **Contribución:** el margen interior de reservas y el cierre bancario común entre los extremos de IOPO
    (2018) y Perez-Orive et al. (2026).
  - **Empírica en dos etapas:**
    1. EE. UU. con Bauer-Swanson, un solo estado (liquidez o servicio de la deuda) y subidas y bajadas separadas.
    2. Panel de la zona euro, solo si pasa la puerta: datos por país en el MANIFEST, exposición contractual × stock,
       potencia ≥ 0,8 por Monte Carlo con 10–12 clústeres y sin ZLB, y placebo con el choque de información de JK.
  - La interacción triple es exploratoria.
  - **Prerregistro:** el signo esperado se fija ex ante. Las predicciones 6.6(2, segunda mitad) y 6.6(4) de
    `FIRST_PRINCIPLES.md` quedan fuera hasta que se deriven.
  - **Motivo:** el planteamiento anterior tenía identificación 2 y afirmaciones refutadas (cota del 3 %, novedad
    de TFG1 ⊂ TFG2, diferencias con IOPO y Perez-Orive).
- 2026-11-04 · **Los autores aprueban el prerregistro de la etapa 1** sobre el borrador `exploration/PREREG_DRAFT.md`, con cuatro decisiones:
  1. **Choque principal `mps_bs23_orth`**, con `mps_bs25_me` como robustez desde 1994. La serie con discursos no está publicada (Datos lo comprobó).
  2. **E1** (amplifica o atenúa) **queda exploratoria**: la teoría no fija su signo, y la medida de exposición disponible (E.2 STBL,
     préstamos nuevos 1997–2017) cubre solo 53 de las 102 observaciones.
  3. **Umbral de refutación: 0,146 = ω_min de TFG2**, no un 10 % fijo.
  4. **El estado DSR pasa de secundario confirmatorio a robustez (`r_dsr`)**, porque sus celdas tienen 11–18 observaciones. Por eso
     desaparece `s1_dsr` del borrador.
- 2026-11-07 · **Los autores deciden rediseñar la etapa 1** sobre la propuesta del Director científico
  (`exploration/REDESIGN_POWER_2026-11-04.md`) y la auditoría R-F4 (`audits/2026-11-05_F4_mc.md`, APROBADO CON CAMBIOS).
  Resumen de la decisión en `exploration/DECISIONES_AUTORES_2026-11-07.md`. Aceptan las 7 recomendaciones:
  1. **`s1_liq` no se estima tal como está**: frente a β_ref su potencia ≈ tamaño (F4), y con la condición de H0 el 92 % de
     los resultados serían "H1 no se interpreta" (R-F4).
  2. **Romer-Romer pasa a ser el choque principal** (sustituye a la decisión 1 del 2026-11-04); `mps_bs23_orth` queda como
     réplica posterior a 1984. La robustez sin 1979Q4–1982Q4 es obligatoria.
  3. **H1 con subidas y bajadas juntas**; la asimetría pasa a exploratoria. Revierte en parte el diseño F ("subidas y bajadas
     separadas") porque separarlas no tiene potencia en ningún diseño agregado de EE. UU.
  4. **Estadístico: media de h = 4..12**, en vez de h = 0..4.
  5. **Errores estándar: la Desviación de F4 (NW(5) con residuos HC3) no se registra todavía.** Primero el MC nuevo la valida
     también con ruido heterocedástico ligado a los trimestres de alto apalancamiento; se registra con ese resultado, y si no
     pasa se elige otro error antes de estimar. (Postura de la Coordinación; el Director proponía registrarla ya.)
  6. **Se abre la etapa 1b transversal** (gradiente de exposición ∂I_u/∂g = 1 − ω > 0, panel con efectos fijos de tiempo),
     condicionada a datos (G ≥ 40) y a un MC con potencia ≥ 0,8. **Los autores no tienen acceso a WRDS** (confirmado el
     2026-11-07): la etapa 1b depende de una fuente gratuita (QFR del Census u otra), que busca Datos en F7.
  7. **Se acepta prerregistrar una H1 con potencia esperada ≈ 0,2–0,4**, como medición acotada, con el MDE escrito ex ante,
     las probabilidades de veredicto calculadas con la condición de H0 y el umbral de refutación (b) revisado para que no
     dependa de un β̂_U ruidoso.
  - **Qué no cambia todavía:** el bloque ```prereg``` y su texto congelado (`prereg_commit: af1c346`). El prerregistro nuevo
    (`s1r_*`) se escribe con los resultados del MC nuevo y antes de ver la respuesta de la inversión; al cambiar el texto
    congelado, su Desviación llevará la huella `prereg <hash>` y un `prereg_commit` nuevo cuando lo aprueben los autores.
- 2026-11-07 · **Volcker en la etapa 1 rediseñada (aviso de F7).** 11 de los 13 trimestres de 1979Q4–1982Q4 caen en el estado
  restringido (59 % de Σ|ε| con Volcker; equilibrado sin él, `data/clean/SAMPLE_COUNTS_S1R.md`). Los autores deciden que el
  MC de F9 compare tres variantes y que la principal se elija en el prerregistro nuevo (F11), antes de ver la respuesta de la
  inversión: (V1) muestra completa con la robustez sin Volcker como comprobación; (V2) principal sin Volcker; (V3) muestra
  completa, y H1 solo se confirma si también se sostiene sin Volcker. El estado sigue definido como en el prerregistro
  (mediana de `s_{t−1}` en la muestra completa de cada choque); quitar Volcker no lo redefine.
