# F27 · Observación tras el Corolario 1 — 2026-11-11

Encargo: `desks/teoria/ENCARGO_2026-11-11_f27-observacion-corolario.md`.

## Veredicto

**Se sostiene tal como está escrita** (`paper/main.tex:166-169`). No hay que quitarla ni cambiar el enunciado.

Test: `papers/p01-liquidity/theory/check_nesting.py:141`, `test_remark_chain_I_u_ge_w_pf_a_gt_w_min_pf_a_gt_0`.

## La cadena, eslabón a eslabón

| Eslabón | Forma cerrada (verificada con `check_identity`) | Tipo | Usa |
|---|---|---|---|
| `I_u ≥ ω p_f/a` | `I_u − ω p_f/a = (1−ω) g = B g/(B+γ²a)` | **débil**: igualdad si y solo si `g = 0` | `g ≥ 0`, `B ≥ 0`, `γ, a > 0` |
| `ω p_f/a > ω_min p_f/a` | `γ² p_f (κ_F−B)/((B+γ²a)(κ_F+γ²a))` | **estricta** | `B < κ_F` (Prop. 2(iii), `main.tex:153`), `p_f > 0` |
| `ω_min p_f/a > 0` | `γ² p_f/(κ_F+γ²a)` | estricta | `p_f, γ, κ_F > 0`, `a > 0` |

El `≥` del texto es el signo correcto: con `g = 0` el primer eslabón es igualdad, y el test lo comprueba (el `>` estricto falla en
`g = 0`). Los otros dos son estrictos en todo óptimo interior.

## Bordes

- **`g = 0`:** `I_u = ω p_f/a` exacto; la cadena sigue valiendo con `≥` en el primer eslabón.
- **`B → 0`:** `ω → 1`, `I_u → p_f/a`; no es interior (`Q(z) > 0` con `z` finito), pero la cadena se mantiene en el límite.
- **`B → κ_F` (`z → −∞`):** `ω → ω_min`, así que el segundo `>` se volvería igualdad. El interior lo excluye (`Q < 1` con `z`
  finito), que es justo lo que declara la Prop. 2(iii). Con `g = 0`, `ω_min p_f/a` es un ínfimo que no se alcanza.
- **Test negativo:** con `g < 0`, el primer eslabón falla en toda la rejilla, e `I_u` puede ser negativo (p. ej. `p_f = γ = 1`,
  `a = 0,171`, `B = 3`, `g = −2` ⇒ `I_u < 0`). La hipótesis `g ≥ 0` es necesaria, no decorativa.

## Supuestos usados (todos declarados en el paper)

`p_f > 0` y `γ > 0` (`main.tex:116,129`); `κ_F > 0` (`main.tex:126`); `B = κ_F Q(z) ∈ (0, κ_F)` en el interior (`main.tex:153`);
`g ≥ 0` (hipótesis de la propia Observación). Hay uno **implícito**: `a > 0`. El texto lo da por la frase «its marginal cost
rises with slope `a`» (`main.tex:117-118`), pero no lo escribe como `a > 0`. No es un supuesto nuevo, así que no bloquea.
Redacción puede escribir `a>0` en F29 si quiere hacerlo explícito (opcional).

## HANDOFF

- **Hecho:** test de tres capas de la Observación en `papers/p01-liquidity/theory/check_nesting.py:141-171`. La capa simbólica
  da las formas cerradas de los dos huecos. El signo del segundo lo decide SymPy sin muestrear, sustituyendo `B = κ_F/(1+s)` con
  `s > 0`. La capa numérica usa la rejilla `BOX_Z` (`check_nesting.py:118`). Comprueba los bordes `g = 0`, `B → 0` y `B → κ_F`,
  y tiene un negativo con `g < 0`.
- **Evidencia:** `uv run pytest papers/p01-liquidity/theory -q`: 46 passed. `uv run ruff check papers/p01-liquidity/theory`:
  limpio. Sin commit (lo pide el encargo); base 8c25839.
- **Decisiones y quién las tomó:** Teoría da el veredicto de que se sostiene sin cambios. Lo de `a > 0` se deja como sugerencia
  opcional para Redacción, no como desviación.
- **Supuestos y límites:** solo verifica la Observación sobre `eq:Iu` y `eq:wmin`. Las piezas previas ya estaban verificadas en
  `test_weighted_form` y `test_weight_is_bounded_below_by_w_min`. La rejilla numérica es `BOX_Z`, con `g ∈ (10⁻⁶, 6)` para el
  primer eslabón estricto.
- **Descartado:** debilitar el enunciado, porque el `≥` ya es el correcto en `g = 0`. Un archivo `check_*.py` aparte también se
  descarta: el encargo pide el test en `check_nesting.py`, que comparte `SOL`, `W` y `BOX_Z`.
- **Riesgo para F29:** el cambio en `theory/` hace caducar la aprobación vigente del Referee. `tools/integrity.py` da ahora
  `[gate] paper/main.tex:22`. Es lo que la regla prevé (`CLAUDE.md`, «Flujo de trabajo» 3): solo bloquea los commits que llevan
  un `.tex`. Antes de que Redacción commitee F29, hay que commitear F27 y que el Referee lo audite.
- **Pendiente de decidir:** nada para los autores. En F29, Redacción puede cerrar el `\todo` del test SymPy de la Observación
  citando este test.
