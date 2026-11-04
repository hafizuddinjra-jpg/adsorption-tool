"""Mechanism for Adsorption: three contacting modes and a comparison table.

This page holds the text, sliders and layout. The science is in
modules/isotherms.py and the figures are in modules/mechanism_plots.py.
"""

import pandas as pd
import streamlit as st

from modules.isotherms import (
    freundlich,
    langmuir,
    linear,
    percent_removal,
    solve_batch_equilibrium,
    validate_batch_inputs,
)
from modules.mechanism_plots import (
    ADSORPTION_FACTOR,
    COUNTERCURRENT_FEED,
    END_TIME,
    MAX_STAGES,
    batch_equilibrium_plot,
    breakthrough_plot,
    breakthrough_ratio,
    breakthrough_time,
    countercurrent_comparison_plot,
    countercurrent_schematic,
    fixed_bed_column,
    fixed_bed_schematic,
    single_stage_adsorbent_ratio,
    stage_concentrations,
    stirred_tank_schematic,
)

st.set_page_config(page_title="Mechanism for Adsorption", layout="wide")

# Hide the Plotly toolbar. Students use the sliders, not the zoom tools.
CHART_CONFIG = {"displayModeBar": False}


def show_chart(fig, key):
    """Draw a figure at full width. Each chart needs its own key across tabs."""
    # Streamlit's default chart text is a pale grey, which is hard to read on the
    # small diagram labels, so the text colour follows the page theme instead.
    # The theme in .streamlit/config.toml wins; without one, follow the viewer's.
    base = st.get_option("theme.base") or st.context.theme.type
    if base == "dark":
        ink = "#fafafa"
    else:
        ink = st.get_option("theme.textColor") or "#31333f"
    fig.update_layout(font_color=ink)
    fig.update_xaxes(title_font_color=ink)
    fig.update_yaxes(title_font_color=ink)
    st.plotly_chart(fig, width="stretch", key=key, config=CHART_CONFIG)


def show_pros_and_cons(advantages, disadvantages, applications):
    """Show the three bullet lists that every tab shares, side by side."""
    sections = [
        ("Advantages", advantages),
        ("Disadvantages", disadvantages),
        ("Typical applications", applications),
    ]
    for column, (title, items) in zip(st.columns(3), sections):
        with column:
            st.markdown(f"#### {title}")
            st.markdown("\n".join(f"- {item}" for item in items))


# ---------------------------------------------------------------------------
# Tab 1: stirred tank
# ---------------------------------------------------------------------------


def stirred_tank_demo():
    """Sliders for one batch stage, and the plot of its equilibrium point."""
    st.markdown("#### Try it: find the equilibrium point")
    st.caption(
        "The Freundlich defaults reproduce Example 12.2-1 from the lecture slides "
        "(phenol on activated carbon), scaled to 1 L and 1.4 g with the same S/M. "
        "The adsorbent starts fresh, so $q_F$ = 0 mg/g."
    )

    controls, results = st.columns([1, 2])
    with controls:
        c_F = st.slider(
            "Feed concentration $c_F$ (mg/L)", 0.0, 500.0, 210.0, 5.0, key="st_c_F"
        )
        S = st.slider("Solution volume $S$ (L)", 0.0, 5.0, 1.0, 0.1, key="st_S")
        M = st.slider("Adsorbent mass $M$ (g)", 0.0, 5.0, 1.4, 0.1, key="st_M")
        isotherm_name = st.radio(
            "Isotherm",
            ["Linear", "Freundlich", "Langmuir"],
            index=1,
            horizontal=True,
            key="st_isotherm",
        )

        # The lower limits stay above 0 so an isotherm can never divide by zero.
        if isotherm_name == "Linear":
            K = st.slider("$K$ (L/g)", 0.1, 10.0, 1.0, 0.1, key="st_linear_K")

            def isotherm(c):
                return linear(c, K)

        elif isotherm_name == "Freundlich":
            K = st.slider(
                "$K$ (mg/g)(L/mg)$^n$", 1.0, 100.0, 41.0, 1.0, key="st_freundlich_K"
            )
            n = st.slider("$n$ (dimensionless)", 0.05, 1.0, 0.23, 0.01, key="st_n")

            def isotherm(c):
                return freundlich(c, K, n)

        else:
            q0 = st.slider("$q_0$ (mg/g)", 10.0, 300.0, 150.0, 5.0, key="st_q0")
            K = st.slider("$K$ (mg/L)", 1.0, 100.0, 30.0, 1.0, key="st_langmuir_K")

            def isotherm(c):
                return langmuir(c, q0, K)

    with results:
        problems = validate_batch_inputs(c_F, S, M)
        if problems:
            # Plain if/else here, because st.stop() would also hide the other
            # tabs and the comparison table.
            for problem in problems:
                st.warning(problem)
        else:
            c_eq, q_eq = solve_batch_equilibrium(c_F, S, M, isotherm)
            metrics = st.columns(3)
            metrics[0].metric("Equilibrium c (mg/L)", f"{c_eq:.1f}")
            metrics[1].metric("Equilibrium q (mg/g)", f"{q_eq:.1f}")
            metrics[2].metric("Removal (%)", f"{percent_removal(c_F, c_eq):.1f}")
            show_chart(
                batch_equilibrium_plot(c_F, S, M, isotherm, c_eq, q_eq),
                "st_equilibrium_plot",
            )
            st.caption(f"Operating line slope: −S/M = −{S / M:.2f} L/g.")


