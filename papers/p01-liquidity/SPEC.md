# p01-liquidity — SPEC

Estado: **Diseño F elegido por los autores (2026-11-04).** Falta el prerregistro, que se escribirá cuando
Teoría entregue las verificaciones. Hasta entonces, la pregunta y la identificación de F están en `exploration/DEVILS_ADVOCATE_2026-11-04.md` §5.

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
