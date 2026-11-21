"""
core/exact_equations.py — Ecuaciones exactas y factores integrantes
====================================================================

Implementa el MÉTODO DE ECUACIONES EXACTAS, que es la técnica asignada en
el proyecto de aula. Trabaja con una EDO escrita en forma diferencial:

        M(x, y)·dx + N(x, y)·dy = 0                           (1)

--------------------------------------------------------------------------
1) CRITERIO DE EXACTITUD
--------------------------------------------------------------------------
La ecuación (1) es EXACTA si existe una función F(x, y) tal que:

        ∂F/∂x = M      y      ∂F/∂y = N

En ese caso la solución general es la curva de nivel  F(x, y) = C.

Por el teorema de Clairaut (igualdad de las derivadas cruzadas de F), una
condición NECESARIA de exactitud es:

        ∂M/∂y = ∂N/∂x                                        (2)

En nuestro dominio (simplemente conexo) la condición (2) también es
SUFICIENTE: si se cumple, la ecuación es exacta.

--------------------------------------------------------------------------
2) FACTOR INTEGRANTE (convierte una ecuación no exacta en exacta)
--------------------------------------------------------------------------
Si (1) NO es exacta, se busca una función μ que, al multiplicar toda la
ecuación, la vuelva exacta:

        μ·M dx + μ·N dy = 0

Imponiendo la condición (2) a la ecuación multiplicada:

        ∂(μM)/∂y = ∂(μN)/∂x

Cuando μ depende de UNA SOLA variable surgen dos casos sencillos:

    CASO 1 — μ = μ(x):  si  (M_y - N_x)/N  depende SOLO de x, entonces
            μ(x) = exp( ∫ (M_y - N_x)/N dx )                 (3a)

    CASO 2 — μ = μ(y):  si  (N_x - M_y)/M  depende SOLO de y, entonces
            μ(y) = exp( ∫ (N_x - M_y)/M dy )                 (3b)

Si ninguno de los dos cocientes depende de una única variable, NO se puede
encontrar factor integrante por estos dos criterios (se informa al usuario
en lugar de inventar un resultado).

--------------------------------------------------------------------------
3) CONSTRUCCIÓN DE LA FUNCIÓN POTENCIAL F(x, y)
--------------------------------------------------------------------------
Con la ecuación ya exacta (original o tras multiplicar por μ):

        F(x, y) = ∫ M̃(x, y) dx + g(y)                        (4)

donde g(y) es la "constante de integración" que depende de y. Derivando
(4) respecto a y e igualando a Ñ:

        ∂F/∂y = ∂/∂y ∫M̃ dx + g'(y) = Ñ
        g'(y) = Ñ - ∂/∂y ∫M̃ dx
        g(y)  = ∫ [ Ñ - ∂/∂y ∫M̃ dx ] dy

La solución general es  F(x, y) = C. Si es posible despejar y, se obtiene
la solución explícita; si no, se deja en forma implícita.

--------------------------------------------------------------------------
4) CONEXIÓN CON LOS CIRCUITOS DEL PROYECTO
--------------------------------------------------------------------------
Circuito RC (descarga):  dV/dt + V/τ = 0  →  (V/τ)·dt + 1·dV = 0
    M(t, V) = V/τ,  N(t, V) = 1  →  no exacta, μ(t) = e^{t/τ}

Circuito RL:  L·di/dt + R·i = E₀  →  (R·i - E₀)·dt + L·di = 0
    M(t, i) = R·i - E₀,  N(t, i) = L  →  no exacta, μ(t) = e^{(R/L)t}
"""

from __future__ import annotations

import sympy as sp


# ─────────────────────────────────────────────────────────────────────────────
# Núcleo genérico del método
# ─────────────────────────────────────────────────────────────────────────────


def _fmt_sol_list(sols):
    """Convierte una lista de soluciones simbólicas a (texto, tipo_render).

    Devuelve ('...', 'latex') si hay soluciones y ('...', 'text') si no se
    pudo despejar la variable dependiente.
    """
    if not sols:
        return "No se puede despejar y(x) explícitamente; la solución queda en forma implícita.", "text"
    return " ; ".join(sp.latex(s) for s in sols), "latex"


