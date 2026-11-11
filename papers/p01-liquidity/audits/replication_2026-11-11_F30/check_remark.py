"""F30 (Referee): comprobación independiente de la Observación tras el Corolario 1 (main.tex:156-159) y de las KKT (main.tex:113-117).
No importa theory/check_nesting.py: deriva todo desde el problema de la empresa.

1. KKT desde un objetivo explícito. El texto no escribe el objetivo. Con la penalización CUADRÁTICA del déficit de TFG2
   (l. 1365-1368: l(m) = delta m + (kappa/2) E[(xi-m)_+^2]) salen exactamente lambda = q - aI y kappa G(m) = delta + gamma lambda,
   con B = -kappa G'(m) = kappa Q(z). Con la penalización LINEAL habitual (kappa E[(xi-m)_+]) la KKT es kappa Q(z) = delta + gamma lambda
   y la "curvatura" es kappa phi(z)/sigma, que no está acotada por kappa: la cota (iii) cambiaría de fórmula.
2. Cadena I_u >= w p_f/a > w_min p_f/a > 0, con signos decididos simbólicamente (sin muestreo).
3. Mutaciones del test de F27: cada afirmación falsa cercana debe fallar.
Uso: uv run python papers/p01-liquidity/audits/replication_2026-11-11_F30/check_remark.py
"""

import sympy as sp

xi, m, mu, sig, kap, dlt, gam, a, q, H, lam, I = sp.symbols("xi m mu sigma kappa delta gamma a q H lambda I", real=True)
pos = dict(positive=True)
sig_p, kap_p = sp.Symbol("sigma", **pos), sp.Symbol("kappa", **pos)
z = sp.Symbol("z", real=True)
phi = sp.exp(-z**2 / 2) / sp.sqrt(2 * sp.pi)
Q = sp.erfc(z / sp.sqrt(2)) / 2
ok = []


def check(name, cond):
    ok.append(bool(cond))
    print(("OK   " if cond else "FALLA") + " " + name)


# ---------------------------------------------------------------- 1. KKT desde el objetivo
# Formas cerradas con xi ~ N(mu, sig^2), z = (m - mu)/sig (TFG2 l. 1364-1366), comprobadas aquí contra su definición:
G = sig_p * (phi - z * Q)                      # E[(xi-m)_+]
S2 = sig_p**2 * ((1 + z**2) * Q - z * phi)     # E[(xi-m)_+^2]
u = sp.Symbol("u", real=True)                  # xi = mu + sig u
dens = sp.exp(-u**2 / 2) / sp.sqrt(2 * sp.pi)
for zv in (sp.Rational(-3, 2), 0, sp.Rational(7, 10)):
    s3 = sp.Rational(3, 10)
    G_int = sp.Integral(s3 * (u - zv) * dens, (u, zv, sp.oo)).evalf(30)
    S2_int = sp.Integral(s3**2 * (u - zv) ** 2 * dens, (u, zv, sp.oo)).evalf(30)
    check(f"forma cerrada de G y E[(xi-m)_+^2] en z = {zv}",
          abs(G.subs({z: zv, sig_p: sp.Rational(3, 10)}).evalf(30) - G_int) < 1e-20
          and abs(S2.subs({z: zv, sig_p: sp.Rational(3, 10)}).evalf(30) - S2_int) < 1e-20)
dz_dm = 1 / sig_p
check("d/dm (1/2) E[(xi-m)_+^2] = -G(m)", sp.simplify(sp.diff(S2 / 2, z) * dz_dm + G) == 0)
check("G'(m) = -Q(z)", sp.simplify(sp.diff(G, z) * dz_dm + Q) == 0)

