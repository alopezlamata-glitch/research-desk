"""Monte Carlo estándar de un estimador (skill mc-validate).

Formato fijo: sesgo, RMSE, cobertura del IC y potencia, con el T de los datos y con T/2. Regla de parada:
si la cobertura queda fuera de la banda, el estimador no es interpretable con ese T y no se aplica a los
datos reales.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
from scipy import stats


@dataclass(frozen=True)
class MCResult:
    T: int
    reps: int
    param: str
    true: float
    bias: float
    rmse: float
    coverage: float
    power: float  # rechazo de H0: θ = 0 al nivel alpha
    failed: int  # réplicas en las que el estimador no devolvió valores finitos

    def row(self) -> str:
        return (f"{self.param:>10} T={self.T:<5} sesgo={self.bias:+.4f} RMSE={self.rmse:.4f} "
                f"cobertura={self.coverage:.3f} potencia={self.power:.3f} fallos={self.failed}")


class CoverageOutOfBand(AssertionError):
    """La cobertura del IC está fuera de la banda aceptable: el estimador no se aplica con este T."""


def run(dgp: Callable[[int, np.random.Generator], object],
        estimator: Callable[[object], tuple[np.ndarray, np.ndarray]],
        true: dict[str, float], T: int, reps: int = 500, seed: int = 0, alpha: float = 0.05,
        ) -> list[MCResult]:
    """`dgp(T, rng)` simula datos; `estimator(datos)` devuelve (estimaciones, errores estándar) en el orden de `true`."""
    rng = np.random.default_rng(seed)
    names, theta = list(true), np.array(list(true.values()), dtype=float)
    est = np.full((reps, len(names)), np.nan)
    se = np.full((reps, len(names)), np.nan)
    for r in range(reps):
        try:
            b, s = estimator(dgp(T, rng))
            est[r], se[r] = np.asarray(b, float), np.asarray(s, float)
        except (np.linalg.LinAlgError, ValueError, FloatingPointError):
            continue
    z = stats.norm.ppf(1 - alpha / 2)
    out = []
    for j, name in enumerate(names):
        ok = np.isfinite(est[:, j]) & np.isfinite(se[:, j]) & (se[:, j] > 0)
        e, s = est[ok, j], se[ok, j]
        out.append(MCResult(
            T=T, reps=reps, param=name, true=theta[j],
            bias=float(e.mean() - theta[j]), rmse=float(np.sqrt(((e - theta[j]) ** 2).mean())),
            coverage=float((np.abs(e - theta[j]) <= z * s).mean()),
            power=float((np.abs(e) > z * s).mean()), failed=int((~ok).sum())))
    return out


def validate(dgp, estimator, true: dict[str, float], T: int, reps: int = 500, seed: int = 0,
             alpha: float = 0.05, band: tuple[float, float] = (0.92, 0.98)) -> list[MCResult]:
    """Ejecuta el MC con T y T/2; lanza CoverageOutOfBand si alguna cobertura (con T) cae fuera de `band`."""
    results = run(dgp, estimator, true, T, reps, seed, alpha) + run(dgp, estimator, true, T // 2, reps, seed + 1, alpha)
    bad = [r for r in results if r.T == T and not band[0] <= r.coverage <= band[1]]
    if bad:
        raise CoverageOutOfBand("; ".join(r.row() for r in bad))
    return results
