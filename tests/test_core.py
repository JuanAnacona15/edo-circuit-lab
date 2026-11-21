"""
tests/test_core.py — Pruebas de aceptación del motor matemático.

Ejecutar desde la raíz del proyecto con el entorno activado:

    python tests/test_core.py

Cada prueba cubre un criterio de aceptación del documento (sección 15) y
verifica un resultado numérico concreto. Si todo pasa, imprime "OK".
"""

import sys
from pathlib import Path

# Permite importar `core` sin instalar el paquete.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import sympy as sp

from core import (exact_equations, numerical_solver, rc_model, regression,
                  rl_model, symbolic_solver, validation)

PASOS = 0


def check(nombre, condicion):
    """Registra una prueba: imprime ✓/✗ y lanza AssertionError si falla."""
    global PASOS
    PASOS += 1
    estado = "✓" if condicion else "✗"
    print(f"  [{estado}] {nombre}")
    if not condicion:
        raise AssertionError(f"Prueba fallida: {nombre}")


# ── 1. Circuito RC ───────────────────────────────────────────────────────────
def test_rc():
    print("\nCircuito RC")
    V0, tau = 9.2128, 0.4896
    check("τ = R·C", rc_model.time_constant(1000.0, 0.0004896) - 0.4896 < 1e-6)
    check("V(0) = V₀", abs(rc_model.discharge_solution(0.0, V0, tau) - V0) < 1e-12)
    # V(τ) = V₀·e⁻¹ ≈ 0.3679·V₀
    check("V(τ) = V₀·e⁻¹",
          abs(rc_model.discharge_solution(tau, V0, tau) - V0 * np.exp(-1)) < 1e-9)
    check("descarga → 0 (límite)",
          rc_model.discharge_solution(1e6, V0, tau) < 1e-9)
    # Carga: V(5τ) ≈ 0.9933·E₀
    check("carga llega ≈99.3% a 5τ",
          abs(rc_model.charge_solution(5 * tau, 12.0, 0.0, tau) - 12.0 * (1 - np.exp(-5))) < 1e-9)


# ── 2. Circuito RL ───────────────────────────────────────────────────────────
def test_rl():
    print("\nCircuito RL")
    R, L, E0, i0 = 4.0, 2.0, 12.0, 0.0
    check("τ = L/R = 0.5 s", abs(rl_model.time_constant(R, L) - 0.5) < 1e-12)
    check("I∞ = E₀/R = 3 A", abs(rl_model.steady_state_current(E0, R) - 3.0) < 1e-12)
    check("i(0) = i₀", abs(rl_model.current_solution(0.0, R, L, E0, i0) - i0) < 1e-12)
    # i(t) = 3(1 - e^{-2t});  en t=0.5 → 3(1-e^{-1})
    check("i(t) = 3(1−e^(−2t))",
          abs(rl_model.current_solution(0.5, R, L, E0, i0) - 3 * (1 - np.exp(-1))) < 1e-9)


# ── 3. Ecuaciones exactas ────────────────────────────────────────────────────
def test_exact():
    print("\nEcuaciones exactas")
    # RL: no exacta, μ(t) = e^{(R/L)t}, y tras μ sí es exacta.
    p = exact_equations.preset_rl(4, 2, 12, 0)
    res = exact_equations.analyze(p["M"], p["N"], p["x"], p["y"],
                                  initial_condition=p["initial_condition"])
    check("RL no es exacta", res["is_exact"] is False)
    check("RL factor integrante μ(t) = e^(2t)",
          res["mu"] is not None and sp.simplify(res["mu"] - sp.exp(2 * p["x"])) == 0)
    check("RL exacta tras μ", res["is_exact_after"] is True)
    check("RL PVI = 3(1−e^(−2t))",
          res["solution_ivp"] and
          sp.simplify(res["solution_ivp"][0] - 3 * (1 - sp.exp(-2 * p["x"]))) == 0)

    # RC: no exacta, μ(t) = e^{t/τ}.
    p2 = exact_equations.preset_rc(0.4896, 9.2128)
    res2 = exact_equations.analyze(p2["M"], p2["N"], p2["x"], p2["y"],
                                   initial_condition=p2["initial_condition"])
    check("RC no es exacta", res2["is_exact"] is False)
    check("RC factor integrante μ(t) = e^(t/τ)",
          res2["mu"] is not None and
          sp.simplify(res2["mu"] - sp.exp(p2["x"] / 0.4896)) == 0)
    check("RC exacta tras μ", res2["is_exact_after"] is True)