def analyze(M, N, x, y, initial_condition=None) -> dict:
    """Aplica el método de ecuaciones exactas a M·dx + N·dy = 0.

    Parámetros:
        M, N              : expresiones simbólicas de SymPy en x e y
        x, y              : símbolos de SymPy (x = variable independiente)
        initial_condition : tupla (x0, y0) opcional para resolver el PVI

    Devuelve un diccionario con los resultados de CADA paso:
        is_exact         : bool, ¿la ecuación original es exacta?
        mu               : factor integrante (None si no se encontró)
        mu_type          : 'x', 'y' o None
        M_tilde, N_tilde : coeficientes tras multiplicar por μ
        is_exact_after   : ¿la ecuación transformada es exacta?
        F                : función potencial F(x, y)
        solution_implicit: igualdad F(x, y) = C
        solution_explicit: lista de soluciones y(x) si se pudo despejar
        solution_ivp     : lista de soluciones con la condición inicial
        steps            : lista de pasos {title, detail, kind} para mostrar
        errors           : lista de mensajes de error (vacía si todo OK)
    """
    M = sp.sympify(M)
    N = sp.sympify(N)

    steps: list[dict] = []
    errors: list[str] = []

    def add(title: str, detail, kind: str = "latex"):
        """Registra un paso. kind='latex' convierte a LaTeX; 'text' lo deja tal cual."""
        if kind == "latex":
            try:
                detail = sp.latex(sp.sympify(detail))
            except Exception:
                kind = "text"
        steps.append({"title": title, "detail": str(detail), "kind": kind})

    # --- Paso 1 y 2: identificar M, N y sus derivadas parciales ------------
    add("M(x, y)", M)
    add("N(x, y)", N)
    My = sp.diff(M, y)      # ∂M/∂y
    Nx = sp.diff(N, x)      # ∂N/∂x
    add("∂M/∂y", My)
    add("∂N/∂x", Nx)

    # --- Paso 3: criterio de exactitud -------------------------------------
    is_exact = bool(sp.simplify(My - Nx) == 0)

    if is_exact:
        add("Criterio de exactitud",
            "∂M/∂y = ∂N/∂x — la ecuación SÍ es exacta.", kind="text")
        mu = None
        mu_type = None
        M_tilde, N_tilde = M, N
    else:
        add("Criterio de exactitud",
            "∂M/∂y ≠ ∂N/∂x — la ecuación NO es exacta.", kind="text")

        # --- Paso 4: buscar factor integrante ------------------------------
        mu, mu_type, q = _integrating_factor(M, N, My, Nx, x, y, steps, errors)

        if mu is None:
            M_tilde, N_tilde = M, N
        else:
            if mu_type == "x":
                add(f"Factor integrante μ({x})", mu)
            else:
                add(f"Factor integrante μ({y})", mu)
            M_tilde = sp.simplify(mu * M)
            N_tilde = sp.simplify(mu * N)
            add("M̃ = μ·M", M_tilde)
            add("Ñ = μ·N", N_tilde)

            # --- Paso 5: verificar que la transformada es exacta -----------
            if bool(sp.simplify(sp.diff(M_tilde, y) - sp.diff(N_tilde, x)) == 0):
                add("Verificación tras μ",
                    "∂M̃/∂y = ∂Ñ/∂x — ahora SÍ es exacta.", kind="text")
            else:
                errors.append(
                    "El factor integrante no logró que la ecuación fuera exacta."
                )

    # --- Paso 6: función potencial F(x, y) ---------------------------------
    F_parcial = sp.integrate(M_tilde, x)          # ∫M̃ dx
    dF_parcial_dy = sp.diff(F_parcial, y)
    g_prima = sp.simplify(N_tilde - dF_parcial_dy)
    g = sp.integrate(g_prima, y)
    F = sp.simplify(F_parcial + g)

    add("∫M̃ dx", F_parcial)
    add("g′(y) = Ñ − ∂/∂y(∫M̃ dx)", g_prima)
    add("Función potencial F(x, y)", F)

    # --- Paso 7: solución general (implícita y explícita) -------------------
    C = sp.Symbol("C")
    sol_implicita = sp.Eq(F, C)
    add("Solución implícita F(x, y) = C", sol_implicita)

    sol_explicita = sp.solve(sol_implicita, y)
    texto_explicita, kind_explicita = _fmt_sol_list(sol_explicita)
    add("Solución explícita y(x)", texto_explicita, kind=kind_explicita)

    # --- Paso 8: problema de valor inicial (si se pide) ---------------------
    sol_ivp = []
    if initial_condition is not None:
        x0, y0 = initial_condition
        C_val = F.subs({x: x0, y: y0})          # C = F(x0, y0)
        add("C = F(x₀, y₀)", C_val)
        sol_ivp = sp.solve(sp.Eq(F, C_val), y)
        texto_ivp, kind_ivp = _fmt_sol_list(sol_ivp)
        add("Solución del PVI", texto_ivp, kind=kind_ivp)

    return {
        "M": M, "N": N, "x": x, "y": y,
        "My": My, "Nx": Nx,
        "is_exact": is_exact,
        "mu": mu, "mu_type": mu_type,
        "M_tilde": M_tilde, "N_tilde": N_tilde,
        "is_exact_after": bool(sp.simplify(sp.diff(M_tilde, y) - sp.diff(N_tilde, x)) == 0),
        "F": F,
        "solution_implicit": sol_implicita,
        "solution_explicit": sol_explicita,
        "solution_ivp": sol_ivp,
        "steps": steps,
        "errors": errors,
    }