def stirred_tank_tab():
    """Single-stage batch contacting."""
    schematic, explanation = st.columns([3, 2])
    with schematic:
        show_chart(stirred_tank_schematic(), "st_schematic")
    with explanation:
        st.markdown("#### How it works")
        st.markdown(
            "1. Fill a tank with a known volume $S$ of solution at concentration "
            "$c_F$.\n"
            "2. Add a mass $M$ of adsorbent and stir, so every particle touches "
            "the solution.\n"
            "3. Solute moves onto the solid. The fluid concentration $c$ falls "
            "and the loading $q$ rises until they reach equilibrium.\n"
            "4. Stop stirring and separate the solid by filtering or settling."
        )

    st.markdown("#### Governing equations")
    st.markdown("Solute balance: what enters the tank equals what is there at the end.")
    st.latex(r"q_F M + c_F S = q M + c S")
    st.markdown("Rearranged, this is the operating line, with a slope of $-S/M$:")
    st.latex(r"q = q_F + \frac{S}{M}\,(c_F - c)")
    st.markdown("The isotherm gives the equilibrium relationship. Three common forms:")
    st.latex(r"q = K c \quad \text{(Linear, Henry's law, for dilute solutions)}")
    st.latex(r"q = K c^{\,n} \quad \text{(Freundlich)}")
    st.latex(r"q = \frac{q_0\, c}{K + c} \quad \text{(Langmuir)}")
    st.caption(
        "In each form, K (and n or $q_0$) are constants found by experiment at a "
        "fixed temperature."
    )
    st.markdown(
        "The answer lies where the operating line crosses the isotherm, because "
        "only that point satisfies both. The removal is then:"
    )
    st.latex(r"\%\ \text{removal} = \frac{c_F - c}{c_F} \times 100")

    show_pros_and_cons(
        advantages=[
            "Simple, low-cost equipment",
            "Works well with fine powdered adsorbents",
            "Easy to run in the lab, so it suits isotherm tests",
        ],
        disadvantages=[
            "One equilibrium stage limits the removal",
            "All the adsorbent ends in contact with the final, dilute fluid, so "
            "its capacity is under-used",
            "Solid must be separated from the fluid afterwards",
        ],
        applications=[
            "Decolourising sugar solutions and vegetable oils",
            "Small-volume water and wastewater treatment",
            "Laboratory screening of adsorbents",
        ],
    )

    st.divider()
    stirred_tank_demo()


# ---------------------------------------------------------------------------
# Tab 2: continuous countercurrent
# ---------------------------------------------------------------------------


def countercurrent_demo():
    """Stage slider, animated diagram and the illustrative comparison plot."""
    st.markdown("#### Try it: add stages")
    st.caption(
        "Illustrative calculation, not a design method. It assumes ideal stages, a "
        f"linear isotherm, $c_F$ = {COUNTERCURRENT_FEED:.0f} mg/L and a fixed "
        f"adsorption factor $A$ = {ADSORPTION_FACTOR}."
    )

    n_stages = st.slider(
        "Number of stages $N$", 1, MAX_STAGES, 3, 1, key="cc_stages"
    )
    st.markdown(
        "Press **Play** to watch the streams. Fluid dots fade as solute is removed. "
        "Adsorbent dots start faint and grow stronger as they load up. The value in "
        "each stage is the concentration of the fluid leaving it."
    )
    show_chart(countercurrent_schematic(n_stages, animate=True), "cc_animation")

    c_stages = stage_concentrations(COUNTERCURRENT_FEED, ADSORPTION_FACTOR, n_stages)
    c_out = float(c_stages[-1])
    ratio = single_stage_adsorbent_ratio(COUNTERCURRENT_FEED, c_out, ADSORPTION_FACTOR)

    chart, summary = st.columns([2, 1])
    with chart:
        show_chart(countercurrent_comparison_plot(n_stages), "cc_comparison")
    with summary:
        st.metric("Outlet concentration (mg/L)", f"{c_out:.1f}")
        st.metric("Removal (%)", f"{percent_removal(COUNTERCURRENT_FEED, c_out):.1f}")
        st.metric("Single-stage adsorbent ratio", f"{ratio:.1f}×")
        st.caption(
            "A single stage would need this many times as much adsorbent for the "
            "same removal."
        )


