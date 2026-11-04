# p01 — PLAN

## Fase 0: exploración (actual)

| Paso | Qué | Responsable | Salida |
|---|---|---|---|
| 0.1 | Inventario del material de los autores: literatura, propuestas descartadas, borradores | Literatura | `exploration/INVENTORY.md` |
| 0.2 | Fichas de literatura con identificación, datos y resultados | Literatura | `kb/topics/<topic>/papers/*.md` + mapa en el README del topic |
| 0.3 | Fichas de propuestas descartadas: por qué cayeron y qué se salva | Director científico | `exploration/discarded/*.md` |
| 0.4 | Generar **5–8 diseños candidatos** de familias distintas (ver abajo), cada uno en 1–2 páginas | Director científico (+ Teoría para la formalización) | `exploration/candidates/*.md` |
| 0.5 | Comprobación rápida de datos y potencia de los candidatos finalistas | Datos + Econometría | Una sección por candidato |
| 0.6 | Pre-mortem adversarial de los 3 mejores: "¿por qué fracasaría?" | Referee | `audits/2026-xx_phase0_premortem.md` |
| 0.7 | Informe con la rúbrica, ranking y recomendación | Coordinación | `exploration/REPORT.md` |
| 0.8 | **Decisión de los autores** y reescritura de la SPEC | Autores | `SPEC.md` |

## Familias de diseño que deben estar representadas en 0.4
Que el abanico sea amplio es intencionado: así se evita anclarse en v22.
- **Regímenes explícitos:** Markov-switching, threshold y smooth-transition (VAR o LP).
- **Dependencia de estado con agregación de factores:** candidato B (LP + CES), interacciones.
- **Descubrimiento de la no linealidad a partir de los datos:**
  - GAM / LP semiparamétricas;
  - random forests o árboles causales para encontrar qué estados importan, con inferencia honesta (sample splitting).
- **Distribución, no media:** LP por cuantiles (enfoque tipo *growth-at-risk* aplicado a la liquidez).
- **Más datos:**
  - panel internacional o histórico (JST, BIS);
  - frecuencia alta (mercados de financiación, repo, spreads diarios).
- **Estructural parsimonioso:** si aparece un modelo con pocos parámetros bien identificados.

## Lo que se conserva de v22 pase lo que pase
- El diagnóstico: `prior/diagnosis_v22.md`.
- Los checks de teoría (`theory/`).
- Las lecciones en `kb/lessons/`.
