# Lecciones — Dirección científica

## 2026-11-04 · T8 · Investigar mejoras de las desks
Estado: candidata
estado: candidata
evidencia: specs/research-desk/IMPROVEMENT_PROPOSAL.md (§0 lista qué fuentes se leyeron y cuáles no)
alcance: Dirección, encargos de investigación externa
caduca: 2027-05-04
regla: Distinguir en cada fuente "leída", "solo resumen/snippet" y "no cargó"; no apoyar una recomendación en lo no leído.

- Los foros (Reddit, HN) no salieron en la búsqueda y `jfimbett/cloco` dio 404: lo declaré en vez de rellenar. Si los autores quieren foros, hará falta que aporten enlaces concretos.
- Casi toda la evidencia sobre memoria y fallos de agentes son preprints 2025–26 vistos solo como resumen de buscador. Antes de implantar, Literatura debe leer los textos.
- Las prácticas de Cunningham y Goldsmith-Pinkham llegaron vía resúmenes de terceros: tratarlas como práctica reportada, no como protocolo verificado.
- Criterio: preferir convertir una lección en test/hook antes que en prosa de prompt.

## 2026-11-04 · p01 · Contrastar una cifra citada con la tabla del borrador antes de convertirla en cota
Estado: candidata
estado: candidata
evidencia: papers/p01-liquidity/exploration/DEVILS_ADVOCATE_2026-11-04.md §2.4 (la "cota ≈3 %" usaba parámetros que no son los de TFG2; con su tabla sale 10–65 %)
alcance: Dirección y Coordinación, cualquier resultado "acotado" que cita una calibración
regla: Una cota o magnitud que dependa de una calibración se calcula leyendo la tabla de parámetros del borrador, se da como función de los parámetros y se comprueba en `theory/check_*.py`; no se cita "la calibración de X" de memoria.

- El valor salía de elegir ηv pequeño frente a b+ψ/N (unidades arbitrarias): con η=5 ya era 14 %.
- La afirmación "se verificó con SymPy" sin script en el repo no cuenta como verificada.

## 2026-11-04 · p01 · Buscar la "novedad" en el propio borrador y en el paper rival antes de darla por nueva
Estado: candidata
estado: candidata
evidencia: DEVILS_ADVOCATE_2026-11-04.md §1 (la fórmula de §2 es la Prop. `fs-transmission` de TFG2; el caso rígido es IOPO 2018, p. 11; la "diferencia" con Perez-Orive et al. no existe, p. 12)
alcance: Dirección, evaluación de candidatos y de "resultados formales" propuestos por la Coordinación
regla: Antes de anotar un resultado como nuevo, localizar la proposición equivalente en (i) los borradores de los autores y (ii) el texto completo del paper rival más cercano, con página; un contraste con un rival se formula sobre lo que el rival afirma, no sobre lo que se supone.

- Las diapositivas no son el paper (Ottonello-Winberry en la biblioteca): decirlo y no citar definiciones que solo estarían en el texto.
- Si el signo del resultado central queda libre en la teoría, la literatura (que discrepa en el signo) lo encajará todo: fijar el signo ex ante.

## 2026-11-04 · p01 · Una predicción prerregistrable tiene que salir de la forma funcional del modelo
Estado: candidata
estado: candidata
evidencia: DEVILS_ADVOCATE_2026-11-04.md §1 (la "transición abrupta en N" contradice `T_I = N/(ψ+(b+ηv)N)`; "la coordinación solo actúa por v" contradice TFG2 Prop. `fs-coordination`)
alcance: Dirección, redacción de hipótesis para SPEC.md
regla: Cada predicción de la SPEC lleva la ecuación del modelo de la que sale; si requiere un ingrediente que el modelo no tiene (un umbral, un canal), se añade al modelo o se marca como exploratoria.

- Además, en el diseño de panel con efectos fijos de tiempo, el choque común se absorbe: contar clústeres y colinealidad entre exposición y restricción por país antes de prometer una interacción triple.