def countercurrent_tab():
    """Multi-stage contacting with fluid and adsorbent flowing in opposite ways."""
    schematic, explanation = st.columns([3, 2])
    with schematic:
        show_chart(countercurrent_schematic(3), "cc_schematic")
    with explanation:
        st.markdown("#### How it works")
        st.markdown(
            "Fluid and adsorbent flow in opposite directions through a series of "
            "stages. Fresh adsorbent meets the most dilute fluid, so it can still "
            "pull out the last of the solute. Nearly full adsorbent meets the "
            "strongest fluid, so it can still pick up more.\n\n"
            "This keeps a driving force in every stage. For the same removal, it "
            "needs less adsorbent than a single stage."
        )

    st.markdown("#### Governing equations")
    st.markdown(
        "Here $S$ and $M$ are flow rates, in L/min and g/min. The overall solute "
        "balance says that solute in equals solute out:"
    )
    st.latex(r"S c_F + M q_{in} = S c_{out} + M q_{out}")
    st.markdown("The operating line links the two streams passing each other:")
    st.latex(r"q = q_{in} + \frac{S}{M}\,(c - c_{out})")
    st.markdown(
        "Its slope is $+S/M$, whereas the single-stage line has a slope of $-S/M$. "
        "It runs from ($c_{out}$, $q_{in}$) at the dilute end to ($c_F$, $q_{out}$) "
        "at the strong end."
    )
    st.markdown(
        "The demo below uses a linear isotherm $q = K_{lin} c$ with fresh adsorbent "
        "($q_{in}$ = 0), which gives a simple result:"
    )
    st.latex(
        r"\frac{c_{out}}{c_F} = \frac{A - 1}{A^{N+1} - 1}"
        r"\qquad A = \frac{K_{lin} M}{S}"
    )

    show_pros_and_cons(
        advantages=[
            "Highest driving force across the process",
            "Uses less adsorbent for the same removal",
            "Runs continuously at a steady outlet quality",
        ],
        disadvantages=[
            "Moving solids is mechanically difficult",
            "Particles wear down as they move",
            "More complex equipment and control",
        ],
        applications=[
            "Carbon-in-pulp gold recovery",
            "Moving-bed and pulsed-bed carbon columns for water treatment",
            "Simulated moving beds for xylene and sugar separation",
        ],
    )

    st.divider()
    countercurrent_demo()


# ---------------------------------------------------------------------------
# Tab 3: fixed bed
# ---------------------------------------------------------------------------


def bed_status(t):
    """Describe in words what the bed is doing at time t (min)."""
    t_b = breakthrough_time()
    ratio = float(breakthrough_ratio(t))
    if t < t_b:
        return (
            f"Outlet c/c₀ = {ratio:.2f}. The MTZ is still inside the bed, so the "
            "outlet stays clean."
        )
    if ratio < 0.95:
        return (
            f"Outlet c/c₀ = {ratio:.2f}. The MTZ has reached the outlet, so solute "
            "is breaking through. A real bed would already be stopped."
        )
    return (
        f"Outlet c/c₀ = {ratio:.2f}. The whole bed is saturated, so solute passes "
        "straight through."
    )


def fixed_bed_demo():
    """Time slider driving the column and the breakthrough curve together."""
    st.markdown("#### Try it: watch the MTZ move")
    st.caption(
        "Illustrative only. Both views come from one logistic function for a bed of "
        "height $H_T$ = 100 cm, not from real data."
    )

    t = st.slider(
        "Time since the start of the run (min)",
        0,
        int(END_TIME),
        50,
        1,
        key="fb_time",
    )
    column, curve = st.columns([2, 3])
    with column:
        show_chart(fixed_bed_column(t), "fb_column")
    with curve:
        show_chart(breakthrough_plot(t), "fb_breakthrough")
    st.markdown(f"**At t = {t} min:** {bed_status(t)}")


