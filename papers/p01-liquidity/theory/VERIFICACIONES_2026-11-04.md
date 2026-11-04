# Verificaciones de teoría de p01 · 2026-11-04

Desk: Teoría. Encargo: `desks/teoria/ENCARGO_2026-11-04_verificaciones-p01.md`. Scripts (43 tests, `uv run pytest papers/p01-liquidity/theory`;
cada uno corre también con `uv run python <script>`): `check_nesting.py`, `check_aggregation.py`, `check_coordination.py`.
Fuente de las ecuaciones: TFG2 `Liquidity_Transmission_Debt_Service.tex` (l. citadas) y TFG1 `manuscript/model.tex`; IOPO 2018 p. 10–11 solo
a través del informe del abogado del diablo (no re-leído por Teoría). Todo test positivo tiene su test negativo (`pytest.raises(ClaimFailed)`).

## 1. Nido de modelos (`check_nesting.py`)

Se derivan las KKT de TFG2 (`fs-kkt`) respecto de u con q_u = p_f, H_u = g, κG' = −B, y SymPy devuelve
`I_u = (γ²p_f + B g)/(B + γ²a) = ω p_f/a + (1−ω) g`, ω = γ²a/(B+γ²a), con `m_u` y `λ_u` como en `fs-buffer-transmission`.

| Afirmación del informe / FIRST_PRINCIPLES | Veredicto |
|---|---|
| `I_u = ω p_f/a + (1−ω) g` con ω = γ²a/(B+γ²a) | **Confirmada** (derivada de las KKT, no copiada) |
| «Verificado con SymPy el 2026-11-04» (FIRST_PRINCIPLES) | **No lo estaba** (el informe acertó); ahora sí, con `check_nesting.py` |
| Sin restricción = límite B→0 | **Confirmada**: I_u → p_f/a |
| TFG1 (`min{H, q/a}`) = B→∞ con g = 0 | **Confirmada**: I_u → 0. Las dos ramas del min dan p_f/a (holgada) y H_u = g (tope) |
| IOPO 2018 (p. 11, eq. 7): ∂K1/∂r1 = −L0 | **Confirmada**: B→∞ con g = γE_D, γ=1, E_D = −∂J_F/∂u = L0 (deuda toda flotante). Con reserva ajustable ya no es exacto (test negativo) |
| «B→∞ importa poco: está acotado por κ_F» | **Confirmada y precisada** (abajo) |

**Qué límite es alcanzable con B = κ_F·Q(z_F) (TFG2 l. 283).** Q es estrictamente decreciente de 1 a 0, luego B ∈ (0, κ_F) y
ω ∈ (ω_min, 1), con **ω_min = γ²a/(κ_F + γ²a)**.
- **Alcanzable (asintóticamente):** el extremo sin restricción (B→0, z_F→+∞, reservas muy por encima de la necesidad esperada).
- **Alcanzable hasta ω_min, no más:** B→κ_F (z_F→−∞). En la calibración de TFG2 con A_P=2 (a=0,171, κ_F=γ=1): ω_min = 0,146, así que
  incluso con g = 0 la transmisión es **≥ 0,146·p_f/a = 0,854**, no 0.
- **No alcanzable en el interior:** el límite rígido (ω=0: TFG1/IOPO). Exige κ_F→∞ o una **esquina** (m_F en su cota o buffer fijo), donde
  I = H − γ m̄ e I_u = g **exactamente** (test `fixed_buffer_corner`). Es el «extremo» del que habla TFG2 l. 358.
- Cruce con TFG2 l. 793 (g = 0, A_P=2, I_u = 1,769): implica B ≈ 0,394 ∈ (0, κ_F=1), ω ≈ 0,30. Coherente. (No he reproducido el caso g = 5 → 5,201:
  B depende del estado de equilibrio y cambia con g; no es una discrepancia comprobada.)

## 2. Agregación con banco común (`check_aggregation.py`)