# ── 4. Solución simbólica (SymPy) ────────────────────────────────────────────
def test_sympy():
    print("\nSymPy")
    t = sp.symbols("t", real=True)
    rl = symbolic_solver.solve_rl(4, 2, 12, 0)
    check("SymPy RL → 3(1−e^(−2t))",
          sp.simplify(rl["rhs"] - 3 * (1 - sp.exp(-2 * t))) == 0)
    rc = symbolic_solver.solve_rc(0.4896, 9.2128)
    # τ y V₀ son flotantes: comparamos numéricamente (la igualdad simbólica
    # exacta no es fiable con Float de precisión finita).
    f = sp.lambdify(t, rc["rhs"], "numpy")
    g = sp.lambdify(t, 9.2128 * sp.exp(-t / 0.4896), "numpy")
    tt = np.linspace(0.0, 2.0, 50)
    check("SymPy RC → 9.2128·e^(−t/0.4896)", np.max(np.abs(f(tt) - g(tt))) < 1e-9)


# ── 5. Solución numérica (SciPy / RK45) ──────────────────────────────────────
def test_scipy():
    print("\nSciPy (RK45)")
    num_rc = numerical_solver.simulate_rc_numerical(9.2128, 0.4896, 1.0, 0.02)
    ana_rc = rc_model.discharge_solution(num_rc["t"], 9.2128, 0.4896)
    check("RC numérica ≈ analítica (err < 1e-5)",
          np.max(np.abs(num_rc["y"] - ana_rc)) < 1e-5)

    num_rl = numerical_solver.simulate_rl_numerical(4, 2, 12, 0, 1.0, 0.02)
    ana_rl = rl_model.current_solution(num_rl["t"], 4, 2, 12, 0)
    check("RL numérica ≈ analítica (err < 1e-5)",
          np.max(np.abs(num_rl["y"] - ana_rl)) < 1e-5)


# ── 6. Regresión de los datos experimentales ─────────────────────────────────
def test_regression():
    print("\nRegresión")
    df, problemas = regression.load_dataset(
        path=str(Path(__file__).resolve().parents[1] / "data" / "Volts.csv"))
    check("50 mediciones cargadas", len(df) == 50)
    check("sin problemas de datos", len(problemas) == 0)
    fit = regression.fit_discharge(df["t"].to_numpy(), df["V"].to_numpy())
    check("τ ≈ 0.4896 s", abs(fit["tau"] - 0.4896) < 0.01)
    check("V₀ ≈ 9.2128 V", abs(fit["V0"] - 9.2128) < 0.1)
    check("R² ≈ 0.9991", abs(fit["r2"] - 0.9991) < 0.002)


# ── 7. Validación / comparación ──────────────────────────────────────────────
def test_validation():
    print("\nValidación")
    t = np.linspace(0, 1.0, 200)
    y_ana = rc_model.discharge_solution(t, 9.2128, 0.4896)
    y_num = numerical_solver.simulate_rc_numerical(9.2128, 0.4896, 1.0, 0.005)["y"]
    # resolver en la misma malla
    tn = np.linspace(0, 1.0, len(y_num))
    y_ana2 = rc_model.discharge_solution(tn, 9.2128, 0.4896)
    comp = validation.compare_analytical_numerical(tn, y_ana2, y_num)
    check("error absoluto pequeño", comp["max_abs"] < 1e-4)
    check("condición inicial correcta",
          validation.check_solution(lambda tt, y: rc_model.ode_rhs_discharge(y, 0.4896),
                                    tn, y_ana2, 9.2128, 0.0)["ic_ok"])


if __name__ == "__main__":
    test_rc()
    test_rl()
    test_exact()
    test_sympy()
    test_scipy()
    test_regression()
    test_validation()
    print(f"\n✅ {PASOS} pruebas pasadas.")
