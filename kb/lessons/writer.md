# Lecciones — Redacción (writer)

## 2026-11-11 · p01 · F31, cambios del Referee (F30)
Estado: candidata
1. **Lo que limita la potencia es el diseño, no «los datos».** Al describir un MC de potencia, acotar a «this design / this
   estimator»: otro estimador sobre la misma muestra podría detectar más (el Referee corrigió la introducción).
2. **Un nombre de hoja o de archivo no verifica autoría.** La lección 1 de F29 se quedó corta: «Wieland construye la extensión»
   tampoco estaba verificado. Decir solo lo que respalda la nota del `.bib` y escribir explícitamente lo no verificado.
3. **Rangos de cifras con las macros de ambos extremos** (`\MdeHetC{} to \MdeHomoC{}`) en vez de redondear en palabras
   («about five» quedaba corto en un caso).
4. **Escribir el objetivo del que salen las condiciones de óptimo y todos los signos de los parámetros** (`a>0`); si una letra
   cambia de significado entre secciones, decir cuál es en cada una.
5. **«Verified symbolically» solo si todos los tests son simbólicos**; si hay comprobaciones de signo muestreadas, decirlo.

## 2026-11-11 · p01 · F29, cierre de `\todo` del borrador
Estado: candidata
1. **Atribuir a la fuente solo lo que la nota del `.bib` dice que se verificó** (p. ej. que Wieland construye la extensión, no que
   sea `resid_full`); si la cita no respalda la frase, se deja el `\todo` con el motivo.
2. **Macros de cifras con `{}` final** (`\CovAumNwHcLo{}`) para que LaTeX no se coma el espacio.
3. **Tras quitar un rodeo, compilar con `compile_main.py` y `latexmk`**, no suponer que funciona.

## 2026-11-08 · p01 · F23, borrador del paper A
Estado: candidata
1. **Compilar las macros antes de darlas por buenas.** `output/macros.tex` pasó una auditoría que comparaba cada cadena con su celda
   de origen (F22), pero no compilaba: cuatro nombres llevan el dígito 0 (`\PwHomoH0Falla`), y LaTeX no admite dígitos en un nombre de
   macro. Regla: el generador de macros usa solo letras en los nombres, y alguien compila un `.tex` mínimo con `\input` antes de
   la auditoría.
2. **El check `numbers` solo mira lo que hay después de `\begin{document}`** en cada `.tex` (`tools/integrity.py:171-177`). En un
   archivo de sección incluido con `\input` no comprueba nada. Regla: todo el texto con cifras va en `main.tex`, o el check se amplía
   antes de partir el paper en secciones.
3. **El campo `note` del `.bib` es el estado de verificación**, y `plainnat` lo imprime en la bibliografía. Regla: usar
   `paper/p01.bst` (plainnat sin `note`) o una copia equivalente en cada paper.
4. **Medición sin veredicto.**
   - La regla de decisión se escribe con «p < 0.05», no con «significant».
   - No se cuenta cuántas filas pasan; se dan todas.
   - El p unilateral y el IC bilateral al 95 % van con una nota que avisa de que tienen niveles distintos.
   - El MDE con c·β_ref en los dos estados no es un efecto «state-dependent».
   - «No es evidencia de ausencia de efecto» se apoya en el IC (contiene 0 y β_ref), no en una línea de la SPEC de otra rama del árbol.
5. **No convertir un ejemplo numérico en un resultado general.** Que la fórmula rígida «subestima» solo se comprobó en un equilibrio
   numérico; el test general solo dice que no coincide. Regla: antes de escribir el sentido de una desigualdad, buscar el test que la
   firma; si no existe, escribir lo que el test dice («does not hold») o marcar `\todo` para Teoría.