Cada empresa toma r_L = r_f + (ψ/N)L como dado: su curvatura propia es a_0 = b+ηv, y ψ/N entra solo por el precio. Con φ = ψ/N.

| Afirmación | Veredicto |
|---|---|
| `dI_s/du = [p_f − φ(1−s)g]/(a_0 + sφ)` (informe §2.3) | **Confirmada** (SymPy y diferencias finitas), **solo si las restringidas son rígidas** (I = H, H_u = g) |
| «La fórmula de §5 (a_i = b+ηv_i+ψ/N individual) no tiene el efecto expulsión» | **Confirmada**: usar p_f/(a_0+φ) para la holgada es falso (test negativo) |
| Respuesta de las holgadas decrece en g y en la masa de restringidas | **Confirmada**: ∂/∂g < 0. Cambia de signo si g > p_f/(φ(1−s)); en TFG2 (p_f=1, φ=0,05, g ≤ 5) el umbral es ≥ 20: no ocurre |
| Agregado con restringidas rígidas | `dL/du = [s p_f + a_0(1−s) g]/(a_0 + sφ)` |
| La fórmula del informe para el agregado con restringidas de **reserva ajustable** (TFG2) | **Corregida** (abajo): con ω_0<1 el informe subestima. En un equilibrio no lineal con G normal exacta (a_0=0,12, φ=0,05, s=0,4, g=0,5): dL/du = **3,968** frente a 3,114 de la fórmula rígida |

**Fórmula agregada general** (K tipos j, masa s_j, curvatura propia a_j, peso ω_j = γ_j²a_j/(B_j+γ_j²a_j), ω_j = 1 si está holgada, alivio g_j):

```
x     = p_f − φ L_u                        (choque efectivo de precio, tras el efecto expulsión)
I_j,u = ω_j x/a_j + (1−ω_j) g_j
Θ = Σ s_j ω_j/a_j      Ḡ = Σ s_j (1−ω_j) g_j
L_u = (Ḡ + Θ p_f) / (1 + φ Θ)              dI_j,u/du se obtiene sustituyendo x = p_f − φ L_u
```

- El término `1/(1+φΘ) < 1` es el **amortiguamiento por banco común**: con g_j = 0 el agregado es siempre menor que Θ p_f.
- Con una sola clase (s=0) coincide con el agente representativo de TFG2 (`a = a_0 + ψ/N`): el «potencial» de TFG2 es consistente con el equilibrio de
  empresas que toman r_L como dado.
- Caso rígido del informe: ω_j = 0 para las restringidas, ω_j = 1 para las holgadas.
- Verificada contra el equilibrio no lineal con `scipy` (error < 1e-6 en dL/du), comprobando λ>0, m_F interior y holgadas interiores.

**Límites:** s fijo localmente (la holgura es endógena y puede cruzar el codo con choques finitos); equilibrio parcial, precio fijo; B_j se toma en el equilibrio inicial.

## 3. Coordinación (`check_coordination.py`)

**Régimen interior** (pendiente p_f/a, a = b + η(v_0+v_pol) + ψ/N). Quitar v_pol sube la pendiente en
`Δ = η v_pol /(b + η v_0 + ψ/N)`; la fracción de a que es política es `η v_pol/a`, y `Δ = share/(1−share)`.

| Afirmación | Veredicto |
|---|---|
| Con la calibración de TFG2 (l. 1690–1694, v_0 = 0,05, v_pol = 1,44ρ²), A_P=2: Δ = 10 % | **Confirmada**: 10,3 % (a = 0,171, pendiente 5,848 → 6,452; coincide con l. 767/793) |
| Ídem A_P=0,2: Δ = 65 % | **Confirmada**: 64,5 % (v = 1,05, a = 0,255) |
| Columna «η·v_pol/a» (9 %, 39 %) del informe | **Confirmada** (9,4 %, 39,2 %), pero es el *peso de la política en a*, **no** la subida de la pendiente; las dos métricas difieren en share/(1−share) |
| «≈3 %» de FIRST_PRINCIPLES §6.4 | **Aritméticamente correcta con sus parámetros** (b=η=1, v=0,05, ψ/N=0,5: Δ=3,3 %), pero **no** son los de TFG2: con los de TFG2 es >3 veces mayor (refutada como cifra de TFG2, como dice el informe) |
| Ejemplos del informe η=5 → 14 %, η=10 y v=0,2 → 57 % | Aritmética a mano (no en script): son pesos en a; la subida correspondiente es 16,7 % y 133 % |

