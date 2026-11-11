"""F30 (Referee): ¿puede fallar de verdad test_remark_chain_I_u_ge_w_pf_a_gt_w_min_pf_a_gt_0 (theory/check_nesting.py, F27)?
Se cambia en el módulo un objeto del que depende el test y se comprueba que el test falla. Si alguna mutación pasara, el test no
estaría comprobando lo que dice. No modifica el archivo: solo los objetos ya cargados en memoria.
Uso: uv run python papers/p01-liquidity/audits/replication_2026-11-11_F30/mutate_f27.py
"""

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PATH = ROOT / "papers" / "p01-liquidity" / "theory" / "check_nesting.py"


def load():
    spec = importlib.util.spec_from_file_location("check_nesting_f30", PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


base = load()
base.test_remark_chain_I_u_ge_w_pf_a_gt_w_min_pf_a_gt_0()
print("OK    test original pasa")

gam, a, B, g, p_f, kap, q = base.gam, base.a, base.B, base.g, base.p_f, base.kap, base.q
MUTATIONS = {
    "peso sin el cuadrado de gamma (w = gamma a/(B + gamma a))": {"W": gam * a / (B + gam * a)},
    "repreciación con el signo cambiado (I_u = (gamma^2 p_f - B g)/(B + gamma^2 a))":
        {"SOL": {**base.SOL, base.I_u: (gam**2 * p_f - B * g) / (B + gam**2 * a)}},
    "B fuera del interior (B = kappa (1 + q) > kappa)": {"B_REACH": kap * (1 + q)},
    "peso del canal de precio en vez del de repreciación (I_u = w g + (1-w) p_f/a)":
        {"SOL": {**base.SOL, base.I_u: base.W * g + (1 - base.W) * p_f / a}},
}
fails = 0
for name, patch in MUTATIONS.items():
    mod = load()
    for k, v in patch.items():
        setattr(mod, k, v)
    try:
        mod.test_remark_chain_I_u_ge_w_pf_a_gt_w_min_pf_a_gt_0()
        print(f"FALLA la mutación no se detecta: {name}")
        fails += 1
    except (AssertionError, Exception) as e:  # ClaimFailed hereda de AssertionError; pytest.raises fallido da Failed
        print(f"OK    mutación detectada: {name} -> {type(e).__name__}")
sys.exit(1 if fails else 0)