def _integrating_factor(M, N, My, Nx, x, y, steps, errors):
    """Busca el factor integrante por los dos casos especiales.

    CASO 1: (M_y - N_x)/N depende solo de x  →  μ(x) = exp(∫·dx)
    CASO 2: (N_x - M_y)/M depende solo de y  →  μ(y) = exp(∫·dy)

    Devuelve (μ, tipo, cociente) o (None, None, None) si no se encontró.
    """
    if sp.simplify(N) == 0:
        q1 = None
        errors.append("N(x,y) es cero; no se puede aplicar el caso μ(x).")
    else:
        q1 = sp.simplify((My - Nx) / N)

    if sp.simplify(M) == 0:
        q2 = None
    else:
        q2 = sp.simplify((Nx - My) / M)

    # "depende solo de x" ⇔ no contiene el símbolo y (una constante también
    # califica, y se trata como f(x)).
    if q1 is not None and not q1.has(y):
        steps.append({
            "title": "Caso 1: (M_y − N_x)/N depende solo de x",
            "detail": sp.latex(q1), "kind": "latex",
        })
        mu = sp.exp(sp.integrate(q1, x))
        return sp.simplify(mu), "x", q1

    if q2 is not None and not q2.has(x):
        steps.append({
            "title": "Caso 2: (N_x − M_y)/M depende solo de y",
            "detail": sp.latex(q2), "kind": "latex",
        })
        mu = sp.exp(sp.integrate(q2, y))
        return sp.simplify(mu), "y", q2

    errors.append(
        "No se encontró factor integrante por los dos criterios (μ(x) o μ(y))."
    )
    return None, None, None


# ─────────────────────────────────────────────────────────────────────────────
# Ecuaciones predeterminadas de los circuitos del proyecto
# ─────────────────────────────────────────────────────────────────────────────


def preset_rc(tau=0.4896, V0=9.2128) -> dict:
    """Ecuación exacta correspondiente al circuito RC en descarga.

    dV/dt + V/τ = 0  →  (V/τ)·dt + 1·dV = 0
    M(t, V) = V/τ, N(t, V) = 1, con PVI V(0) = V₀.
    """
    t, V = sp.symbols("t V", real=True)
    tau_s = sp.sympify(tau)
    return {
        "M": V / tau_s, "N": sp.Integer(1),
        "x": t, "y": V,
        "x_label": "t (s)", "y_label": "V (V)",
        "initial_condition": (0, sp.sympify(V0)),
        "nombre": "Circuito RC (descarga)",
    }


def preset_rl(R=4, L=2, E0=12, i0=0) -> dict:
    """Ecuación exacta correspondiente al circuito RL.

    L·di/dt + R·i = E₀  →  (R·i - E₀)·dt + L·di = 0
    M(t, i) = R·i - E₀, N(t, i) = L, con PVI i(0) = i₀.
    """
    t, i = sp.symbols("t i", real=True)
    R_s, L_s, E0_s = sp.sympify(R), sp.sympify(L), sp.sympify(E0)
    return {
        "M": R_s * i - E0_s, "N": L_s,
        "x": t, "y": i,
        "x_label": "t (s)", "y_label": "i (A)",
        "initial_condition": (0, sp.sympify(i0)),
        "nombre": "Circuito RL",
    }


def parse_MN(M_str: str, N_str: str, x_str: str = "x", y_str: str = "y"):
    """Convierte texto del usuario en expresiones simbólicas de SymPy.

    Devuelve (M, N, x, y). Lanza ValueError con un mensaje claro si el texto
    no es una expresión válida.
    """
    x, y = sp.symbols(f"{x_str} {y_str}", real=True)
    try:
        M = sp.sympify(M_str, locals={x_str: x, y_str: y})
        N = sp.sympify(N_str, locals={x_str: x, y_str: y})
    except Exception as exc:  # sympify lanza SympifyError o SyntaxError
        raise ValueError(f"No se pudo interpretar la expresión: {exc}") from exc
    return M, N, x, y
