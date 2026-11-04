# p01-liquidity — SPEC

Estado: **Fase 0: exploración.** No hay diseño elegido · 2026-11-04

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
