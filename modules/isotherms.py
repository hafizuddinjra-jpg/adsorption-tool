"""Adsorption isotherms and the single-stage batch material balance.

An isotherm links the two phases at equilibrium: given a fluid concentration c,
it tells you the loading q held on the solid. Geankoplis notation is used here.

Units used across the whole tool:
    c, c_F   fluid concentration            mg/L
    q, q_F   loading on the adsorbent       mg adsorbate per g adsorbent (mg/g)
    S        volume of solution             L
    M        mass of adsorbent              g

This file contains no Streamlit code, so the Batch Adsorption Calculation
section can import these functions directly.
"""

from typing import Callable

import numpy as np
from scipy.optimize import brentq


def linear(c, K):
    """Linear isotherm (Henry's law): q = K * c.

    Holds for dilute solutions, where the adsorbent is still far from full.

    Args:
        c: Fluid concentration in mg/L. A single number or a NumPy array.
        K: Linear (Henry's law) constant in L/g. Must be above 0.

    Returns:
        Equilibrium loading q in mg/g, with the same shape as c.
    """
    return K * np.asarray(c, dtype=float)


def freundlich(c, K, n):
    """Freundlich isotherm: q = K * c^n.

    Args:
        c: Fluid concentration in mg/L. A single number or a NumPy array.
        K: Freundlich constant in (mg/g)(L/mg)^n.
        n: Freundlich exponent (dimensionless). Must be above 0.

    Returns:
        Equilibrium loading q in mg/g, with the same shape as c.
    """
    return K * np.power(np.asarray(c, dtype=float), n)


def langmuir(c, q0, K):
    """Langmuir isotherm in Geankoplis form: q = q0 * c / (K + c).

    Args:
        c: Fluid concentration in mg/L. A single number or a NumPy array.
        q0: Maximum (monolayer) loading in mg/g.
        K: Concentration at which q = q0 / 2, in mg/L. Must be above 0.

    Returns:
        Equilibrium loading q in mg/g, with the same shape as c.
    """
    c = np.asarray(c, dtype=float)
    return q0 * c / (K + c)


def batch_operating_line(c, c_F, S, M, q_F=0.0):
    """Operating line for one batch stage: q = q_F + (S/M)(c_F - c).

    This is the material balance q_F*M + c_F*S = q*M + c*S rearranged for q.
    Every point on the line conserves solute, and its slope is -S/M.

    Args:
        c: Fluid concentration in mg/L. A single number or a NumPy array.
        c_F: Feed concentration in mg/L.
        S: Volume of solution in L. Must be above 0.
        M: Mass of adsorbent in g. Must be above 0.
        q_F: Initial loading on the adsorbent in mg/g (usually 0).

    Returns:
        Loading q in mg/g, with the same shape as c.
    """
    return q_F + (S / M) * (c_F - np.asarray(c, dtype=float))


def solve_batch_equilibrium(
    c_F, S, M, isotherm: Callable[[float], float], q_F=0.0
) -> tuple[float, float]:
    """Find where the isotherm crosses the batch operating line.

    The crossing is the only point that satisfies both the material balance and
    equilibrium. The isotherm rises with c while the operating line falls, so
    their difference always increases and there is exactly one crossing. It lies
    between c = 0 and the point where the operating line reaches q = 0.

    Args:
        c_F: Feed concentration in mg/L.
        S: Volume of solution in L. Must be above 0.
        M: Mass of adsorbent in g. Must be above 0.
        isotherm: Function that takes c in mg/L and returns q in mg/g.
        q_F: Initial loading on the adsorbent in mg/g (usually 0).

    Returns:
        The equilibrium (c, q), with c in mg/L and q in mg/g.

    Raises:
        ValueError: If the inputs fail validate_batch_inputs.
    """
    problems = validate_batch_inputs(c_F, S, M, q_F)
    if problems:
        raise ValueError(" ".join(problems))

    def gap(c):
        return isotherm(c) - batch_operating_line(c, c_F, S, M, q_F)

    c_upper = c_F + q_F * M / S

    # With a lot of adsorbent the answer can be a tiny c, such as 1e-12 mg/L, where
    # a Freundlich curve is almost vertical. The default absolute tolerance would
    # stop far too early there, so the tolerance is set relative to c instead.
    c_eq = brentq(gap, 0.0, c_upper, xtol=1e-300, rtol=1e-14, maxiter=2000)
    return float(c_eq), float(isotherm(c_eq))


def percent_removal(c_F, c):
    """Percentage of the solute removed: (c_F - c) / c_F * 100.

    Args:
        c_F: Feed concentration in mg/L. Must be above 0.
        c: Final fluid concentration in mg/L.

    Returns:
        Removal in percent.
    """
    return (c_F - c) / c_F * 100.0


def validate_batch_inputs(c_F, S, M, q_F=0.0) -> list[str]:
    """Check the inputs for a batch calculation before any division happens.

    Args:
        c_F: Feed concentration in mg/L.
        S: Volume of solution in L.
        M: Mass of adsorbent in g.
        q_F: Initial loading on the adsorbent in mg/g.

    Returns:
        A list of friendly messages, one per problem. Empty if inputs are valid.
    """
    problems = []
    if c_F <= 0:
        problems.append(
            "Feed concentration c_F must be above 0 mg/L, otherwise there is "
            "no solute to remove."
        )
    if S <= 0:
        problems.append("Solution volume S must be above 0 L.")
    if M <= 0:
        problems.append(
            "Adsorbent mass M must be above 0 g. With no adsorbent, the slope "
            "−S/M is undefined and nothing can be adsorbed."
        )
    if q_F < 0:
        problems.append("Initial loading q_F cannot be negative.")
    return problems
