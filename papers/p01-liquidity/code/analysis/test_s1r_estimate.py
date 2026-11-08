"""Tests de F15: árbol V3s sin la regla (b), script de análisis `01_s1r_estimate.py` y su réplica en R, con datos simulados (DGP de
F9). Ninguno estima nada con la inversión real: el panel lleva siempre la inversión simulada."""

import importlib
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent / "mc")]
import f9_power
import s1r_lp
from integrity import PARITY_RTOL

est_mod = importlib.import_module("01_s1r_estimate")
PARQUET = HERE.parents[1] / "data" / "clean" / "stage1r_us.parquet"
R_SCRIPT = HERE.parent / "replication_r" / "s1r_replication.R"
needs_data = pytest.mark.skipif(not PARQUET.exists(), reason="ejecuta build_stage1r_us.py (el parquet no se versiona)")
DOF = 100
T = 1.8  # |t| que da p unilateral < 0,05 con 100 g.l.


def test_h1_verdict_has_no_rule_b():
    assert s1r_lp.h1_verdict(-T, 1.0, DOF) == "confirma"
    assert s1r_lp.h1_verdict(T, 1.0, DOF) == "refuta_a"
    assert s1r_lp.h1_verdict(0.0, 0.01, DOF) == "no_concluyente"  # con (b) y δ = 0,1 habría sido 'refuta_b'
    assert s1r_lp.h1_verdict(-1.0, 1.0, DOF) == "no_concluyente"


def fake(b_lin: float, b_C: float, b_C_nov: float, b_lin_nov: float = 0.0) -> pd.DataFrame:
    """Estimaciones construidas a mano (ee = 1): solo importan los t."""
    rows = [("s1r_lin", "b_lin", b_lin), ("s1r_liq", "b_C", b_C), ("s1r_liq", "b_U", -5.0), ("s1r_liq_nov", "b_C", b_C_nov),
            ("s1r_liq_nov", "b_U", -5.0), ("r1r_lags4", "b_C", 5.0)]
    est = pd.DataFrame(rows, columns=["spec_id", "term", "estimate"]).assign(std_error=1.0, dof=DOF)
    return est[est_mod.COLUMNS]


@pytest.mark.parametrize("b_lin, b_C, b_C_nov, expected", [
    (-0.5, -T, -T, "h0_falla"),                   # puerta H0: aunque H1 confirme en las dos muestras
    (+T, +T, +T, "h0_falla"),                     # sin H0 tampoco se refuta
    (-T, -T, -T, "confirma"),                     # V3s: completa y sin Volcker confirman
    (-T, -T, -1.0, "no_concluyente"),             # no se sostiene sin Volcker
    (-T, -T, +T, "no_concluyente"),               # completa confirma y sin Volcker β̂_C > 0 significativo
    (-T, +T, -T, "refuta_a"),                     # (a) solo con la muestra completa, sea lo que sea sin Volcker
    (-T, +T, +T, "refuta_a"),
    (-T, -1.0, -T, "no_concluyente"),             # la completa no decide: sin Volcker no rescata
    (-T, 0.0, +T, "no_concluyente"),              # (a) sin Volcker no refuta
])
def test_v3s_tree_on_hand_built_estimates(b_lin, b_C, b_C_nov, expected):
    assert est_mod.verdict(fake(b_lin, b_C, b_C_nov)) == expected


def test_h0_only_uses_full_sample():
    # un b_lin sin Volcker no existe en el árbol: cambiar otras filas no mueve la puerta H0
    assert est_mod.verdict(fake(-T, -T, -T)) == est_mod.verdict(fake(-T, -T, -T, b_lin_nov=+9.0)) == "confirma"


@pytest.fixture(scope="module")
def sim():
    """Panel real de F7 con la inversión sustituida por la simulada del DGP de F9 (β_C ≠ β_U, ruido het_eps)."""
    df = f9_power.panel()
    smp = f9_power.samples(df)
    rr = {k: smp[k] for k in ("RR", "RR_noV")}
    dgp = f9_power.DGP(df, "rr_shock", rr, -6.0, -1.0, "het_eps", specs=("aum",))
    level = dgp.level(np.random.default_rng(20261108))
    return df.assign(inv=np.exp(level / 100)), dgp, level, rr