**Régimen restringido** (Prop. `fs-coordination`, l. 365–385):
- **`Gap_θ = −γκφ(z_0)/B_0 · (σ_F)_θ + (q/a²) a_θ`: Confirmada.** (Con G_m = −Q, G_σ = φ(z), m_0σ = φ/Q; B_0 = κQ(z_0).)
- Con capacidad vinculante: `I_θ = [γ² (−a_θ) I + γ κ φ(z) (−σ_θ)] / (B + γ² a)` > 0 y m_θ < 0 (**confirma** «inversión no decreciente, reserva no creciente»).
- **El canal σ_F actúa sin ningún cambio en v:** con a_θ = 0 (η v_pol sin cambio) I sube igualmente. Por tanto la cota `η v_pol/a` (solo mira v) **no acota** el efecto con restricción activa.
  El peso del canal σ_F en I_θ recorre (0,1) según S/A: no hay proporción fija entre los dos canales.
- **Sobre la pendiente I_u** con restricción activa: `∂I_u/∂a < 0` (el canal v siempre suma), pero `∂I_u/∂B = γ²(a g − p_f)/(B+γ²a)²`, de signo libre (el de a g − p_f). Como σ_F mueve
  B (z_θ = (m_θ − zσ_θ)/σ), el efecto total de la coordinación sobre la **pendiente** no tiene signo fijo (el test confirma que ni «+» ni «−» se sostienen en el dominio).

**¿Existe una cota que no dependa de la calibración? No.**
- Relativa: Δ = x/c con x = η v_pol > 0 y c = b + η v_0 + ψ/N > 0 libres; sup Δ = ∞ y para cada objetivo hay una calibración que lo alcanza (tests: ni 0,5 ni 0,03 valen en el dominio).
- La única cota es **de nivel**: ganancia de pendiente < p_f/(b + ψ/N), para cualquier (η, v_0, v_pol). Depende de b y ψ/N, y es la cota de «capacidad bancaria + coste del proyecto».
- Con restricción activa, ni siquiera ese límite aplica al canal σ_F de I (depende de κ, φ(z), σ_θ).

## 4. Estado de las afirmaciones del informe (resumen)

| Informe | Resultado |
|---|---|
| §2: álgebra de ω; «no hay script» | confirmada / script ahora existe |
| §2: caso rígido = IOPO; B acotado por κ_F | confirmada, con ω_min explícito |
| §2.3: `dI_s/du` con banco común | confirmada con restringidas rígidas; **corregida** para reserva ajustable (fórmula general arriba) |
| §2.4: 10 % / 65 % | confirmada (10,3 % / 64,5 %) |
| §2.4: canales fuera de v en régimen restringido | confirmada; sin cota calibration-free |
| 6.3 «coordinación solo por v» | refutada (confirma el informe) |

## 5. Advertencias

- La Prop. `fs-coordination` y todo el §3 asumen H, K, q, δ, μ_F fijos y a_θ, σ_θ < 0, como TFG2.
- El §2 usa el agente representativo para el régimen restringido (a incluye ψ/N); la heterogeneidad con banco común solo está en `check_aggregation.py`.
- Los números del equilibrio no lineal usan parámetros ilustrativos (no de TFG2); el test comprueba la fórmula, no un valor calibrado.
- El mapa a IOPO usa las ecuaciones tal como las cita el informe (p. 10–11); conviene que Literatura confirme la página con el PDF antes de citar en el paper.
- No he editado FIRST_PRINCIPLES, el informe del abogado del diablo ni los borradores.
