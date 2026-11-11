"""F32: ¿qué empresa tiene curvatura a = a_0 + phi? (main.tex:109-112 frente a Prop. 3(ii), main.tex:184-185).

Modelo de un solo tipo, restringido y con reserva interior, banco común r_L = r_f + phi L, L = I (masa 1).
El rendimiento neto de invertir es q - r_L (como en check_aggregation.py:144). Se comparan tres empresas:
  1. precio-aceptante en equilibrio: lambda = q - phi L - a_0 I, con L = I tras derivar;
  2. empresa única que INTERNALIZA r_L(I): max (q - r_f - phi I) I - a_0 I^2/2 -> lambda = q - (a_0 + 2 phi) I;
  3. la empresa de la §2.1 con a = a_0 + phi: lambda = q - a I.
No importa código del autor. Ejecutar: uv run python papers/p01-liquidity/audits/replication_2026-11-11_F32/check_representative.py
"""

import sympy as sp

p_f, gam, a0, phi, B, g = sp.symbols("p_f gamma a_0 phi B g", positive=True)
I_u, m_u, lam_u = sp.symbols("I_u m_u lambda_u")
results = []


def check(name, ok):
    results.append(ok)
    print(("OK    " if ok else "FALLA ") + name)


def solve(lam_eq):
    """Deriva respecto de u: lambda_u = lam_eq; -B m_u = gamma lambda_u; I_u + gamma m_u = g."""
    sol = sp.solve([lam_u - lam_eq, -B * m_u - gam * lam_u, I_u + gam * m_u - g], [I_u, m_u, lam_u], dict=True)[0]
    return sp.simplify(sol[I_u])


def eq_Iu(a):  # main.tex eq. (Iu)
    return (gam**2 * p_f + B * g) / (B + gam**2 * a)


taker = solve(p_f - phi * I_u - a0 * I_u)  # L_u = I_u en equilibrio
internal = solve(p_f - (a0 + 2 * phi) * I_u)
check("precio-aceptante en equilibrio = eq. (Iu) con a = a_0 + phi (Prop. 3(ii))", sp.simplify(taker - eq_Iu(a0 + phi)) == 0)
check("empresa que internaliza r_L(I) = eq. (Iu) con a = a_0 + 2 phi", sp.simplify(internal - eq_Iu(a0 + 2 * phi)) == 0)
check("empresa que internaliza != eq. (Iu) con a = a_0 + phi", sp.simplify(internal - eq_Iu(a0 + phi)) != 0)

# Objetivo de la §2.1 con a = a_0 + phi: el coste marginal (a_0 + phi) I iguala a_0 I + r_L - r_f con L = I,
# es decir, el de una empresa precio-aceptante; la que internaliza paga además phi I sobre las unidades inframarginales.
I = sp.Symbol("I", positive=True)
mc_sec21 = sp.diff((a0 + phi) / 2 * I**2, I)
mc_taker = a0 * I + phi * I
mc_internal = sp.diff(a0 / 2 * I**2 + phi * I * I, I)
check("coste marginal de la §2.1 (a = a_0 + phi) = el del precio-aceptante", sp.simplify(mc_sec21 - mc_taker) == 0)
check("coste marginal de la que internaliza = (a_0 + 2 phi) I", sp.simplify(mc_internal - (a0 + 2 * phi) * I) == 0)

# Prop. 3(iii) no depende de las masas: con s_j >= 0 (alguna > 0), w_j in (0, 1], a_j > 0, g_j >= 0, L_u > 0.
K = 3
s = sp.symbols(f"s1:{K + 1}", nonnegative=True)
w = sp.symbols(f"w1:{K + 1}", positive=True)
a = sp.symbols(f"a1:{K + 1}", positive=True)
gg = sp.symbols(f"g1:{K + 1}", nonnegative=True)
Theta = sum(s[j] * w[j] / a[j] for j in range(K))
Gbar = sum(s[j] * (1 - w[j]) * gg[j] for j in range(K))
num = Gbar + Theta * p_f
check("Theta >= 0 para cualquier masa (SymPy)", Theta.is_nonnegative is True)
check("1 + phi Theta > 0 para cualquier masa (SymPy)", (1 + phi * Theta).is_positive is True)
# 1 - w_j >= 0 con w_j <= 1: sustituir w_j = 1/(1+t_j), t_j >= 0
t = sp.symbols(f"t1:{K + 1}", nonnegative=True)
num_t = num.subs({w[j]: 1 / (1 + t[j]) for j in range(K)})
check("numerador Gbar + Theta p_f >= 0 para cualquier masa (SymPy)", sp.together(num_t).is_nonnegative is True)
check("con una sola masa positiva el numerador es > 0 (s_1 > 0, resto 0)",
      sp.together(num_t.subs({s[1]: 0, s[2]: 0})).subs(s[0], sp.Symbol("S", positive=True)).is_positive is True)

print(f"\n{sum(results)}/{len(results)} comprobaciones OK")
raise SystemExit(0 if all(results) else 1)