@needs_data
def test_samples_states_and_robustness_designs(sim):
    df = sim[0]
    smp = est_mod.samples(df)
    assert {k: len(v) for k, v in smp.items()} == {"full": 146, "nov": 133, "from1971q3": 136}
    D = est_mod.states(df["s_lag"], smp["full"])
    assert int(D["median"].loc[smp["full"]].sum()) == 73 and int(D["median"].loc[smp["nov"]].sum()) == 62  # SAMPLE_COUNTS_S1R.md
    assert int(D["q25"].loc[smp["full"]].sum()) == 37
    F = D["logistic"].loc[smp["full"]]
    assert F.between(0, 1).all() and ((F > 0.5) == (D["median"].loc[smp["full"]] == 1)).all()
    est = est_mod.estimates(df)
    k = est.groupby("spec_id")["dof"].first()
    assert k["s1r_lin"] == 146 - 32 and k["s1r_liq"] == 146 - 34 and k["s1r_liq_nov"] == 133 - 34
    assert k["r1r_from1971q3"] == 136 - 34 and k["r1r_lags4"] == 146 - 42
    assert k["r1r_state_q25"] == k["r1r_state_logistic"] == 146 - 34
    assert est[["estimate", "std_error"]].notna().all().all()


@needs_data
def test_analysis_script_equals_the_mc_estimator(sim):
    df, dgp, level, rr = sim
    est = est_mod.estimates(df, est_mod.CONFIRMATORY)
    y = s1r_lp.ybar(level / 100)
    ctrl = dgp.ctrl.assign(dlinv=level.diff())
    X = {(sp, m): s1r_lp.design(dgp.eps, dgp.D, ctrl, dgp.all_rows, m, *f9_power.SPECS[sp]) for sp in ("aum",) for m in ("lin", "liq")}
    for sid, model, sample in (("s1r_lin", "lin", "RR"), ("s1r_liq", "liq", "RR"), ("s1r_liq_nov", "liq", "RR_noV")):
        b, se, dof = f9_power.estimate(dgp.data(y, X, rr[sample], "aum"), model, f9_power.TESTED_SE)
        for i, name in enumerate(s1r_lp.TERMS[model]):
            assert est_mod.term(est, sid, name) == pytest.approx((b[i], se[i], dof), rel=1e-10)


@needs_data
@pytest.mark.skipif(shutil.which("Rscript") is None, reason="Rscript no está en el PATH")
def test_python_r_parity_on_simulated_data(sim, tmp_path):
    df = sim[0]
    cols = ["rr_shock", "s_lag", "in_rr_sample", "inv", "gdp", "defl", "ffr"]
    panel_csv, r_csv = tmp_path / "panel.csv", tmp_path / "estimates_r.csv"
    df[cols].assign(quarter=df.index.astype(str), in_rr_sample=df["in_rr_sample"].astype(int)).to_csv(panel_csv, index=False)
    subprocess.run(["Rscript", str(R_SCRIPT), str(panel_csv), str(r_csv)], check=True, capture_output=True)
    py = est_mod.estimates(df, est_mod.CONFIRMATORY).set_index(["spec_id", "term"])
    r = pd.read_csv(r_csv).set_index(["spec_id", "term"])
    assert set(py.index) == set(r.index) and len(py) == 32 + 34 + 34
    r = r.loc[py.index]
    for col in ("estimate", "std_error"):
        tol = PARITY_RTOL * np.maximum(1.0, py[col].abs())
        assert ((py[col] - r[col]).abs() <= tol).all(), (py[col] - r[col]).abs().max()
    assert (py["dof"] == r["dof"]).all()


@needs_data
def test_shock_diagnostics_reproduce_f13(sim):
    md = est_mod.shock_diagnostics(sim[0])  # no usa la inversión
    full, nov = (ln for ln in md.splitlines() if ln.startswith(("| completa", "| sin Volcker")))
    assert "| 146 | 73 | 73 |" in full and "| 16.78 | 0.158 | 1.07 | (12, 133) | 0.391 |" in full  # f13_shock_diagnostics.md:7
    assert "| 133 | 62 | 71 |" in nov and "| 22.86 | 0.029 | 1.66 | (12, 120) | 0.085 |" in nov  # f13_shock_diagnostics.md:8