# Lagrangiano: max q I - a I^2/2 - delta m - (kappa/2) E[(xi-m)_+^2] + lambda (H - I - gamma m)
Lag_I = q - a * I - lam                                          # d/dI
Lag_m = -dlt + kap_p * G - gam * lam                             # d/dm, usando d/dm (kap/2) S2 = -kap G
check("KKT de I: lambda = q - a I (main.tex:114)", sp.solve(Lag_I, lam)[0] == q - a * I)
check("KKT de m: kappa G(m) = delta + gamma lambda (main.tex:114)", sp.simplify(sp.solve(Lag_m, lam)[0] - (kap_p * G - dlt) / gam) == 0)
B_quad = -sp.diff(kap_p * G, z) * dz_dm
check("con penalización cuadrática, B = -kappa G'(m) = kappa Q(z) (main.tex:117)", sp.simplify(B_quad - kap_p * Q) == 0)
# Alternativa lineal: l(m) = delta m + kappa E[(xi-m)_+]; KKT kappa Q(z) = delta + gamma lambda; B = -d/dm (kappa Q) = kappa phi/sigma
B_lin = -sp.diff(kap_p * Q, z) * dz_dm
check("con penalización lineal, B = kappa phi(z)/sigma (otra fórmula)", sp.simplify(B_lin - kap_p * phi / sig_p) == 0)
check("con penalización lineal, B puede superar kappa (sigma = 0.2, z = 0)", (B_lin / kap_p).subs({z: 0, sig_p: sp.Rational(1, 5)}) > 1)

# ---------------------------------------------------------------- 2. Diferenciación de las KKT y cadena de la Observación
pf, g, Bs, k, gm, aa = sp.symbols("p_f g B kappa_F gamma a", positive=True)
Iu, mu_, lu = sp.symbols("I_u m_u lambda_u")
sol = sp.solve([lu - (pf - aa * Iu), -Bs * mu_ - gm * lu, Iu + gm * mu_ - g], [Iu, mu_, lu], dict=True)[0]
w = gm**2 * aa / (Bs + gm**2 * aa)
w_min = gm**2 * aa / (k + gm**2 * aa)
check("I_u = (gamma^2 p_f + B g)/(B + gamma^2 a) (eq. Iu)", sp.simplify(sol[Iu] - (gm**2 * pf + Bs * g) / (Bs + gm**2 * aa)) == 0)
gap1 = sp.factor(sol[Iu] - w * pf / aa)
check("I_u - w p_f/a = B g/(B + gamma^2 a)", sp.simplify(gap1 - Bs * g / (Bs + gm**2 * aa)) == 0)
g0 = sp.Symbol("g0", nonnegative=True)
check("1.ª desigualdad >= 0 con g >= 0 (decidido por SymPy)", sp.simplify(gap1.subs(g, g0)).is_nonnegative is True)
check("1.ª desigualdad es igualdad con g = 0", sp.simplify(gap1.subs(g, 0)) == 0)
t = sp.Symbol("t", positive=True)  # B = k/(1+t), t > 0  <=>  B en (0, k): óptimo interior
gap2 = sp.factor(((w - w_min) * pf / aa).subs(Bs, k / (1 + t)))
check("2.ª desigualdad > 0 en todo el interior B en (0, kappa_F) (simbólico)", gap2.is_positive is True)
check("2.ª desigualdad se anula en B = kappa_F (borde excluido)", sp.simplify(((w - w_min) * pf / aa).subs(Bs, k)) == 0)
check("3.ª: w_min p_f/a > 0", (w_min * pf / aa).is_positive is True)
a_any = sp.Symbol("a_any", real=True)
check("sin a > 0 la 3.ª no está decidida (hace falta declarar a > 0)",
      (gm**2 * a_any / (k + gm**2 * a_any) * pf / a_any).is_positive is not True)

# ---------------------------------------------------------------- 3. Mutaciones: afirmaciones cercanas y falsas deben fallar
gneg = sp.Symbol("gneg", negative=True)
check("mutación: con g < 0 la 1.ª desigualdad es falsa", sp.simplify(gap1.subs(g, gneg)).is_negative is True)
check("mutación: '>' estricto en la 1.ª con g = 0 es falso", not (sp.simplify(gap1.subs(g, 0)) > 0))
check("mutación: w > w_min falla fuera del interior (B > kappa_F)",
      sp.factor(((w - w_min) * pf / aa).subs(Bs, k * (1 + t))).is_negative is True)
check("mutación: con g < 0 grande, I_u < 0 (el signo de H1 depende de g >= 0)",
      sol[Iu].subs({pf: 1, gm: 1, aa: sp.Rational(171, 1000), Bs: 3, g: -2}) < 0)

print(f"\n{sum(ok)}/{len(ok)} comprobaciones OK")
raise SystemExit(0 if all(ok) else 1)
