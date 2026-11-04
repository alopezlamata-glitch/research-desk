# Encargo de los autores al Director científico — 2026-11-04 · Abogado del diablo

## Petición
Los autores piden que ataques, como abogado del diablo, el planteamiento de p01 que propone la
Coordinación en `papers/p01-liquidity/exploration/FIRST_PRINCIPLES.md` (sobre todo las secciones 2, 3, 5 y 6).
Tu trabajo es encontrar por qué ese planteamiento **no** es el mejor, o por qué fallaría, y proponer algo
mejor si existe. Si después de intentarlo en serio el planteamiento resiste, dilo con la misma claridad.

Rutas relativas a la raíz del repo (`../../`).

## Material
- `papers/p01-liquidity/exploration/FIRST_PRINCIPLES.md`: lo que atacas. **No lo edites.**
- `papers/p01-liquidity/exploration/INVENTORY.md`, `LITERATURE_REPORT.md`, `candidates/B_state_dependent_lp_ces.md`
  y `prior/diagnosis_v22.md`.
- Borradores de TFG1 y TFG2 (texto completo): `papers/p01-liquidity/prior/archive/unzipped/z01/Liquidity_Transmission_TFG_1_Simulate_This_2026_10_20/*.tex`
  y `.../Liquidity_Transmission_TFG_2_October_20_2026/Liquidity_Transmission_Debt_Service.tex`. **No leas otros
  archivos de `prior/archive/`.**
- Biblioteca: `kb/library/INDEX.md` → `kb/library/md/<clave>.md`. Lee **el texto completo** (con su índice) de al menos:
  PerezOriveTimmerVanDerGhote2026, IppolitoOzdagliPerezOrive2018, Auclert2019, Jeenas (la clave que figure en
  el índice), JarocinskiKaradi2020, BauerSwanson2023 y OttonelloWinberry2020. Cita con página (`<!-- p. N -->`).
- Datos disponibles: `datalake/CATALOG.md`.

## Qué atacar (como mínimo)
1. **La teoría.**
   - ¿Es cierto que TFG1 es un caso límite de TFG2, y que eso importa económicamente?
   - ¿La "fórmula general" (§2 y §5) es correcta y nueva, o ya está en Auclert (2019), Perez-Orive et al. u
     Ottonello-Winberry?
   - ¿La agregación (§5) esconde supuestos fuertes, como la independencia entre la holgura y la exposición
     o el equilibrio parcial?
2. **La novedad.** Para cada predicción de §6.6: ¿algún paper de la biblioteca ya la muestra? Sé concreto,
   con página.
3. **La identificación del diseño de la zona euro (§6.5).**
   - Shocks del BCE con efecto información.
   - Exposición a la repreciación endógena a la calidad del crédito o a la historia del país.
   - Países con mucha deuda variable que son también los de banca débil (confusión en la interacción triple).
   - Pocos países, errores estándar con clusters escasos, y crisis de deuda soberana 2010–12 como
     observación influyente.
   - ¿Hay datos trimestrales por país de inversión y de los tipos sobre saldos vivos?
4. **La cota de la coordinación (§6.4).** ¿Depende de la calibración elegida? ¿Hay un canal de la
   coordinación que no pase por v y que el planteamiento ignora?
5. **Diseños rivales.** Propón 2–4 alternativas de familias distintas (p. ej., solo EE. UU. con
   Bauer-Swanson y exposición por sectores de Z.1; panel histórico JST con instrumento trilema; un paper
   teórico puro; un enfoque de estadísticos suficientes al estilo Auclert). Puntúalas con la rúbrica de
   `papers/p01-liquidity/SPEC.md` (ajuste, ambición, identificación, datos/potencia, riesgo, coste)
   **junto al planteamiento actual**, justificando cada puntuación.

## Entregable
`papers/p01-liquidity/exploration/DEVILS_ADVOCATE_2026-11-04.md`, con:
1. **Veredicto por afirmación** de FIRST_PRINCIPLES: *se sostiene* / *debilitada* / *refutada*, con su
   razonamiento y su evidencia (paper y página, o el paso de la derivación).
2. **Las 3 amenazas más graves** al planteamiento y, para cada una, qué prueba o qué cambio la resolvería.
3. **Tabla de la rúbrica:** el planteamiento actual frente a los rivales.
4. **Recomendación:** mantener, modificar (qué exactamente) o sustituir (por cuál).

Añade tus lecciones a `kb/lessons/scientific-director.md` con el formato `## AAAA-MM-DD · p01 · <título>` seguido de
`Estado: candidata`.

## Reglas
- Ninguna afirmación sobre la literatura sin página del texto completo. Si solo has podido leer el resumen,
  dilo.
- Marca tu criterio propio como **[criterio propio]**.
- No edites ningún archivo salvo el entregable y tus lecciones.