## 2026-11-04 · p01 F3 · Separar el signo del nivel del signo de la diferencia entre estados
Estado: candidata
estado: candidata
evidencia: papers/p01-liquidity/exploration/PREREG_DRAFT.md §2 y §4 (con F1, `I_u ≥ ω_min p_f/a > 0` fija el signo en cada estado, pero β_C − β_U tiene el signo de `a g − p_f`, libre)
alcance: Dirección, redacción de hipótesis en LP dependientes del estado
caduca: 2027-05-04
regla: En una LP con estados, escribir por separado (i) el signo de la respuesta dentro de cada estado y (ii) el signo de la diferencia entre estados, cada uno con su ecuación; solo lo que tenga signo fijo en la teoría verificada es confirmatorio, y declarar los supuestos de signo (p. ej. g ≥ 0) de los que depende.

- Una predicción con signo fijo puede ser poco exigente (H1 casi cualquier modelo la cumple): decirlo a los autores en vez de venderla como prueba del mecanismo.
- Antes de definir un estado, mirar su figura: la liquidez de Z.1 tiene una tendencia secular fuerte; una mediana en niveles habría confundido el estado con la época (y con el ZLB).
- Comprobar la página contra el marcador `<!-- p. N -->` de cada cita al final: en este borrador corregí 4 páginas desplazadas por saltos de página dentro de un párrafo.

## 2026-11-05 · p01 F6 · Medir la información del choque antes de prerregistrarlo
Estado: candidata
estado: candidata
evidencia: papers/p01-liquidity/exploration/REDESIGN_POWER_2026-11-04.md §1 (F = 4,2 de `mps_bs23_orth` sobre Δffr; BS p. 41 ya avisaba con F = 2,44; F4 tuvo que descubrirlo con un MC de 8 min)
alcance: Dirección, elección del choque y de la muestra en cualquier SPEC con LP o SVAR
caduca: 2027-05-05
regla: Antes de prerregistrar un choque, calcular en la muestra exacta su primera etapa sobre el tipo oficial (π, F), N·π²·var(ε) y el % de Σε² en los 4 mayores, y una cota de oráculo del MDE con el ruido univariante de la variable de resultado; si c = MDE/|β_ref| > 3, no se prerregistra sin escalar.

- Cuando la LP está a ×1,2–1,4 del oráculo con el DGP conocido, cambiar de estimador (VAR, suavizado, bayesiano) no arregla la potencia: solo la arreglan más información del choque, más N o menos ruido.
- Leer en la fuente la advertencia de relevancia de la propia serie (aquí, la versión de BS sin discursos) antes de elegirla.
- En un panel con efectos fijos de tiempo, buscar una predicción con signo fijado por la teoría sobre la *diferencia* (aquí ∂I_u/∂g = 1 − ω); el nivel deja de estar identificado.

## 2026-11-08 · p01 F11 · Al redactar un prerregistro, recorrer rama por rama el árbol de decisión simulado
Estado: candidata
estado: candidata
evidencia: papers/p01-liquidity/exploration/PREREG_S1R_DRAFT.md, HANDOFF (preguntas 1–3: controles, consecuencia de los diagnósticos y refutación en V3s; las 7 decisiones no las fijaban, `s1r_lp.decide` sí)
alcance: Dirección, redacción de prerregistros a partir de decisiones de los autores y de un MC
caduca: 2027-05-08
regla: Escribir la regla de decisión leyendo el código del árbol que se simuló, no el resumen de las decisiones. Para cada rama y cada elemento de la especificación (controles, muestra, diagnósticos), comprobar que lo cubre una decisión de los autores; lo que solo cubre el código se escribe tal cual y se lleva a los autores como pregunta explícita.

- Un diagnóstico prerregistrado necesita su consecuencia escrita. Si se puede calcular sin la variable de resultado y ya se sabe que rechazará, hay que decirlo en el propio texto.
- Antes de pegar texto encima de un bloque ```prereg, mirar qué congela `integrity.py::prereg_text` (desde el último `## `): un subencabezado `## ` deja fuera todo lo que está por encima.
- Cada estimación que decide lleva su propio id confirmatorio, aunque sea la misma ecuación en otra muestra: la paridad usa la clave (spec_id, term).