def fixed_bed_tab():
    """Packed column with fluid flowing through a stationary adsorbent."""
    schematic, explanation = st.columns([3, 2])
    with schematic:
        show_chart(fixed_bed_schematic(), "fb_schematic")
    with explanation:
        st.markdown("#### How it works")
        st.markdown(
            "Fluid flows through a column packed with adsorbent while the solid "
            "stays still. The bed near the inlet fills up first and becomes the "
            "**saturated zone**. Just ahead of it is the **mass transfer zone "
            "(MTZ)**, where the concentration falls from $c_0$ to almost zero. "
            "Further on, the **fresh zone** has not yet taken up any solute.\n\n"
            "The MTZ moves down the bed with time. While it stays inside the bed, "
            "the outlet is almost free of solute."
        )

    st.markdown("#### The breakthrough curve")
    st.markdown(
        "A breakthrough curve plots the outlet ratio $c/c_0$ against time. It stays "
        "near zero, then rises in an S shape when the MTZ reaches the outlet. The "
        "**breakthrough time** $t_b$ is when the outlet reaches its allowed limit, "
        "often $c/c_0$ between 0.01 and 0.05. The bed is stopped near $t_b$, then "
        "regenerated or replaced."
    )

    st.markdown("#### Key ideas")
    st.markdown(
        "- $t_t$ is the **time equivalent to total capacity**: how long the feed "
        "would take to fill the whole bed if all solute were captured.\n"
        "- $t_u$ is the **time equivalent to usable capacity**: the same idea, but "
        "only up to $t_b$.\n"
        "- $H_B$ is the **used bed length**: the part of the bed filled by $t_b$.\n"
        "- $H_{UNB}$ is the **unused bed length**: the part wasted when the bed is "
        "stopped, which is about half the MTZ."
    )
    st.latex(
        r"t_t = \int_0^\infty \left(1 - \frac{c}{c_0}\right) dt"
        r"\qquad t_u = \int_0^{t_b} \left(1 - \frac{c}{c_0}\right) dt"
    )
    st.latex(
        r"H_B = \frac{t_u}{t_t}\, H_T"
        r"\qquad H_{UNB} = \left(1 - \frac{t_u}{t_t}\right) H_T"
    )
    st.info("Full design calculation is in the Design Fixed Bed section.")

    show_pros_and_cons(
        advantages=[
            "No moving solids, so the equipment is simple",
            "Can reach very low outlet concentrations",
            "Adsorbent can often be regenerated in place",
        ],
        disadvantages=[
            "Runs in cycles, so continuous service needs two or more beds",
            "The unused part of the MTZ is lost capacity in every cycle",
            "Pressure drop, and fouling by suspended solids",
        ],
        applications=[
            "Drinking water treatment with activated carbon",
            "Solvent vapour recovery from air",
            "Drying gases with molecular sieves or alumina",
        ],
    )

    st.divider()
    fixed_bed_demo()


# ---------------------------------------------------------------------------
# Page layout
# ---------------------------------------------------------------------------

st.title("Mechanism for Adsorption")
st.write(
    "Adsorption is a separation process in which a solute moves from a fluid and "
    "attaches to the surface of a porous solid. The solute keeps transferring until "
    "equilibrium is reached, when the amount on the solid stops changing. At that "
    "point the fluid concentration and the solid loading are linked by an isotherm. "
    "How the fluid and solid are brought together decides how well the solid is used, "
    "and the tabs below compare three ways of doing this."
)

terms = st.columns(4)
terms[0].markdown("**Adsorbent**  \nThe porous solid that takes up the solute, such as activated carbon.")
terms[1].markdown("**Adsorbate**  \nThe solute removed from the fluid, such as phenol.")
terms[2].markdown("**Equilibrium loading, q**  \nSolute held per mass of adsorbent at equilibrium, in mg/g.")
terms[3].markdown("**Fluid concentration, c**  \nSolute per volume of fluid, in mg/L.")

tab_stirred, tab_countercurrent, tab_fixed = st.tabs(
    ["Stirred Tank", "Continuous Countercurrent", "Fixed Bed"]
)
with tab_stirred:
    stirred_tank_tab()
with tab_countercurrent:
    countercurrent_tab()
with tab_fixed:
    fixed_bed_tab()

st.divider()
st.subheader("Comparing the three modes")
comparison = pd.DataFrame(
    {
        "Contacting mode": ["Stirred tank", "Continuous countercurrent", "Fixed bed"],
        "Operation type": [
            "Batch",
            "Continuous",
            "Batch/cyclic (fluid flows continuously, adsorbent stays in place)",
        ],
        "Adsorbent use efficiency": [
            "Low: all solid ends in equilibrium with the final, dilute fluid",
            "High: fresh solid meets the most dilute fluid",
            "Medium to high: only the MTZ is left partly unused",
        ],
        "Equipment": [
            "Stirred tank plus filter or settler",
            "Staged contactors or a moving bed, with solids handling",
            "Packed column, usually two or more in rotation",
        ],
        "Typical use": [
            "Small volumes, powdered adsorbent, lab tests",
            "Large, steady flows that use a lot of adsorbent",
            "Water treatment, gas drying, solvent recovery",
        ],
        "Main limitation": [
            "One equilibrium stage limits the removal",
            "Moving solids is complex and wears the particles",
            "Must stop to regenerate, and runs in cycles",
        ],
    }
).set_index("Contacting mode")
st.table(comparison)
