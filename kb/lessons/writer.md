# Lecciones — Redacción (writer)

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
