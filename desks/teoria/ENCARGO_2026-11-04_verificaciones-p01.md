# Encargo de la Coordinación a Teoría — 2026-11-04 · Verificaciones de p01

Rutas relativas a la raíz del repo (`../../`).

## Contexto
El abogado del diablo (`papers/p01-liquidity/exploration/DEVILS_ADVOCATE_2026-11-04.md`, §1, §2.3, §2.4 y §5.3)
encontró afirmaciones de `exploration/FIRST_PRINCIPLES.md` sin verificar o erróneas. Estas tres
verificaciones hacen falta con cualquier diseño que elijan los autores. Material: los borradores TFG1 y TFG2 en
`papers/p01-liquidity/prior/archive/unzipped/z01/` (solo los `.tex` de TFG1 y `Liquidity_Transmission_Debt_Service.tex`).
Usa la skill `../../.claude/skills/sympy-check/SKILL.md` y `tools/symcheck.py`.

## Tareas
1. **`papers/p01-liquidity/theory/check_nesting.py`:** casos límite de `I_u = ω p_f/a + (1−ω) g`,
   con ω = γ²a/(B+γ²a). Debes recuperar TFG1 (min{}), IOPO 2018 (p. 11, eq. 7: ∂K1/∂r1 = −L0) y el caso sin
   restricción. Indica qué límite es económicamente alcanzable con `B = κ_F·Q(z_F)` (TFG2 l. 283).
2. **`papers/p01-liquidity/theory/check_aggregation.py`:** agregación con **banco común**
   `r_L = r_f + ψL/N`, `L = ΣI`, con una masa 1−s de restringidas y s de holgadas.
   - Comprueba o corrige la derivación a mano del informe (§2.3): `dI_s/du = [p_f − (ψ/N)(1−s)g]/(a_0 + sψ/N)`.
   - Da la fórmula agregada general.
3. **`papers/p01-liquidity/theory/check_coordination.py`:** efecto de quitar la varianza de política, como
   función de (η, v_pol, b, ψ/N, σ_F).
   - En el régimen interior: reproduce con la tabla de calibración de TFG2 (l. 1690–1694) el 10 % (A_P=2)
     y el 65 % (A_P=0,2).
   - En el régimen restringido: el canal σ_F de la Prop. `fs-coordination` (l. 365–385).
   - Di si existe una cota que no dependa de la calibración, o demuestra que no existe.

Cada script tiene que fallar si la afirmación es falsa, igual que el test negativo de `tools/symcheck.py`.

## Entregable
- Los tres scripts, que pasen con `uv run python <script>`.
- `papers/p01-liquidity/theory/VERIFICACIONES_2026-11-04.md`: para cada afirmación del informe, *confirmada*,
  *corregida* (con la expresión buena) o *refutada*.
- Lecciones en `kb/lessons/theory.md` (`## AAAA-MM-DD · p01 · <título>`, `Estado: candidata`).

## Reglas
No edites `FIRST_PRINCIPLES.md`, el informe del abogado del diablo ni los borradores.
